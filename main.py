import math, json
from pybit import usdt_perpetual
from datetime import datetime
from extensions import db
from models import UserSetting, Signal

with open('config.json') as f:
		config = json.load(f)

api_key = config['api_key']
api_secret = config['api_secret']


class ByBit:
    def __init__(self):
        self.run = False
        self.ENDPOINT = 'https://api-testnet.bybit.com'
        self.api_key = api_key
        self.api_secret = api_secret


    def _try_request(self, method: str, **kwargs):
        session = usdt_perpetual.HTTP(self.ENDPOINT, api_key=self.api_key, api_secret=self.api_secret)
        try:
            res = session.set_leverage(symbol=kwargs.get('symbol'), buy_leverage=self.leverage, sell_leverage=self.leverage)
        except:
            pass
        try:
            res = session.position_mode_switch(symbol=kwargs.get('symbol'), mode="MergedSingle")
        except:
            pass
        try:
            if method=='get_wallet_balance':
                res = session.get_wallet_balance(coin=kwargs.get('coin'))
            elif method=='my_position':
                res = session.my_position(symbol=kwargs.get('symbol'))
            elif method=='place_active_order':
                print('.............................................................')
                res = session.place_active_order(symbol=kwargs.get('symbol'), 
                                                    side=kwargs.get('side'), 
                                                    order_type=kwargs.get('order_type', "Market"), 
                                                    qty=kwargs.get('qty'), 
                                                    price=kwargs.get('price', None), 
                                                    stop_loss=kwargs.get('stop_loss', None), 
                                                    time_in_force=kwargs.get('time_in_force', "GoodTillCancel"), 
                                                    reduce_only=kwargs.get('reduce_only'), 
                                                    close_on_trigger=kwargs.get('close_on_trigger', False),
                                                    #order_link_id = kwargs.get('symbol')+'-'+kwargs.get('side')+'-'+str(kwargs.get('qty')),
                                                    position_idx=0)
            elif method=='query_symbol':
                res = session.query_symbol()
                
            elif method=='set_trading_stop':
                    res = session.set_trading_stop(symbol=kwargs.get('symbol'), 
                                                    side=kwargs.get('side'), # Side of the open position
                                                    stop_loss=kwargs.get('stop_loss', None),
                                                    take_profit=kwargs.get('take_profit', None),
                                                    tp_size=kwargs.get('tp_size', None),
                                                    sl_size=kwargs.get('sl_size', None),
                                                    position_idx=0)

        except Exception as e:
            return {"success": False,"error": str(e)}

        if res['ret_code']: return {"success": False,"error": res['ret_msg']}
        else: res['success'] = True
        return res

    def entry_position(self, **kwargs):
        symbol = kwargs.get('symbol')
        price = float(kwargs.get('price'))
        side = kwargs.get('side')
        r = self._try_request('get_wallet_balance', coin="USDT")
        if not r['success']: return r
        free_margin = r['result']['USDT']['available_balance']
        print('margin:  ', free_margin)
        cost = (self.risk * free_margin ) / 100
        qty = (cost * self.leverage) / price 
        size = math.trunc(qty*1000)/1000
        print('cost/size:.........', cost, size)
        res = self._try_request('place_active_order', 
                            symbol=symbol, 
                            side=side, 
                            order_type='Market', 
                            qty=size, 
                            time_in_force="GoodTillCancel", 
                            reduce_only=False, 
                            close_on_trigger=False)
        if not res['success']: print(res); return res
        print(res)
        return res


    def exit_position(self, ticker, position_side, position_size):
        close_side = 'Sell' if position_side == 'Buy' else 'Buy'
        r = self._try_request('place_active_order', 
                            symbol=ticker,
                            side=close_side,
                            order_type="Market",
                            qty=position_size,
                            price=None,
                            time_in_force="GoodTillCancel",
                            reduce_only=True,
                            close_on_trigger=False)

        if not r['success']:
            return r
        return {"success": True}



bybit = ByBit()

#print(bybit.extreme(symbol="ADAUSDT", side="Sell"))

def check_input():
	print("check user input")
	user = db.session.execute(db.select(UserSetting).order_by(UserSetting.id.desc())).scalar()
	if not user: return None
	if user.risk and user.leverage:
		bybit.run = True
		bybit.leverage = float(user.leverage)
		bybit.risk = float(user.risk)
		print("ok")


def handle_webhook(payload: dict):
    check_input()
    if not bybit.run:
        print("No input. please set params!")
        return "please set params!"

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(payload)
    ticker = payload['ticker']
    price = payload['price']
    side = payload['action']
    side = 'Buy' if side == 'Long' else "Sell"
    ticker = ticker.split('.')[0]
    message = payload['message']

    # if position['size'] and message=='entry':
    #     print(f"we have position on {ticker}")
    #     return '200'

    if message == 'entry':
        order = bybit.entry_position(symbol=ticker, price=price, side=side, order_type="Market", reduce_only=False )
        if not order['success']: 
            print("position Not success. ")
            return order

        position = bybit._try_request(method='my_position', symbol=ticker)['result'][0]
        # Db
        from app import app
        with app.app_context():
            pos = Signal()
            pos.symbol = ticker
            pos.side = side
            pos.time = now
            pos.size = float(position['size'] )
            pos.price = float(position['entry_price'] )
            pos.status = 'entry'
            db.session.add(pos)
            db.session.commit()

    elif message == 'exit':
        position = bybit._try_request(method='my_position', symbol=ticker)
        position = position['result'][0]
        position_size = position['size']
        order = bybit.exit_position(ticker, position_side=position['side'], position_size=position_size)
        print("exit position: ", order)

        from app import app
        with app.app_context():
            pos = db.session.execute(db.select(Signal).where(Signal.symbol==ticker).order_by(Signal.id.desc())).scalar()
            pos.status = "closed"
            pos.time_exit = now
            pos.price_exit = float(price)
            db.session.commit()
        return '200'