import os
import re
import xml.etree.ElementTree as elementTree
from _elementtree import ParseError
import textwrap
from os import listdir
from os.path import isfile, join
import webbrowser
from difflib import SequenceMatcher

from items.container import Container
from items.enemy import Enemy
from items.food import Food
from items.object import Object
from items.readable import Readable
from movement.coordinate import coordinate_from_direction, Coordinate
from movement.destination import Destination
from movement.scene import Scene
from player.inventory import Inventory
from player.playerentity import PlayerEntity
from console.colors import white, reset, pink


class Map:
    name = None
    splash = None
    scenes = []
    player = []

    # Define the constructor to be called when a new Map object is created
    # This object can be passed to the get_map() function
    def __init__(self, name, splash, scenes, player):
        self.name = name
        self.splash = splash
        self.scenes = scenes
        self.player = player

    # Getters
    def get_name(self):
        return self.name

    def get_splash(self):
        return self.splash

    def get_player(self):
        return self.player

    # Find a scene by its coordinates
    def find_scene(self, coordinate: Coordinate) -> Scene:
        for scene in self.scenes:
            if coordinate == scene.get_coordinate():
                return scene

    # Print a map of scene on the current Z level of the player
    def print_map(self, player: PlayerEntity):
        # Lists to store all x and y coordinates
        x_coords = []
        y_coords = []

        # Empty string to concatenate to
        print_str = ""

        # For every scene in the current Z level of the player,
        # add it's x and y coordinates to the lists
        for scene in self.scenes:
            if scene.get_coordinate().z == player.get_z():
                x_coords.append(scene.get_coordinate().x)
                y_coords.append(scene.get_coordinate().y)
        print_str += f"You are on Level {str(player.get_z())}.\n\n"

        # For each x value from highest to lowest in the list
        for x in reversed(sorted(set(x_coords))):
            # For each y coordinate
            for y in sorted(set(y_coords)):
                current_coord = Coordinate(x, y, player.get_z())
                adj_coord = Coordinate(x, y + 1, player.get_z())
                # Check if the iterated coordinate is a scene, if the player is
                # in it, and if there is a scene to the right of it
                if self.find_scene(current_coord) is not None:
                    print_str += "[Y]" if self.find_scene(current_coord) is player.get_current_scene() else "[ ]"
                    if self.find_scene(adj_coord) is not None:
                        if any(adj_coord == x.get_coordinate() for x in self.find_scene(current_coord).get_destinations()):
                            current_scene = self.find_scene(current_coord).get_items()
                            adj_scene = self.find_scene(adj_coord).get_items()
                            current_enemies = [item for item in current_scene if isinstance(item, Enemy)]
                            adj_enemies = [item for item in adj_scene if isinstance(item, Enemy)]
                            for current_enemy in current_enemies:
                                if "east" in current_enemy.get_blocking() and current_enemy.is_alive():
                                    print_str += "×"
                                    break
                            for adj_enemy in adj_enemies:
                                if "west" in adj_enemy.get_blocking() and adj_enemy.is_alive():
                                    print_str += "×"
                                    break
                            print_str += "-" if print_str[-1:] != "×" else ""
                        else:
                            print_str += " "
                    else:
                        print_str += " "
                else:
                    print_str += "    "
            print_str += "\n"
            for y in sorted(set(y_coords)):
                # Check if the iterated coordinate is a scene and if there is a scene below it
                current_coord = Coordinate(x, y, player.get_z())
                adj_coord = Coordinate(x - 1, y, player.get_z())
                print_str += " "

                if self.find_scene(current_coord) is not None:
                    if self.find_scene(adj_coord) is not None:
                        if any(current_coord == x.get_coordinate() for x in self.find_scene(adj_coord).get_destinations()):
                            current_scene = self.find_scene(current_coord).get_items()
                            adj_scene = self.find_scene(adj_coord).get_items()
                            current_enemies = [item for item in current_scene if isinstance(item, Enemy)]
                            adj_enemies = [item for item in adj_scene if isinstance(item, Enemy)]
                            for current_enemy in current_enemies:
                                if "south" in current_enemy.get_blocking() and current_enemy.is_alive():
                                    print_str += "×"
                                    break
                            for adj_enemy in adj_enemies:
                                if "north" in adj_enemy.get_blocking() and adj_enemy.is_alive():
                                    print_str += "×"
                                    break
                            print_str += "|  " if print_str[-1:] != "×" else ""
                        else:
                            print_str += "   "
                    else:
                        print_str += "   "
                else:
                    print_str += "   "

            print_str += "\n"

        scene_objects = player.get_current_scene().get_items()

        if len(scene_objects) < 1:
            items = "There are no items here."
        else:
            scene_objects_names = []
            for obj in scene_objects:
                scene_objects_names.append(obj.get_name())
            items = f'There is a {white}{f"{reset}, a {white}".join(scene_objects_names)}{reset}' \
                    f' here. '

        # Print the string, removing whitespaces
        print_str = print_str.strip()
        print_str += "\n\n[Y] = You"
        print_str += "\n× = Enemy"
        print_str += f"\n\nYou are at the {white}{player.get_current_scene().get_name()}{reset}."
        print_str += f"\n{items}"
        return print_str


