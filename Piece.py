from type_enum import *

class Piece(): # defines the pieces with their colour, their piece type(it also contains the most general moves they can make) and their position
    def __init__(self, piece_type:PieceType, position, colour: Colour):
        self.piece_type = piece_type
        self.position = np.array(position)
        self.Colour = colour
        self.name = self.piece_type.name
        if self.name in ["K","R"]:
            self.castle = True
        if self.name == "p":
            self.K_from_en_passant = False
        self.destroyed = False

    def get_info(self) -> dict:
        return self.piece_type.value
    
    def get_colour(self) -> int:
        return self.Colour.value
    
    def get_points(self) -> int:
        return self.piece_type.value[1]
    
    def get_position(self):
        return self.position
    
    def change_pos(self,new_pos):
        self.position = new_pos
        self.destroyed = False
    
    def get_name(self) -> str:
        return self.name
    
    def change_type(self,new_type: PieceType):
        self.piece_type = new_type
        self.name = new_type.name
        
    def get_castle(self) -> bool:
        return self.castle

    def change_castle(self):
        if self.name in ["K","R"]:
            self.castle = False
            
    def isDestroyed(self):
        return self.destroyed
    
    def can_be_en_passant(self):
        if self.name != "p":
            return False
        return self.K_from_en_passant
    
    def change_en_passant(self, condition):
        if self.name != "p":
            return
        self.K_from_en_passant = condition