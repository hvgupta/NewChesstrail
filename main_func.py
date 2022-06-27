import numpy as np
from type_enum import *
import pygame as p

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
IMAGES = {}

def loadImages():
    pieces = ["wp","bp","wR","wB","wK","wQ","wN","bR","bB","bK","bQ","bN"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("chess_pngs/{piece}.png".format(piece= piece)),(SQ_SIZE,SQ_SIZE))

def gameState(screen, board):
    drawboard(screen)
    drawPieces(screen,board)
    
def drawboard(screen):
    colours = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[((r+c)%2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def position_shower(all_possible, WhiteList, BlackList, screen, selected_p,king_array,all_attack = None):
    p_name = selected_p.get_name()
    isCheck = check(king_array[0],king_array[1],WhiteList,BlackList,True)
    other_condition = True
    surface = surface_creator(50)
    draw(screen,surface,"p",selected_p.get_position())
    for turn_set in all_possible: 

        for pos in turn_set:
            
            if (pos[0] > 7 or pos[0] <0) or (pos[1] > 7 or pos[1] < 0):
                break
            surface = surface_creator()
            output = piece_at_that_point(pos,WhiteList,BlackList)
            if isCheck!= False and selected_p.get_name() != "K":
                checked_colour = king_array[0] if isCheck.get_colour() == Colour.b.value else king_array[1]
                if isCheck.get_name() != "p":
                    attacking_p_movs,skip = valueDefiner(isCheck)
                else:
                    p_movs, attacking_p_movs = valueDefiner(isCheck)
                    attacking_p_movs = np.expand_dims(attacking_p_movs,axis=1)
                choosen_dir = np.nonzero(((checked_colour.get_position() == attacking_p_movs).all(axis=2))*1)
                if choosen_dir[0].size == 0:
                    break
                attacking_p_movs = attacking_p_movs[choosen_dir[0][0],0:choosen_dir[1][0]+1]
                attacking_p_movs = np.append(attacking_p_movs,isCheck.get_position())
                attacking_p_movs = attacking_p_movs.reshape((int(attacking_p_movs.shape[0]/2),2))
                other_condition = ((attacking_p_movs == pos).all(axis=1)).any()
                
            if output == 0 and other_condition:
                old = selected_p.get_position()
                selected_p.change_pos(pos)
                Check = check(king_array[0],king_array[1],WhiteList,BlackList)
                selected_p.change_pos(old)
                if Check != False and Check.get_colour() == selected_p.get_colour():
                    continue
                else:
                    draw(screen,surface,"c",pos)
            
                    
            elif output != 0 and output.get_colour() != selected_p.get_colour() and selected_p.get_name() != "p" and other_condition:
                old = selected_p.get_position()
                selected_p.change_pos(pos)
                if isCheck != False:
                    a_old = isCheck.get_position()
                    if (pos == isCheck.get_position()).all():
                        isCheck.change_pos(np.array([-1,-1]))
                Check = check(king_array[0],king_array[1],WhiteList,BlackList)
                selected_p.change_pos(old)
                if isCheck != False:
                    isCheck.change_pos(a_old)
                if Check != False and Check.get_colour() == selected_p.get_colour():
                    continue
                else:
                    draw(screen,surface,"r",pos)
                break
            elif output != 0 and output.get_colour() == selected_p.get_colour():
                break
            elif p_name == "p" and output != 0:
                break

    if p_name == "p":
        for attack in all_attack:
            surface = surface_creator()
            output = piece_at_that_point(attack,WhiteList,BlackList)
            if output == 0:
                pass
            elif output.get_colour() != selected_p.get_colour():
                old = selected_p.get_position()
                a_old = output.get_position()
                selected_p.change_pos(pos)
                output.change_pos(np.array([-1,-1]))
                Check = check(king_array[0],king_array[1],WhiteList,BlackList)
                selected_p.change_pos(old)
                output.change_pos(a_old)
                if Check != False and Check.get_colour() == selected_p.get_colour():
                    continue
                else:
                    draw(screen,surface,"r",attack)
    
    if selected_p.get_name() == "K" and selected_p.get_castle():
        p_pos = selected_p.get_position()
        for pos in np.array([[0,-2],[0,2]]):
            new_pos = pos+p_pos
                # output = check_line(selected_p,np.array([[[0,-1],[0,-2]]])+p_pos,new_pos,WhiteList,BlackList)
                # if piece_at_that_point(new_pos+np.array([0,-1]),WhiteList,BlackList):
                #     output = False
                # if piece_at_that_point(np.array([7,0]),WhiteList,BlackList) != 
            output = castle_checker(selected_p,new_pos,None,WhiteList,BlackList,True)
            if piece_at_that_point(new_pos,WhiteList,BlackList) == 0 and output:
                surface = surface_creator()
                draw(screen,surface,"c",new_pos)
                 
def surface_creator(alpha=25):
    surface = p.Surface((512,512),p.SRCALPHA)
    surface.set_colorkey(p.Color("White"))
    surface.set_alpha(alpha)
    return surface

def draw(screen,surface, r_or_c:str, pos):
    if r_or_c.lower() == "c":       
        p.draw.circle(surface,(0,0,0), (32 + (64*pos[1]),32 + (64*pos[0])), DIMENSION*1.5)
    elif r_or_c.lower() == "r":
        p.draw.rect(surface,(255,0,0),p.Rect(pos[1]*SQ_SIZE,pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    else:
        p.draw.rect(surface,(255,255,0),p.Rect(pos[1]*SQ_SIZE,pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    screen.blit(surface,(0,0))

def destroyed_p(attacked_p):
    if attacked_p != 0:
        attacked_p.change_pos(np.array([-100,-100]))

def move_piece(piece, to:list, board):
    old_pos = piece.get_position()
    piece.change_pos(to)
    old = board[old_pos[0]][old_pos[1]]
    board[to[0]][to[1]] = old
    board[old_pos[0]][old_pos[1]] = "--"
                
def piece_at_that_point(coord, w_list, b_list):
    piece = None
    for p in w_list+b_list:
        if (p.get_position() == coord).all():
            piece = p
            break   
    if piece !=None:
        return piece
    else:
        return 0
    
def check_line(selected_p,all_possible, to,w_list,b_list):
    choosen_dir = np.nonzero(((to == all_possible).all(axis= 2))*1)
    if choosen_dir[0].size == 0:
        return False
    for pos in all_possible[choosen_dir[0][0], 0: choosen_dir[1][0]+1]:
        output = piece_at_that_point(list(pos),w_list,b_list)
        if output != 0 and selected_p.get_colour() == output.get_colour():
            return False
        elif output != 0 and selected_p.get_colour() != output.get_colour() and not (to == output.get_position()).all(axis=0):
            return False
        else:
            continue
    return True

def valueDefiner(piece):
    if piece == False:
        return 
    p_info = piece.get_info()
    p_colour = piece.get_colour()
    p_pos = piece.get_position()
    p_name = piece.get_name()
    
    if p_name == "p":
        if (p_pos[0] == 6 and p_colour == Colour.w.value) or (p_pos[0] == 1 and p_colour == Colour.b.value):
            all_possible = p_pos + np.expand_dims(p_info[1],axis=1)*p_colour*np.arange(1,2).reshape(1,1)
        else:
            all_possible = p_pos + np.expand_dims(p_info[1][0:1],axis=1)*p_colour*np.arange(1,2).reshape(1,1)
        all_attack = p_pos + p_info[2]*p_colour*np.arange(1,2).reshape(1,1)
        all_attack = all_attack[(np.max(all_attack,axis=1) < 8) & (np.min(all_attack,axis=1) > -1)]
        return all_possible, all_attack
    
    elif p_name == "N" or p_name == "K":
        all_possible = p_pos + np.expand_dims(p_info[1],axis=1)*p_colour
        return all_possible,None
    
    else:
        all_possible = p_pos + np.expand_dims(p_info[1],axis=1)*np.arange(1,8).reshape(7,1)*p_colour
        return all_possible,None
    
def castle_checker(king,to, board,Whitelist,Blacklist,for_pos=False):
    if not king.get_castle():
        return king, board,0
    K_pos = king.get_position()
    dif = to[1] - K_pos[1]
    if dif > 0:
        R_pos = to + np.array([0,1])
    else:
        R_pos = to + np.array([0,-2])

    there  = False
    piece = piece_at_that_point(R_pos,Whitelist,Blacklist)
    if piece != 0 and piece.get_name() == "R" and piece.get_colour() == king.get_colour():
        there = True
    
    if there:
        if not piece.get_castle():
            return (king,board,0) if for_pos == False else False

        if dif < 0  and piece_at_that_point(to+np.array([0,-1]),Whitelist,Blacklist) != 0:
            return (king,board,0) if for_pos == False else False
        
        if dif<0:
            r_val = 3
            k_val = 2
        elif dif > 0:
            r_val = 5
            k_val = 6
        if board != None:
            piece.change_pos(np.array([R_pos[0],r_val]))
            king.change_pos(np.array([K_pos[0],k_val]))
            old = board[R_pos[0]][R_pos[1]]
            board[R_pos[0]][R_pos[1]] = "--"
            board[R_pos[0]][r_val] = old
            old = board[K_pos[0]][K_pos[1]]
            board[K_pos[0]][K_pos[1]] = "--"
            board[K_pos[0]][k_val] = old
        
        return (king,board,piece) if for_pos == False else True
    return (king,board,0) if for_pos == False else False

def check(wking, bking, WhiteList ,BlackList, piece_return=False):
    for king in [wking,bking]:
        if king == None:
            continue
        king_movs = king.get_info()[1]
        k_pos = king.get_position()
        for mov in king_movs:
            mov_num = mov*np.arange(1,8).reshape(7,1) + k_pos
            mov_num = mov_num[(np.max(mov_num,axis=1)<8) & (np.min(mov_num,axis=1)>-1)]
            for each in mov_num:
                output = piece_at_that_point(each,WhiteList,BlackList)
                if output != 0 and output.get_colour() != king.get_colour():
                    if ((mov == output.get_info()[1]).all(axis=1)).any() and output.get_name() != "p":
                        if output.get_name() == "K" and np.where(each == mov_num) == 0:
                            pass
                        elif output.get_name() == "K" and np.where(each == mov_num) != 0:
                            break
                        return king if not piece_return else output
                    elif output != 0  and output.get_name() == "p":
                        index_array = (each == mov_num).all(axis=1).nonzero()        
                                   
                        if ((mov == output.get_info()[2]).all(axis=1)).any() and len(index_array) == 1 and index_array[0] == 0:
                            return king if not piece_return else output
                        else:
                            break
                    else:
                        break
                elif output !=0 and output.get_colour() == king.get_colour():
                    break
        K_horse_check = type.N.value[1]+k_pos
        K_horse_check = K_horse_check[(np.max(K_horse_check,axis=1)<8) & (np.min(K_horse_check,axis=1)>-1)]
        for movs in K_horse_check:
            output = piece_at_that_point(movs,WhiteList,BlackList)
            if output != 0  and output.get_info() == type.N.value and output.get_colour() != king.get_colour():
                return king if not piece_return else output
            
    return False

def check_mate(w_king,b_king, whitelist, blacklist):
    w_check_m = False
    b_check_m = False
    output_arr = []
    for king in [w_king,b_king]:
        old = king.get_position()
        currently_check = check(king,b_king,whitelist,blacklist)
        if king == currently_check:
            new_pos = old + np.array([[[1,0]],[[1,1]],[[0,1]],[[-1,1]],[[-1,0]],[[-1,-1]],[[0,-1]],[[1,-1]]])
            for pos in new_pos:
                if (np.max(pos[0]) > 7).all() or (np.min(pos[0]) < 0).all():
                    continue
                if piece_at_that_point(pos,whitelist,blacklist) == 0:
                    king.change_pos(pos[0])
                    output = check(king,None,whitelist,blacklist)
                else:
                    output = None
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
        correct_self_list = np.array([whitelist,blacklist])[np.array([w_check_m,b_check_m])]
        attacking_p = check(check_array[0], None,whitelist,blacklist,True)
        attacking_p_movs,skip = valueDefiner(attacking_p)
        attacking_phile = get_attack_phile(check_array[0],attacking_p_movs,attacking_p.get_position())
        if attacking_phile.any() == False:
            return w_check_m,b_check_m
        for piece in correct_self_list[0]:
            to,piece_movs = move_to_attack_line(piece,attacking_phile,True)
            if to.size > 0:
                for movs in to:
                    if check_line(piece,piece_movs,movs,whitelist,blacklist):
                        if piece.get_name() == "K" and not (movs == attacking_p.get_position()).all():
                            break
                        if check_array[0] == w_king:
                            w_check_m = False
                        elif check_array[0] == b_king:
                            b_check_m = False
                    else:
                        break
    
    return w_check_m,b_check_m

def get_attack_phile(king, all_possible,p_pos):
    choosen_dir = np.nonzero(((king.get_position() == all_possible).all(axis=2))*1)
    if choosen_dir[0].size == 0:
        return np.array([-1,-1])
    attacking_movs = all_possible[choosen_dir[0][0], 0:choosen_dir[1][0]]
    attacking_movs = np.append(attacking_movs,p_pos)
    attacking_movs = attacking_movs.reshape((int(attacking_movs.shape[0]/2),2))
    return attacking_movs

def pawn_promotion(piece,screen,board,AI=False):
    if piece == None or piece == 0:
        return
    p_pos = piece.get_position()
    current_Colour = 0
    if piece.get_name() == "p" and p_pos[0] in [0,7]:
        current_Colour = 0
        if piece.get_colour() == Colour.w.value:
            current_Colour = Colour.w
        elif piece.get_colour() == Colour.b.value:
            current_Colour = Colour.b
    if current_Colour != 0:
        q_piece = p.transform.scale(p.image.load(f"chess_pngs/{current_Colour.name}Q.png"),(SQ_SIZE,SQ_SIZE))
        n_piece = p.transform.scale(p.image.load(f"chess_pngs/{current_Colour.name}N.png"),(SQ_SIZE,SQ_SIZE))
        if 7-p_pos[1] >= 3:
            p.draw.rect(screen,(250,250,250),p.Rect((p_pos[1]+1)*SQ_SIZE,p_pos[0]*SQ_SIZE,SQ_SIZE*2,SQ_SIZE))
            position_possible = p_pos + np.array([[0,1],[0,2]])
        else:
            p.draw.rect(screen,(250,250,250),p.Rect((p_pos[1]-2)*SQ_SIZE,p_pos[0]*SQ_SIZE,SQ_SIZE*2,SQ_SIZE))
            position_possible = p_pos + np.array([[0,-1],[0,-2]])
        running = True
        screen.blit(q_piece, p.Rect(position_possible[0,1]*SQ_SIZE,position_possible[0,0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        screen.blit(n_piece, p.Rect(position_possible[1,1]*SQ_SIZE,position_possible[1,0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
        p.display.update()
        while running:
            for e in p.event.get():
                if e.type == p.MOUSEBUTTONDOWN:
                    mouse_pos = p.mouse.get_pos()
                    col = mouse_pos[0]//SQ_SIZE
                    row = mouse_pos[1]//SQ_SIZE
                    index = np.where((position_possible == (row,col)).all(axis=1) == True)[0][0]
                    if index:
                        piece.change_type(type.N)
                        screen.blit(n_piece,p.Rect(p_pos[1]*SQ_SIZE,p_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
                        board[p_pos[0]][p_pos[1]] = f"{current_Colour.name}N"
                        running = False
                        break
                    else:
                        piece.change_type(type.Q) 
                        screen.blit(q_piece,p.Rect(p_pos[1]*SQ_SIZE,p_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
                        board[p_pos[0]][p_pos[1]] = f"{current_Colour.name}Q"
                        running = False
                        break

def move_to_attack_line(piece, attack_movs, p_pos_return=False):
    p_movs,all_attack = valueDefiner(piece)
    attack_movs = attack_movs.reshape(attack_movs.shape[0],1,1,attack_movs.shape[1])
    if piece.get_name() != "p":
        t_table = ((p_movs-attack_movs) == 0).all(axis=3)
        to = p_movs[t_table.any(axis=0)]
        if p_pos_return:
            return to,p_movs
        else:
            return to
    elif piece.get_name() == "p":
        all_attack = np.expand_dims(all_attack,axis=1)
        t_table = ((all_attack-attack_movs) == 0).all(axis=3)
        to = all_attack[t_table.any(axis=0)]
        t_table = ((p_movs-attack_movs[:-1]) == 0).all(axis=3)
        to_extended = p_movs[t_table.any(axis=0)]
        to = np.append(to,to_extended)
        to = to.reshape((int(to.shape[0]/2),2))
        if p_pos_return:
            return to,all_attack
        else:
            return to