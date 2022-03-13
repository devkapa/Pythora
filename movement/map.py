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
from movement.direction import Direction, get_index
from movement.scene import Scene


def get_map(path):
    game_map = elementTree.parse(path)

    root = game_map.getroot()
    map_name = root.attrib.get("name")
    map_splash = textwrap.dedent(root.find("splash").text)

    map_scenes = root.find("scenes").findall("scene")
    scenes = []

    for scene in map_scenes:
        scene_name = scene.attrib.get("name")
        scene_id = scene.attrib.get("id")
        scene_setting = textwrap.dedent(scene.find("setting").text)

        scene_directions = scene.find("directions")
        directions = []

        for direction in scene_directions:
            direction_uuid = direction.attrib.get("destination")
            direction_message = direction.text
            direction_health = direction.attrib.get("health")
            directions.insert(get_index(direction.tag),
                              make_direction(direction_uuid, direction_message, direction_health))

        scene_objects = scene.find("objects")
        items = []

        if scene_objects is not None:
            scene_items = scene_objects.findall("item")
            for item in scene_items:
                item_name = item.find("name").text
                item_stats = item.find("stats")
                item_take = item.find("take")
                item_take_bool = bool(item_take.attrib.get("bool"))
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
                                item_blocking_list.append(int(i))
                        items.append(
                            Enemy(item_name, item_take_bool, item_mass, item_damage, item_health, item_blocking_list))
                    case "weapon":
                        item_event = ""
                        if item_take.text is not None:
                            item_event = textwrap.dedent(item_take.text)
                        items.append(Weapon(item_name, item_take_bool, item_mass, item_damage, item_event))

        scenes.append(Scene(scene_id, scene_name, scene_setting, directions, items))

    return Map(map_name, map_splash, scenes)


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

        print("Please choose which map you would like to play:")

        for file in files:
            if file.lower().endswith(".athora"):
                game_map = elementTree.parse(f'{maps_dir}{file}')
                print(f'{files.index(file)}: {game_map.getroot().attrib.get("name")} ({file})')

        u_input = input('> ')

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


def make_direction(uuid, message, health):
    if message is None:
        return Direction(uuid, None, None)
    if health is None:
        return Direction(None, textwrap.dedent(message).strip(), None)
    else:
        return Direction(None, textwrap.dedent(message).strip(), health)


class Map:
    name = None
    splash = None
    scenes = []

    def __init__(self, name, splash, scenes):
        self.name = name
        self.splash = splash
        self.scenes = scenes

    def get_splash(self):
        return self.splash

    def find_scene(self, uuid):
        for scene in self.scenes:
            if uuid == scene.get_uuid():
                return scene
