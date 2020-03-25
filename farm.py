import classes
import state
from enum import Enum, auto

class Soil(classes.Floor):
    def __init__(self, x, y):
        super().__init__(self, x, y)
        self.symbol = "."
        self.color = (129,71,4) #brown for soil


class Plant(classes.Floor):
    class PlantStates():
        DRY = "DRY"
        WATERED = "WATERED"
        RIPE = "RIPE"
        DEAD = "DEAD"

    def save_json(self):
        return {"x":self.x, "y": self.y, "tile": type(self).__name__, "state": self.state, "age": self.age, "health": self.health}

    def load_json(self, d):
        self.x = d["x"]
        self.y = d["y"]
        self.state = d["state"]
        self.age = d["age"]
        self.health = d["health"]

    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = "f"
        self.color = (0,255,0)
        self.state = Plant.PlantStates.DRY
        self.age = 0
        self.health = 100

    def update(self, level):
        if self.state == Plant.PlantStates.DRY:
            self.health -= 1
            if self.health <= 0:
                self.state = Plant.PlantStates.DEAD
        elif self.state == Plant.PlantStates.WATERED:
            if self.health < 100:
                self.health += 1
        elif self.state == Plant.PlantStates.RIPE:
            pass
        elif self.state == Plant.PlantStates.DEAD:
            self.color = (128,64,64)
        self.age += 1

class Potato(Plant):
    def __init__(self, x, y):
        super().__init__(x, y)

    def update(self, level):
        super().update(level)
        if self.age > 10 and self.state != Plant.PlantStates.DEAD:
            self.symbol = "F"
            self.state = Plant.PlantStates.RIPE
