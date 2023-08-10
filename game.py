from Piece import *
from board import *
from Helper_func import *
from click_handle import *

BASE = 100

class Game():
    def __init__(self, WhiteK:Piece, BlackK:Piece, turn: int, board: Board) -> None:
        self.WhiteK = WhiteK
        self.BlackK = BlackK
        self.board = board
        self.turn = turn
        self.validMovesNum = 0
        self.allowedPiece,self.allowedActions = self.get_allowedMoves()

    def get_encodedState(self) -> np.ndarray:
        encoded_array = np.zeros((3,9,9)) # the 3 8x8 arrays which contain the information about the point of the piece and their colour denoted by the sign 
        for piece in self.board.white_pList:
            if piece.isDestroyed(): continue
            piecePos = piece.get_position()
            encoded_array[0, piecePos[0],piecePos[1]] = piece.get_info()["points"]
        for piece in self.board.black_pList:
            if piece.isDestroyed(): continue
            piecePos = piece.get_position()
            encoded_array[1, piecePos[0],piecePos[1]] = piece.get_info()["points"]
        
        encoded_array[2] = (encoded_array[0] == 0) & (encoded_array[1] == 0)
        encoded_array = np.float32(encoded_array)
        return encoded_array
    
    def move_piece(self, actionNum: int)->tuple:
        '''
        1234
        id: 12
        moveType: 3
        multiple: 4
        get id by //BASE, then iterate through the piece list to get id
        then %BASE to get moveType and multiple
            //10 to get moveType 
            %10 get multiple
        '''
        id: int = actionNum//BASE
        moveAndmultiple: int = actionNum%BASE
        selected_piece: Piece = None
        for piece in self.board.black_pList + self.board.white_pList:
            if piece.id == id:
                selected_piece = piece
                break
        index:int = self.allowedPiece.index(piece)
        legalMoves: np.ndarray = self.allowedActions[index]
        move: np.ndarray
        if selected_piece.get_name() in ["N", "K"]:
            if selected_piece.get_name() == "K":
                moves: np.ndarray = np.concatenate((PieceType.K.value["moves"], PieceType.K.value["castle"]))
            else:
                moves: np.ndarray = selected_piece.get_info()["moves"]
            move = moves[moveAndmultiple%10].reshape((2))
        elif selected_piece.get_name() == "p":
            if moveAndmultiple%10 > 3:
                move = np.array([1,0])
            else:
                moves: np.ndarray = np.concatenate((PieceType.p.value["moves"], PieceType.p.value["attack"]))
                move = moves[moveAndmultiple%10].reshape((2))
        else:
            moves: np.ndarray[np.ndarray] = selected_piece.get_info()["moves"]
            moves = np.expand_dims(moves, axis=1)
            multiple : np.ndarray = np.arange(1,8).reshape((7,1))
            moves = moves*multiple
            move = moves[moveAndmultiple//10, moveAndmultiple%10].reshape((2))
            
        move = move*piece.get_colour() + selected_piece.get_position()
        newBoard = self.board.copy()
        newPiece = newBoard.piece_at_that_pos(selected_piece.get_position())
        second_click(newBoard,legalMoves,newPiece, tuple(move),[tuple(newPiece.get_position()), tuple(move)])
        newWKing, newBKing = getKing(newBoard)
        if newPiece.get_name() == "p" and moveAndmultiple%10 > 3:
            promotionArray: list[PieceType] = [PieceType.Q, PieceType.N, PieceType.R, PieceType.B]
            newPiece.change_type(promotionArray[(moveAndmultiple%10)-4])
        return newWKing, newBKing, newBoard
    
    def get_allowedMoves(self)->tuple[list[Piece], list[np.ndarray]]:
        '''
        gives the piece and the moves which can be moved in the current board state
        '''
        # initialise the Piece_can_move and moves (based on the each turn)
        self.validMovesNum = 0
        Piece_can_move: list[Piece] = []
        moves = []
        colour_choosen_list = self.board.white_pList if self.turn == Colour.w.value else self.board.black_pList
        for piece in colour_choosen_list:
            if piece.isDestroyed():
                continue
            all_moves,all_attack = movesReturn(piece)
            if piece.get_name() == "p":
                all_moves = all_moves.reshape((all_moves.shape[1], all_moves.shape[0],2))   
            legal_moves = returnValidPos(all_moves,self.board,None,piece,[self.WhiteK,self.BlackK],all_attack if piece.get_name() == "p" else None,True)
            if legal_moves.size > 0:
                Piece_can_move.append(piece)
                moves.append(legal_moves)
                self.validMovesNum += len(legal_moves)
        return Piece_can_move, moves   
        
    def get_validMoves(self)-> tuple:
        '''
        how to define action?
        id * BASE {could be between 0:31}
        moveType: {U: 0, UR: 1, R: 2, DR: 3, D: 4, DL: 5, L: 6, UL: 7}*10
        multiple {1:8}*1
        therefore a 4 digit number
        there index is the actions and the value in the index is the state (1) being allowed, and 0 being not allowed
        '''
        actionTruth: np.ndarray = np.zeros(3288)
        values:list = []
        for index in range(len(self.allowedPiece)):
            piece = self.allowedPiece[index]
            action = piece.id*BASE
            mov:np.ndarray = (self.allowedActions[index] - piece.get_position())*piece.get_colour() # get the action type
            data:list
            basic_moves: np.ndarray
            Axis: int
            # since I have already found the valid mvoes in terms of position on board, how I have to convert it 
            if not piece.get_name() in ["p", "N", "K"]: 
                basic_moves = np.expand_dims(piece.get_info()["moves"],axis=1) # get the base moves
                multiple = np.arange(1,8).reshape((7,1)) # since these pieces can move the at most 7 times the base move (ie 7*[1,0])
                
                basic_moves = basic_moves*multiple
                mov = np.reshape(mov, (mov.shape[0], 1,1, mov.shape[1]))
                Axis = 3 # this is just a variable to at which the coordinate comparasion will be done
            else:
                if piece.get_name() == "p":
                    basic_moves: np.ndarray = np.concatenate((PieceType.p.value["moves"], PieceType.p.value["attack"])) # since horse cannot move & times its base move thats why it is here
                elif piece.get_name() == "K":
                    basic_moves: np.ndarray = np.concatenate((PieceType.K.value["moves"], PieceType.K.value["castle"]))
                else:
                    basic_moves: np.ndarray = piece.get_info()["moves"]
                basic_moves = np.expand_dims(basic_moves,axis=1)
                Axis = 2 # since all of these units are not being check for multiples of the move thats why it is 1 dimension lower than the previous one
            
            truth = (basic_moves == mov).all(axis= Axis)
            data:list[np.ndarray] = np.where(truth)
            if piece.get_name() in ["N", "K"]:
                data = [np.zeros(data[0].size,dtype=int), data[0]]
            elif piece.get_name() == "p":
                index: int  = 0 if piece.get_colour() == Colour.w.value else 1
                
                if (piece.get_position() + np.array([1,0])*piece.get_colour() == np.array([[0,0],[7,0]])[index]).all():
                    data = [np.zeros(data[0].size + 4, dtype=int), np.concatenate((data[1], np.array([4,5,6,7])))] # over here I defined the case which in promotions will be done
                else:
                    data = [np.zeros(data[0].size,dtype=int), data[1]]
            
            actions = data[Axis-2]*10 + data[Axis-1] + action
            actionTruth[actions] = 1
            values += actions.tolist()
        
        return actionTruth, values
    
    def valueAndterminated(self):
        isChecked = check(self.WhiteK, self.BlackK, self.board)
        
        if isChecked == EMPTY_POS:
            return 0,False
        
        if check_mate(isChecked, self.board):
            return 100, True
        return 1, False
            