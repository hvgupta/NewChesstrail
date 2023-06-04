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
        self.allowedPiece,self.allowedActions = self.get_allowedMoves()

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
        '''
        1234
        id: 12
        moveType: 3
        multiple: 4
        get id by //100, then iterate through the piece list to get id
        then %100 to get moveType and multiple
            //10 to get moveType 
            %10 get multiple
        '''
        id: int = actionNum//100
        moveAndmultiple: int = actionNum%100
        selected_piece: Piece = None
        for piece in self.black_pList + self.white_pList:
            if piece.id == id:
                selected_piece = piece
                break
        move: np.ndarray
        if selected_piece.get_name() in ["p", "N", "K"]:
            moves : np.ndarray = np.concatenate((PieceType.p.value["moves"], PieceType.p.value["attack"])) if selected_piece.get_name() == "p" else selected_piece.get_info()["moves"]
            move = moves[moveAndmultiple%10].reshape((2))
        else:
            moves: np.ndarray[np.ndarray] = selected_piece.get_info()["moves"]
            moves = np.expand_dims(moves, axis=1)
            multiple : np.ndarray = np.arange(1,8).reshape((7,1))
            moves = moves*multiple
            move = moves[moveAndmultiple//10, moveAndmultiple%10].reshape((2))
        newWhite_pList = copy.deepcopy(self.white_pList)
        newBlack_pList = copy.deepcopy(self.black_pList)
        newPiece = piece_at_that_pos(selected_piece.get_position(),newWhite_pList,newBlack_pList)
        self.board.move_piece(newPiece,move)
        return newWhite_pList,newBlack_pList
    
    def get_allowedMoves(self)->tuple[list[Piece], list[np.ndarray]]:
        '''
        gives the piece and the moves which can be moved in the current board state
        '''
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
        '''
        how to define action?
        id * 100 {could be between 0:31}
        moveType: {U: 0, UR: 1, R: 2, DR: 3, D: 4, DL: 5, L: 6, UL: 7}*10
        multiple {1:8}*1
        therefore a 4 digit number
        '''
        indices = []
        for index in range(len(self.validMovesNum)):
            piece = self.allowedPiece[index]
            action = piece.id*100
            mov:np.ndarray = self.allowedActions[index] - piece.get_position()
            data:list
            basic_moves: np.ndarray
            Axis: int
            if not piece.get_name() in ["p", "N", "K"]:
                basic_moves = np.expand_dims(piece.get_info()["moves"],axis=1)
                multiple = np.arange(1,8).reshape((7,1))
                basic_moves = basic_moves*multiple
                mov = np.reshape(mov, (mov.shape[0], 1,1, mov.shape[1]))
                Axis = 3
            else:
                basic_moves = np.concatenate((PieceType.p.value["moves"], PieceType.p.value["attack"])) if piece.get_name() == "p" else piece.get_info()["moves"]
                basic_moves = np.expand_dims(basic_moves,axis=1)
                Axis = 2
            
            truth = (basic_moves == mov).all(axis= Axis)
            data = np.where(truth)
            if piece.get_name() in ["p", "N"]:
                data:list[np.ndarray] = [np.zeros(data[0].size,dtype=int), data[1]]
            actions = data[1]*10 + data[2] + action
            indices += actions.tolist()  
        
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
            