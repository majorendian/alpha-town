import globs
import classes
import farm
from enum import Enum, auto

class Item(object):
    def __init__(self):
        self.name = "Default item"
        self.description = "Default item description"
        self.count = 1
        self.tile = classes.Tile(0,0)

    def save_json(self):
        return {"module": self.__module__, "item": type(self).__name__, "count" : self.count}

    def use(self):
        print("item",self.name,"used")

class ItemTile(classes.Tile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Default item"
        self.description = "Default item description"
        self.count = 1
        self.item = Item
        self.symbol = "i"

    def save_json(self):
        d = super().save_json()
        d["count"] = self.count
        return d

    def load_json(self, jsond):
        super().load_json(jsond)
        self.count = jsond["count"]

class ToolHandler(object):
    class Tools(Enum):
        WATERING_BUCKET = auto()
        SHOVEL = auto()
        SPADE = auto()
        
    def __init__(self, player, level):
        self.level = level
        self.player = player
        self.current_tool = None
        self.toolfuncs = {
            ToolHandler.Tools.WATERING_BUCKET : self.water_bucket,
            ToolHandler.Tools.SHOVEL : self.shovel,
            ToolHandler.Tools.SPADE : self.spade,
        }

    def use_tool(self, vector):
        self.toolfuncs[self.current_tool](vector)

    # tool functions
    def water_bucket(self, vector): #data = vector to spawn the water on
        if vector[0] != 0:
            globs.gEventHandler.emit("add_object_append", classes.WaterDroplet(self.player.x+vector[0], self.player.y+vector[1]))
            globs.gEventHandler.emit("add_object_append", classes.WaterDroplet(self.player.x+vector[0], self.player.y+vector[1]+1))
            globs.gEventHandler.emit("add_object_append", classes.WaterDroplet(self.player.x+vector[0], self.player.y+vector[1]-1))
        if vector[1] != 0:
            globs.gEventHandler.emit("add_object_append", classes.WaterDroplet(self.player.x+vector[0], self.player.y+vector[1]))
            globs.gEventHandler.emit("add_object_append", classes.WaterDroplet(self.player.x+vector[0]+1, self.player.y+vector[1]))
            globs.gEventHandler.emit("add_object_append", classes.WaterDroplet(self.player.x+vector[0]-1, self.player.y+vector[1]))

    def create_object(self, vector, objclass):
        objects = self.level.objects_at(self.player.x + vector[0], self.player.y + vector[1])
        if len(objects) == 0:
            newtile = objclass(self.player.x+vector[0], self.player.y+vector[1])
            globs.gEventHandler.emit("add_object", newtile)
        else:
            for obj in objects:
                if isinstance(obj, objclass):
                    globs.gEventHandler.emit("object_destroy", obj)
        

    def spade(self, vector):
        self.create_object(vector, farm.Soil)

    def shovel(self, vector):
        self.create_object(vector, farm.Hole)

class NonToolHandler(object):
    class Objects(Enum):
        SEEDS = auto()
        FURNITURE = auto()

    def __init__(self, player, level):
        self.player = player
        self.level = level
        self.obj = None
        self.funcs = {
            NonToolHandler.Objects.SEEDS : self.seeds,
            NonToolHandler.Objects.FURNITURE : self.furniture
        }

    def use_object(self, vector):
        return self.funcs[self.obj.type](vector)

    def seeds(self, vector):
        print("using seeds on vector:",vector,self.obj)
        found_soil = False
        error = False
        msg = ""
        if self.obj.count <= 0:
            return (True, "No more seeds of this kind")
        objects = self.level.objects_at(self.player.x+vector[0], self.player.y+vector[1])
        for obj in objects:
            if isinstance(obj, farm.Soil):
                self.obj.count -= 1
                globs.gEventHandler.emit("object_destroy", obj)
                obj = self.obj.plant(obj.x, obj.y)
                globs.gEventHandler.emit("add_object", obj)
                found_soil = True
        if not found_soil:
            error = True
            msg = "No soil to plant the seed"
        return (error, msg)
    def furniture(self, vector):
        print("placing furniture:",self.obj)
        
class Tool(Item):
    def __init__(self):
        super().__init__()
        self.name = "Default tool"
        self.description = "No use"
        self.tool = None

    def use(self):
        globs.gEventHandler.emit("use_tool", self.tool)

class WateringBucket(Tool):
    def __init__(self):
        super().__init__()
        self.name = "Watering bucket"
        self.description = "Used to water crops"
        self.tool = ToolHandler.Tools.WATERING_BUCKET
        self.tile = WateringBucketTile

class WateringBucketTile(ItemTile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = "b"
        self.color = (50,50,200)
        self.item = WateringBucket

class Shovel(Tool):
    def __init__(self):
        super().__init__()
        self.name = "Shovel"
        self.description = "Used to dig into the ground"
        self.tool = ToolHandler.Tools.SHOVEL
        self.tile = ShovelTile

class ShovelTile(ItemTile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = "v"
        self.color = (200,200,200)
        self.item = Shovel

        
class Spade(Tool):
    def __init__(self):
        super().__init__()
        self.name = "Spade"
        self.description = "Used tild soil"
        self.tool = ToolHandler.Tools.SPADE
        self.tile = SpadeTile

class SpadeTile(ItemTile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = "j"
        self.color = (200,200,200)
        self.item = Spade


class Seeds(Item):
    def __init__(self):
        super().__init__()
        self.name = "Default seeds"
        self.description = "Default seeds"
        self.tile = SeedsTile
        self.type = NonToolHandler.Objects.SEEDS
        self.plant = farm.Plant

    def use(self):
        globs.gEventHandler.emit("use_non_tool", self)

class SeedsTile(ItemTile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Default seeds tile"
        self.description = "Default seeds tile"
        self.item = Seeds
        self.symbol = "s"

class Potato(Seeds):
    def __init__(self):
        super().__init__()
        self.name = "Potatos"
        self.description = "Can be planted into the ground" 
        self.tile = PotatoTile
        self.plant = farm.Potato

class PotatoTile(SeedsTile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.name = "Potato"
        self.description = "Can be planted for more potatoes"
        self.item = Potato
        self.color = (100,30,10)
