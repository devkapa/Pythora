class Object:

    name: str = None
    take: tuple = None
    mass: int = None
    damage: int = None

    # The constructor to be called when a new Object is created.
    def __init__(self, name, take, mass, damage):
        self.name = name
        self.take = take
        self.mass = mass
        self.damage = damage

    # Getters and setters
    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_mass(self) -> int:
        return self.mass

    def get_damage(self) -> int:
        return self.damage

    def get_take(self) -> tuple:
        return self.take
