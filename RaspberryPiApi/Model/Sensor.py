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