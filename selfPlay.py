from AI import *
from ResNet import *
from MCTS import *
from AlphaZero import *

c_board = Board()
White_pList: list[Piece]
Black_pList: list[Piece]
c_board.initialise()
running = True
current_turn = Colour.w.value

whiteKing, blackKing = getKing(c_board)
game : Game = Game(whiteKing, blackKing,Colour.w.value,c_board)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model: ResNet = ResNet(5,1161, device)
optimizer = torch.optim.Adam(model.parameters(), lr= 0.001)
args = {
    'C': 2,
    'num_searches': 600,
    'num_iterations': 8,
    'num_selfPlay_iterations': 500,
    'num_parallel_games': 500,
    'num_epochs': 4,
    'batch_size': 128,
    'temperature': 1.25,
    'dirichlet_epsilon': 0.25,
    'dirichlet_alpha': 0.3
}

alphaZero = AlphaZeroParallel(model, optimizer, game, args)
alphaZero.learn()

print("done")