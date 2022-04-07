import threading
import time
from difflib import SequenceMatcher
from threading import Thread

from items.container import Container
from items.enemy import Enemy
from items.food import Food
from items.object import Object
from items.readable import Readable
from movement.destination import Destination
from movement.coordinate import convert_direction
from movement.map import Map
from movement.scene import Scene
from player.playerentity import PlayerEntity
from console.colors import white, reset, bg_white, black, red

# Create map global variable
global_map: Map
global_console = None

combat = False
combat_time = 0
u_input: str = ""


def start_game(game_map: Map, console):
    # Set the global map to the map passed to start_game()
    global global_map, global_console
    global_map = game_map
    global_console = console

    # If a corrupt or invalid map was provided, throw error
    if game_map is None:
        print(f"Error initialising map.")
        return
    else:
        print("")
        console.wrap(f"{bg_white}{black}{game_map.get_name()}")

    # Initialise a new player with the health, inventory and starting position as defined in map file
    map_player = global_map.get_player()
    player = PlayerEntity(map_player[0], map_player[1], global_map.find_scene(map_player[2]))

    # Print the map splash and setting of the first scene
    print(game_map.get_splash())

    console.wrap(look(player))

    global combat

    # While the player is alive, keep the game running
    while player.get_health() > 0:

        console.set_map_window(global_map.print_map(player))

        global combat_time

        sec = 25

        timer = Thread(target=combat_timer, args=(console, sec), name="CT")
        if not any(th.name == "CT" for th in threading.enumerate()):
            timer.start()

        global u_input, combat
        u_input = console.ginput()

        if combat_time >= sec:
            console.wrap(f"{red}You were in combat, and took too long to fight back!")
            combat = False
            break

        # Convert and trim player input to lowercase, and find the directive verb in the input
        command = u_input.lower().strip()
        verb = get_verb(command, player)

        # If there was no directive verb, ignore input and print error.
        if verb is None:
            print(f"I don't know what you mean by \"{command}\".")
            continue

        # Get all input arguments excluding the directive verb
        args = command.replace(verb, "").strip() if isinstance(verb, str) else ""

        # Execute code dependent on the directive verb
        match verb:
            case "look":
                # Print the setting of the player's current scene
                console.wrap(look(player))
            case ("north" | "east" | "south" | "west" | "up" | "down" | "forward" | "backward" | "left" | "right"):
                if player.combat:
                    console.wrap(f"{red}You were in combat, and didn't fight back!")
                    break
                # Move in the respective compass direction
                move(verb, player, console)
            case ("move" | "go" | "walk"):
                if player.combat:
                    console.wrap(f"{red}You were in combat, and didn't fight back!")
                    break
                # Find the compass direction the user wants to move in
                # If it exists, move the player there
                direction = get_verb(args, player)
                if direction in ["north", "east", "south", "west", "up", "down",
                                 "forward", "backward", "left", "right"]:
                    move(direction, player, console)
                else:
                    if isinstance(direction, Scene):
                        for x in player.get_current_scene().get_destinations():
                            if direction is global_map.find_scene(x.get_coordinate()):
                                move(x.get_direction(), player, console)
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
                        percent = item.get_contents().get_percent()
                        inv += f'\n* {white}{item.get_name()}{reset} ({percent}% full)'
                        for obj in item.get_contents().get_items():
                            inv += f'\n   - {white}{obj.get_name()}{reset}'
                    else:
                        inv += f'\n* {white}{item.get_name()}{reset}'
                # If the inventory is empty, let the player know
                if inv == "":
                    inv = "Empty"
                    percent = 0
                else:
                    percent = player.get_inventory().get_percent()
                console.wrap(f'Backpack ({percent}% full): {inv}\nHealth: {player.get_health()}'.strip())
            case ("pickup" | "pick" | "take" | "steal"):
                if "out" in args or "from" in args:
                    # If the player wants to take an item out of or from a container,
                    # then remove it from queried container
                    player.container_remove(args, player.get_container(args))
                else:
                    # Otherwise, pick up a present item in the scene
                    player.pick_up(args)
            case "drop":
                # Drop an item from the player's inventory
                player.drop(args)
            case "open":
                open_container(player.get_container(args), console)
            case "map":
                # Print a stylised map of the player's surroundings
                console.wrap(global_map.print_map(player))
            case ("action" | "cmd" | "command" | "what" | "help"):
                # Print a list of actions the player can do
                print(possible_cmds(player))
            case ("put" | "place" | "insert"):
                # Put an inventory item inside a container
                if "in" not in args:
                    print("Specify what you want to put that in.")
                    print("Syntax: put [item] in [container]")
                else:
                    player.container_add(args, player.get_container(args))
            case "remove":
                # Take an item out of a container and add it to the player's inventory
                if "out" in args or "from" in args:
                    print("Specify what you want to take that out of.")
                    print("Syntax: take [item] out of [container]")
                else:
                    player.container_remove(args, player.get_container(args))
            case ("eat" | "consume" | "drink"):
                # Eat an item in the player's inventory
                player.eat(args)
            case "read":
                player.read(args)
            case ("kill" | "attack" | "knife" | "stab" | "hit" | "murder"):
                # Attack an enemy in the current scene, using a weapon
                # in the player's inventory
                if "with" in args or "using" in args:
                    player.swing(args, player.get_enemy(args))
                else:
                    print("Specify what you want to attack with.")
                    print("Syntax: attack [enemy] with [weapon]")
            case _:
                if isinstance(verb, Scene):
                    for x in player.get_current_scene().get_destinations():
                        if verb is global_map.find_scene(x.get_coordinate()):
                            move(x.get_direction(), player, console)

        combat = True if player.combat else False

    # Once the player is dead (health is below or equal to 0) and
    # the while loop has ended, print the death message
    console.wrap(deathMessage, end='')
    combat = False
    console.set_map_window("")


