import tcod
import tcod.event
import globs
from pydispatch import Dispatcher

class MainControlsEmitter(Dispatcher):
    _events_ = ["interaction"]

class MainControls(object):
    def __init__(self, player, renderer, level):
        #mapobj and renderer is needed because it controls the scrolling and camera
        self.player = player
        self.r = renderer
        self.level = level
        self.emitter = MainControlsEmitter()

    def handlekeys(self):
        for event in tcod.event.get():
            if event.type == "QUIT":
                raise SystemExit()
            elif event.type == "KEYDOWN":
                if event.scancode == tcod.event.SCANCODE_DOWN:
                    if self.level.check_walkable(self.player.x, self.player.y+1):
                        self.player.y += 1
                elif event.scancode == tcod.event.SCANCODE_UP:
                    if self.level.check_walkable(self.player.x, self.player.y-1):
                        self.player.y -= 1
                elif event.scancode == tcod.event.SCANCODE_LEFT:
                    if self.level.check_walkable(self.player.x-1, self.player.y):
                        self.player.x -= 1
                elif event.scancode == tcod.event.SCANCODE_RIGHT:
                    if self.level.check_walkable(self.player.x+1, self.player.y):
                        self.player.x += 1
                elif event.scancode == tcod.event.SCANCODE_I:
                    self.emitter.emit("interaction")
                    #readjust camera
                if self.player.x >= globs.gWidth/2:
                    if self.r.start_x+self.r.w < self.level.mapobj.w or abs(self.player.x - globs.gWidth/2) <= 40:
                        self.r.start_x = int(abs(self.player.x - globs.gWidth/2))
                if self.player.y >= globs.gHeight/2:
                    if self.r.start_y+self.r.h < self.level.mapobj.h or abs(self.player.y - globs.gHeight/2) <= 40:
                        self.r.start_y = int(abs(self.player.y - globs.gHeight/2))

class InteractionControlsEmitter(Dispatcher):
    _events_ = ["interaction_finished"]

class InteractionControls(object):
    def __init__(self, player, level):
        self.level = level
        self.player = player
        self.emitter = InteractionControlsEmitter()

    def handlekeys(self):
        for event in tcod.event.wait():
            if event.type == "QUIT":
                raise SystemExit()
            elif event.type == "KEYDOWN":
                interactible, obj = self.level.check_interactible(self.player.x+1, self.player.y)
                if interactible:
                    obj.interact()
                self.emitter.emit("interaction_finished", obj=obj)


class ConversationControlsEmitter(Dispatcher):
    _events_ = ["confirm"]

class ConversationControls(object):
    def __init__(self):
        self.emitter = ConversationControlsEmitter()
        
    def handlekeys(self):
        for event in tcod.event.wait():
            if event.type == "QUIT":
                raise SystemExit()
            elif event.type == "KEYDOWN":
                if event.scancode == tcod.event.SCANCODE_SPACE:
                    print("space pressed")
                    self.emitter.emit("confirm")
                    
