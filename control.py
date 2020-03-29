import tcod
import tcod.event
import globs
from pydispatch import Dispatcher

class MainControlsEmitter(Dispatcher):
    _events_ = ["interaction", "inventory_open", "in_game_menu", "pickup_item"]

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
                # print("playerx:",self.player.x,"playery:",self.player.y)
                if event.scancode == tcod.event.SCANCODE_DOWN:
                    if self.player.y+2 < self.level.mapobj.h:
                        if self.level.check_walkable(self.player.x, self.player.y+1):
                            self.player.y += 1
                elif event.scancode == tcod.event.SCANCODE_UP:
                    if self.player.y > 0:
                        if self.level.check_walkable(self.player.x, self.player.y-1):
                            self.player.y -= 1
                elif event.scancode == tcod.event.SCANCODE_LEFT:
                    if self.player.x > 0:
                        if self.level.check_walkable(self.player.x-1, self.player.y):
                            self.player.x -= 1
                elif event.scancode == tcod.event.SCANCODE_RIGHT:
                    if self.player.x+2 < self.level.mapobj.w:
                        if self.level.check_walkable(self.player.x+1, self.player.y):
                            self.player.x += 1
                elif event.scancode == tcod.event.SCANCODE_E:
                    self.emitter.emit("interaction")
                elif event.scancode == tcod.event.SCANCODE_I:
                    self.emitter.emit("inventory_open")
                elif event.scancode == tcod.event.SCANCODE_ESCAPE:
                    self.emitter.emit("in_game_menu")
                elif event.scancode == tcod.event.SCANCODE_U:
                    globs.gEventHandler.emit("use_tool")
                elif event.scancode == tcod.event.SCANCODE_G:
                    obj = self.level.check_item(self.player.x, self.player.y) or self.level.check_plant(self.player.x, self.player.y)
                    if obj:
                        self.emitter.emit("pickup_item", obj)


class InteractionControlsEmitter(Dispatcher):
    _events_ = ["interaction_direction"]

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
                self.emitter.emit("interaction_direction", obj=obj)

class ToolControlsEmitter(Dispatcher):
    _events_ = ["direction"]

class ToolControls(object):
    def __init__(self, player, level):
        self.level = level
        self.player = player
        self.emitter = ToolControlsEmitter()

    def handlekeys(self):
        for event in tcod.event.wait():
            if event.type == "QUIT":
                raise SystemExit()
            elif event.type == "KEYDOWN":
                if event.scancode == tcod.event.SCANCODE_LEFT:
                    self.emitter.emit("direction", data=(-1,0))
                elif event.scancode == tcod.event.SCANCODE_RIGHT:
                    self.emitter.emit("direction", data=(1,0))
                elif event.scancode == tcod.event.SCANCODE_UP:
                    self.emitter.emit("direction", data=(0,-1))
                elif event.scancode == tcod.event.SCANCODE_DOWN:
                    self.emitter.emit("direction", data=(0,1))
                
class NonToolsControlsEmitter(ToolControlsEmitter):
    pass

class NonToolsControls(ToolControls):
    def __init__(self, player, level):
        super().__init__(player, level)
        self.emitter = NonToolsControlsEmitter()


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
    _events_ = ["move_down", "move_up", "cancel", "select", "drop"]

class InventoryControls(MenuControls):
    def __init__(self):
        self.emitter = InventoryControlsEmitter()

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
                elif event.scancode == tcod.event.SCANCODE_D:
                    self.emitter.emit("drop")
