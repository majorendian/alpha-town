
import tcod
import time
import tcod.event
import classes
from random import randrange
import state
import render
from globs import *
import control
import level
from enum import Enum, auto
import menu
import item
import farm
import os.path
import threading

gRootConsole = None # just so that we can reference it inside the classes
# Basic states of the game
class GameState:
    class Intro(state.State):
        def __init__(self, fsm):
            super().__init__(fsm)
            self.fsm.game_continue = False
            with open("intro.ascii","r") as f:
                self.protag_ascii = f.read()
            items = [menu.MenuItem("New Game", self.new_game), menu.MenuItem("Quit", self.quit_game)]
            if os.path.isfile("save.json"):
                items.insert(0, menu.MenuItem("Continue", self.continue_game))
            self.menu = menu.Menu(gRootConsole, 30, gHeight+30, items, int(gWidth - gWidth/4),0)
            self.menu.title = ""
            self.menu_controls = control.MenuControls()
            self.menu_controls.emitter.bind(move_down=self.menu.move_down)
            self.menu_controls.emitter.bind(move_up=self.menu.move_up)
            self.menu_controls.emitter.bind(select=self.menu.select)

        def new_game(self):
            self.fsm.game_continue = False
            self.fsm.transition("from_intro_to_game")

        def quit_game(self):
            raise SystemExit()

        def continue_game(self):
            self.fsm.game_continue = True
            self.fsm.transition("from_intro_to_game")

        def run(self):
            gRootConsole.print(x=0,y=0,string=self.protag_ascii)
            self.menu.render_items()
            self.menu_controls.handlekeys()

    class Game(state.State):

        class ControlState(Enum):
            ROAM = auto()
            INTERACTION = auto()
            DIALOGUE = auto()
            INVENTORY = auto()
            MENU = auto()
            TOOL = auto()
            NONTOOL = auto()
            SIMPLE_CRAFTING = auto()
            SIMPLE_CRAFTING_SUBMENU = auto()

        def __init__(self, fsm):
            super().__init__(fsm)

        def enter(self):
            self.r = render.Renderer(gRootConsole, gWidth, gHeight)
            self.help_statusbar = menu.HelpStatusBar(gRootConsole, gWidth, gHeight)

            #clears the status bar after 10 seconds
            self.help_statusbar_timer = None
            
            self.inventory = menu.Inventory(gRootConsole, gWidth, gHeight)
            self.lm = level.LevelManager()
            self.lm.inventory = self.inventory
            if self.fsm.game_continue:
                print("LOADING")
                self.lm.load_save("save.json")
                self.player = self.lm.player
            else:
                print("NEW LEVEL")
                self.lm.new_level()
                # self.lm.load_level("basic_starter_level.json")
                self.player = self.lm.player
                self.lm.level.objects.append(self.player)
            self.interaction_state = GameState.Game.ControlState.ROAM

            self.controls = control.MainControls(self.player, self.r, self.lm.level)
            self.interaction_controls = control.InteractionControls(self.player, self.lm.level)
            self.controls.emitter.bind(interaction=self.on_interaction)
            self.controls.emitter.bind(inventory_open=self.on_inventory_open)
            self.controls.emitter.bind(in_game_menu=self.on_in_game_menu_open)
            self.controls.emitter.bind(pickup_item=self.on_item_pickup)
            self.controls.emitter.bind(simple_crafting_menu=self.on_simple_crafting_menu)

            self.interaction_controls.emitter.bind(interaction_direction=self.on_interaction_direction)
            self.conversation_controls = control.ConversationControls()

            #we need a handle for the text window to be persitent or else the function will not be called so we need this textwindow variable
            self.text_window = None

            #inventory
            self.inventory_controls = control.InventoryControls()
            self.inventory_controls.emitter.bind(move_down=self.inventory.move_down)
            self.inventory_controls.emitter.bind(move_up=self.inventory.move_up)
            self.inventory_controls.emitter.bind(select=self.inventory.select)
            self.inventory_controls.emitter.bind(cancel=self.on_inventory_close)
            self.inventory_controls.emitter.bind(drop=self.inventory.drop_item)

            #tools
            self.tool_controls = control.ToolControls(self.player, self.lm.level)
            self.tool_controls.emitter.bind(direction=self.on_tool_use_direction)

            #non-tools
            self.nontool_controls = control.NonToolsControls(self.player, self.lm.level)
            self.nontool_controls.emitter.bind(direction=self.on_nontool_use_direction)
            self.nontool_handler = item.NonToolHandler(self.player, self.lm.level)

            #in game menu
            self.menu_controls = control.MenuControls()
            self.in_game_menu = None # needs to be none just like for the text window

            #crafting menu
            self.simple_crafting_controls = control.SimpleCraftingControls()
            self.simple_crafting_menu = None

            self.simple_crafting_submenu_controls = control.SimpleCraftingSubmenuControls()
            self.simple_crafting_submenu = None

            #global events
            self.tool_handler = item.ToolHandler(self.player, self.lm.level)
            # gEventHandler.bind("inventory_item_close", self.on_inventory_close)
            self._last_used = None
            gEventHandler.bind("use_tool", self.on_use_tool)
            gEventHandler.bind("drop_item", self.on_drop_item)
            gEventHandler.bind("use_non_tool", self.on_nontool_use)
            gEventHandler.bind("interact_description", self.interact_description)
            gEventHandler.bind("interact_npc", self.interact_npc)
            gEventHandler.bind("interact_door", self.interact_door)

            # Crafting submenu
            gEventHandler.bind("simple_crafting_submenu_open", self.on_simple_crafting_submenu_open)
            gEventHandler.bind("simple_crafting_craft", self.on_simple_crafting_craft)

        def on_simple_crafting_menu(self):
            self.interaction_state = GameState.Game.ControlState.SIMPLE_CRAFTING
            self.simple_crafting_menu = menu.SimpleCraftingMenu(gRootConsole, gWidth, gHeight)
            self.simple_crafting_controls.emitter.bind(move_down=self.simple_crafting_menu.move_down)
            self.simple_crafting_controls.emitter.bind(move_up=self.simple_crafting_menu.move_up)
            self.simple_crafting_controls.emitter.bind(cancel=self.cancel_simple_crafting)
            self.simple_crafting_controls.emitter.bind(select=self.simple_crafting_menu.select)
            self.simple_crafting_menu.render_items()
            
        def cancel_simple_crafting(self):
            self.interaction_state = GameState.Game.ControlState.ROAM
            self.simple_crafting_menu = None # free up crafting menu space
            
        def on_simple_crafting_submenu_open(self, selected_item):
            self.interaction_state = GameState.Game.ControlState.SIMPLE_CRAFTING_SUBMENU
            self.simple_crafting_submenu = menu.SimpleCraftingSubMenu(selected_item, gRootConsole, self.inventory, gWidth, gHeight)
            self.simple_crafting_submenu_controls.emitter.bind(move_left=self.simple_crafting_submenu.move_left)
            self.simple_crafting_submenu_controls.emitter.bind(move_right=self.simple_crafting_submenu.move_right)
            self.simple_crafting_submenu_controls.emitter.bind(select=self.simple_crafting_submenu.select)
            self.simple_crafting_submenu.render()

        def on_simple_crafting_craft(self, craft, can_craft, recipie):
            if can_craft and craft:
                newitem = recipie.gives_item()
                for ritem in recipie.required_items:
                    for invitem in self.inventory.items:
                        if isinstance(invitem, ritem["item"]):
                            invitem.count -= ritem["count"]
                self.inventory.update_inventory()
                self.inventory.add_item(newitem)
                self.help_statusbar.set_text("Item " + newitem.name + " crafted")

                self.help_statusbar_timer = threading.Timer(2, self.help_statusbar.clear_text)
                self.help_statusbar_timer.start()
                # self.show_message("Message", ["Item " + newitem.name + " crafted"])
                # self.interaction_state = GameState.Game.ControlState.SIMPLE_CRAFTING_SUBMENU

            elif not can_craft and craft:
                self.show_message("Message", ["Not enough materials to craft this item"])
            elif not craft:
                self.on_simple_crafting_submenu_cancel()

        def on_simple_crafting_submenu_cancel(self):
            self.render()
            self.simple_crafting_menu.render_items()
            self.interaction_state = GameState.Game.ControlState.SIMPLE_CRAFTING

        def on_nontool_use(self, obj=None):
            print("using nontool:",obj)
            self.on_inventory_close()
            self.render()
            if obj:
                self.nontool_handler.obj = obj
                self._last_used = self.nontool_handler

            self.interaction_state = GameState.Game.ControlState.NONTOOL

        def on_nontool_use_direction(self, data):
            print("using in direction",data)
            error, msg = self.nontool_handler.use_object(data)
            if error:
                self.show_message("Message", [msg])
            else:
                self.interaction_state = GameState.Game.ControlState.ROAM

        def on_use_tool(self, tool=None):
            print("use_tool")
            if tool:
                self.on_inventory_close()
                self.render()
                self.tool_handler.current_tool = tool # set the tool which is being handeled
                self._last_used = self.tool_handler
                self.interaction_state = GameState.Game.ControlState.TOOL
            elif self._last_used is self.tool_handler and tool == None and self.tool_handler.current_tool:
                self.interaction_state = GameState.Game.ControlState.TOOL
            elif self._last_used is self.nontool_handler:
                self.on_nontool_use()

        def on_drop_item(self, it, index):
            print("dropping item", it)
            objects = self.lm.level.objects_at(self.player.x, self.player.y)
            if len(objects) == 1 and isinstance(objects[0], classes.Player):
                newtile = it.tile(self.player.x, self.player.y)
                gEventHandler.emit("add_object", newtile)

            elif len(objects) >= 2:
                found = False
                for o in objects:
                    if isinstance(o, it.tile) and isinstance(o, item.ItemTile):
                        #if this object is the same object as the item.tile and the object is of type ItemTile, increase item count
                        print("adding count to obj",o)
                        o.count += 1
                        found = True
                if not found:
                    self.show_message("Message", ["Cannot drop item, space occupied"])
                    self.inventory.items.insert(index, it)

        def on_item_pickup(self, obj):
            # item is at player coord
            if isinstance(obj, item.ItemTile):
                it = obj.item()
                it.count = obj.count
                self.inventory.add_item(it)
                gEventHandler.emit("object_destroy", obj)
                if it.count > 1:
                    self.show_message("Message", [it.name + "("+str(it.count)+")" +" picked up"])
                else:
                    self.show_message("Message", [it.name +" picked up"])
            elif isinstance(obj, farm.Plant):
                plant_items = []
                msg = "Picked up: "
                for i in obj.gives_items:
                    newitem = i["class"]()
                    newitem.count = i["count"]
                    msg += newitem.name + "("+str(newitem.count)+") "
                    plant_items.append(newitem)
                for i in plant_items:
                    self.inventory.add_item(i)
                gEventHandler.emit("object_destroy", obj)
                self.show_message("Message", [msg])


        def on_tool_use_direction(self, data):
            print("tool used in vector:", data)
            self.tool_handler.use_tool(data)
            self.interaction_state = GameState.Game.ControlState.ROAM

        def on_interaction(self):
            self.interaction_state = GameState.Game.ControlState.INTERACTION

        def on_interaction_direction(self, *args, **kwargs):
            if kwargs["obj"]:
                obj = kwargs["obj"]
                print("start conversation state with", obj)
                obj.interact()
            else:
                self.interaction_state = GameState.Game.ControlState.ROAM

        def interact_description(self, obj):
            self.show_message(obj.name, obj.text)

        def interact_npc(self, obj):
            print("interacting with npc:",obj.name)

        def interact_door(self, obj):
            print("interacting with door")
            self.interaction_state = GameState.Game.ControlState.ROAM

        def on_text_window_close(self):
            self.interaction_state = GameState.Game.ControlState.ROAM
            self.text_window = None # free up the window, basically deleting it

        def show_message(self, title, text_list):
            self.interaction_state = GameState.Game.ControlState.DIALOGUE
            self.text_window = menu.TextWindow(gRootConsole, gWidth, 10, title)
            self.text_window.set_pages(text_list)
            self.text_window.on_confirm()
            self.conversation_controls.emitter.bind(confirm=self.text_window.on_confirm)
            self.text_window.emitter.bind(close=self.on_text_window_close)


        def on_in_game_menu_open(self):
            def __save_game_item__():
                self.lm.save_level("save.json")
                self.show_message("Save progress", ["Game saved"])
            def __quit_item__():
                raise SystemExit()
            self.in_game_menu = menu.Menu(gRootConsole, gWidth, gHeight, [menu.MenuItem("Save Game", __save_game_item__),
                                                                          menu.MenuItem("Quit", __quit_item__)])
            self.menu_controls.emitter.bind(move_down=self.in_game_menu.move_down)
            self.menu_controls.emitter.bind(move_up=self.in_game_menu.move_up)
            self.menu_controls.emitter.bind(select=self.in_game_menu.select)
            self.menu_controls.emitter.bind(cancel=self.on_in_game_menu_close)
            self.interaction_state = GameState.Game.ControlState.MENU
            self.in_game_menu.render_items()

        def on_in_game_menu_close(self):
            self.interaction_state = GameState.Game.ControlState.ROAM
            self.in_game_menu = None

        def on_inventory_open(self):
            self.interaction_state = GameState.Game.ControlState.INVENTORY
            self.inventory.render_items()

        def on_inventory_close(self):
            self.interaction_state = GameState.Game.ControlState.ROAM

        def run(self):

            # readjust camera immediatelly after load, before render
            # NOTE: start_x isn't always properly adjusted. it is never 0 and it sometimes can lead to the player leaving the map
            if self.player.x >= gWidth/2:
                if abs(self.player.x - gWidth/2) <= self.lm.level.mapobj.w - gWidth:
                    self.r.start_x = int(abs(self.player.x - gWidth/2))
            if self.player.y >= gHeight/2:
                if abs(self.player.y - gHeight/2) <= self.lm.level.mapobj.h - gHeight:
                    self.r.start_y = int(abs(self.player.y - gHeight/2))

            if self.interaction_state == GameState.Game.ControlState.INTERACTION:
                self.interaction_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.ROAM:
                self.render()
                self.controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.DIALOGUE:
                self.conversation_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.MENU:
                self.menu_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.INVENTORY:
                self.inventory_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.TOOL:
                self.tool_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.NONTOOL:
                self.nontool_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.SIMPLE_CRAFTING:
                self.simple_crafting_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.SIMPLE_CRAFTING_SUBMENU:
                self.simple_crafting_submenu_controls.handlekeys()

            obj = self.lm.level.check_item(self.player.x, self.player.y) or self.lm.level.check_plant(self.player.x, self.player.y)
            if obj:
                self.help_statusbar.set_text("Press 'g' to pick up " + obj.name)

        def render(self):
            gRootConsole.clear()
            self.r.render(self.lm.mapobj, self.lm.level.objects)

        def update(self):
            if self.interaction_state == GameState.Game.ControlState.ROAM:
                for o in self.lm.level.objects:
                    if o.updatable:
                        o.update(self.lm.level)

        def draw(self):
            if self.interaction_state == GameState.Game.ControlState.ROAM:
                for o in self.lm.level.objects:
                    o.draw()

    class GameOver(state.State):
        def run(self):
            print("game over state")

