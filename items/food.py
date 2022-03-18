from items.object import Object


# An extension of the Object class with a saturation integer
class Food(Object):

    saturation = None

    def __init__(self, name, take, mass, damage, saturation):
        super().__init__(name, take, mass, damage)
        self.saturation = saturation

    def get_saturation(self):
        return self.saturation
