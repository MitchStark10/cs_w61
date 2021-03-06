from tkinter import *
import random

from attack.water_attack import WaterAttack
from cell import *
from path import *
from character.invader import *
from character.wave import Wave
from resource_manager import ResourceManager
from bank import Bank


CANVAS_DIM = 600
SQUARE_SIZE = 30
NUM_CELLS_PER_DIM = int(CANVAS_DIM / SQUARE_SIZE)

TIME_BETWEEN_WAVES = 60    # seconds
INIT_GOLD_AMOUNT = 100

class App:
    def __init__(self, root):
        self.resource_manager = ResourceManager(Bank(self))
        self.wave_count = 1
        self._root = root
        self._gameRunning = False
        self._currWaveNumber = 0
        self._currWave = None

        self._canv = Canvas(root, width=CANVAS_DIM, height=CANVAS_DIM)
        

        self._bottom_panel = Frame(root)
        self._bottom_panel.pack()
        self._canv.pack()

        self._btStartGame = Button(self._bottom_panel, text="Start Game",
                                   command=self.startGame)
        self._btStartGame.pack(side=LEFT)

        Label(self._bottom_panel, text="Gold: ").pack(side=LEFT)
        self._goldAmtVar = IntVar()
        self._goldAmtVar.set(self.resource_manager.getMoney())
        self._goldLbl = Label(self._bottom_panel, textvariable=self._goldAmtVar)
        self._goldLbl.pack(side=LEFT)

        self._btNextWave = Button(self._bottom_panel, text="Start Wave",
                                  command=self.startNextWave)
        self._btNextWave.pack(side=LEFT)

        Label(self._bottom_panel, text="Time till next wave starts: ").pack(side=LEFT)
        self._timeLeftTilWave = IntVar()
        self._timeLeftTilWave.set(TIME_BETWEEN_WAVES)
        self._timeLeftLbl = Label(self._bottom_panel, textvariable=self._timeLeftTilWave)
        self._timeLeftLbl.pack(side=LEFT)

        # A 2-d grid of locations
        self._grid = []
        for row in range(NUM_CELLS_PER_DIM):
            rowlist = []
            for col in range(NUM_CELLS_PER_DIM):
                cell = Cell(self._canv, col, row, SQUARE_SIZE, self.resource_manager)
                rowlist.append(cell)
            self._grid.append(rowlist)

        # Follow the mouse everywhere and highlight the cell it is in.
        # self._canv.bind("<Motion>", self.highlight_cell)

        # Read path info from a file and highlight the path on the screen.
        self.readPathInfo()
        self.wave = Wave(self.resource_manager, self._canv, self._path)


    def updateGoldAmount(self, new_gold_amount):
        self._goldAmtVar.set(new_gold_amount)

    def sendWave(self):
        # Create invader wave and let them move
        self.resource_manager.removeAllInvaders()
        self.wave.readAndSendNextWave()
        self._timeLeftTilWave.set(TIME_BETWEEN_WAVES)


    def highlight_cell(self, event):
        '''Highlight the cell the mouse is over.'''
        if not self._gameRunning:
            return
        x, y = event.x, event.y
        for row in range(NUM_CELLS_PER_DIM):
            for col in range(NUM_CELLS_PER_DIM):
                if (x, y) in self._grid[col][row]:
                    self._grid[col][row].render()


    def startGame(self):
        if self._gameRunning:
            return

        self._gameRunning = True
        self.updateTimer()

    def startNextWave(self):
        '''Start the next wave now, instead of waiting for the timer to go down to 0.'''
        if not self._gameRunning:
            return
        print("Start next wave now...")
        self._timeLeftTilWave.set(TIME_BETWEEN_WAVES)
        self.sendWave()

    def updateTimer(self):
        timeLeft = self._timeLeftTilWave.get()
        if timeLeft == 0:
            self.sendWave()
            self._canv.after(1000, self.updateTimer)
            return

        timeLeft -= 1
        self._timeLeftTilWave.set(timeLeft)
        self._canv.after(1000, self.updateTimer)
        self.wave.sendInvader()

    def readPathInfo(self):
        '''Read path information from a file and create a path object for it.'''
        self._path = Path(NUM_CELLS_PER_DIM)
        with open('path.txt') as pf:
            for elem in pf:
                elem = elem.strip()
                x, y = map(int, elem.split(','))   # map(int) to make ints.
                self._path.add_cell(self._grid[y][x])
                self._grid[y][x].set_type('path')



root = Tk()
root.title("Calvin Tower Defense")
App(root)
root.wm_attributes('-topmost', 1)
root.mainloop()

