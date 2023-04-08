import numpy as np
from Piece import *
import pygame as p
import copy

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
IMAGES = {}
BLANK_POS = 0

def getKing(white_pList:list[Piece],black_pList:list[Piece]):
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

def loadImages():
    pieces = ["wp","bp","wR","wB","wK","wQ","wN","bR","bB","bK","bQ","bN"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("chess_pngs/{piece}.png".format(piece= piece)),(SQ_SIZE,SQ_SIZE))

def gameState(screen: p.Surface, board:list[list[str]]):
    colours = [p.Color("white"), p.Color("gray")]
    for row in range(DIMENSION):
        for column in range(DIMENSION):
            colour = colours[((row+column)%2)]
            p.draw.rect(screen, colour, p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))
            piece = board[row][column]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(column*SQ_SIZE,row*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def position_shower(all_possible:np.ndarray, White_pList: list[Piece], Black_pList: list[Piece], screen: p.Surface, selected_p: Piece, king_array: list[Piece],all_attack:np.ndarray = None, return_mov:bool = False):
    # this is the visual part of the chess game, it moves to the position, check if it is legal and then moves back
    
    legal_moves = []
    attacking_p_movs = []
    
    p_name = selected_p.get_name()
    isCheck = check(king_array[0],king_array[1],White_pList,Black_pList,True)
    checked_king = king_array[0] if selected_p.get_colour() == Colour.w.value else king_array[1]
    
    surface = surface_creator(50)
    draw(screen,surface,"p",selected_p.get_position()) if not return_mov else 0
    
    if isCheck != False:
        if isCheck.get_name() != "p":
            attacking_p_movs,skip = movesReturn(isCheck)
            attacking_p_movs = get_attack_line(checked_king,attacking_p_movs, isCheck.get_position())
        else:
            attacking_p_movs = np.expand_dims(copy.deepcopy(isCheck.get_position()),axis=0)
        
    for turn_set in all_possible: 

        for pos in turn_set:
            
            if (pos[0] > 7 or pos[0] <0) or (pos[1] > 7 or pos[1] < 0):
                break
            surface = surface_creator()
            output = piece_at_that_pos(pos,White_pList,Black_pList)

            can_move = check_after_move(selected_p, output, checked_king, pos, White_pList, Black_pList)
            
            end_of_Phile = False
            
            if output == BLANK_POS and can_move:
                    draw(screen,surface,"c",pos) if not return_mov else 0
                    legal_moves.append(pos)
            
            elif output != BLANK_POS and can_move:
                draw(screen,surface,"r",pos) if not return_mov else 0
                legal_moves.append(pos)
                end_of_Phile = True
                
            elif (output != BLANK_POS and output.get_colour() == selected_p.get_colour()) or (p_name == "p" and output != BLANK_POS):
                end_of_Phile = True
            
            if end_of_Phile:break

    if p_name == "p":
        position_show_for_pawn_attack(all_attack, White_pList, Black_pList, selected_p, checked_king, screen, legal_moves, return_mov)
    
    if selected_p.get_name() == "K" and selected_p.get_castle():
        p_pos = selected_p.get_position()
        for pos in PieceType.K.value["castle"]:
            new_pos = pos+p_pos
            output = castle_checker(selected_p,new_pos,White_pList,Black_pList)
            if output:
                surface = surface_creator()
                draw(screen,surface,"c",new_pos) if not return_mov else 0
                legal_moves.append(new_pos)
    return np.array(legal_moves)

def position_show_for_pawn_attack(all_attack: np.ndarray, White_pList: list[Piece], Black_pList: list[Piece], selected_p: Piece, checked_king: Piece, screen: p.Surface, legal_moves: list[np.ndarray], return_mov):
    for attack in all_attack:
        surface = surface_creator()
        output = piece_at_that_pos(attack,White_pList,Black_pList)
        if output == BLANK_POS:
            en_passanted_pawn = piece_at_that_pos(np.array([attack[0]-selected_p.get_colour(),attack[1]]), White_pList, Black_pList)
            if en_passanted_pawn == BLANK_POS or (en_passanted_pawn.get_name() != "p") or (en_passanted_pawn.get_name() == "p" and not en_passanted_pawn.can_be_en_passant()) or en_passanted_pawn.get_colour() == selected_p.get_colour():
                continue
            can_move = check_after_move(selected_p, en_passanted_pawn, checked_king, attack, White_pList, Black_pList)
            if not can_move:
                continue
            draw(screen, surface,"c", attack) if not return_mov else 0
            draw(screen, surface,"r", en_passanted_pawn.get_position()) if not return_mov else 0
            legal_moves.append(attack)
            
        elif output.get_colour() != selected_p.get_colour():
            can_move = check_after_move(selected_p, output, checked_king, attack, White_pList, Black_pList)
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
    p_old = selected_p.get_position()
    selected_p.change_pos(to)
    if attacked_p == BLANK_POS:
        valid_move = check(king, None, White_pList, Black_pList)
        selected_p.change_pos(p_old)
        return (valid_move == False)
    elif attacked_p.get_colour() != selected_p.get_colour():
        attacked_p_old = attacked_p.get_position()
        destroyed_p(attacked_p)
        valid_move = check(king, None, White_pList, Black_pList)
        attacked_p.change_pos(attacked_p_old)
        selected_p.change_pos(p_old)
        return (valid_move == False)
    selected_p.change_pos(p_old)
    return (king == False)
        
def draw(screen:p.Surface,surface:p.Surface, r_or_c:str, pos:np.ndarray):
    if r_or_c.lower() == "c":       
        p.draw.circle(surface,(0,0,0), (32 + (64*pos[1]),32 + (64*pos[0])), DIMENSION*1.5)
    elif r_or_c.lower() == "r":
        p.draw.rect(surface,(255,0,0),p.Rect(pos[1]*SQ_SIZE,pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    else:
        p.draw.rect(surface,(255,255,0),p.Rect(pos[1]*SQ_SIZE,pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    screen.blit(surface,(0,0))

def destroyed_p(attacked_p:Piece):
    if attacked_p != BLANK_POS:
        attacked_p.change_pos(None)
        attacked_p.destroyed = True
                
def piece_at_that_pos(coord:np.ndarray, w_list:list[Piece], b_list: list[Piece]) -> Piece:
    piece = None
    for p in (w_list if w_list != None else [])+(b_list if b_list != None else []):
        try:
            if (p.get_position() == coord).all():
                piece = p
                return piece
        except:
            continue   

    return 0

def check_line(selected_p: Piece,all_possible: np.ndarray,to: np.ndarray,w_list: list[Piece],b_list: list[Piece]) -> bool:
    choosen_dir = np.nonzero(((to == all_possible).all(axis= 2))*1)
    if choosen_dir[0].size == 0:
        return False
    
    line = np.array([])
    if selected_p.get_name() != "p":
        line = all_possible[choosen_dir[0][0], 0: choosen_dir[1][0]+1]
    else:
        line = (all_possible[choosen_dir[0][0],choosen_dir[1][0]]).reshape((1,2))
        
    if selected_p.get_name() == "K" and abs(to[1] - selected_p.get_position()[1]) == 2:
        if to[1] - selected_p.get_position()[1] == 2:
            line = np.append(line,np.array([line[0][0],line[0][1]-1])).reshape((2,2))
        else:
            np.add(line[0],np.array([line[0][0],line[0][1]+1]))
    
    for pos in line:
        output = piece_at_that_pos(list(pos),w_list,b_list)
        if output != BLANK_POS and selected_p == output:
            continue
        if output != BLANK_POS and selected_p.get_colour() == output.get_colour():
            return False
        elif output != BLANK_POS and selected_p.get_colour() != output.get_colour() and not (to == output.get_position()).all(axis=0):
            return False
        else:
            continue
    return True

def movesReturn(piece: Piece)-> list[np.ndarray]:
    if piece == False or piece.isDestroyed():
        return 
    p_info = piece.get_info()
    p_colour = piece.get_colour()
    p_pos = piece.get_position()
    p_name = piece.get_name()
    
    if p_name == "p":
        if (p_pos[0] == 6 and p_colour == Colour.w.value) or (p_pos[0] == 1 and p_colour == Colour.b.value):
            all_possible = p_pos + np.expand_dims(p_info["moves"],axis=1)*p_colour*np.arange(1,2).reshape(1,1)
        else:
            all_possible = p_pos + np.expand_dims(p_info["moves"][0:1],axis=1)*p_colour*np.arange(1,2).reshape(1,1)
        all_attack = p_pos + p_info["attack"]*p_colour*np.arange(1,2).reshape(1,1)
        all_attack = all_attack[(np.max(all_attack,axis=1) < 8) & (np.min(all_attack,axis=1) > -1)]
        return all_possible, all_attack
    
    elif p_name == "N":
        all_possible = p_pos + np.expand_dims(p_info["moves"],axis=1)*p_colour
        return all_possible,None
    
    elif p_name == "K":
        all_possible = p_pos + np.expand_dims(p_info["moves"],axis=1)*p_colour
        return all_possible,None
    
    else:
        all_possible = p_pos + np.expand_dims(p_info["moves"],axis=1)*np.arange(1,8).reshape(7,1)*p_colour
        return all_possible,None
    
def castle_checker(king: Piece, to: np.ndarray, White_pList: list[Piece], Black_pList: list[Piece]) -> bool:
    currently_checked = check(king,None,White_pList,Black_pList)
    if not king.get_castle() or (currently_checked != False and currently_checked.get_colour() == king.get_colour()):
        return False
    K_pos = king.get_position()
    dif = to[1] - K_pos[1]
    if dif > 0:
        R_pos = to + np.array([0,1])
    else:
        R_pos = to + np.array([0,-2])

    piece = piece_at_that_pos(R_pos,White_pList,Black_pList)
    
    rook_sanity_check = piece != BLANK_POS and piece.get_name() == "R" and piece.get_colour() == king.get_colour()
    
    if rook_sanity_check:
        if not piece.get_castle():
            return False
        
        if dif<0:
            r_val = 3
            k_val = 2
        elif dif > 0:
            r_val = 5
            k_val = 6

        if (not check_line(king,movesReturn(king)[0],np.array([K_pos[0],k_val]),White_pList,Black_pList) and 
            not check_line(piece,movesReturn(piece)[0],np.array([K_pos[0],r_val]),White_pList,Black_pList)):
            return False
        
        k_old = king.get_position()
        r_old = piece.get_position()
        king.change_pos(np.array(to))
        piece.change_pos(np.array([k_old[0],r_val]))
        not_possible = False
        isCheck = check(king,None,White_pList,Black_pList)
        if isCheck != False and isCheck.get_colour() == king.get_colour():
            not_possible = True
        king.change_pos(k_old)
        piece.change_pos(r_old)
        return False if not_possible else True
    return False

def check(wking: Piece, bking: Piece, White_pList: list[Piece],Black_pList: list[Piece],attacking_p_return:bool=False):
    for king in [wking,bking]:
        if king == None or king.isDestroyed():
            continue
        king_movs = king.get_info()["moves"]
        k_pos = king.get_position()
        for mov in king_movs:
            mov_num = mov*np.arange(1,8).reshape(7,1) + k_pos
            mov_num = mov_num[(np.max(mov_num,axis=1)<8) & (np.min(mov_num,axis=1)>-1)]
            for each in mov_num:
                output = piece_at_that_pos(each,White_pList,Black_pList)
                if output == BLANK_POS:
                    continue
                elif output.get_colour() == king.get_colour(): # output != BLANK_POS
                    break
                elif output.get_name() == "p": # output != BLANK_POS and colour NOT same
                    index_array = (each == mov_num).all(axis=1).nonzero()        
                    if ((np.array([mov[0]*king.get_colour(),mov[1]]) == output.get_info()["attack"]).all(axis=1)).any() and len(index_array) == 1 and index_array[0][0] == 0:
                        king.change_pos(k_pos)
                        return king if not attacking_p_return else output
                    else:
                        break
                elif ((mov == output.get_info()["moves"]).all(axis=1)).any(): # output != BLANK_POS and colour NOT same and not Pawn
                    if output.get_name() != "K":
                        king.change_pos(k_pos)
                        return king if not attacking_p_return else output
                    if np.where((each == mov_num).all(axis=1) == True)[0] == 0:
                        return king if not attacking_p_return else output
                    break
        K_horse_check = PieceType.N.value["moves"]+k_pos
        K_horse_check = K_horse_check[(np.max(K_horse_check,axis=1)<8) & (np.min(K_horse_check,axis=1)>-1)]
        for movs in K_horse_check:
            output = piece_at_that_pos(movs,White_pList,Black_pList)
            if output != BLANK_POS  and output.get_info() == PieceType.N.value and output.get_colour() != king.get_colour():
                king.change_pos(k_pos)
                return king if not attacking_p_return else output
            
    return False

def check_mate(w_king:Piece,b_king:Piece, white_pList: list[Piece], black_pList: list[Piece]):
    w_check_m = False
    b_check_m = False
    output_arr = []
    for king in [w_king,b_king]:
        old = king.get_position()
        currently_check = check(king,b_king,white_pList,black_pList)
        if king != currently_check:
            continue
        new_pos = old + np.array([[[1,0]],[[1,1]],[[0,1]],[[-1,1]],[[-1,0]],[[-1,-1]],[[0,-1]],[[1,-1]]])
        for pos in new_pos:
            if (np.max(pos[0]) > 7).all() or (np.min(pos[0]) < 0).all():
                continue
            piece = piece_at_that_pos(pos,white_pList,black_pList)
            output = None
            if piece == BLANK_POS or (piece != BLANK_POS and piece.get_colour() != king.get_colour()):
                output = check_after_move(king,piece,king,pos, white_pList, black_pList)
            output_arr.append(output)
            
        if not (False in output_arr) and king in output_arr and len(output_arr) > 0:
            if king == w_king:
                w_check_m = True
            else:
                b_check_m = True
        output_arr = []
        king.change_pos(old)
        
    if w_check_m or b_check_m:
        check_array = np.array([w_king,b_king])
        check_array = check_array[np.array([w_check_m,b_check_m])]
        correct_self_list = np.array([white_pList,black_pList])[np.array([w_check_m,b_check_m])]
        attacking_p = check(check_array[0], None,white_pList,black_pList,True)
        attacking_line = []
        
        if attacking_p.get_name() !=  'p':
            attacking_p_movs,skip = movesReturn(attacking_p)
            attacking_line = get_attack_line(check_array[0],attacking_p_movs,attacking_p.get_position())
        else:
            attacking_line = np.expand_dims(copy.deepcopy(attacking_p.get_position()),axis=0)
            
        if attacking_line.any() == False:
            return False,False
        for piece in correct_self_list[0]:
            try:
                to,piece_movs = move_to_attack_line(piece,attacking_line,True)
            except:
                continue
            
            if to.size <= 0:
                continue
            
            for movs in to:
                line_clear = check_line(piece,piece_movs,movs,white_pList,black_pList)
                if not line_clear:
                    break
                if piece.get_name() == "K":
                    break
                if check_array[0] == w_king:
                    w_check_m = False
                elif check_array[0] == b_king:
                    b_check_m = False
    
    return w_check_m,b_check_m

def get_attack_line(king: Piece,attacking_piece_moves: np.ndarray,p_pos: np.ndarray):
    choosen_dir = np.nonzero(((king.get_position() == attacking_piece_moves).all(axis=2))*1)
    if choosen_dir[0].size == 0:
        return np.array([-1,-1])
    attacking_movs = attacking_piece_moves[choosen_dir[0][0], 0:choosen_dir[1][0]]
    attacking_movs = np.append(attacking_movs,p_pos)
    attacking_movs = attacking_movs.reshape((int(attacking_movs.shape[0]/2),2))
    return attacking_movs

def pawn_promotion(piece:Piece,screen: p.Surface,board: list[list[str]],AI: bool=False):
    if piece == BLANK_POS:
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

    pawn_promotion_screen = p.Surface((WIDTH,HEIGHT))
    pawn_promotion_screen.fill((0,0,0))
    pawn_promotion_screen.set_alpha(200)
    Piece_screen = p.Surface((WIDTH,HEIGHT))
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
    if piece.get_name() != "p":
        t_table = ((p_movs-attack_movs) == 0).all(axis=3)
        to = p_movs[t_table.any(axis=0)]
        return to,p_movs if p_pos_return else to
    
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
    game_end_screen = p.Surface((WIDTH,HEIGHT))
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
                legal_moves = position_shower(all_moves.reshape((all_moves.shape[1],all_moves.shape[0],2)),White_pList,Black_pList,None, piece,king_array,all_attack,True)
            else:
                all_moves,all_attack = movesReturn(piece)
                legal_moves = position_shower(all_moves,White_pList,Black_pList,None, piece,king_array,all_attack,True)
            if legal_moves.size > 0:
                P_bool = True
                break
        if not P_bool:
            return True 
    return False