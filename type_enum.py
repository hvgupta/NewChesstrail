from enum import Enum
import numpy as np

# the first class has the points and the basic moves the chess pieces could move so the tuple is like ([points], [most basic moves], [pawn special case])

class type(Enum):
    p = (1, np.array([[1,0],[2,0]]), np.array([[1,-1],[1,1]]))
    N = (3, np.array([[2,1],[1,2],[-1,2],[-2,1],[-2,-1],[-1,-2],[1,-2],[2,-1]]))
    B = (3,np.array([[1,1],[-1,1],[-1,-1],[1,-1]]))
    R = (5,np.array([[1,0],[0,1],[-1,0],[0,-1]]))
    Q = (9,np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1]]))
    K = (np.inf,np.array([[1,0],[1,1],[0,1],[-1,1],[-1,0],[-1,-1],[0,-1],[1,-1],[0,2],[0,-2]]))
    
class Colour(Enum):
    w = -1
    b = 1