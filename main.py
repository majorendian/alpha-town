
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

gRootConsole = None # just so that we can reference it inside the classes
# Basic states of the game
class GameState:
    class Intro(state.State):
        def run(self):
            gRootConsole.print(x=0,y=0,string="Intro state")
            for event in tcod.event.wait():
                if event.type == "QUIT":
                    raise SystemExit()
                elif event.type == "KEYDOWN":
                    if event.scancode == tcod.event.SCANCODE_SPACE:
                        self.fsm.transition("from_intro_to_game")
                

    class Game(state.State):

        class ControlState(Enum):
            ROAM = auto()
            INTERACTION = auto()
            DIALOGUE = auto()
            INVENTORY = auto()
            MENU = auto()

        def __init__(self, fsm):
            super().__init__(fsm)
            self.r = render.Renderer(gRootConsole, gWidth, gHeight)
            self.lm = level.LevelManager()
            try:
                self.lm.load_save("save.json")
                self.player = self.lm.player
            except IOError:
                self.lm.load_level("basic_starter_level.json")
                self.player = self.lm.player
                self.lm.level.objects.append(self.player)
            self.interaction_state = GameState.Game.ControlState.ROAM

            self.controls = control.MainControls(self.player, self.r, self.lm.level)
            self.interaction_controls = control.InteractionControls(self.player, self.lm.level)
            self.controls.emitter.bind(interaction=self.on_interaction)
            self.controls.emitter.bind(inventory_open=self.on_inventory_open)
            self.controls.emitter.bind(in_game_menu=self.on_in_game_menu_open)
            
            self.interaction_controls.emitter.bind(interaction_finished=self.on_interaction_finished)
            self.conversation_controls = control.ConversationControls()

            #we need a handle for the text window to be persitent or else the function will not be called so we need this textwindow variable
            self.text_window = None

            #inventory
            self.inventory_controls = control.InventoryControls()
            self.inventory = menu.Inventory(gRootConsole, gWidth, gHeight)
            self.inventory_controls.emitter.bind(move_down=self.inventory.move_down)
            self.inventory_controls.emitter.bind(move_up=self.inventory.move_up)
            self.inventory_controls.emitter.bind(select=self.inventory.select)
            self.inventory_controls.emitter.bind(cancel=self.on_inventory_close)

            #in game menu
            self.menu_controls = control.MenuControls()
            self.in_game_menu = None # needs to be none just like for the text window

        def on_interaction(self):
            self.interaction_state = GameState.Game.ControlState.INTERACTION

        def on_interaction_finished(self, *args, **kwargs):
            if kwargs["obj"]:
                obj = kwargs["obj"]
                print("start conversation state with", obj)
                self.interaction_state = GameState.Game.ControlState.DIALOGUE
                self.text_window = menu.TextWindow(gRootConsole, gWidth, 10, obj.name)
                self.text_window.set_pages(obj.text)
                self.text_window.on_confirm()
                self.conversation_controls.emitter.bind(confirm=self.text_window.on_confirm)
                self.text_window.emitter.bind(close=self.on_text_window_close)
            else:
                self.interaction_state = GameState.Game.ControlState.ROAM

        def on_text_window_close(self):
            self.interaction_state = GameState.Game.ControlState.ROAM
            self.text_window = None # free up the window, basically deleting it

        def on_in_game_menu_open(self):
            def __save_game_item__():
                self.lm.save_level("save.json")
                self.interaction_state = GameState.Game.ControlState.DIALOGUE
                self.text_window = menu.TextWindow(gRootConsole, gWidth, 10, "Save progress")
                self.text_window.set_pages(["Game saved"])
                self.text_window.on_confirm()
                self.conversation_controls.emitter.bind(confirm=self.text_window.on_confirm)
                self.text_window.emitter.bind(close=self.on_text_window_close)
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
            if self.player.x >= gWidth/2:
                if abs(self.player.x - gWidth/2) <= self.lm.level.mapobj.w - gWidth:
                    self.r.start_x = int(abs(self.player.x - gWidth/2))
            if self.player.y >= gHeight/2:
                if abs(self.player.y - gHeight/2) <= self.lm.level.mapobj.h - gHeight:
                    self.r.start_y = int(abs(self.player.y - gHeight/2))

            if self.interaction_state == GameState.Game.ControlState.INTERACTION:
                self.interaction_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.ROAM:
                gRootConsole.clear()
                self.r.render(self.lm.mapobj, self.lm.level.objects)
                self.controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.DIALOGUE:
                self.conversation_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.MENU:
                self.menu_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.INVENTORY:
                self.inventory_controls.handlekeys()


        def update(self):
            if self.interaction_state == GameState.Game.ControlState.ROAM:
                for o in self.lm.level.objects:
                    o.update(self.lm.level)

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
        "terminal16x16_gs_ro.png",
        tcod.FONT_LAYOUT_ASCII_INROW,
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
