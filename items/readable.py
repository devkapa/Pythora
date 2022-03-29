from items.object import Object


# An extension of the Object class with a string text
class Readable(Object):

    text = None

    def __init__(self, name, take, damage, text):
        super().__init__(name, take, damage)
        self.text = text
