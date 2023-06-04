from click_handle import *
from AI import *
from ResNet import *
from MCTS import *
from AlphaZero import *

screen = p.display.set_mode((WIDTH,HEIGHT))
screen.fill(p.Color("white"))
c_board = Board()
White_pList: list[Piece]
Black_pList: list[Piece]
White_pList, Black_pList = c_board.initialise(c_board.board)
loadImages()
running = True
current_turn = Colour.w.value
sqSelected = ()
player_click = []
def reset(sqSelected,player_click): # resets the sqSelected and player_click
    sqSelected = ()
    player_click = []
    return sqSelected,player_click

whiteKing = White_pList[12]
blackKing = Black_pList[4]
HUMAN = Colour.w.value
AI = Colour.b.value
selected_p = Piece
w_checkMated = False
b_checkMated = False
game : Game = Game(White_pList, Black_pList,whiteKing, blackKing,Colour.w.value,c_board)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model: ResNet = ResNet(game,20,200, device)