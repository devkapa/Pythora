class Coordinate:

    x: int
    y: int
    z: int

    # Define the constructor to be called when a new Coordinate object is created
    # Coordinate objects have x and y values for horizontal position, and z for vertical
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    # Define the method to be called when a Coordinate is compared with ==
    # Returns true if the x, y and z values for both coordinates are equal
    def __eq__(self, other):
        if not isinstance(other, Coordinate):
            return NotImplemented
        return self.x == other.x and self.y == other.y and self.z == other.z


# Given a specific compass direction and set of coordinates, return a Coordinate
# object with either the x, y or z value shifted in that direction
def coordinate_from_direction(x, y, z, direction):
    match direction:
        case ("north" | "forward"):
            return Coordinate(x + 1, y, z)
        case ("south" | "backward"):
            return Coordinate(x - 1, y, z)
        case ("east" | "right"):
            return Coordinate(x, y + 1, z)
        case ("west" | "left"):
            return Coordinate(x, y - 1, z)
        case "up":
            return Coordinate(x, y, z + 1)
        case "down":
            return Coordinate(x, y, z - 1)


def convert_direction(direction):
    match direction:
        case ("north" | "forward"):
            return "north"
        case ("south" | "backward"):
            return "south"
        case ("east" | "right"):
            return "east"
        case ("west" | "left"):
            return "west"
        case "up":
            return "up"
        case "down":
            return "down"
