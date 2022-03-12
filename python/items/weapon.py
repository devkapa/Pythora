from python.items.object import Object


class Weapon(Object):

    event = None

    def __init__(self, name, take, mass, damage, event):
        super().__init__(name, take, mass, damage)
        self.event = event
