from items.object import Object


# An extension of the Object class with a string event
class Weapon(Object):

    event = None

    def __init__(self, name, take, mass, damage, event):
        super().__init__(name, take, mass, damage)
        self.event = event
