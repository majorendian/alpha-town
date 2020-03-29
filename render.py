import json
import classes

class Map(object):
    def __init__(self, json_file=None):
        if json_file:
            self.load_map(json_file)
        else:
            self.m = None
            self.w = 0
            self.h = 0

    def load_map(self, json_file):
        self.m = self.process(self.parse(json_file))
        self.h = len(self.m)
        self.w = len(self.m[0])

    def set_map(self, parsed_json):
        self.m = self.process(parsed_json)
        self.h = len(self.m)
        self.w = len(self.m[0])
        

    def parse(self, json_file):
        with open(json_file) as f:
            return json.load(f)

    def process(self, jsonarray):
        y = 0
        newmap = []
        for row in jsonarray:
            x = 0
            newr = []
            for cel in row:
                t = classes.Tile(x,y) # need categorization for this
                if cel == "#":
                    t = classes.Wall(x,y)
                elif cel == ".":
                    t = classes.Floor(x,y)
                elif cel == "h":
                    t = classes.WoodenChair(x,y)
                elif cel == "T":
                    t = classes.WoodenTable(x,y)
                elif cel == ",":
                    t = classes.Grass(x, y)
                newr.append(t)
                x += 1
            newmap.append(newr)
            y += 1
        return newmap

class Renderer(object):
    def __init__(self, tcod_console, width, height):
        self.console = tcod_console
        self.w = width
        self.h = height
        self.start_x = 0
        self.start_y = 0

    def render(self, mapobj, objects):
        #mapobj is the underlying map
        #objects are objects overlayed on the map
        assert isinstance(mapobj, Map)
        # print("start_x:",self.start_x)
        for row in mapobj.m:
            for tile in row:
                if tile.x < self.w+self.start_x and tile.y < self.h+self.start_y and\
                   tile.x >= self.start_x and tile.y >= self.start_y:
                    self.console.print(x=tile.x-self.start_x, y=tile.y-self.start_y, string=tile.symbol, fg=tile.color)

        for obj in objects:
            if obj.x < self.w+self.start_x and obj.y < self.h+self.start_y and\
               obj.x >= self.start_x and obj.y >= self.start_y:
                self.console.print(x=obj.x-self.start_x, y=obj.y-self.start_y, string=obj.symbol, fg=obj.color)
                
            
