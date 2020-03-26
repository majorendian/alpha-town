import random
import globs

class Universal(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.symbol = " "
        self.color = (255,255,255)
        self.walkable = True
        self.interactible = False

    def save_json(self):
        return {"x": self.x, "y": self.y, "tile": type(self).__name__}

    def load_json(self, d):
        self.x = d["x"]
        self.y = d["y"]
        print("loaded obj",self)

    def draw(self):
        pass

    def update(self, mapobj):
        pass

class Player(Universal):
    def __init__(self,x,y):
        super().__init__()
        self.x = x
        self.y = y
        self.symbol = "@"
        self.color = (255,0,0)

class Entity(Universal):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y

class Furniture(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.text = ["A Piece of furniture"]
        self.name = "Furniture"
        self.walkable = False
        self.interactible = True


class WoodenChair(Furniture):
    def __init__(self,x ,y):
        super().__init__(x, y)
        self.name = "Wooden chair"
        self.symbol = "h"
        self.color = (129,71,4)
        self.text = ["A simple wooden chair. Comfortable to sit on"]

class WoodenTable(Furniture):
    def __init__(self,x ,y):
        super().__init__(x, y)
        self.name = "Wooden table"
        self.color = (129,71,4)
        self.symbol = "T"
        self.text = ["A wooden table"]


class NPC(Entity):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.symbol = "@"
        self.walkable = False
        self.interactible = True
        self.text = ["Default npc text"]
        self.name = "Default npc"

    def update(self, level):
        randx = random.randrange(3)-1
        randy = random.randrange(3)-1
        nextx = self.x + randx
        nexty = self.y + randy
        if nextx > 0 and nextx < level.mapobj.w and level.check_walkable(nextx, self.y):
            self.x += randx
        if nexty > 0 and nexty < level.mapobj.h and level.check_walkable(self.x, nexty):
            self.y += randy
    

class Tile(Universal):
    def __init__(self, x, y):
        super().__init__()
        self.walkable = True
        self.x = x
        self.y = y

    def draw(self):
        pass

class WaterDroplet(Tile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.ttl = 1
        self.accum = 0
        self.symbol = "~"
        self.color = (20,20,250)

    def draw(self):
        self.accum += 1
        if self.accum % 4 == 0:
            self.symbol = "-"
        else:
            self.symbol = "~"
            
    def update(self, level):
        if self.ttl <= 0:
            globs.gEventHandler.emit("object_destroy", self)
        self.ttl -= 1
        

        
class Wall(Tile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = "#"
        self.walkable = False

class Floor(Tile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.walkable = True
        self.symbol = "."
        self.color = (50,50,50)

class Grass(Floor):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.symbol = ","
        self.color = (50,255,50)
