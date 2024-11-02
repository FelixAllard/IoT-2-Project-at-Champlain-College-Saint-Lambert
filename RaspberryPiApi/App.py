from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask import Response
import json
import time
import random

from Model.Sensor import Sensor

app = Flask(__name__)
CORS(app)

raspberryPiCredentials = {
    'id': '1',
    'password': 'pwd'
}

sensors = [
    Sensor(1, "Left Foot", 10.0, 20.0, 5.0, 1.2, 85.0),
    Sensor(2, "Right Foot", 15.5, 25.0, 7.8, 0.5, 60.0),
    Sensor(3, "Left Knee", 18.0, 30.0, 12.0, 22.1, 50.0),
    Sensor(4, "Right Knee", 11.0, 37.0, 32.0, 6.1, 70.0),
    Sensor(5, "Waist", 39.0, 34.0, 32.0, 3.1, 100.0)
]

@app.route('/ping', methods=['GET'])
def ping():
    current_time = datetime.now().isoformat()
    return jsonify({'message': 'pong', 'datetime': current_time}), 200

@app.route('/sensor-stream', methods=['GET'])
def stream_sensors():
    def event_stream():
        while True:
            for sensor in sensors:
                #Fake data, will have to be replaced when connecting to actual sensor data
                velocity_change = random.uniform(-1.0, 1.0)
                sensor.velocity += velocity_change

                sensor.velocity = max(0, min(sensor.velocity, 30.0))

                sensor.x += sensor.velocity * 0.1
                sensor.y += sensor.velocity * 0.1
                sensor.z += sensor.velocity * 0.1

                sensor.battery_percentage = max(sensor.battery_percentage - 0.01, 0)

            data = [sensor_to_dict(sensor) for sensor in sensors]
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(0.1)

    return Response(event_stream(), mimetype="text/event-stream")

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
    app.run(debug=True, host='0.0.0.0', port=4999)
