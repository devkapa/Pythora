class Coordinate:

    x: int
    y: int
    z: int

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            return NotImplemented
        return self.x == other.x and self.y == other.y and self.z == other.z


def coordinate_from_direction(x, y, z, direction):
    match direction:
        case "north":
            return Coordinate(x + 1, y, z)
        case "south":
            return Coordinate(x - 1, y, z)
        case "east":
            return Coordinate(x, y + 1, z)
        case "west":
            return Coordinate(x, y - 1, z)
        case "up":
            return Coordinate(x, y, z + 1)
        case "down":
            return Coordinate(x, y, z - 1)
