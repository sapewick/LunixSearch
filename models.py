from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(39), unique=True, nullable=False)  # Soporte para IPv4 e IPv6
    port = db.Column(db.Integer, nullable=False)
    service = db.Column(db.String(100))  # Aumentado a 100 por si los nombres de los servicios son más largos

    def __repr__(self):
        return f"<Device {self.ip_address}:{self.port} - {self.service}>"

class ScanHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scan_time = db.Column(db.DateTime, default=datetime.utcnow)
    results = db.Column(db.Text)  # Si quieres almacenar como texto plano
    # Si prefieres almacenar los resultados como JSON:
    # results = db.Column(db.JSON)  # Dependiendo de tu versión de SQLAlchemy

    def __repr__(self):
        return f"<ScanHistory {self.scan_time}>"

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(100))
    device_type = db.Column(db.String(50))  # Considerar Enum si tiene valores limitados
    location = db.Column(db.String(100))  # Considerar Enum si tiene valores limitados

    def __repr__(self):
        return f"<Inventory {self.device_name} ({self.device_type}) at {self.location}>"
