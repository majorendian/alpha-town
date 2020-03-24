from pydispatch import Dispatcher

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
