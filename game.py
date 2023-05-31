from Piece import *
from board import *
from Helper_func import *
import copy

class Game():
    def __init__(self, white_pList:list[Piece], black_pList:list[Piece], WhiteK:Piece, BlackK:Piece, turn: int, board: Board) -> None:
        self.white_pList = copy.deepcopy(white_pList)
        self.black_pList = copy.deepcopy(black_pList)
        self.WhiteK = WhiteK
        self.BlackK = BlackK
        self.board = copy.deepcopy(board)
        self.turn = turn
        self.validMovesNum = 0
        self.allowedActions:tuple = self.get_allowedMoves()

    def get_encodedState(self) -> np.ndarray:
        encoded_array = np.zeros((3,8,8)) # the 3 8x8 arrays which contain the information about the point of the piece and their colour denoted by the sign 
        for piece in self.white_pList:
            if piece.isDestroyed(): continue
            encoded_array[0, tuple(piece.get_position())] = piece.get_info()["points"]
        for piece in self.black_pList:
            if piece.isDestroyed(): continue
            encoded_array[1, tuple(piece.get_position())] = piece.get_info()["points"]
        
        encoded_array[2] = (encoded_array[0] == 0) & (encoded_array[1] == 0)
        
        return encoded_array
    
    def move_piece(self, actionNum: int)->tuple:
        piece:Piece = self.allowedActions[0][(actionNum//10)-1]
        action = self.allowedActions[1][(actionNum//10)-1][actionNum%10]
        newWhite_pList = copy.deepcopy(self.white_pList)
        newBlack_pList = copy.deepcopy(self.black_pList)
        newPiece = piece_at_that_pos(piece.get_position(),newWhite_pList,newBlack_pList)
        self.board.move_piece(newPiece,action)
        return newWhite_pList,newBlack_pList
    
    def get_allowedMoves(self)->list:
        # initialise the Piece_can_move and moves (based on the each turn)
        self.validMovesNum = 0
        Piece_can_move: list[Piece] = []
        moves = []
        colour_choosen_list = self.white_pList if self.turn == Colour.w.value else self.black_pList
        for piece in colour_choosen_list:
            if piece.isDestroyed():
                continue
            all_moves,all_attack = movesReturn(piece)   
            legal_moves = returnValidPos(all_moves,self.white_pList,self.black_pList,None,piece,[self.WhiteK,self.BlackK],all_attack if piece.get_name() == "p" else None,True)
            if legal_moves.size > 0:
                Piece_can_move.append(piece)
                moves.append(legal_moves)
                self.validMovesNum += len
        return Piece_can_move, moves   
        
    def get_validMoves(self)-> tuple:
        moves:list = self.allowedActions[1]
        indices = []
        firstDnums = list(range(0, len(moves)))
        for n in firstDnums:
            indices += list(range(n*10,n*10+len(moves[n-1])))   
        
        return indices  
    
    def valueAndterminated(self):
        isChecked = check(self.WhiteK, self.BlackK, self.white_pList, self.black_pList)
        
        if isChecked == EMPTY_POS:
            return 0,False
        
        if isChecked.get_colour() == self.turn:
            if check_mate(isChecked,self.white_pList,self.black_pList):
                return -100, True
            return -1, False
        else:
            if check_mate(isChecked, self.white_pList, self.black_pList):
                return 100, True
            return 1, False
            