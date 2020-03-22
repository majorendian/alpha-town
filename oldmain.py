
import tcod
import time
import tcod.event
import classes
from random import randrange

gPlayer = classes.Player()

# Setup the console text
tcod.console_set_custom_font(
        "terminal16x16_gs_ro.png",
        tcod.FONT_LAYOUT_ASCII_INROW,
)

# Setup the console main window and flush it
gWidth = 80
gHeight = 40
gRootConsole = tcod.console_init_root(gWidth,gHeight,order="F")
stars = []
for y in range(0,gHeight):
    l = []
    if y % (randrange(10)+3) == 0:
        for x in range(1,gWidth):
            if x % (randrange(30)+1) == 0:
                print(x)
                l.append(classes.MovingBackroundStar(x,y))
        stars.append(l)

def main(root_console):
    root_console.clear()
    for l in stars:
        for star in l:
            star.update()
            root_console.print(x=star.x, y=star.y, string=star.symbol)
    root_console.print(x=gPlayer.x,y=gPlayer.y, string=gPlayer.symbol, fg=(255,0,0))

#Roughly equals a framerate of 30. sleep x amount of time every refresh (might need something more complex)
timetosleep = 1 / 30
while True:
    tcod.console_flush()
    for event in tcod.event.get():
        if event.type == "QUIT":
            raise SystemExit()
        if event.type == "KEYDOWN":
            if event.scancode == tcod.event.SCANCODE_S:
                gPlayer.y += 1
            elif event.scancode == tcod.event.SCANCODE_W:
                gPlayer.y -= 1
            elif event.scancode == tcod.event.SCANCODE_D:
                gPlayer.x += 1
            elif event.scancode == tcod.event.SCANCODE_A:
                gPlayer.x -= 1
    main(gRootConsole)
    gRootConsole.print(x=20,y=20,string="Testing string @")
    time.sleep(timetosleep)

