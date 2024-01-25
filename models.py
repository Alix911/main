from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False,unique=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    blocks = db.Column(db.Integer,server_default='0')
    is_admin = db.Column(db.Boolean,server_default='0')


class Logs(db.Model):
    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    priority = db.Column(db.String(255),default="Low") 
    color = db.Column(db.String(255),default="primary")

    

class Rules(db.Model):
    rule_id = db.Column(db.Integer, primary_key=True)
    rule = db.Column(db.String(255), unique=True, nullable=False)

class Alerts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,nullable  =False)
    message = db.Column(db.String(255),nullable=False)
    time = db.Column(db.DateTime, nullable=False)

class BannedIPAddress(db.Model):
    ip_id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)

class BannedCountries(db.Model):
    country_id = db.Column(db.Integer, primary_key=True) 
    rule_id = db.Column(db.Integer, nullable=False)
    country = db.Column(db.String(120), nullable=False)

class BannedBrowsers(db.Model):
    browser_id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, nullable=False)
    browser = db.Column(db.String(30), nullable=False)

class AllowedTime(db.Model):
    time_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer ,unique=True,nullable=False)
    rule_id = db.Column(db.Integer, nullable=False)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)

class AllowedTries(db.Model):
    try_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer ,unique=True,nullable=False)
    rule_id = db.Column(db.Integer, nullable=False)
    tries = db.Column(db.Integer, nullable=False,server_default="5")
    

class Counter(db.Model):
    counter_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"),unique=True,nullable=False)
    banned_browser_count = db.Column(db.Integer,  nullable=False,server_default="0")
    suspicious_ip_count = db.Column(db.Integer, nullable=False,server_default="0")
    banned_country_count = db.Column(db.Integer, nullable=False,server_default="0")
    allowed_tries_break_count = db.Column(db.Integer,  nullable=False,server_default="0")
    allowed_time_break_count = db.Column(db.Integer,nullable=False,server_default="0")


