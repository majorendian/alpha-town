from pydispatch import Dispatcher
import item
import globs
import sys

class TextWindowEmitter(Dispatcher):
    _events_ = ["close"]

class TextWindow(object):
    def __init__(self, tcod_console, width, height, title):
        self.console = tcod_console
        self.w = width
        self.h = height
        self.title = title
        self.pages = []
        self.pindex = 0
        self.emitter = TextWindowEmitter()

    def set_pages(self, l):
        self.pages = l

    def draw_frame(self, title):
        self.console.draw_frame(x=0, y=0, width=self.w, height=self.h, title=title, fg=(255,255,255), bg=(0,0,0))

    def print_text(self, text):
        self.draw_frame(self.title)
        self.console.print_box(x=1, y=1, width=self.w-1, height=self.h-1, string=text)

    def on_confirm(self):
        if len(self.pages) > self.pindex:
            self.print_text(self.pages[self.pindex])
            self.pindex += 1
        else:
            self.pindex = 0
            self.emitter.emit("close")

class MenuItem(object):
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def execute(self):
        self.func()

class Menu(object):
    def __init__(self, root_console, width, height, items=[]):
        self.console = root_console
        self.items = items
        self.cursor_symbol = ">"
        self.cursor_index = 0
        self.w = width
        self.h = height
        self.title = "Menu"

    def draw_frame(self):
        print("item length", len(self.items))
        self.console.draw_frame(x=0, y=int(self.h/4), width=self.w, height=len(self.items)+2, title=self.title, fg=(255,255,255), bg=(0,0,0))

    def render_items(self):
        row = 0
        self.draw_frame()
        for item in self.items:
            if self.cursor_index == row:
                self.console.print(x=1, y=int(self.h/4)+1+row, string=self.cursor_symbol + item.name, fg=(20,20,255))
            else:
                self.console.print(x=1, y=int(self.h/4)+1+row, string=" " + item.name)
            row += 1

    def move_up(self):
        if self.cursor_index > 0:
            self.cursor_index -= 1
        self.render_items()

    def move_down(self):
        if self.cursor_index+1 < len(self.items):
            self.cursor_index += 1
        self.render_items()

    def select(self):
        item = self.items[self.cursor_index]
        print("selected item:",item)
        item.execute()

class Inventory(Menu):
    def __init__(self, root_console, width, height):
        super().__init__(root_console, width, height, [])
        self.slots = 20
        seeds = item.Seeds()
        seeds.count = 5
        self.items = [item.Item(), item.WateringBucket(), item.Shovel(), item.Spade(), seeds]

    def draw_frame(self):
        self.console.draw_frame(x=0, y=int(self.h/4), width=self.w, height=self.slots, title=self.title, fg=(255,255,255), bg=(0,0,0))

    def render_items(self):
        row = 0
        self.draw_frame()
        for item in self.items:
            count_display = False
            if item.count > 1:
                count_display = True
            if self.cursor_index == row:
                if count_display:
                    self.console.print(x=1, y=int(self.h/4)+1+row, string=self.cursor_symbol + item.name + " ("+str(item.count)+")", fg=(20,20,255))
                else:
                    self.console.print(x=1, y=int(self.h/4)+1+row, string=self.cursor_symbol + item.name, fg=(20,20,255))
                        
            else:
                if count_display:
                    self.console.print(x=1, y=int(self.h/4)+1+row, string=" " + item.name + "("+str(item.count)+")")
                else:
                    self.console.print(x=1, y=int(self.h/4)+1+row, string=" " + item.name)
            row += 1

    def save_json(self):
        invlist = []
        for item in self.items:
            invlist.append(item.save_json())
        return invlist

    def load_json(self, d):
        for entry in d:
            item = getattr(sys.modules[entry["module"]], entry["item"])()
            item.count = entry["count"]
            self.items.append(item)

    def move_up(self):
        if self.cursor_index > 0:
            self.cursor_index -= 1
        self.render_items()

    def move_down(self):
        print("moving down")
        if self.cursor_index < self.slots and self.cursor_index+1 < len(self.items):
            self.cursor_index += 1
        self.render_items()

    def select(self):
        item = self.items[self.cursor_index]
        item.use()

    def add_item(self, it):
        found = False
        for i in self.items:
            if type(it) == type(i):
                i.count += it.count
                found = True
        if not found:
            print("addind to inventory:",it,"count:",it.count)
            self.items.append(it)
        

    def drop_item(self):
        item = self.items[self.cursor_index]
        if item.count == 1:
            self.items.remove(item)
        else:
            item.count -= 1
        self.render_items()
        globs.gEventHandler.emit("drop_item", item, self.cursor_index)


