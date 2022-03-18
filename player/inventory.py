from items.object import Object


# The Inventory constructor class
class Inventory:

    # Initialise the list of items in the inventory,
    # and the maximum weight it can hold
    items: list[Object]
    max_mass: int

    # Define the constructor to be called when a new Inventory object is created
    def __init__(self, items, max_mass):
        self.items = items
        self.max_mass = max_mass

    # Return a list of items in the inventory
    def get_items(self):
        return self.items

    # Return the maximum weight the inventory can hold
    def get_max_mass(self):
        return self.max_mass

    # Get the total mass of all items in the inventory
    def get_mass(self):
        mass = 0
        for item in self.items:
            mass += item.get_mass()
        return mass