# Basic transitions
class GameTransition:
    class IntroToGameTransition(state.Transition):
        def execute(self):
            pass

    class InteractionToGameTransition(state.Transition):
        def execute(self):
            pass

# Setup the console text
tcod.console_set_custom_font(
        "terminal10x16_gs_tc.png",
        tcod.FONT_LAYOUT_TCOD,
)

# Setup the console main window
gRootConsole = tcod.console_init_root(gWidth,gHeight,order="F")
# Setup main state machine
gFSM = state.StateMachine()
gFSM.states = {
    "intro" : GameState.Intro(gFSM),
    "game" : GameState.Game(gFSM),
    "gameover" : GameState.GameOver(gFSM)
}
gFSM.transitions = {
    "from_intro_to_game" : GameTransition.IntroToGameTransition(gFSM, "intro", "game"),
    "from_interaction_to_game" : GameTransition.InteractionToGameTransition(gFSM, "interaction", "game"),
}
gFSM.set_state("intro")
print(gFSM.cur_state)
sleeptime = 1 / 30
time_cumul = 0

while True:
    tcod.console_flush()
    gFSM.run()
    time.sleep(sleeptime)
    time_cumul += sleeptime
    if time_cumul > 1:
        time_cumul = 0
        if callable(getattr(gFSM.get_state(), "update", None)):
            gFSM.get_state().update()
    if callable(getattr(gFSM.get_state(), "draw", None)):
        gFSM.get_state().draw()
