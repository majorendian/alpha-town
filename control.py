import tcod
import tcod.event
import globs
from pydispatch import Dispatcher

class MainControlsEmitter(Dispatcher):
    _events_ = ["interaction", "inventory_open", "in_game_menu"]

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
                elif event.scancode == tcod.event.SCANCODE_E:
                    self.emitter.emit("interaction")
                elif event.scancode == tcod.event.SCANCODE_I:
                    self.emitter.emit("inventory_open")
                elif event.scancode == tcod.event.SCANCODE_ESCAPE:
                    self.emitter.emit("in_game_menu")
                    #readjust camera
                # if self.player.x >= globs.gWidth/2:
                #     if self.r.start_x+self.r.w < self.level.mapobj.w or abs(self.player.x - globs.gWidth/2) <= self.level.mapobj.w - self.player.x:
                #         self.r.start_x = int(abs(self.player.x - globs.gWidth/2))
                # if self.player.y >= globs.gHeight/2:
                #     if self.r.start_y+self.r.h < self.level.mapobj.h or abs(self.player.y - globs.gHeight/2) <= 40:
                #         self.r.start_y = int(abs(self.player.y - globs.gHeight/2))
                #170 256

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
                interactible, obj = (None, None)
                if event.scancode == tcod.event.SCANCODE_RIGHT:
                    interactible, obj = self.level.check_interactible(self.player.x+1, self.player.y)
                elif event.scancode == tcod.event.SCANCODE_LEFT:
                    interactible, obj = self.level.check_interactible(self.player.x-1, self.player.y)
                elif event.scancode == tcod.event.SCANCODE_UP:
                    interactible, obj = self.level.check_interactible(self.player.x, self.player.y-1)
                elif event.scancode == tcod.event.SCANCODE_DOWN:
                    interactible, obj = self.level.check_interactible(self.player.x, self.player.y+1)
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
                    


class MenuControlsEmitter(Dispatcher):
    _events_ = ["move_up", "move_down", "select", "cancel"]

class MenuControls(object):
    def __init__(self):
        self.emitter = MenuControlsEmitter()

    def handlekeys(self):
        for event in tcod.event.wait():
            if event.type == "QUIT":
                raise SystemExit()
            elif event.type == "KEYDOWN":
                if event.scancode == tcod.event.SCANCODE_DOWN:
                    self.emitter.emit("move_down")
                elif event.scancode == tcod.event.SCANCODE_UP:
                    self.emitter.emit("move_up")
                elif event.scancode == tcod.event.SCANCODE_I or event.scancode == tcod.event.SCANCODE_ESCAPE:
                    self.emitter.emit("cancel")
                elif event.scancode == tcod.event.SCANCODE_SPACE:
                    self.emitter.emit("select")

class InventoryControlsEmitter(MenuControlsEmitter):
    pass

class InventoryControls(MenuControls):
    def __init__(self):
        self.emitter = InventoryControlsEmitter()
