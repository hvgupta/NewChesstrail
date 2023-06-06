from click_handle import *
from AI import *
from ResNet import *
from MCTS import *
from AlphaZero import *

c_board = Board()
White_pList: list[Piece]
Black_pList: list[Piece]
White_pList, Black_pList = c_board.initialise(c_board.board)
running = True
current_turn = Colour.w.value

whiteKing = White_pList[12]
blackKing = Black_pList[4]
game : Game = Game(White_pList, Black_pList,whiteKing, blackKing,Colour.w.value,c_board)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model: ResNet = ResNet(game,5,1161, device)
optimizer = torch.optim.Adam(model.parameters(), lr= 0.001)
args = {
    'C': 2,
    'num_searches': 600,
    'num_iterations': 8,
    'num_selfPlay_iterations': 500,
    'num_parallel_games': 100,
    'num_epochs': 4,
    'batch_size': 128,
    'temperature': 1.25,
    'dirichlet_epsilon': 0.25,
    'dirichlet_alpha': 0.3
}

alphaZero = AlphaZero(model, optimizer, game, args)
alphaZero.learn()

print("done")