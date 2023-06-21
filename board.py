from Piece import *

EMPTY_POS = 0

class Board(): 
    """ 
    defines the board according to the fen string inputted. An empty fen string would initalise the board in the deafult case
    """
    def __init__(self, fen: str= ""):
        
        self.board = [[],[],[],[],[],[],[],[]]
        if fen == "":
            self.board = [
                ["bR","bN","bB","bQ","bK","bB","bN","bR"],
                ["bp","bp","bp","bp","bp","bp","bp","bp"],
                ["--","--","--","--","--","--","--","--"],
                ["--","--","--","--","--","--","--","--"],
                ["--","--","--","--","--","--","--","--"],
                ["--","--","--","--","--","--","--","--"],
                ["wp","wp","wp","wp","wp","wp","wp","wp"],
                ["wR","wN","wB","wQ","wK","wB","wN","wR"]
                ]
            self.Turn = Colour.w

        else:
            row = 0
            index = 0
            for letter in fen:
                if letter.isnumeric():
                    self.board[row].extend(["--"]*int(letter))
                elif letter.isalpha():
                    self.board[row].append("{colour}{piece}".format(piece = letter.lower() if letter in ["p","P"] else letter.upper(), colour = "b" if letter.islower() else "w"))
                elif letter == "/":
                    row+=1
                else: break
                index +=1
            turn = fen[index+1]
            self.Turn = Colour.w if turn == "w" else Colour.b
            
        self.PieceonBoard: dict[str,Piece] = {}
        self.white_pList: list[Piece] = []
        self.black_pList: list[Piece] = []
    
    def move_piece(self,piece: Piece,to: np.ndarray):
        if piece == "--":
            self.board[to[0]][to[1]] = "--"
            return
        old_pos = piece.get_position()
        piece.change_pos(to)
        old = self.board[old_pos[0]][old_pos[1]]
        self.board[to[0]][to[1]] = old
        self.board[old_pos[0]][old_pos[1]] = "--"
        del self.PieceonBoard[str(old_pos.tolist())]
        self.PieceonBoard[str(to.tolist())] = piece
    
    # I thought a list of objects would be cool, so here it is 
    def initialise(self): 
        self.black_pList = []
        self.white_pList = []
        Id: int = 0
        for row in range(8):
            eachLin: list[Piece] = []
            for col in range(8):
                if self.board[row][col] == "--":
                    eachLin.append(EMPTY_POS)
                    continue
                colour:Colour = getattr(Colour,self.board[row][col][0])
                piece_type = getattr(PieceType,self.board[row][col][1])
                Piece_created = Piece(piece_type,np.array((row,col)),colour,Id)
                eachLin.append(Piece_created)
                if colour.value == Colour.w.value:
                    self.white_pList.append(Piece_created)
                else:
                    self.black_pList.append(Piece_created)
                
                Id+=1
                self.PieceonBoard[str([row,col])] = Piece_created
                    
        # return self.white_pList, self.black_pList, self.PieceonBoard

    def piece_at_that_pos(self, coord:np.ndarray) -> Piece:
        piece = EMPTY_POS
        if str(coord.tolist()) in self.PieceonBoard.keys():
            return self.PieceonBoard[str(coord.tolist())]
        return piece
    
    @staticmethod
    def get_encodedState(White_pList: list[Piece], Black_pList: list[Piece]) -> np.ndarray:
        encoded_array = np.zeros((3,8,8)) # the 3 8x8 arrays which contain the information about the point of the piece and their colour denoted by the sign 
        for piece in White_pList:
            if piece.isDestroyed(): continue
            encoded_array[0, tuple(piece.get_position())] = piece.get_info()["points"]
        for piece in Black_pList:
            if piece.isDestroyed(): continue
            encoded_array[1, tuple(piece.get_position())] = piece.get_info()["points"]
        
        encoded_array[2] = (encoded_array[0] == 0) & (encoded_array[1] == 0)
        
        return encoded_array
    
    def copy(self):
        newBoard : list = []
        for chrac in self.board:
            newBoard.append(chrac.copy())
        objBoard = Board()
        objBoard.board = newBoard
        return objBoard