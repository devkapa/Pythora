from items.container import Container
from items.enemy import Enemy
from items.food import Food
from items.weapon import Weapon
from player.inventory import Inventory
from movement.scene import Scene


# Filter through a list of items and find all that match the string query
def get_match(args, item_list):
    items = []
    for item in item_list:
        arg_split = [x for x in args.split()]
        name_split = [x for x in item.get_name().lower().split()]
        for arg in arg_split:
            if arg in name_split:
                items.append(item)
    return list(dict.fromkeys(items))


# The player constructor class
class PlayerEntity:
    # Initialise the health, inventory and current scene of the player
    health = 0
    inventory: Inventory
    current_scene: Scene

    # Define the constructor to be called when a new Player object is created
    def __init__(self, health, inventory, current_scene):
        self.health = health
        self.inventory = inventory
        self.current_scene = current_scene

    # Return the health of the player
    def get_health(self):
        return self.health

    # Change the health of the player by an amount passed in parameters
    def change_health(self, amount):
        self.health += int(amount)
        if self.health > 10:
            self.health = 10

    # Get the current scene the player is in
    def get_current_scene(self):
        return self.current_scene

    # Set the current scene the player is in
    def set_current_scene(self, scene):
        self.current_scene = scene

    def get_z(self):
        return self.current_scene.get_coordinate().z

    # Return a list of all items in the player's inventory
    def get_inventory(self):
        return self.inventory

    # Return a list of all weapons in the player's inventory
    def get_weapons(self):
        weapons = []
        for item in self.inventory.get_items():
            if not isinstance(item, Food):
                weapons.append(item)
        return weapons

    # Get a queried Container object from the player's inventory
    def get_container(self, args):
        inventory_objects = get_match(args, self.inventory.get_items())
        for obj in inventory_objects:
            if isinstance(obj, Container):
                return obj

    # Get a queried Enemy object from the player's current scene
    def get_enemy(self, args):
        scene_objects = get_match(args, self.get_current_scene().get_items())
        for obj in scene_objects:
            if isinstance(obj, Enemy):
                return obj

    # Deduct health from the player from a weapon consequence
    def execute_event(self, weapon: Weapon):
        self.change_health(-weapon.get_damage())
        print(f'{weapon.event} -{weapon.get_damage()} HP')

    # Add an item from the player's inventory to a container in the player's inventory
    def add_item(self, args: str, container: Container):
        # If no item or container was specified
        if container is None:
            print("You must have the container in your inventory.")
            return
        if args == "":
            print("Specify what you want to add to that container.")
            print("Syntax: put [item] in [container]")
            return
        # Get a list of items in the player's inventory that match the player's query
        matches = get_match(args.replace(container.get_name().lower(), ""), self.inventory.get_items())
        if len(matches) < 1:
            print("You do not have that.")
            return
        # For each item found, add it to the container if it is light enough and not a container itself
        for match in matches:
            if not isinstance(match, Container):
                if container.get_self_mass() + match.get_mass() <= container.get_max_mass():
                    container.get_contents().append(match)
                    self.inventory.get_items().remove(match)
                    print(f"You put {match.get_name()} into {container.get_name()}. "
                          f"Now it deals {container.get_damage()} damage.")
                else:
                    print(f"The {container.get_name()} is too full to fit {match.get_name()}")
            else:
                print("You cannot put a container inside a container.")

    # Remove an item from a container in the player's inventory
    def remove_item(self, args: str, container: Container):
        # If no item or container was specified
        if container is None:
            print("You must have the container in your inventory.")
            return
        if args == "":
            print("Specify what you want to take out of that container.")
            print("Syntax: take [item] out of [container]")
            return
        # Get a list of items in the container that match the player's query
        matches = get_match(args, container.get_contents())
        if len(matches) < 1:
            print(f"That item isn't in the {container.get_name()}.")
            return
        # For each item found, remove it from the container and add to inventory
        for match in matches:
            container.get_contents().remove(match)
            self.inventory.get_items().append(match)
            print(f"You took {match.get_name()} out of {container.get_name()}. "
                  f"Now it deals {container.get_damage()} damage.")

    # Pick up an item in the player's scene
    def pick_up(self, args: str):
        # If no item was specified
        if args == "":
            print("What do you want to pick up?")
            print("Syntax: take [item]")
            return
        # Get a list of items in the player's current scene that match the player's query
        matches = get_match(args, self.get_current_scene().get_items())
        if len(matches) < 1:
            print(f"Theres no \"{args}\" here.")
            return
        # If the item can be taken and is not an enemy, then add it
        # to the player's inventory and remove it from the scene
        for match in matches:
            if match.get_take() == "true" and not isinstance(match, Enemy):
                if self.inventory.get_mass() + match.get_mass() <= self.inventory.get_max_mass():
                    self.inventory.get_items().append(match)
                    self.get_current_scene().get_items().remove(match)
                    print(f"You picked up {match.get_name()}.")
                else:
                    print("Your inventory is too full to pick that up!")
            else:
                if isinstance(match, Weapon):
                    self.execute_event(match)
                else:
                    print(f"You can't pick up a {match.get_name()}!")

    # Remove/drop an item from player's inventory
    def drop(self, args: str):
        # If no item was specified
        if args == "":
            print("What do you want to drop?")
            print("Syntax: drop [item]")
            return
        # Get a list of items in the player's inventory that match the player's query
        matches = get_match(args, self.inventory.get_items())
        if len(matches) < 1:
            print(f"You don't have that.")
            return
        # For each match, remove it from the player's inventory
        for match in matches:
            self.inventory.get_items().remove(match)
            self.get_current_scene().get_items().append(match)
            print(f"Dropped {match.get_name()}.")

    # Eat an item in the player's inventory
    def eat(self, args):
        # If no item was specified
        if args == "":
            print("Specify what you want to eat.")
            print("Syntax: eat [item]")
            return
        # Get a list of items in the player's inventory that match the player's query
        matches = get_match(args, self.inventory.get_items())
        if len(matches) < 1:
            print(f"You don't have that.")
            return
        # For each match in the inventory, add saturation of the food to the player's health
        # and remove it from their inventory, as long it is an actual food and edible.
        for match in matches:
            if match.get_take() == "true" and isinstance(match, Food):
                self.change_health(match.get_saturation())
                self.inventory.get_items().remove(match)
                print(f"You ate {match.get_name()}. It tasted good. You gained {match.get_saturation()} HP."
                      f"\nYou are now on {self.health} HP.")
            else:
                print(f"You cannot eat a {match.get_name()}!")

    # Swing a weapon at an enemy, dealing it damage
    def swing(self, args, enemy: Enemy):
        # If no weapon or enemy was specified
        if enemy is None:
            print("No enemy found.")
            return
        if args == "":
            print("Specify what you want to attack.")
            print("Syntax: attack [enemy] with [weapon]")
            return
        # Get a list of all items in the player's inventory that match the query
        matches = get_match(args, self.get_weapons())
        if len(matches) < 1:
            print(f"You don't have that.")
            return
        # If the enemy is alive, attack it and change the player's health depending on
        # the enemy's strength. If it is dead, do not attack it.
        for match in matches:
            if enemy.is_alive():
                enemy.change_health(-match.get_damage())
                print(f"You attacked the {enemy.get_name()} with a {match.get_name()} for {match.get_damage()} damage.")
                if enemy.is_alive():
                    print(f"It swings back at you, dealing {enemy.get_damage()} damage to you."
                          f"\nThe {enemy.get_name()} is now on {enemy.get_health()} HP.")
                    self.change_health(-enemy.get_damage())
                else:
                    print(f"The {enemy.get_name()} is now dead.")
                    enemy.set_name(f"Dead {enemy.get_name()}")
            else:
                print(f"That {enemy.get_name()} is already dead.")
