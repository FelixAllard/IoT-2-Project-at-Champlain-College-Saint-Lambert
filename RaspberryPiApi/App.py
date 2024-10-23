from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

from Model.Sensor import Sensor

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})

raspberryPiCredentials = {
    'id': '1',
    'password': 'pwd'
}

sensors = [
    Sensor(1, "Temperature Sensor", 10.0, 20.0, 5.0, 1.2, 85.0),
    Sensor(2, "Humidity Sensor", 15.5, 25.0, 7.8, 0.5, 60.0),
    Sensor(3, "Pressure Sensor", 18.0, 30.0, 12.0, 2.1, 50.0)
]

@app.route('/ping', methods=['GET'])
def ping():
    current_time = datetime.now().isoformat()
    return jsonify({'message': 'pong', 'datetime': current_time}), 200

@app.route('/sensors', methods=['GET'])
def get_sensors():
    return jsonify([sensor_to_dict(sensor) for sensor in sensors])

@app.route('/id', methods=['GET'])
def get_raspberry_pi_id():
    return jsonify({'id': raspberryPiCredentials['id']})

@app.route('/password', methods=['POST'])
def verify_password():
    data = request.json
    password = data.get('password')

    if (password == raspberryPiCredentials['password']):
        return jsonify({'authenticated': True}), 200
    else:
        return jsonify({'authenticated': False}), 403

def sensor_to_dict(sensor):
    return {
        'id': sensor.id,
        'name': sensor.name,
        'coordinates': {
            'x': sensor.x,
            'y': sensor.y,
            'z': sensor.z
        },
        'velocity': sensor.velocity,
        'battery_percentage': sensor.battery_percentage
    }

if __name__ == '__main__':
    app.run(debug=True, port=4999)
