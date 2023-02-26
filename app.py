import json
from flask import Flask, request, render_template
from forms import UserSettingForm
from models import UserSetting, Signal
from main import  handle_webhook


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ByBit.db'
app.config['SECRET_KEY'] = 'abc123def%&*SHA16x16'

from extensions import db
db.init_app(app)


@app.route('/', methods=['POST', 'GET'])
def index():
	form = UserSettingForm(request.form)

	user = db.session.execute(db.select(UserSetting).order_by(UserSetting.id.desc())).scalar()
	if request.method == "POST":
		data = request.form.to_dict()
		#print(data)

		risk = data['risk']
		leverage = data['leverage']
		
		if not user:
			setting = UserSetting()
			setting.risk = risk
			setting.leverage = leverage
			db.session.add(setting)
			db.session.commit()
		else:
			if risk: user.risk = risk
			if leverage: user.leverage = leverage
			db.session.commit()

	user = db.session.execute(db.select(UserSetting).order_by(UserSetting.id.desc())).scalar()
	orders = db.session.execute(db.select(Signal).limit(10).order_by(Signal.id.desc())).scalars()
	return render_template("index.html", form=form, orders=orders, user=user)
	

@app.route("/webhook", methods=['POST'])
def webhook():
	
	webhook_passphrase = "SHA16x16"
	data = json.loads(request.data)
	
	if 'passphrase' not in data.keys():
		return {
		"success": False,
		"message": "no passphrase entered"
		}

	if data['passphrase'] != webhook_passphrase:
		return {
		"success": False,
		"message": "invalid passphrase"
		}

	orders = handle_webhook(data)
	return "200"

with app.app_context():
	db.create_all()



if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0', port=5000)

