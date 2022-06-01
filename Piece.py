from type_enum import *

class Piece(): # defines the pieces with their colour, their piece type(it also contains the most general moves they can make) and their position
    def __init__(self, piece_type:type, position, colour):
        self.piece_type = piece_type
        self.position = np.array(position)
        self._Colour = colour
        self.name = self.piece_type.name

    def get_info(self):
        return self.piece_type.value
    
    def get_colour(self):
        return self._Colour.value
    
    def get_points(self):
        return self.piece_type.value
    
    def get_position(self):
        return self.position
    
    def change_pos(self,new_pos):
        self.position = new_pos
    
    def get_name(self):
        return self.name