# Converts an Athora Map file (.athora) to a Map object
def get_map(path):
    try:
        # Create an XML element tree to read the map file
        game_map = elementTree.parse(path)

        # Get the map name and splash from contents
        root = game_map.getroot()
        map_name = root.attrib.get("name")
        map_splash = textwrap.dedent(root.find("splash").text)

        # Get player health, inventory and starting coordinates
        player = root.find("player").attrib
        player_coordinate = Coordinate(int(player.get("x")), int(player.get("y")), int(player.get("z")))
        player_stats = [int(player.get("health")), Inventory([], int(player.get("inventory-slots"))), player_coordinate]

        # Get all scene nodes in the map
        map_scenes = root.find("scenes").findall("scene")
        scenes = []

        # For every <scene> node, create a Scene object
        for scene in map_scenes:

            # Get the name and setting of the scene from map contents
            scene_name = scene.attrib.get("name")
            scene_setting = textwrap.dedent(scene.find("setting").text)

            scene_directions = scene.find("directions")
            compass_directions = ["north", "east", "south", "west", "up", "down"]
            directions_attribs = scene_directions.attrib
            directions = []

            scene_pwd = False if scene.attrib.get("pwd") is None else scene.attrib.get("pwd")

            scene_coordinates = Coordinate(int(directions_attribs.get("x")), int(directions_attribs.get("y")),
                                           int(directions_attribs.get("z")))

            # For each compass direction, check it's corresponding value in the map. Create a new Destination object
            # with the coordinates of the destination scene, or the message to be sent when no destination exists.
            for direction in compass_directions:
                if any(x.tag == direction for x in scene_directions):
                    direction_message = scene_directions.find(direction).text
                    direction_health = scene_directions.find(direction).attrib.get("health")
                    directions.append(Destination(direction, None, textwrap.dedent(direction_message).strip(),
                                                  direction_health))
                else:
                    direction_coordinate = coordinate_from_direction(int(directions_attribs.get("x")),
                                                                     int(directions_attribs.get("y")),
                                                                     int(directions_attribs.get("z")), direction)
                    directions.append(Destination(direction, direction_coordinate, None, None))

            # Get all item nodes in the scene
            scene_items = scene.find("items")
            items = []

            # If the scene does contain items
            if scene_items is not None:

                scene_items = scene_items.findall("item")

                for item in scene_items:
                    create_item(item, items)

            # Add the scene to a list
            scenes.append(Scene(scene_coordinates, scene_name, scene_setting, directions, items, scene_pwd))

        # Return a new Map with its name, splash, scenes and player configuration
        return Map(map_name, map_splash, scenes, player_stats)
    except (AttributeError, ParseError):
        print(f"That map is not compatible with this version of Athora.")
        return None


