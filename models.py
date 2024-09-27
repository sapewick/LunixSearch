from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(15), unique=True, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    service = db.Column(db.String(50))

class ScanHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_time = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.Column(db.Text)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    device_type = db.Column(db.String(50))
    location = db.Column(db.String(100))
