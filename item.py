import globs
import classes
from enum import Enum, auto

class Item(object):
    def __init__(self):
        self.name = "Default item"
        self.description = "Default item description"

    def use(self):
        print("item",self.name,"used")

class ToolHandler(object):
    class Tools(Enum):
        WATERING_BUCKET = auto()
        SHOVEL = auto()
        
    def __init__(self, player, level):
        self.level = level
        self.player = player
        self.current_tool = None

    def use_tool(self, vector):
        if self.current_tool == ToolHandler.Tools.WATERING_BUCKET:
            self.water_bucket(vector)

    # tool functions
    def water_bucket(self, vector): #data = vector to spawn the water on
        newtile = classes.WaterDroplet(self.player.x+vector[0], self.player.y+vector[1])
        globs.gEventHandler.emit("add_object", newtile)
        

class WateringBucket(Item):
    def __init__(self):
        super().__init__()
        self.name = "Watering bucket"
        self.description = "Used to water crops"

    def use(self):
        globs.gEventHandler.emit("use_tool", ToolHandler.Tools.WATERING_BUCKET)
