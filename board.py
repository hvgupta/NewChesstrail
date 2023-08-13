from Piece import *

EMPTY_POS = 0
DEFAULTFEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"

class Board(): 
    """ 
    defines the board according to the fen string inputted. An empty fen string would initalise the board in the deafult case
    """
    def __init__(self, fen=""):
        self.Turn: Colour
        self.board: list[list[str]] = [[],[],[],[],[],[],[],[]]    
        self.PieceonBoard: dict[str,Piece] = {} # indexes the pieces based on their position
        self.white_pList: list[Piece] = [] # custering indexes the piece's id for white
        self.black_pList: list[Piece] = [] # custering indexes the piece's id for white
        remainingBlocks:list[str] = self.createBoard(fen if fen != "" else DEFAULTFEN)
        
        whiteKing:Piece = [piece for piece in self.white_pList if piece.get_name() == "K"][0]
        blackKing:Piece = [piece for piece in self.black_pList if piece.get_name() == "K"][0]
        for letter in remainingBlocks[0]:
            if remainingBlocks[0] == "-":
                break
            king:Piece
            if letter.upper():
                king = whiteKing
            else:
                king = blackKing

            king.castle = True
            if letter.lower() == "q":
                self.piece_at_that_pos(king.get_position() + np.array([0,-4])).castle = True
            else:
                self.piece_at_that_pos(king.get_position()+np.array([0,3])).castle = True
        
        if remainingBlocks[1] != "-":
            row:int = ord(remainingBlocks[1][0]) - ord("A")
            col:int = ord(remainingBlocks[1][1]) - ord("1")
            self.piece_at_that_pos(np.array([row,col])).K_from_en_passant = True
            
    def createBoard(self, fen:str):
        fenParts:list[str] = fen.split()
        row = 0
        index = 0
        col = 0
        letter:str
        for letter in fenParts[0]:
            if letter.isnumeric():
                self.board[row].extend(["--"]*int(letter))
                col += int(letter)
            elif letter.isalpha():
                colour = "b" if letter.islower() else "w"
                piece = letter.lower() if letter in ["p","P"] else letter.upper()
                self.board[row].append(f"{colour}{piece}")
                pieceAdded = Piece(getattr(PieceType,piece),np.array((row,col)),getattr(Colour,colour),index)
                if colour == "b":
                    self.black_pList.append(pieceAdded)
                else:
                    self.white_pList.append(pieceAdded)
                self.PieceonBoard[str(pieceAdded.get_position().tolist())] = pieceAdded
                index +=1
                col +=1
                
            elif letter == "/":
                row +=1
                col = 0
            else: break
        self.Turn = Colour.w if fenParts[1] == "w" else Colour.b
        
        return fenParts[2:]
    
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
        newwhite_plist:list[Piece] = []
        newblack_plist:list[Piece] = []
        for piece in self.white_pList:
            newwhite_plist.append(piece.copy())
        for piece in self.black_pList:
            newblack_plist.append(piece.copy())
        newPieceonBoard: dict[str, Piece] = {}
        for piece in newwhite_plist+newblack_plist:
            if piece.isDestroyed():
                continue
            newPieceonBoard[str(piece.get_position().tolist())] = piece
        objBoard = Board()
        objBoard.board = newBoard
        objBoard.white_pList = newwhite_plist
        objBoard.black_pList = newblack_plist
        objBoard.PieceonBoard = newPieceonBoard
        objBoard.Turn = self.Turn
        return objBoard