def combat_timer(console, timer):
    global combat, combat_time
    while combat:
        if combat_time < timer:
            combat_time += 1
            console.timer((timer + 1) - combat_time, True)
            time.sleep(1)
        elif combat_time >= timer:
            console.timer("Dead", True)
        else:
            break
    else:
        console.timer(">", False)
        combat_time = 0


def reset_timer():
    global combat_time
    combat_time = 0


# Filter through a string to check if it contains or is similar to a verb
def get_verb(args: str, player: PlayerEntity):
    scene_names = get_scene_names(player)
    args = args.split()
    for a in args:
        for v in verbs:
            if similar(v, a) >= 0.9:
                return v
        for s in scene_names:
            name = s.get_name().lower().split()
            for n in name:
                if similar(n, a) >= 0.9:
                    return s


def get_scene_names(player: PlayerEntity):
    scene_names = []
    for x in player.get_current_scene().get_destinations():
        if global_map.find_scene(x.get_coordinate()) is not None:
            scene_names.append(global_map.find_scene(x.get_coordinate()))
    return scene_names


# Returns a string, containing the name, setting and items of the scene the player is in
def look(player: PlayerEntity):
    return f"{white}{player.get_current_scene().get_name()}{reset}" \
           f"{player.get_current_scene().get_setting()}" \
           f"{format_items(player)}" \
           f"\nType \"help\" to see what you can do."


def format_items(player):
    # Get all objects in the player's current scene
    scene_objects = player.get_current_scene().get_items()
    # For each object in the scene, separate them with a comma
    # and print the setting with items included
    if len(scene_objects) < 1:
        return "There are no items here."
    else:
        scene_objects_names = []
        for obj in scene_objects:
            scene_objects_names.append(obj.get_name())
        return f'There is a {white}{f"{reset}, a {white}".join(scene_objects_names)}{reset}' \
               f' here. '


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
    if any(isinstance(x, Readable) for x in inv):
        cmds.append("read")
    if any(isinstance(x, Container) for x in inv):
        cmds.append("put")
        if any(isinstance(x, Container) and len(x.get_contents().get_items()) > 0 for x in inv):
            cmds.append("remove")
    # Return the list joined with commas
    return "Actions you can do: " + ", ".join(cmds)


# Move the player in a compass direction
def move(direction, player: PlayerEntity, console):
    # Get the Destination object of the compass direction
    destination: Destination = player.get_current_scene().get_destination(convert_direction(direction))

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
    scene = global_map.find_scene(destination.get_coordinate())
    if scene is None:
        print("Athora encountered a problem. The map is not configured properly.")
        return
    if scene.pin is not False:
        print(f"{scene.name} requires a passcode to enter: ", end='')
        pin = console.ginput()
        if pin != scene.pin:
            print(f"That is not the right passcode.")
            return
    player.set_current_scene(scene)
    console.wrap(look(player))
    scene.pin = False


# Check how similar two strings are
# Returns a float between 0.0 and 1.0 (no match to complete match)
def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


# The player constructor class
def open_container(container: Container, console):
    if container is None:
        print("That container doesn't seem to exist")
        print("Syntax: open [container]")
        return
    items = f"{reset}\n* {white}".join([item.get_name()
                                              for item in container.get_contents().get_items()])
    items = f"{reset}\n* {white}" + items
    console.wrap(f'Opening the {white}{container.get_name()}{reset} reveals', end='')
    console.wrap(f': {items}' if len([item for item in container.get_contents().get_items()]) >= 1 else " no items inside.")


# String list of verbs which can be used to make decisions and movements in the game
verbs = ["quit", "go", "take", "pick", "pickup", "drop", "move", "inventory", "inv", "what", "help",
         "kill", "attack", "look", "north", "east", "south", "west", "up", "down", "knife", "steal",
         "stab", "hit", "murder", "items", "walk", "eat", "consume", "drink", "hp", "health", "read",
         "open", "put", "place", "insert", "remove", "backpack", "bp", "map", "action", "cmd", "command",
         "forward", "backward", "left", "right"]

# The coloured message printed when the player has died/game is ended
deathMessage = f"""
                
              {red}**Poof! You have died.**{reset}
            Please restart to play again.
            
            """
