import render
import json
import classes
import farm
import globs
import sys

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
    def check_item(self, x, y):
        objects = self.objects_at(x, y)
        for obj in objects:
            if obj.item:
                return obj

    def objects_at(self, x, y):
        objlist = []
        for obj in self.objects:
            if obj.x == x and obj.y == y:
                objlist.append(obj)
        return objlist

class LevelManager(object):
    def __init__(self):
        self.mapobj = render.Map()
        self.level = Level(self.mapobj, [])
        self.filename = None
        self.player = None
        self.inventory = None
        globs.gEventHandler.bind("object_destroy", self.destroy_object)
        globs.gEventHandler.bind("add_object", self.add_object)
        globs.gEventHandler.bind("add_object_append", self.add_object_append)

    def add_object(self, obj):
        print("adding object",obj)
        self.level.objects.insert(0, obj)

    def add_object_append(self, obj):
        self.level.objects.append(obj)

    def destroy_object(self, obj):
        print("destroying object", obj)
        self.level.objects.remove(obj) # this should remove the water droplet

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
        d["inventory"] = self.inventory.save_json()
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
            self.inventory.load_json(d["inventory"])

    def get_level(self):
        return self.level

    def process_objects(self, json_objects, load=False):
        objects = []
        for obj in json_objects:
            tile = classes.Tile(0,0)
            if obj["tile"] == "Player":
                tile = classes.Player(obj["x"], obj["y"])
                self.player = tile
            else:
                print("obj:",obj)
                tile = getattr(sys.modules[obj["module"]], obj["tile"])(obj["x"], obj["y"])
            if load:
                tile.load_json(obj)
            objects.append(tile)
        self.level.objects = objects
