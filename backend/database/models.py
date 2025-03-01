from flask_sqlalchemy import SQLAlchemy
from numpy.ma.extras import unique

db = SQLAlchemy()

class Stock(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    symbol=db.Column(db.String(10),unique=True)
    company_name=db.Column(db.String(100))

class Portfolio(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    stock_id=db.Column(db.Integer,db.ForeignKey('stock.id'))
    shares=db.Column(db.Float)
