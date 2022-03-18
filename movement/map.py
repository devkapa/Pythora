import os
import xml.etree.ElementTree as elementTree
import textwrap
from os import listdir
from os.path import isfile, join
import webbrowser

from items.container import Container
from items.enemy import Enemy
from items.food import Food
from items.object import Object
from items.weapon import Weapon
from movement.coordinate import coordinate_from_direction, Coordinate
from movement.destination import Destination
from movement.scene import Scene
from player.inventory import Inventory
from player.playerentity import PlayerEntity


def get_map(path):
    game_map = elementTree.parse(path)

    root = game_map.getroot()
    map_name = root.attrib.get("name")
    map_splash = textwrap.dedent(root.find("splash").text)

    map_scenes = root.find("scenes").findall("scene")
    scenes = []

    player = root.find("player").attrib
    player_coordinate = Coordinate(int(player.get("x")), int(player.get("y")), int(player.get("z")))
    player_stats = [int(player.get("health")), Inventory([], int(player.get("max-inventory"))), player_coordinate]

    for scene in map_scenes:
        scene_name = scene.attrib.get("name")
        scene_setting = textwrap.dedent(scene.find("setting").text)

        scene_directions = scene.find("directions")
        compass_directions = ["north", "east", "south", "west", "up", "down"]
        directions_attribs = scene_directions.attrib
        directions = []

        scene_coordinates = Coordinate(int(directions_attribs.get("x")), int(directions_attribs.get("y")),
                                       int(directions_attribs.get("z")))

        for direction in compass_directions:
            if any(x.tag == direction for x in scene_directions):
                direction_message = scene_directions.find(direction).text
                direction_health = scene_directions.find(direction).attrib.get("health")
                directions.append(make_direction(direction, None, direction_message, direction_health))
            else:
                direction_coordinate = coordinate_from_direction(int(directions_attribs.get("x")),
                                                                 int(directions_attribs.get("y")),
                                                                 int(directions_attribs.get("z")), direction)
                directions.append(make_direction(direction, direction_coordinate, None, None))

        scene_objects = scene.find("items")
        items = []

        if scene_objects is not None:
            scene_items = scene_objects.findall("item")
            for item in scene_items:
                item_name = item.find("name").text
                item_stats = item.find("stats")
                item_take = item.find("take")
                item_take_bool = item_take.attrib.get("bool")
                item_mass = int(item_stats.attrib.get("mass"))
                item_damage = int(item_stats.attrib.get("damage"))
                match item.attrib.get("type"):
                    case "food":
                        item_saturation = int(item_stats.attrib.get("saturation"))
                        items.append(Food(item_name, item_take_bool, item_mass, item_damage, item_saturation))
                    case "container":
                        item_max_mass = int(item_stats.attrib.get("max-mass"))
                        items.append(Container(item_name, item_take_bool, item_mass, item_damage, item_max_mass, []))
                    case "object":
                        items.append(Object(item_name, item_take_bool, item_mass, item_damage))
                    case "enemy":
                        item_blocking_list = []
                        item_health = int(item_stats.attrib.get("health"))
                        if item.find("blocking").text is not None:
                            item_blocking = item.find("blocking").text.split(",")
                            for i in item_blocking:
                                item_blocking_list.append(i)
                        items.append(
                            Enemy(item_name, item_take_bool, item_mass, item_damage, item_health, item_blocking_list))
                    case "weapon":
                        item_event = ""
                        if item_take.text is not None:
                            item_event = textwrap.dedent(item_take.text).strip()
                        items.append(Weapon(item_name, item_take_bool, item_mass, item_damage, item_event))

        scenes.append(Scene(scene_coordinates, scene_name, scene_setting, directions, items))

    return Map(map_name, map_splash, scenes, player_stats)


def choose_map(maps_dir):
    if not os.path.isdir(maps_dir):
        print("No maps folder was found. Creating one...")
        os.mkdir(maps_dir)

    while True:
        files = [f for f in listdir(maps_dir) if isfile(join(maps_dir, f))]

        if len(files) < 1:
            print("The maps folder is empty. Please add some maps.")
            webbrowser.open('file:///' + os.path.realpath(maps_dir))
            return

        print("Choose a map to play, or \"exit\":")

        for file in files:
            if file.lower().endswith(".athora"):
                game_map = elementTree.parse(f'{maps_dir}{file}')
                print(f'{files.index(file)}: {game_map.getroot().attrib.get("name")} ({file})')

        u_input = input('> ')

        if u_input == "quit" or u_input == "exit":
            return None

        try:
            val = int(u_input)
            if val >= len(files):
                print("That is not an option in the list of maps.")
                continue
            else:
                return maps_dir + files[val]
        except ValueError:
            print("Enter a valid number")
            continue


def make_direction(direction, coordinate, message, health):
    if message is None:
        return Destination(direction, coordinate, None, None)
    if health is None:
        return Destination(direction, None, textwrap.dedent(message).strip(), None)
    else:
        return Destination(direction, None, textwrap.dedent(message).strip(), health)


class Map:
    name = None
    splash = None
    scenes = []
    player = []

    def __init__(self, name, splash, scenes, player):
        self.name = name
        self.splash = splash
        self.scenes = scenes
        self.player = player

    def get_splash(self):
        return self.splash

    def get_player(self):
        return self.player

    def find_scene(self, coordinate: Coordinate) -> Scene:
        for scene in self.scenes:
            if coordinate == scene.get_coordinate():
                return scene

    def print_map(self, player: PlayerEntity):
        x_coords = []
        y_coords = []

        for scene in self.scenes:
            if scene.get_coordinate().z == player.get_z():
                x_coords.append(scene.get_coordinate().x)
                y_coords.append(scene.get_coordinate().y)
        print(f"You are on Level {str(player.get_z())}.\n")

        for x in reversed(sorted(set(x_coords))):
            for y in sorted(set(y_coords)):
                current_coord = Coordinate(x, y, player.get_z())
                adj_coord = Coordinate(x, y + 1, player.get_z())
                if self.find_scene(current_coord) is not None:
                    print("[Y]" if self.find_scene(current_coord) is player.get_current_scene() else "[ ]", end='')
                    print("-" if self.find_scene(adj_coord) is not None else " ", end='')
                else:
                    print("    ", end='')
            print()
            for y in sorted(set(y_coords)):
                current_coord = Coordinate(x, y, player.get_z())
                adj_coord = Coordinate(x - 1, y, player.get_z())
                print(" ", end='')
                if self.find_scene(adj_coord) and self.find_scene(current_coord) is not None:
                    print("|  " if any(current_coord == x.get_coordinate() for x in
                                       self.find_scene(adj_coord).get_destinations()) else "   ", end='')
                else:
                    print("   ", end='')
            print()

        print("[Y] = You")
