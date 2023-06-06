import numpy as np
from Piece import *
import pygame as p
import copy

IMGWIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
IMAGES = {}
EMPTY_POS = 0

def getKing(white_pList:list[Piece],black_pList:list[Piece]) -> tuple[Piece]:
    white_king = ''
    black_king = ''
    for piece in white_pList:
        if piece.get_name() == "K" and piece.get_colour() == Colour.w.value:
            white_king = piece
            break
        
    for piece in black_pList:
        if piece.get_name() == "K" and piece.get_colour() == Colour.b.value:
                black_king = piece
                break
    return white_king,black_king

def loadImages(): # loads the sprites of the chess pieces
    pieces = ["wp","bp","wR","wB","wK","wQ","wN","bR","bB","bK","bQ","bN"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("chess_pngs/{piece}.png".format(piece= piece)),(SQ_SIZE,SQ_SIZE))

def gameState(screen: p.Surface, board:list[list[str]]): #draws the chess board and the pieces on the screen
    colours = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            colour = colours[((row+column)%2)]
            p.draw.rect(screen, colour, p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def returnValidPos(all_possible:np.ndarray, White_pList: list[Piece], Black_pList: list[Piece], screen: p.Surface, selected_p: Piece, king_array: list[Piece],all_attack:np.ndarray = None, return_mov:bool = False) -> np.ndarray:
    # this is the visual part of the chess game, it moves to the position, check if it is legal and then moves back
    legal_moves = []
    attacking_p_movs = []
    
    p_name = selected_p.get_name()
    attackingPiece = check(king_array[0],king_array[1],White_pList,Black_pList,True) # if the king is checked, then attackingPiece is the Piece checking the king
    checked_king = king_array[0] if selected_p.get_colour() == Colour.w.value else king_array[1]
    
    surface = surface_creator(50)
    draw(screen,surface,"p",selected_p.get_position()) if not return_mov else 0
    
    if attackingPiece != False:
        if attackingPiece.get_name() != "p":
            attacking_p_movs,skip = movesReturn(attackingPiece)
            attacking_p_movs = get_attack_line(checked_king,attacking_p_movs, attackingPiece.get_position())
        else:
            attacking_p_movs = np.expand_dims(copy.deepcopy(attackingPiece.get_position()),axis=0)

    for turn_set in all_possible: # one of the base movement as shown in the PieceType class

        for pos in turn_set: # depending on the piece, this iterated through the mutiple of the base movement + the Piece's position
            
            if (pos[0] > 7 or pos[0] <0) or (pos[1] > 7 or pos[1] < 0): # if the Piece is outside the board
                break
            surface = surface_creator()
            output = piece_at_that_pos(pos,White_pList,Black_pList) # returns the cell status at that position
            can_move = check_after_move(selected_p, output, checked_king, pos, White_pList, Black_pList) # can move is a bool, can sees if the king is checked after moving to `pos`
            
            if not can_move:
                break
            
            elif output == EMPTY_POS:
                draw(screen,surface,"c",pos) if not return_mov else 0 # draw a circle if it is an empty space, and a normal move
                legal_moves.append(pos)
            
            elif p_name == "p":
                break
            
            else:
                draw(screen,surface,"r",pos) if not return_mov else 0 # draw a red rectange if the Piece at the position is opposite colour
                legal_moves.append(pos)
                break

    if p_name == "p": # this checks for pawn attacking (normal attacks and en passant)
        position_show_for_pawn_attack(all_attack, White_pList, Black_pList, selected_p, checked_king, screen, legal_moves, return_mov)
    
    if selected_p.get_name() == "K" and selected_p.get_castle(): # this checks if the king can castle
        p_pos = selected_p.get_position()
        for pos in PieceType.K.value["castle"]:
            new_pos = pos+p_pos
            output = castle_checker(selected_p,new_pos,White_pList,Black_pList)
            if output:
                surface = surface_creator()
                draw(screen,surface,"c",new_pos) if not return_mov else 0 # draw a circle if the king can castle
                legal_moves.append(new_pos)

    return np.array(legal_moves)

def position_show_for_pawn_attack(all_attack: np.ndarray, White_pList: list[Piece], Black_pList: list[Piece], selected_p: Piece, checked_king: Piece, screen: p.Surface, legal_moves: list[np.ndarray], return_mov):
    for attack in all_attack: # iterates through pawn's normal attack moves 
        surface = surface_creator()
        output = piece_at_that_pos(attack,White_pList,Black_pList)
        if output == EMPTY_POS: #if the attacking is towards an empty position 
            en_passanted_pawn = piece_at_that_pos(np.array([attack[0]-selected_p.get_colour(),attack[1]]), White_pList, Black_pList) # checks if there is a pawn which can be en passant
            if en_passanted_pawn == EMPTY_POS or (en_passanted_pawn.get_name() != "p") or (en_passanted_pawn.get_name() == "p" and not en_passanted_pawn.can_be_en_passant()) or en_passanted_pawn.get_colour() == selected_p.get_colour():
                continue
            can_move = check_after_move(selected_p, en_passanted_pawn, checked_king, attack, White_pList, Black_pList) #checks if the attack does not cause the moving side to be checked
            if not can_move:
                continue
            draw(screen, surface,"c", attack) if not return_mov else 0 
            draw(screen, surface,"r", en_passanted_pawn.get_position()) if not return_mov else 0
            legal_moves.append(attack)
            
        elif output.get_colour() != selected_p.get_colour():
            can_move = check_after_move(selected_p, output, checked_king, attack, White_pList, Black_pList)#checks if the attack does not cause the moving side to be checked
            if not can_move:
                continue
            draw(screen,surface,"r",attack) if not return_mov else 0
            legal_moves.append(attack)

def surface_creator(alpha:int=25):
    surface = p.Surface((512,512),p.SRCALPHA)
    surface.set_colorkey(p.Color("White"))
    surface.set_alpha(alpha)
    return surface

def check_after_move(selected_p: Piece, attacked_p: Piece, king:Piece, to: np.ndarray, White_pList: list[Piece], Black_pList: list[Piece]) -> bool:
    p_old = selected_p.get_position() # saves the old position 
    selected_p.change_pos(to) # changes the position to the new position
    if attacked_p == EMPTY_POS: # if the position being moved to is empty
        valid_move = check(king, None, White_pList, Black_pList) # move does not cause checks on its side, returns if the king is checked
        selected_p.change_pos(p_old) # position returns to old position
        return (valid_move == False) 
    elif attacked_p.get_colour() != selected_p.get_colour(): #if the position being moved to is not empty and of the opposite colour
        attacked_p_old = attacked_p.get_position() # get the position of the attacked piece
        destroyed_p(attacked_p) # destroy the piece
        valid_move = check(king, None, White_pList, Black_pList) # check if the move causes can checks on its side, returns if the king is checked
        attacked_p.change_pos(attacked_p_old)
        selected_p.change_pos(p_old) # return to prev positions
        return (valid_move == False)
    selected_p.change_pos(p_old)
    return False
        
def draw(screen:p.Surface,surface:p.Surface, r_or_c:str, pos:np.ndarray):
    if r_or_c.lower() == "c":       
        p.draw.circle(surface,(0,0,0), (32 + (64*pos[1]),32 + (64*pos[0])), DIMENSION*1.5)
    elif r_or_c.lower() == "r":
        p.draw.rect(surface,(255,0,0),p.Rect(pos[1]*SQ_SIZE,pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    else:
        p.draw.rect(surface,(255,255,0),p.Rect(pos[1]*SQ_SIZE,pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    screen.blit(surface,(0,0))

def destroyed_p(attacked_p:Piece):
    if attacked_p != EMPTY_POS:
        attacked_p.change_pos(None)
        attacked_p.destroyed = True
                
def piece_at_that_pos(coord:np.ndarray, White_pList:list[Piece], Black_pList: list[Piece]) -> Piece:
    piece = None
    for p in (White_pList if White_pList != None else [])+(Black_pList if Black_pList != None else []): # iterates through the list of Pieces
        try:
            if (p.get_position() == coord).all(): # looks for a piece with a specific position
                piece = p
                return piece
        except:
            continue   

    return EMPTY_POS

def check_line(selected_p: Piece,all_possible: np.ndarray,to: np.ndarray,w_list: list[Piece],b_list: list[Piece]) -> bool:
    choosen_dir = np.nonzero(((to == all_possible).all(axis= 2))*1) # looks for which basic move is selected, gives the index of the basic move
    if choosen_dir[0].size == 0:
        return False
    
    line = np.array([])
    if selected_p.get_name() != "p": # if the piece being checked for is not a pawn
        line = all_possible[choosen_dir[0][0], 0: choosen_dir[1][0]+1]
    else:
        line = (all_possible[choosen_dir[0][0],choosen_dir[1][0]]).reshape((1,2))
        
    if selected_p.get_name() == "K" and abs(to[1] - selected_p.get_position()[1]) == 2: # this is to check if castle can be done
        if to[1] - selected_p.get_position()[1] == 2:
            line = np.append(line,np.array([line[0][0],line[0][1]-1])).reshape((2,2)) # stores the position to check for castling king side
        else:
            np.add(line[0],np.array([line[0][0],line[0][1]+1])) # stores the position to check for castling queen side
    
    for pos in line:
        output = piece_at_that_pos(list(pos),w_list,b_list)
        if output == EMPTY_POS: # if the position is empty then continue
            continue
        elif selected_p == output: # if the position is not empty and it is the piece itself, then continue
            continue
        else: # otherwise return False (there is something in between the move you want to make)
            return False
    return True

def movesReturn(piece: Piece)-> list[np.ndarray]:
    if piece == False or piece.isDestroyed(): # checks if the piece is valid
        return None, None
    p_info = piece.get_info()
    p_colour = piece.get_colour()
    p_pos = piece.get_position()
    p_name = piece.get_name()
    # gets the basic info the piece
    if p_name == "p": # if the Piece is a pawn
        if (p_pos[0] == 6 and p_colour == Colour.w.value) or (p_pos[0] == 1 and p_colour == Colour.b.value): #checks if the pawn is at the starting position, therefore can do double move
            all_possible = p_pos + np.expand_dims(p_info["moves"],axis=1)*p_colour*np.arange(1,2).reshape(1,1)
        else:
            all_possible = p_pos + np.expand_dims(p_info["moves"][0:1],axis=1)*p_colour*np.arange(1,2).reshape(1,1)
        all_attack = p_pos + p_info["attack"]*p_colour*np.arange(1,2).reshape(1,1) # checks for the attacks the pawn can make
        all_attack = all_attack[(np.max(all_attack,axis=1) < 8) & (np.min(all_attack,axis=1) > -1)]
        return all_possible, all_attack
    
    elif p_name == "N": # if the Piece is a knight
        all_possible = p_pos + np.expand_dims(p_info["moves"],axis=1)*p_colour
        return all_possible,None
    
    elif p_name == "K": # if the Piece is a king
        all_possible = p_pos + np.expand_dims(p_info["moves"],axis=1)*p_colour
        return all_possible,None
    
    else: # rest of the pieces
        all_possible = p_pos + np.expand_dims(p_info["moves"],axis=1)*np.arange(1,8).reshape(7,1)*p_colour
        return all_possible,None
    
def castle_checker(king: Piece, to: np.ndarray, White_pList: list[Piece], Black_pList: list[Piece]) -> bool:
    currently_checked = check(king,None,White_pList,Black_pList) # if the king currently checked?
    if not king.get_castle() or (currently_checked != False and currently_checked.get_colour() == king.get_colour()): #checks if the king can castle
        return False
    K_pos = king.get_position()
    dif = to[1] - K_pos[1]
    if dif > 0: # gets the position of the rock being used to castle
        R_pos = to + np.array([0,1])
    else:
        R_pos = to + np.array([0,-2])

    piece = piece_at_that_pos(R_pos,White_pList,Black_pList) # gets the piece at the location
    
    rook_sanity_check = piece != EMPTY_POS and piece.get_name() == "R" and piece.get_colour() == king.get_colour()
    
    if rook_sanity_check:
        if not piece.get_castle(): # checks if the rook can castle 
            return False
        
        #notes the future values of king and rook
        if dif<0: 
            r_val = 3
            k_val = 2
        elif dif > 0:
            r_val = 5
            k_val = 6

        if (not check_line(king,movesReturn(king)[0],np.array([K_pos[0],k_val]),White_pList,Black_pList) and 
            not check_line(piece,movesReturn(piece)[0],np.array([K_pos[0],r_val]),White_pList,Black_pList)): # sees if there is something blocking the way
            return False
        
        can_castle = check_after_move(king, EMPTY_POS, king, to, White_pList, Black_pList) # checks if the move causes checks
        if can_castle:
            return True
        
    return False

def check(wking: Piece, bking: Piece, White_pList: list[Piece],Black_pList: list[Piece],attacking_p_return:bool=False):
    for king in [wking,bking]:
        if king == None or king.isDestroyed(): # this is for error checking/ when one of the king is not specified
            continue
        king_movs = king.get_info()["moves"]
        k_pos = king.get_position()
        
        for mov in king_movs: # iterates through king's basic moves
            mov_num = mov*np.arange(1,8).reshape(7,1) + k_pos # from king's perspective the move is scaled to 8
            mov_num = mov_num[(np.max(mov_num,axis=1)<8) & (np.min(mov_num,axis=1)>-1)] # remove the position checks beyond the board
            for each in mov_num: # iterates through the positions to check
                output = piece_at_that_pos(each,White_pList,Black_pList)
                
                if output == EMPTY_POS:
                    continue
                
                elif output.get_colour() == king.get_colour(): # when output is not empty position and output is of the same colour
                    break
                elif output.get_name() == "p": # output != EMPTY POS and colour NOT same
                    index_array = (each == mov_num).all(axis=1).nonzero()        
                    
                    if ((np.array([mov[0]*king.get_colour(),mov[1]]) == output.get_info()["attack"]).all(axis=1)).any() and len(index_array) == 1 and index_array[0][0] == 0:
                        king.change_pos(k_pos) # this is for resetting the king
                        return king if not attacking_p_return else output # the pawn can check the king
                    
                    else:
                        break # breaks if the pawn cannot check, since, nothing else can check the king from that direction 
                    
                elif ((mov == output.get_info()["moves"]).all(axis=1)).any(): # output != BLANK_POS and colour NOT same and not Pawn
                    
                    if output.get_name() != "K": # when attacking piece is not king
                        king.change_pos(k_pos) # this is for resetting the king
                        return king if not attacking_p_return else output
                    
                    if np.where((each == mov_num).all(axis=1) == True)[0] == 0: 
                        return king if not attacking_p_return else output
                    break
                
        K_horse_check = PieceType.N.value["moves"]+k_pos # checks if the king can be checked by a horse
        K_horse_check = K_horse_check[(np.max(K_horse_check,axis=1)<8) & (np.min(K_horse_check,axis=1)>-1)]
        
        for movs in K_horse_check:
            output = piece_at_that_pos(movs,White_pList,Black_pList)
            if output != EMPTY_POS  and output.get_info() == PieceType.N.value and output.get_colour() != king.get_colour():
                king.change_pos(k_pos)
                return king if not attacking_p_return else output
            
    return False

def check_mate(king:Piece,white_pList: list[Piece], black_pList: list[Piece]) -> bool:
    check_m = False
    output_arr = []
    # if the king is in check, then can the king do something to aviod the check
    old = king.get_position() # stores, king's old position
    currently_check = check(king,None,white_pList,black_pList) # is the king currently checked?
    if king != currently_check:
        return False
    new_pos = old + king.get_info()["moves"] # if not, then goes through all the moves that the king could make
    for pos in new_pos:
        if (np.max(pos[0]) > 7).all() or (np.min(pos[0]) < 0).all(): # removes position if they are out of board 
            continue
        piece = piece_at_that_pos(pos,white_pList,black_pList)
        output = None # output can be None (undecided), True (move which is not check), False (move which is check)
        if piece == EMPTY_POS or (piece != EMPTY_POS and piece.get_colour() != king.get_colour()):
            output = check_after_move(king,piece,king,pos, white_pList, black_pList)
        output_arr.append(output)
        
    if not (True in output_arr): # checks if there are any `True`
        check_m = True
    output_arr = []
    # if not then checks if other pieces can break the check     
    if check_m:
        correct_self_list = white_pList if white_pList[0].get_colour() == king.get_colour() else black_pList
        attacking_p = check(king, None,white_pList,black_pList,True)
        attacking_line = []
        
        if attacking_p.get_name() !=  'p': # if the piece is not Pawn
            attacking_p_movs,skip = movesReturn(attacking_p)
            attacking_line = get_attack_line(king,attacking_p_movs,attacking_p.get_position()) # gets how the piece is attacking, the line in which it is attacking from
        else:
            attacking_line = np.expand_dims(copy.deepcopy(attacking_p.get_position()),axis=0) # if it is a pawn, get its position and apply matrix operation so that the dimension is same
            
        if attacking_line.any() == False: #if the attacking line does not exist then there is no check, (just as a precaution)
            return False
        for piece in correct_self_list:
            try:
                to,piece_movs = move_to_attack_line(piece,attacking_line,True) # sees if any piece can break the attack line
            except:
                continue
            
            if to.size <= 0: # if the piece cut the line, then continue
                continue
            
            for movs in to:
                line_clear = check_line(piece,piece_movs,movs,white_pList,black_pList)
                if not line_clear:
                    break
                if piece.get_name() == "K":
                    break
                check_m = False
    
    return check_m

def get_attack_line(king: Piece,attacking_piece_moves: np.ndarray,p_pos: np.ndarray):
    choosen_dir = np.nonzero(((king.get_position() == attacking_piece_moves).all(axis=2))*1) # checks which basic move to choose from
    if choosen_dir[0].size == 0: # if none then return false condition 
        return np.array([-1,-1])
    attacking_movs = attacking_piece_moves[choosen_dir[0][0], 0:choosen_dir[1][0]] # otherwise get the array from attacking piece loc to one before the king
    attacking_movs = np.append(attacking_movs,p_pos)
    attacking_movs = attacking_movs.reshape((int(attacking_movs.shape[0]/2),2))
    return attacking_movs

def pawn_promotion(piece:Piece,screen: p.Surface,board: list[list[str]]):
    if piece == EMPTY_POS:
        return
    p_pos = piece.get_position()
    current_Colour = 0
    if piece.get_name() == "p" and p_pos[0] in [0,7]:
        current_Colour = 0
        if piece.get_colour() == Colour.w.value:
            current_Colour = Colour.w
        elif piece.get_colour() == Colour.b.value:
            current_Colour = Colour.b
    if current_Colour == 0:
        return
        
    piece_image = {"Q": '', "R": '', "B": '', "N": ''}
    for Piece_letter in piece_image.keys():
        piece_image[Piece_letter] = p.transform.scale(p.image.load(f"chess_pngs/{current_Colour.name}{Piece_letter}.png"),(2*SQ_SIZE,2*SQ_SIZE))

    pawn_promotion_screen = p.Surface((IMGWIDTH,HEIGHT))
    pawn_promotion_screen.fill((0,0,0))
    pawn_promotion_screen.set_alpha(200)
    Piece_screen = p.Surface((IMGWIDTH,HEIGHT))
    p.draw.rect(pawn_promotion_screen,(250,250,250),p.Rect(5*SQ_SIZE,5*SQ_SIZE,SQ_SIZE*6,SQ_SIZE*3))
    
    position_possible = np.array([[3,0],[3,1],[4,0],[4,1],[3,2],[3,3],[4,2],[4,3],[3,4],[3,5],[4,4],[4,5],[3,6],[3,7],[4,6],[4,7]])
    running = True
    coord = 0
    for image in piece_image.values():
        Piece_screen.blit(image, p.Rect(coord*SQ_SIZE,3*SQ_SIZE,2*SQ_SIZE,2*SQ_SIZE))
        coord+=2

    pawn_promotion_screen.blit(Piece_screen,(0,0))
    screen.blit(pawn_promotion_screen,(0,0))
    p.display.update()
    while running:
        
        for e in p.event.get():
            if e.type == p.MOUSEBUTTONDOWN:
                mouse_pos = p.mouse.get_pos()
                col = mouse_pos[0]//SQ_SIZE
                row = mouse_pos[1]//SQ_SIZE
                allowed = (position_possible == (row,col)).all(axis=1).any()
                if not allowed:
                    continue
                
                index = np.where((position_possible == (row,col)).all(axis=1))[0][0]
                piece_type = ''
                if index in [12,13,14,15]:
                    piece_type = 'N'
                elif index in [8,9,10,11]:
                    piece_type = 'B'
                elif index in [4,5,6,7]:
                    piece_type = 'R'
                else:
                    piece_type = 'Q'
                piece.change_type(getattr(PieceType,piece_type))
                screen.blit(piece_image[piece_type],p.Rect(p_pos[1]*SQ_SIZE,p_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
                board[p_pos[0]][p_pos[1]] = f"{current_Colour.name}{piece_type}"
                running = False
                break

def move_to_attack_line(piece: Piece, attack_movs: np.ndarray, p_pos_return: bool=False):
    p_movs,all_attack = movesReturn(piece)
    attack_movs = attack_movs.reshape(attack_movs.shape[0],1,1,attack_movs.shape[1])
    if piece.get_name() != "p": # if the Piece is not pawn
        t_table = ((p_movs-attack_movs) == 0).all(axis=3) # this constructs a truth table
        to = p_movs[t_table.any(axis=0)] # uses the truth table to construct the possible moves table
        return to,p_movs if p_pos_return else to
    # does the same for pawn
    elif piece.get_name() == "p":
        all_attack = np.expand_dims(all_attack,axis=1)
        t_table = ((all_attack-attack_movs[-1]) == 0).all(axis=2).reshape(1,2,1)
        to = all_attack[t_table[0]]
        t_table = ((p_movs-attack_movs[:-1]) == 0).all(axis=3)
        to_extended = p_movs[t_table.any(axis=0)]
        to = np.append(to,to_extended)
        to = to.reshape((int(to.shape[0]/2),2))
        return_total = np.concatenate((all_attack,p_movs))
        return to,return_total if p_pos_return else to

def game_end(case: int,screen: p.Surface):
    game_end_screen = p.Surface((IMGWIDTH,HEIGHT))
    game_end_screen.fill((0,0,0))
    game_end_screen.set_alpha(200)
    p.font.init()
    font = p.font.SysFont("monospace",70)
    font.bold
    text = "White wins" if case == 2 else ("draw" if case == 0 else "Black wins")
    text_to_display = font.render(text,1, (165, 42, 42))
    screen.blit(game_end_screen,(0,0))
    screen.blit(text_to_display,(35,100))
    p.display.update()

def draw_check(White_pList: list[Piece], Black_pList: list[Piece], king_array: list[Piece])-> bool:
    w_has_legal_moves = False
    b_has_legal_moves = False
    for side,P_bool in zip([White_pList,Black_pList],[w_has_legal_moves,b_has_legal_moves]):
        for piece in side:
            if piece.isDestroyed():
                continue
            legal_moves = 0
            if piece.get_name() == "p":
                all_moves,all_attack = movesReturn(piece)
                if type(all_moves) == type(None):
                    continue
                legal_moves = returnValidPos(all_moves.reshape((all_moves.shape[1],all_moves.shape[0],2)),White_pList,Black_pList,None, piece,king_array,all_attack,True)
            else:
                all_moves,all_attack = movesReturn(piece)
                if type(all_moves) == type(None):
                    continue
                legal_moves = returnValidPos(all_moves,White_pList,Black_pList,None, piece,king_array,all_attack,True)
            if legal_moves.size > 0:
                P_bool = True
                break
        if not P_bool:
            return True 
    return False