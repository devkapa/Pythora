from items.container import Container
from items.enemy import Enemy
from items.food import Food
from items.object import Object
from items.weapon import Weapon
from movement.scene import Scene


def get_match(args, item_list):
    items = []
    for item in item_list:
        arg_split = [x for x in args.split()]
        name_split = [x for x in item.get_name().lower().split()]
        for arg in arg_split:
            if arg in name_split:
                items.append(item)
    return list(dict.fromkeys(items))


class Player:
    health = 0
    inventory: list[Object] = []
    current_scene: Scene

    def __init__(self, health, inventory, current_scene):
        self.health = health
        self.inventory = inventory
        self.current_scene = current_scene

    def get_health(self):
        return self.health

    def change_health(self, amount):
        self.health += int(amount)
        if self.health > 10:
            self.health = 10

    def get_current_scene(self):
        return self.current_scene

    def set_current_scene(self, scene):
        self.current_scene = scene

    def get_inventory(self):
        return self.inventory

    def get_weapons(self):
        weapons = []
        for item in self.inventory:
            if not isinstance(item, Food):
                weapons.append(item)
        return weapons

    def get_container(self, args):
        inventory_objects = get_match(args, self.inventory)
        for obj in inventory_objects:
            if isinstance(obj, Container):
                return obj

    def get_enemy(self, args):
        scene_objects = get_match(args, self.get_current_scene().get_items())
        for obj in scene_objects:
            if isinstance(obj, Enemy):
                return obj

    def execute_event(self, weapon: Weapon):
        self.change_health(-weapon.get_damage())
        print(f'{weapon.event} -{weapon.get_damage()} HP')

    def add_item(self, args: str, container: Container):
        if container is None:
            print("You must have the container in your inventory.")
            return
        if args == "":
            print("Specify what you want to add to that container.")
            return
        matches = get_match(args.replace(container.get_name().lower(), ""), self.inventory)
        if len(matches) < 1:
            print("You do not have that.")
            return
        for match in matches:
            if not isinstance(match, Container):
                if container.get_mass() + match.get_mass() <= container.get_max_mass():
                    container.get_contents().append(match)
                    self.inventory.remove(match)
                    print(f"You put {match.get_name()} into {container.get_name()}. "
                          f"Now it deals {container.get_damage()} damage.")
                else:
                    print(f"The {container.get_name()} is too heavy to fit {match.get_name()}")
            else:
                print("You cannot put a container inside a container.")

    def remove_item(self, args: str, container: Container):
        if container is None:
            print("You must have the container in your inventory.")
            return
        if args == "":
            print("Specify what you want to take out of that container.")
            return
        matches = get_match(args, container.get_contents())
        if len(matches) < 1:
            print(f"That item isn't in the {container.get_name()}.")
            return
        for match in matches:
            container.get_contents().remove(match)
            self.inventory.append(match)
            print(f"You took {match.get_name()} out of {container.get_name()}. "
                  f"Now it deals {container.get_damage()} damage.")

    def pick_up(self, args: str):
        if args == "":
            print("What do you want to pick up?")
            return
        matches = get_match(args, self.get_current_scene().get_items())
        if len(matches) < 1:
            print(f"Theres no \"{args}\" here.")
            return
        for match in matches:
            if match.get_take() and not isinstance(match, Enemy):
                self.inventory.append(match)
                self.get_current_scene().get_items().remove(match)
                print(f"You picked up {match.get_name()}.")
            else:
                if isinstance(match, Weapon):
                    self.execute_event(match)
                else:
                    print(f"You can't pick up a {match.get_name()}!")

    def drop(self, args: str):
        if args == "":
            print("What do you want to drop?")
            return
        matches = get_match(args, self.inventory)
        if len(matches) < 1:
            print(f"You don't have that.")
            return
        for match in matches:
            self.inventory.remove(match)
            self.get_current_scene().get_items().append(match)
            print(f"Dropped {match.get_name()}.")

    def eat(self, args):
        if args == "":
            print("Specify what you want to eat.")
            return
        matches = get_match(args, self.inventory)
        if len(matches) < 1:
            print(f"You don't have that.")
            return
        for match in matches:
            if match.get_take() and isinstance(match, Food):
                self.change_health(match.get_saturation())
                self.inventory.remove(match)
                print(f"You ate {match.get_name()}. It tasted good. You gained {match.get_saturation()} HP."
                      f"\nYou are now on {self.health} HP.")
            else:
                print(f"You cannot eat a {match.get_name()}!")

    def swing(self, args, enemy: Enemy):
        if enemy is None:
            print("No enemy found.")
            return
        if args == "":
            print("Specify what you want to attack.")
            return
        matches = get_match(args, self.get_weapons())
        if len(matches) < 1:
            print(f"You don't have that.")
            return
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

