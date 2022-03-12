class Direction:

    uuid = None
    message = None
    health = None

    def __init__(self, uuid, message, health):
        self.uuid = uuid
        self.message = message
        self.health = health

    def get_uuid(self):
        return self.uuid

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
