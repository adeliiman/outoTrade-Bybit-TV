from flask_wtf import FlaskForm
from wtforms import  SubmitField, StringField, SelectField


class UserSettingForm(FlaskForm):
    risk = StringField()
    leverage = StringField()
    R_R = StringField()
    submit = SubmitField()


