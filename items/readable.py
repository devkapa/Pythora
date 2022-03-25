from items.object import Object


# An extension of the Object class with a string text
class Readable(Object):

    text = None

    def __init__(self, name, take, mass, damage, text):
        super().__init__(name, take, mass, damage)
        self.text = text
