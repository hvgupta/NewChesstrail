from game import *
from Node import *

class SPG():
    def __init__(self) -> None:
        initBoard = Board()
        White_pList, Black_pList, PieceonBoard = initBoard.initialise(initBoard.board)
        WhiteK, BlackK = getKing(White_pList, Black_pList)
        self.game = Game(White_pList, Black_pList, WhiteK, BlackK, Colour.w.value, initBoard)
        self.memory: list[Game,int,int] = []
        self.root:Node = None
        self.node:Node = None