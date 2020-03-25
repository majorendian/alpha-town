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
            obj = self.mapobj.m[y][x]
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
        self.filename = None
        self.player = None

    def load_level(self, level_json):
        self.filename = level_json
        with open(level_json, "r") as f:
            jsondata = json.load(f)
            self.mapobj.set_map(jsondata["map"])
            if "objects" in jsondata.keys():
                self.process_objects(jsondata["objects"])
            self.player = classes.Player(jsondata["spawn_point"][0], jsondata["spawn_point"][1])

    def save_level(self, save_file):
        d = {"level": self.filename, "objects": []}
        for obj in self.level.objects:
            objd = obj.save_json()
            d["objects"].append(objd)
        with open(save_file, "w") as f:
            f.write(json.dumps(d))

    def load_save(self, save_file):
        with open(save_file, "r") as f:
            d = json.load(f)
            self.mapobj = render.Map()
            self.level = Level(self.mapobj, [])
            self.filename = d["level"]
            with open(self.filename) as lf:
                self.mapobj.set_map(json.load(lf)["map"])
            self.process_objects(d["objects"], True)

    def get_level(self):
        return self.level

    def process_objects(self, json_objects, load=False):
        objects = []
        for obj in json_objects:
            tile = classes.Tile(0,0)
            if obj["tile"] == "NPC":
                tile = classes.NPC(obj["x"], obj["y"])
            elif obj["tile"] == "Player":
                tile = classes.Player(obj["x"], obj["y"])
                self.player = tile
            else:
                tile.color = (255,0,0)
            if load:
                tile.load_json(obj)
            objects.append(tile)
        self.level.objects = objects
