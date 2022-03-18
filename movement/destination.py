from movement.coordinate import Coordinate


class Destination:

    direction = None
    coordinate: Coordinate
    message = None
    health = None

    # Define the constructor to be called when a new Destination object is created
    def __init__(self, direction, coordinate, message, health):
        self.direction = direction
        self.coordinate = coordinate
        self.message = message
        self.health = health

    # Getters
    def get_coordinate(self):
        return self.coordinate

    def get_direction(self):
        return self.direction

    def get_health(self):
        return self.health

    def get_message(self):
        return self.message
