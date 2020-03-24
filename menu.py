from pydispatch import Dispatcher
import item

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

class Inventory(object):
    def __init__(self, root_console, width, height):
        self.console = root_console
        self.slots = 20
        self.items = [item.Item(), item.Item()]
        self.w = width
        self.h = height
        self.cursor_index = 0
        # self.cursor_symbol = "▶" 
        self.cursor_symbol = ">" 

    def draw_frame(self):
        self.console.draw_frame(x=0, y=int(self.h/4), width=self.w, height=self.slots, title="Inventory", fg=(255,255,255), bg=(0,0,0))

    def render_items(self):
        row = 0
        self.draw_frame()
        for item in self.items:
            if self.cursor_index == row:
                self.console.print(x=1, y=int(self.h/4)+1+row, string=self.cursor_symbol + item.name)
            else:
                self.console.print(x=1, y=int(self.h/4)+1+row, string=" " + item.name)
            row += 1

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


