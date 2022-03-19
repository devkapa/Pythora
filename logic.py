import colorama
from colorama import Fore, Back

from items.container import Container
from items.enemy import Enemy
from items.food import Food
from items.object import Object
from movement.destination import Destination
from movement.map import Map
from player.playerentity import PlayerEntity
from difflib import SequenceMatcher

# Initialise ANSI escape colour codes for Windows
colorama.init()

# Create map global variable
global_map: Map


def start_game(game_map: Map):
    # Set the global map to the map passed to start_game()
    global global_map
    global_map = game_map

    # If no map was provided, throw error
    if game_map is None:
        print("Error initialising map.")
        return
    else:
        print(f"\n{Back.WHITE}{Fore.BLACK}{game_map.get_name()}{Back.RESET}{Fore.RESET}")

    # Initialise a new player with health and inventory
    # Set the player's current scene to 0 (first scene)
    map_player = global_map.get_player()
    player = PlayerEntity(map_player[0], map_player[1], global_map.find_scene(map_player[2]))

    # Print the map splash and setting of the first scene
    print(game_map.get_splash())

    print(look(player))
    verbs_wrong = 0

    # While the player is alive, keep the game running
    while player.get_health() > 0:

        # Colourise the user input
        print("> " + Fore.GREEN, end="")
        u_input = input()

        # Reset colour of succeeding text
        print(Fore.RESET, end="")

        # Convert and trim input to lowercase, and find the directive verb in the input
        command = u_input.lower().strip()
        verb = get_verb(command)

        # If there was no directive verb, ignore input and print error
        if verb is None:
            print(f"I don't know what you mean by \"{command}\".")
            verbs_wrong += 1
            if verbs_wrong < 10:
                print(f"Number of wrong inputs: {verbs_wrong}")
                continue
            else:
                print("You input in too many wrong inputs. Get out.")
                break
        else:
            verbs_wrong -= 1 if verbs_wrong > 0 else 0

        # Get arguments after directive verb
        args = command.replace(verb, "").strip()

        # Execute code dependent on the directive verb
        match verb:
            case "look":
                # Print the setting of the player's current scene
                print(look(player))
            case ("north" | "east" | "south" | "west" | "up" | "down"):
                # Move in the provided compass direction
                move(verb, player)
            case ("move" | "go" | "walk"):
                # Move in the provided compass direction
                direction = get_verb(args)
                if direction is not None:
                    move(direction, player)
                else:
                    print("What direction do you want to move in?")
                    print("Syntax: move [north/east/south/west/up/down]")
            case "quit":
                # Quit the game / kill the player
                break
            case ("inv" | "inventory" | "items" | "health" | "hp" | "backpack" | "bp"):
                inv = ""
                # For each item in the player's inventory, add it to the inventory string
                # and print it alongside the player's health
                for item in player.get_inventory().get_items():
                    if isinstance(item, Container):
                        # If there is a container in the player's inventory, list all of it's contents
                        percent = round((item.get_self_mass() / item.get_max_mass()) * 100)
                        inv += f'\n* {item.get_name()} ({percent}% full)'
                        for obj in item.get_contents():
                            inv += f'\n   - {obj.get_name()}'
                    else:
                        inv += f'\n* {item.get_name()}'
                # If the inventory is empty, simply print (none)
                if inv == "":
                    inv = "Empty"
                    percent = 0
                else:
                    percent = round((player.get_inventory().get_mass() / player.get_inventory().get_max_mass()) * 100)
                print(f'Backpack ({percent}% full): {inv}\nHealth: {player.get_health()}')
            case ("pickup" | "pick" | "take" | "steal"):
                if "out" in args or "from" in args:
                    # If the player wants to take an item out of or from a container,
                    # then remove it from queried container
                    player.remove_item(args, player.get_container(args))
                else:
                    # Otherwise, pick up a present item in the scene
                    player.pick_up(args)
            case "drop":
                # Drop an item from the player's inventory
                player.drop(args)
            case "map":
                global_map.print_map(player)
            case ("action" | "cmd" | "command" | "what" | "help"):
                print(possible_cmds(player))
            case ("put" | "place" | "insert"):
                # Put an inventory item inside a container
                if "in" not in args:
                    print("Specify what you want to put that in.")
                    print("Syntax: put [item] in [container]")
                else:
                    player.add_item(args, player.get_container(args))
            case "remove":
                # Take an item out of a container and add it to the player's inventory
                if "out" in args or "from" in args:
                    print("Specify what you want to take that out of.")
                    print("Syntax: take [item] out of [container]")
                else:
                    player.remove_item(args, player.get_container(args))
            case ("eat" | "consume" | "drink"):
                # Eat an item in the player's inventory
                player.eat(args)
            case ("kill" | "attack" | "knife" | "stab" | "hit" | "murder"):
                # Attack an enemy in the current scene, using a weapon
                # in the player's inventory
                if "with" in args or "using" in args:
                    player.swing(args, player.get_enemy(args))
                else:
                    print("Specify what you want to attack with.")
                    print("Syntax: attack [enemy] with [weapon]")

    # Once the player is dead (health is below or equal to 0) and
    # the while loop has ended, print the death message
    print(deathMessage)


