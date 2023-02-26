import requests
import json


webhook_url = "http://127.0.0.1:5000/webhook"
#webhook_url = "http://45.195.200.119:80/webhook"
webhook_url = "http://49.12.241.179:80/webhook"
#webhook_url = "http://188.34.147.80:80/webhook"
#webhook_url = "http://imanadeli.pythonanywhere.com/webhook"


data = {
    "passphrase": "kh321",
    "time": "{{timenow}}",
    "exchange": "{{exchange}}",
    "ticker": "{{ticker}}",
    "bar": {
        "time": "{{time}}",
        "open": "{{open}}",
        "high": "{{high}}",
        "low": "{{low}}",
        "close": "{{close}}",
        "volume": "{{volume}}"
    },  
    "strategy": {
        "position_size": "{{strategy.position_size}}",
        "order_action": "{{strategy.order.action}}",
        "order_contracts": "{{strategy.order.contracts}}",
        "order_price": "{{strategy.order.price}}",
        "order_id": "{{strategy.order.id}}",
        "message" : "{{strategy.order.alert_message}}",
        "market_position": "{{strategy.market_position}}",
        "market_position_size": "{{strategy.market_position_size}}",
        "prev_market_position": "{{strategy.prev_market_position}}",
        "prev_market_position_size": "{{strategy.prev_market_position_size}}"
    }
}


data = {
	'passphrase': 'SHA16x16',
    'time':'{{timenow}}',
    'ticker': '{{ticker}}',
    'action': '{{strategy.order.action}}',
    'price': '{{strategy.order.price}}',
    'message' : '{{strategy.order.alert_message}}',
    }


data = {
	"passphrase": "SHA16x16",
    "time":"2022-03-01:12z",
    "ticker": "AAVEUSDT",
    "action": "Long",
    "price": "54.0",
    "message": "SL"
    }



res = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
print(res)
#res = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'}, proxies=proxies)


#res = requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})

#print(res)


