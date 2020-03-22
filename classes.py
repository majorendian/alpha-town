import random

class Universal(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.symbol = " "
        self.color = (255,255,255)
        self.walkable = True
        self.interactible = False

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

class NPC(Entity):
    def __init__(self, x, y):
        super().__init__(x,y)
        self.symbol = "@"
        self.walkable = False
        self.interactible = True

    def interact(self):
        print("npc says hello")

    def update(self, level):
        #NOTE we need to check for collisions
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

    def draw():
        pass

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


class MovingBackroundStar(Tile):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.walkable = False
        self.symbol = "."
        self.cupdate = 0
        self.update_freq = 2

    def draw(self):
        if self.update_freq == self.cupdate:
            self.y += 1
            if self.y >= 40:
                self.y = 0
            self.cupdate = 0
        else:
            self.cupdate += 1
                
