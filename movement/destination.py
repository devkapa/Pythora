from movement.coordinate import Coordinate


class Destination:

    direction = None
    coordinate: Coordinate
    message = None
    health = None

    def __init__(self, direction, coordinate, message, health):
        self.direction = direction
        self.coordinate = coordinate
        self.message = message
        self.health = health

    def get_coordinate(self):
        return self.coordinate

    def get_direction(self):
        return self.direction

    def get_health(self):
        return self.health

    def get_message(self):
        return self.message


def get_index(direction):
    match direction:
        case "north":
            return 0
        case "east":
            return 1
        case "south":
            return 2
        case "west":
            return 3
        case "up":
            return 4
        case "down":
            return 5
