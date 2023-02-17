from enum import Enum
import numpy as np

# the first class has the points and the basic moves the chess pieces could move so the tuple is like ([points], [most basic moves], [pawn special case])

class PieceType(Enum):
    p = {"points":1,"moves": np.array([[1,0],[2,0]]),"attack": np.array([[1,-1],[1,1]])}
    N = {"points": 3,"moves": np.array([[2,1],[1,2],[-1,2],[-2,1],[-2,-1],[-1,-2],[1,-2],[2,-1]])}
    B = {"points": 3,"moves": np.array([[1,1],[-1,1],[-1,-1],[1,-1]])}
    R = {"points": 5,"moves": np.array([[1,0],[0,1],[-1,0],[0,-1]])}
    Q = {"points": 9,"moves": np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]])}
    K = {"points": np.inf,"moves": np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]]),"castle": np.array([[0,2],[0,-2]])}
    
class Colour(Enum):
    w = -1
    b = 1