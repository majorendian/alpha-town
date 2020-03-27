import classes
import state
from enum import Enum, auto

class Soil(classes.Floor):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = "."
        self.color = (129,71,4) #brown for soil

class Hole(classes.Floor):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = "o"
        self.color = (129,71,4) #brown for dirt
        self.interactible = True
        self.name = "Hole"
        self.text = ["A hole is in the ground"]

    def interact(self):
        print("interacted with hole")

class Plant(classes.Floor):
    class PlantStates():
        DRY = "DRY"
        WATERED = "WATERED"
        RIPE = "RIPE"
        DEAD = "DEAD"

    def save_json(self):
        return {"x": self.x,
                "y": self.y,
                "tile": type(self).__name__,
                "module": self.__module__,
                "state": self.state,
                "age": self.age,
                "health": self.health,
                "watered_time": self.watered_time}

    def load_json(self, d):
        self.x = d["x"]
        self.y = d["y"]
        self.state = d["state"]
        self.age = d["age"]
        self.health = d["health"]
        self.waterd_time = d["watered_time"]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = "f"
        self.color = (0,128,0)
        self.state = Plant.PlantStates.DRY
        self.age = 0
        self.health = 100
        self.watered_time = 0

    def update(self, level):
        for obj in level.objects_at(self.x, self.y):
            if not obj is self and isinstance(obj, classes.WaterDroplet):
                self.state = Plant.PlantStates.WATERED
                self.watered_time = 100
        if self.watered_time <= 0:
            self.state = Plant.PlantStates.DRY
        if self.state == Plant.PlantStates.DRY:
            self.health -= 1
            if self.health <= 0:
                self.state = Plant.PlantStates.DEAD
            self.color = (0,128,0)
        elif self.state == Plant.PlantStates.WATERED:
            if self.health < 100:
                self.health += 1
            self.color = (0,255,0)
        elif self.state == Plant.PlantStates.RIPE:
            pass
        elif self.state == Plant.PlantStates.DEAD:
            self.color = (128,64,64)
        self.age += 1
        if self.watered_time > 0:
            self.watered_time -= 1
        # print("plant:",self ,"state:",self.state, "watered:", self.watered_time)

class Potato(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self, level):
        super().update(level)
        if self.age > 100 and self.state != Plant.PlantStates.DEAD:
            self.symbol = "F"
            self.state = Plant.PlantStates.RIPE