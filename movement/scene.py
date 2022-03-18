from items.object import Object
from movement.coordinate import Coordinate
from movement.destination import Destination


# The Scene constructor class
class Scene:

    coordinate: Coordinate
    name = None
    setting = None
    destinations: list[Destination] = []
    items: list[Object] = []

    # Define the constructor to be called when a new Scene object is created
    def __init__(self, coordinate, name, setting, destinations, items):
        self.coordinate = coordinate
        self.name = name
        self.setting = setting
        self.destinations = destinations
        self.items = items

    # Getters
    def get_coordinate(self) -> Coordinate:
        return self.coordinate

    def get_name(self):
        return self.name

    def get_setting(self):
        return self.setting

    def get_destinations(self) -> list[Destination]:
        return self.destinations

    def get_destination(self, direction):
        for d in self.destinations:
            if d.get_direction() == direction:
                return d

    def get_items(self):
        return self.items
