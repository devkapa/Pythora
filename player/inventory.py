from items.object import Object


# The Inventory constructor class
class Inventory:

    # Initialise the list of items in the inventory,
    # and the maximum weight it can hold
    items: list[Object]
    slots: int

    # Define the constructor to be called when a new Inventory object is created
    def __init__(self, items, slots):
        self.items = items
        self.slots = slots

    # Return a list of items in the inventory
    def get_items(self):
        return self.items

    # Return the maximum weight the inventory can hold
    def get_slots(self):
        return self.slots

    def get_percent(self):
        return round((len(self.items)/self.slots)*100)

    # Get the total mass of all items in the inventory
    def full(self):
        return len(self.items) == self.slots