# Filter through a string to check if it contains a verb
def get_verb(args: str):
    args = args.split()
    for v in verbs:
        for a in args:
            if similar(v, a) > 0.75:
                return v


# Returns a string of the player's current scene,
# containing the setting string and all items within
def look(player: PlayerEntity):
    # Get all objects in the player's current scene
    scene_objects = player.get_current_scene().get_items()
    # For each object in the scene, separate them with a comma
    # and print the setting with items included
    if len(scene_objects) < 1:
        items = "There are no items here."
    else:
        scene_objects_names = []
        for obj in scene_objects:
            scene_objects_names.append(obj.get_name())
        items = f'There is a {", a ".join(scene_objects_names)} here.'
    return f"{Fore.LIGHTWHITE_EX}{player.get_current_scene().get_name()}{Fore.RESET}" \
           f"{player.get_current_scene().get_setting()}" \
           f"{items}" \
           f"\nType \"help\" to see what you can do."


# Return all possible commands the player can run
def possible_cmds(player: PlayerEntity):
    # Always available commands
    cmds = ["look", "move", "quit", "inventory", "health", "map"]
    objs = player.get_current_scene().get_items()
    inv = player.get_inventory().get_items()
    # Following commands are added if they can be performed
    if any(isinstance(x, Enemy) for x in objs):
        cmds.append("attack")
    if len(objs) > 0:
        if not isinstance(Object, Enemy):
            cmds.append("take")
            cmds.append("pickup")
    if any(isinstance(x, Food) for x in inv):
        cmds.append("eat")
    if any(isinstance(x, Object) for x in inv):
        cmds.append("drop")
    if any(isinstance(x, Container) for x in inv):
        cmds.append("put")
        if any(isinstance(x, Container) and len(x.get_contents()) > 0 for x in inv):
            cmds.append("remove")
    # Return the list joined with commas
    return "Actions you can do: " + ", ".join(cmds)


# Move the player in a compass direction
def move(direction, player: PlayerEntity):
    # Get the Destination object of the compass direction
    destination: Destination = player.get_current_scene().get_destination(direction)

    # If there is no scene corresponding to the direction, print the message of the direction
    if destination.get_coordinate() is None:
        if destination.get_health() is None:
            print(destination.get_message())
            return
        else:
            # Deduct the health consequence of the direction from the player's health,
            # and print the message of the direction
            print(f'{destination.get_message()} {destination.get_health()} HP')
            player.change_health(destination.get_health())
            return
    # For every object in the scene, if it is a living enemy that is blocking the destination scene,
    # do not let the player move in that direction.
    for item in player.get_current_scene().get_items():
        if isinstance(item, Enemy) and item.is_alive():
            if direction in item.get_blocking():
                print("There is an enemy blocking your path.")
                return
    # Set the current scene to the destination scene, and print the setting of the new scene.
    player.set_current_scene(global_map.find_scene(destination.get_coordinate()))
    print(look(player))


# Check how similar two strings are
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# String list of verbs which can be used to make decisions and movements in the game
verbs = ["quit", "go", "take", "pick", "pickup", "drop", "move", "inventory", "inv", "what", "help",
         "kill", "attack", "look", "north", "east", "south", "west", "up", "down", "knife", "steal",
         "stab", "hit", "murder", "items", "walk", "eat", "consume", "drink", "hp", "health",
         "put", "place", "insert", "remove", "backpack", "bp", "map", "action", "cmd", "command"]

# The coloured message printed when the player has died/game is ended
deathMessage = f"""
                
              {Fore.RED}**Poof! You have died.**
            {Fore.RESET}Please restart to play again.
            
            """
