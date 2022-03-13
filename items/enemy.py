from items.object import Object


class Enemy(Object):

    health = None
    blocking = []

    def __init__(self, name, take, mass, damage, health, blocking):
        super().__init__(name, take, mass, damage)
        self.health = health
        self.blocking = blocking

    def get_blocking(self):
        return self.blocking

    def get_health(self):
        return self.health

    def is_alive(self):
        return self.health > 0

    def change_health(self, amount):
        self.health += int(amount)
