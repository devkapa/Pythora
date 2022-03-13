import colorama

from movement.map import Map
from player.player import Player
from items.container import Container
from items.enemy import Enemy
from items.object import Object
from movement.direction import get_index, Direction
from colorama import Fore

colorama.init()

health = 10
inventory: list[Object] = []

global_map: Map


def start_game(game_map: Map):
    global global_map
    global_map = game_map

    if game_map is None:
        print("Error initialising map.")
        return

    player = Player(health, inventory, global_map.scenes[0])

    print(game_map.get_splash())

    print(look(player))

    while player.get_health() > 0:

        print("> " + Fore.GREEN, end="")
        u_input = input()

        print(Fore.RESET, end="")

        command = u_input.lower().strip()
        verb = get_verb(command)

        if verb is None:
            print(f"I don't know what you mean by \"{command}\".")
            continue

        args = command.replace(verb, "").strip()

        match verb:
            case "look":
                print(look(player))
            case ("north" | "east" | "south" | "west" | "up" | "down"):
                move(verb, player)
            case ("move" | "go" | "walk"):
                direction = get_verb(args)
                if direction is not None:
                    move(direction, player)
                else:
                    print("What direction do you want to move in?")
            case "quit":
                break
            case ("inv" | "inventory" | "items" | "health" | "hp"):
                inv = ""
                for item in inventory:
                    if isinstance(item, Container):
                        inv += f'\n* {item.get_name()}'
                        for obj in item.get_contents():
                            inv += f'\n   - {obj.get_name()}'
                    else:
                        inv += f'\n* {item.get_name()}'
                if inv == "":
                    inv = "(none)"
                print(f'Inventory: {inv}\nHealth: {player.get_health()}')
            case ("pick" | "pickup" | "take"):
                if "out" in args or "from" in args:
                    player.remove_item(args, player.get_container(args))
                else:
                    player.pick_up(args)
            case "drop":
                player.drop(args)
            case ("put" | "place" | "insert"):
                if "in" not in args:
                    print("Specify what you want to put that in.")
                else:
                    player.add_item(args, player.get_container(args))
            case "remove":
                if "out" in args or "from" in args:
                    print("Specify what you want to take that out of.")
                else:
                    player.remove_item(args, player.get_container(args))
            case ("eat" | "consume" | "drink"):
                player.eat(args)
            case ("kill" | "attack" | "knife" | "stab" | "hit" | "murder"):
                if "with" in args or "using" in args:
                    player.swing(args, player.get_enemy(args))
                else:
                    print("Specify what you want to attack with.")

    print(deathMessage)


def get_verb(i: str):
    for v in verbs:
        if v in i:
            return v


def look(player: Player):
    scene_objects = player.get_current_scene().get_items()
    if len(scene_objects) < 1:
        return f"{player.get_current_scene().get_name()}" \
               f"{player.get_current_scene().get_setting()}" \
               f"There are no items here."
    scene_objects_names = []
    for obj in scene_objects:
        scene_objects_names.append(obj.get_name())
    return f"{player.get_current_scene().get_name()}" \
           f"{player.get_current_scene().get_setting()}" \
           f'There is a {", a ".join(scene_objects_names)} here.'


def move(direction, player: Player):
    destination: Direction = player.get_current_scene().get_destinations()[get_index(direction)]
    if destination.get_uuid() is None:
        if destination.get_health() is None:
            print(destination.get_message())
            return
        else:
            print(f'{destination.get_message()} {destination.get_health()} HP')
            player.change_health(destination.get_health())
            return
    for item in player.get_current_scene().get_items():
        if isinstance(item, Enemy) and item.is_alive():
            if destination.get_uuid() in item.get_blocking():
                print("There is an enemy blocking your path.")
                return
    player.set_current_scene(global_map.find_scene(destination.get_uuid()))
    print(look(player))


verbs = ["quit", "go", "take", "pick", "pickup", "drop", "open", "move", "inventory", "inv",
         "break", "kill", "attack", "look", "north", "east", "south", "west", "up", "down", "knife",
         "stab", "hit", "murder", "items", "walk", "rid", "eat", "consume", "drink", "hp", "health",
         "exit", "stop", "put", "place", "insert", "remove"]

deathMessage = f"""
                
                {Fore.RED}**Poof! You have died.**
            {Fore.RESET}Please restart the game to play again.
            
            """
