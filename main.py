
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
            CONVERSATION = auto()
            INVENTORY = auto()

        def __init__(self, fsm):
            super().__init__(fsm)
            self.r = render.Renderer(gRootConsole, gWidth, gHeight)
            self.player = classes.Player(0,0)
            self.lm = level.LevelManager()
            self.lm.load_level("somelevel.json")
            self.lm.level.objects.append(self.player)
            self.interaction_state = GameState.Game.ControlState.ROAM
            self.controls = control.MainControls(self.player, self.r, self.lm.level)
            self.interaction_controls = control.InteractionControls(self.player, self.lm.level)

            self.controls.emitter.bind(interaction=self.on_interaction)
            self.interaction_controls.emitter.bind(interaction_finished=self.on_interaction_finished)

        def on_interaction(self):
            self.interaction_state = GameState.Game.ControlState.INTERACTION

        def on_interaction_finished(self):
            self.interaction_state = GameState.Game.ControlState.ROAM

        def run(self):
            gRootConsole.clear()
            self.r.render(self.lm.mapobj, self.lm.level.objects)
            if self.interaction_state == GameState.Game.ControlState.INTERACTION:
                self.interaction_controls.handlekeys()
            elif self.interaction_state == GameState.Game.ControlState.ROAM:
                self.controls.handlekeys()

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
