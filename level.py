import render
import json
import classes

class Level(object):
    def __init__(self, mapobj, objects):
        self.mapobj = mapobj
        self.objects = objects

    def check_walkable(self, x, y):
        walkable = False
        if self.mapobj.m[y][x].walkable:
            walkable = True
        for o in self.objects:
            if o.x == x and o.y == y and not o.walkable:
                walkable = False
        return walkable

    def check_interactible(self, x, y):
        interactible = False
        obj = None
        if self.mapobj.m[y][x].interactible:
            interactible = True
        for o in self.objects:
            if o.x == x and o.y == y and not o.interactible:
                interactible = False
            elif o.x == x and o.y == y and o.interactible:
                obj = o
                interactible = True
        return (interactible, obj)

class LevelManager(object):
    def __init__(self):
        self.mapobj = render.Map()
        self.level = Level(self.mapobj, [])

    def load_level(self, level_json):
        with open(level_json, "r") as f:
            jsondata = json.load(f)
            self.mapobj.set_map(jsondata["map"])
            self.process_objects(jsondata["objects"])

    def get_level(self):
        return self.level

    def process_objects(self, json_objects):
        objects = []
        for obj in json_objects:
            tile = classes.Tile(0,0)
            if obj["type"] == "npc":
                tile = classes.NPC(obj["x"], obj["y"])
            else:
                tile.color = (255,0,0)
            objects.append(tile)
        self.level.objects = objects
