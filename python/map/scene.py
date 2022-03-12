from python.items.object import Object


class Scene:

    uuid = None
    name = None
    setting = None
    destinations = []
    items: list[Object] = []

    def __init__(self, uuid, name, setting, destinations, items):
        self.uuid = uuid
        self.name = name
        self.setting = setting
        self.destinations = destinations
        self.items = items

    def get_uuid(self):
        return self.uuid

    def get_name(self):
        return self.name

    def get_setting(self):
        return self.setting

    def get_destinations(self):
        return self.destinations

    def get_items(self):
        return self.items
