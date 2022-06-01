from Piece import *

class Board(): 
    """ 
    defines the board, thought of using FEN string, but didnt find many resources, so it is just a simple array with the first word
    signifying the colour of the piece b= black and w= white, and the next word signfies the piece type so pawn, king etc, same as the Enum file
    """
    def __init__(self):
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
    
    
    @staticmethod    # I thought a list of objects would be cool, so here it is 
    def initialise(board): 
        blackList = []
        whiteList = []
        for row in range(8):
            for col in range(8):
                if board[row][col] == "--":
                    break
                colour = getattr(Colour,board[row][col][0])
                piece_type = getattr(type,board[row][col][1])
                
                if colour.value == Colour.w.value:
                    whiteList.append(Piece(piece_type,np.array((row,col)),colour))
                else:
                    blackList.append(Piece(piece_type,np.array((row,col)),colour))
                    
        return whiteList, blackList
                
                            
                            
                            
                            
