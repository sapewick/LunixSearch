from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(50), unique=True, nullable=False)
    port = db.Column(db.Integer, nullable=False)
    service = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Device {self.ip_address}>"

def get_devices_from_scan(ip_range):
    result = subprocess.run(['nmap', '-p', '1-65535', ip_range], capture_output=True, text=True)
    devices = []
    
    for line in result.stdout.splitlines():
        if "Nmap scan report for" in line:
            ip_address = line.split()[-1]  # Obtiene la dirección IP
            devices.append({'ip_address': ip_address})
        elif "open" in line:
            port_info = line.split()
            port = int(port_info[0].split('/')[0])  # Extrae el número de puerto
            service = port_info[-1]  # Obtiene el nombre del servicio
            devices[-1]['port'] = port
            devices[-1]['service'] = service

    return devices

def scan_network(ip_range):
    devices = get_devices_from_scan(ip_range)

    for device_info in devices:
        ip_address = device_info['ip_address']
        port = device_info.get('port')  # Obtiene el puerto si existe
        service = device_info.get('service')  # Obtiene el servicio si existe

        # Verifica si el dispositivo ya existe en la base de datos
        existing_device = db.session.query(Device).filter_by(ip_address=ip_address).first()

        if existing_device:
            # Actualiza el registro existente
            existing_device.port = port
            existing_device.service = service
        else:
            # Crea un nuevo registro
            device = Device(ip_address=ip_address, port=port, service=service)
            db.session.add(device)

    db.session.commit()

@app.route('/scan', methods=['GET'])
def scan():
    ip_range = request.args.get('ip_range')
    if not ip_range:
        return jsonify({"error": "No se proporcionó un rango de IP"}), 400

    try:
        scan_network(ip_range)
        return jsonify({"message": "Escaneo completado con éxito"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([{"ip_address": device.ip_address, "port": device.port, "service": device.service} for device in devices])

if __name__ == '__main__':
    with app.app_context():  # Agregar el contexto de la aplicación aquí
        db.create_all()  # Crea las tablas en la base de datos si no existen
    app.run(debug=True)
