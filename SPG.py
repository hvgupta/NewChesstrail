from game import *
from Node import *

class SPG():
    def __init__(self) -> None:
        initBoard = Board()
        initBoard.initialise()
        WhiteK, BlackK = getKing(initBoard)
        self.game = Game(WhiteK, BlackK, Colour.w.value, initBoard)
        self.memory: list[Game,int,int] = []
        self.root:Node = None
        self.node:Node = None