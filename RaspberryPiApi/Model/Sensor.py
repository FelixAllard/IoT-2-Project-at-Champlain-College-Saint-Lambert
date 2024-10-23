class Sensor:
    def __init__(self, sensor_id, name, x, y, z, velocity, battery_percentage):
        self.id = sensor_id                # Unique identifier for the sensor
        self.name = name                   # Name of the sensor
        self.x = x                         # X coordinate
        self.y = y                         # Y coordinate
        self.z = z                         # Z coordinate
        self.velocity = velocity           # Velocity of the sensor
        self.battery_percentage = battery_percentage  # Battery percentage of the sensor

    def __repr__(self):
        return (f"Sensor(Id: {self.id}, Name: {self.name}, "
                f"Coordinates: ({self.x}, {self.y}, {self.z}), "
                f"Velocity: {self.velocity}, "
                f"Battery: {self.battery_percentage}%)")