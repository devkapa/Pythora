from items.object import Object


# An extension of the Object class with a list variable of Objects
# within the container, and the maximum mass the container can hold
from player.inventory import Inventory


class Container(Object):

    contents: Inventory = []
    slots: int = None

    def __init__(self, name, take, damage, contents):
        super().__init__(name, take, damage)
        self.contents = contents

    def get_contents(self):
        return self.contents

    # These functions account for objects within the container and override the Object base class functions
    def get_damage(self):
        n = super().get_damage()
        p = self.contents.get_percent()
        d = 6 if p >= 90 else 4 if p >= 60 else 2 if p >= 30 else 0
        return n + d
