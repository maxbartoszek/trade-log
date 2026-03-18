from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    share_token = db.Column(db.String(64), unique=True, nullable=True)
    trades = db.relationship('Trade', backref='user', lazy=True, cascade='all, delete-orphan')

class Trade(db.Model):
    __tablename__ = 'trades'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ticker = db.Column(db.String(20), nullable=False)
    position_type = db.Column(db.String(10), nullable=False, default='long')
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float)
    stop_limit = db.Column(db.Float)
    entry_date = db.Column(db.Date)
    exit_date = db.Column(db.Date)
    return_pct = db.Column(db.Float)
    status = db.Column(db.String(10), default='open')
    sector = db.Column(db.String(80))
    strategy = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.relationship('TradeNote', backref='trade', uselist=False, cascade='all, delete-orphan')

class TradeNote(db.Model):
    __tablename__ = 'trade_notes'
    id = db.Column(db.Integer, primary_key=True)
    trade_id = db.Column(db.Integer, db.ForeignKey('trades.id'), nullable=False)
    thesis = db.Column(db.Text)
    catalyst = db.Column(db.Text)
    risk_factors = db.Column(db.Text)
    confidence_level = db.Column(db.Integer, default=5)
    post_trade_review = db.Column(db.Text)
    mistakes = db.Column(db.Text)
    lessons = db.Column(db.Text)