# Gives the player a list of all maps in the game folder, and returns it
# as a file path that can be passed to the get_map method.
def choose_map(maps_dir, console):
    maps_dir += "/maps/"

    # If there is no map directory, create one
    if not os.path.isdir(maps_dir):
        print("\nNo maps folder was found. Creating one...")
        os.mkdir(maps_dir)

    while True:
        # Get all files in the maps directory
        files = [f for f in listdir(maps_dir) if isfile(join(maps_dir, f)) and f.lower().endswith(".athora")]

        # If there are no maps, open the maps folder
        if len(files) < 1:
            console.wrap(f"{pink}The maps folder is empty. Add some maps to start playing Athora!")
            webbrowser.open('file:///' + os.path.realpath(maps_dir))
            console.ginput()
            return

        # Display available maps to player
        print("\nChoose a map to play, \"maps\", or \"quit\":")

        file_names = []

        for file in files:
            try:
                game_map = elementTree.parse(f'{maps_dir}{file}')
                print(f'{files.index(file)}: {game_map.getroot().attrib.get("name")} ({file})')
                file_names.append(f'{files.index(file)}: {game_map.getroot().attrib.get("name")} ({file})')
            except ParseError:
                print(f"Error: Could not parse \"{file}\". Invalid map.")
                pass

        u_input = console.ginput()

        # If the player wishes to close the game, return a NoneType
        if similar(u_input, "quit") > 0.7:
            return None
        if similar(u_input, "maps") > 0.7:
            webbrowser.open('file:///' + os.path.realpath(maps_dir))
            console.wrap(f"{pink}Opening the maps folder. ({os.path.realpath(maps_dir)})")
            continue

        # If the input value is a valid integer and present in the map list, return that map's file path
        try:
            for file in files:
                for name in file_names:
                    if file in name:
                        names = sum([re.split(r'[^\w ]', x) for x in name.lower().split()], [])
                        inputs = sum([re.split(r'[^\w ]', x) for x in u_input.lower().split()], [])
                        for n in names:
                            for i in inputs:
                                if similar(n, i) > 0.9:
                                    return maps_dir + file
            print(f"That is not an option in the list of maps.\n")
            continue
        except ValueError:
            print(f"Enter a valid number.\n")
            continue


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def create_item(item, items):
    # Get the item's name, type and stats
    item_name = item.find("name").text
    item_stats = item.find("stats")
    item_take = item.find("take")
    item_take_tuple = (
        item_take.attrib.get("bool"),
        textwrap.dedent(item_take.text).strip() if item_take.text is not None else None
    )
    item_damage = int(item_stats.attrib.get("damage"))
    match item.attrib.get("type"):
        case "food":
            item_saturation = int(item_stats.attrib.get("saturation"))
            items.append(Food(item_name, item_take_tuple, item_damage, item_saturation))
        case "container":
            item_inventory = []
            item_inventory_slots = int(item.find("inventory").attrib.get("slots"))
            item_inventory_items = item.find("inventory").findall("item")
            for i in item_inventory_items:
                create_item(i, item_inventory)
            items.append(Container(item_name, item_take_tuple, item_damage,
                                   Inventory(item_inventory, item_inventory_slots)))
        case "object":
            items.append(Object(item_name, item_take_tuple, item_damage))
        case "enemy":
            item_blocking_list = []
            item_inventory = []
            item_inventory_slots = 0
            item_health = int(item_stats.attrib.get("health"))
            if item.find("blocking").text is not None:
                item_blocking = item.find("blocking").text.split(",")
                for i in item_blocking:
                    item_blocking_list.append(i)
            if item.find("inventory") is not None:
                item_inventory_slots = item.find("inventory").attrib.get("slots")
                item_inventory_items = item.find("inventory").findall("item")
                for i in item_inventory_items:
                    create_item(i, item_inventory)
            items.append(
                Enemy(item_name, item_take_tuple, item_damage, item_health,
                      item_blocking_list, Inventory(item_inventory, item_inventory_slots)))
        case "readable":
            item_text = textwrap.dedent(item.find("text").text).strip()
            items.append(Readable(item_name, item_take_tuple, item_damage, item_text))
