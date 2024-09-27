from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import subprocess

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'kiritachan'  # Necesario para usar sesiones y mensajes
db = SQLAlchemy(app)

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(39), unique=True, nullable=False)  # Soporte para IPv4 e IPv6
    port = db.Column(db.Integer, nullable=False)
    service = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"<Device {self.ip_address}:{self.port} - {self.service}>"

class ScanHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_range = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"<ScanHistory {self.ip_range} at {self.timestamp}>"

def get_devices_from_scan(ip_range):
    try:
        result = subprocess.run(['rustscan', '-a', ip_range, '--ulimit', '5000'], capture_output=True, text=True)
        result.check_returncode()  # Lanza un error si el código de retorno es diferente de cero
    except subprocess.CalledProcessError as e:
        flash(f"Error al ejecutar Rustscan: {e}", "error")
        return []

    print(f"Resultado de Rustscan: {result.stdout}")  # Muestra la salida de Rustscan

    devices = []
    for line in result.stdout.splitlines():
        if "Open" in line:
            parts = line.split()
            ip_address = parts[0]  # Obtiene la dirección IP
            port = int(parts[1].split('/')[0])  # Extrae el número de puerto
            service = parts[-1]  # Obtiene el nombre del servicio
            devices.append({'ip_address': ip_address, 'port': port, 'service': service})

    return devices

def scan_network(ip_range):
    devices = get_devices_from_scan(ip_range)

    if not devices:  # Si no se encuentran dispositivos
        print(f"No se encontraron dispositivos en el rango: {ip_range}")

    for device_info in devices:
        ip_address = device_info['ip_address']
        port = device_info.get('port')
        service = device_info.get('service')

        existing_device = db.session.query(Device).filter_by(ip_address=ip_address).first()

        if existing_device:
            existing_device.port = port
            existing_device.service = service
        else:
            device = Device(ip_address=ip_address, port=port, service=service)
            db.session.add(device)

    # Registrar el escaneo en el historial
    scan_entry = ScanHistory(ip_range=ip_range, timestamp=datetime.now())
    db.session.add(scan_entry)
    db.session.commit()

    print(f"Dispositivos escaneados: {devices}")  # Muestra los dispositivos encontrados

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    ip_range = request.form.get('ip_range')

    # Realiza el escaneo de red
    try:
        devices = scan_network(ip_range)  # Asegúrate de que esta función devuelva una lista de diccionarios
        flash(f"Escaneo completado. Se encontraron {len(devices)} dispositivos.", "success")  # Mensaje de éxito
    except Exception as e:
        flash(f"Error durante el escaneo: {str(e)}", "error")
        return redirect(url_for('index'))  # Redirige a la página principal en caso de error

    return redirect(url_for('scan_results'))  # Redirige a la página de resultados del escaneo

@app.route('/scan_results', methods=['GET'])
def scan_results():
    devices = Device.query.all()  # Obtener todos los dispositivos escaneados
    history = ScanHistory.query.order_by(ScanHistory.timestamp.desc()).all()  # Obtener historial de escaneos
    return render_template('scan_results.html', devices=devices, history=history)

@app.route('/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([{"ip_address": device.ip_address, "port": device.port, "service": device.service} for device in devices])

@app.route('/history', methods=['GET'])
def history():
    histories = ScanHistory.query.order_by(ScanHistory.timestamp.desc()).all()
    return render_template('scan_history.html', histories=histories)

@app.route('/inventory', methods=['GET'])
def inventory():
    devices = Device.query.all()
    return render_template('inventory.html', devices=devices)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas en la base de datos si no existen
    app.run(debug=True)
