from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from extensions import db



class UserSetting(db.Model):
    id = Column(Integer, primary_key=True)
    risk = Column(String)
    leverage = Column(String)
    R_R = Column(String)




class Signal(db.Model):
    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    side = Column(String)
    price = Column(Float)
    time = Column(String)
    size = Column(Float)
    status = Column(String)
    time_exit = Column(String)
    price_exit = Column(Float)







