class Sensor:
    def __init__(self, sensor_id, name, x, y, z, velocity, battery_percentage):
        self.id = sensor_id
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.velocity = velocity
        self.battery_percentage = battery_percentage

    def __repr__(self):
        return (f"Sensor(Id: {self.id}, Name: {self.name}, "
                f"Coordinates: ({self.x}, {self.y}, {self.z}), "
                f"Velocity: {self.velocity}, "
                f"Battery: {self.battery_percentage}%)")


import time
import math
import numpy as np
from smbus2 import SMBus
import json
import paho.mqtt.client as mqtt

# I2C configuration
I2C_BUS = 1
ICM20948_ADDRESS = 0x68
PWR_MGMT_1 = 0x06
GYRO_CONFIG = 0x1B
ACCEL_CONFIG = 0x1C
GYRO_REGISTERS = [0x33, 0x34, 0x35, 0x36, 0x37, 0x38]
ACCEL_REGISTERS = [0x2D, 0x2E, 0x2F, 0x30, 0x31, 0x32]
MAGNETOMETER_CONTROL_REGISTER = 0x31

# Conversion factors
ACCEL_SCALE = 16384.0  # ±2g range
GYRO_SCALE = 131.0  # ±250°/s range
DT = 0.01  # Sampling interval (10ms)


class RealSensor:
    def __init__(self):
        self.position = np.array([0.0, 0.0, 0.0])
        self.velocity = np.array([0.0, 0.0, 0.0])
        self.orientation = [0.0, 0.0, 0.0]  # Roll, Pitch, Yaw
        self.battery_percentage = 100.0
        self.gyro_offsets = [0, 0, 0]
        self.accel_offsets = [0, 0, 0]
        self.bus = SMBus(I2C_BUS)
        self._initialize_sensor()
        self._calibrate_sensor()

    def _initialize_sensor(self):
        """Initialize the ICM20948 sensor."""
        self.bus.write_byte_data(ICM20948_ADDRESS, PWR_MGMT_1, 0x00)  # Wake up sensor
        self.bus.write_byte_data(ICM20948_ADDRESS, GYRO_CONFIG, 0x00)  # Set gyro to ±250°/s
        self.bus.write_byte_data(ICM20948_ADDRESS, ACCEL_CONFIG, 0x00)  # Set accel to ±2g

    def _calibrate_sensor(self, samples=100):
        """Calibrate the gyroscope and accelerometer."""
        print("Calibrating sensor... Keep it stationary.")
        gyro_sums = [0, 0, 0]
        accel_sums = [0, 0, 0]

        for _ in range(samples):
            for i in range(3):
                gyro_sums[i] += self._read_raw_data(GYRO_REGISTERS[i * 2], GYRO_REGISTERS[i * 2 + 1])
                accel_sums[i] += self._read_raw_data(ACCEL_REGISTERS[i * 2], ACCEL_REGISTERS[i * 2 + 1])
            time.sleep(0.01)

        self.gyro_offsets = [s // samples for s in gyro_sums]
        self.accel_offsets = [s // samples for s in accel_sums]

        print(f"Gyro Offsets: {self.gyro_offsets}")
        print(f"Accel Offsets: {self.accel_offsets}")

    def _read_raw_data(self, high_reg, low_reg):
        """Combine high and low bytes to form a 16-bit signed integer."""
        high = self.bus.read_byte_data(ICM20948_ADDRESS, high_reg)
        low = self.bus.read_byte_data(ICM20948_ADDRESS, low_reg)
        value = (high << 8) | low
        return value if value < 32768 else value - 65536

    def _low_pass_filter(self, data, alpha=0.1):
        """Apply a low-pass filter to smooth out data."""
        return alpha * data + (1 - alpha) * data

    def _update_position(self, accel_data):
        """Update position and velocity based on accelerometer data."""
        accel_data = self._low_pass_filter(accel_data)
        accel_magnitude = np.linalg.norm(accel_data)

        if abs(accel_magnitude - 9.81) < 1:  # Stationary threshold
            self.velocity = np.array([0.0, 0.0, 0.0])

        self.velocity += accel_data * DT
        self.position += self.velocity * DT

    def read_sensor(self):
        """Read and update sensor data."""
        # Read accelerometer data
        accel_data = np.array([
            (self._read_raw_data(ACCEL_REGISTERS[0], ACCEL_REGISTERS[1]) - self.accel_offsets[0]) / ACCEL_SCALE,
            (self._read_raw_data(ACCEL_REGISTERS[2], ACCEL_REGISTERS[3]) - self.accel_offsets[1]) / ACCEL_SCALE,
            (self._read_raw_data(ACCEL_REGISTERS[4], ACCEL_REGISTERS[5]) - self.accel_offsets[2]) / ACCEL_SCALE
        ]) * 9.81

        # Read gyroscope data
        gyro_data = np.array([
            (self._read_raw_data(GYRO_REGISTERS[0], GYRO_REGISTERS[1]) - self.gyro_offsets[0]) / GYRO_SCALE,
            (self._read_raw_data(GYRO_REGISTERS[2], GYRO_REGISTERS[3]) - self.gyro_offsets[1]) / GYRO_SCALE,
            (self._read_raw_data(GYRO_REGISTERS[4], GYRO_REGISTERS[5]) - self.gyro_offsets[2]) / GYRO_SCALE
        ])

        # Update orientation
        accel_angle = math.atan2(accel_data[1], accel_data[2]) * (180 / math.pi)
        gyro_angle = self.orientation[1] + gyro_data[0] * DT
        self.orientation[1] = self._low_pass_filter(accel_angle * 0.98 + gyro_angle * 0.02)

        # Update position
        self._update_position(accel_data)

        # Return sensor data as a dictionary
        def send_data_to_mqtt(position, velocity, orientation, high, delta_v, topic, broker_address='localhost',
                              port=1883):
            # Prepare the payload
            payload = {
                'position': {
                    'x': round(position[0], 2),
                    'y': round(position[1], 2),
                    'z': round(position[2], 2)
                },
                'velocity': round(np.linalg.norm(velocity), 2),  # Assuming velocity is a vector
                'orientation': {
                    'pitch': round(orientation[1], 2)
                },
                'high': high,  # Assuming 'high' is a numerical value
                'deltaV': delta_v  # Assuming 'deltaV' is a numerical value
            }

            # Convert the payload to a JSON string
            json_payload = json.dumps(payload)

            # Initialize the MQTT client
            client = mqtt.Client()

            try:
                # Connect to the MQTT broker
                client.connect(broker_address, port, 60)

                # Publish the message to the specified topic
                client.publish(topic, json_payload)
                print(f"Data sent to topic '{topic}': {json_payload}")

            except Exception as e:
                print(f"Failed to send data to MQTT: {e}")

            finally:
                # Disconnect from the broker
                client.disconnect()

    def __del__(self):
        """Ensure the bus is closed on deletion."""
        self.bus.close()
