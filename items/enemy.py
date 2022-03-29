from items.object import Object


# An extension of the Object class with a health variable and a list of
# directions that the Enemy object is obstructing
from player.inventory import Inventory


class Enemy(Object):

    health = None
    inventory: Inventory
    blocking = []

    def __init__(self, name, take, damage, health, blocking, inventory):
        super().__init__(name, take, damage)
        self.health = health
        self.blocking = blocking
        self.inventory = inventory

    def get_blocking(self):
        return self.blocking

    def get_inventory(self) -> Inventory:
        return self.inventory

    def get_health(self):
        return self.health

    def is_alive(self):
        return self.health > 0

    def change_health(self, amount):
        self.health += int(amount)
