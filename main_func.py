import numpy as np
from type_enum import *


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
        all_attack = p_pos + p_info[2]*p_colour
        all_attack = all_attack[(np.max(all_attack,axis=1) < 8) & (np.min(all_attack,axis=1) > -1)]
        return all_possible, all_attack
    
    elif p_name == "N" or p_name == "K":
        all_possible = p_pos + np.expand_dims(p_info[1],axis=1)*p_colour
        return all_possible,None
    
    else:
        all_possible = p_pos + np.expand_dims(p_info[1],axis=1)*np.arange(1,8).reshape(7,1)*p_colour
        return all_possible,None
    
def castle_checker(king,to, board,Whitelist,Blacklist):
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
            return king,board,0

        if dif < 0  and piece_at_that_point(to+np.array([0,-1]),Whitelist,Blacklist) != 0:
            return king,board,0
        
        if dif<0:
            r_val = 3
            k_val = 2
        elif dif > 0:
            r_val = 5
            k_val = 6
        
        piece.change_pos(np.array([R_pos[0],r_val]))
        king.change_pos(np.array([K_pos[0],k_val]))
        old = board[R_pos[0]][R_pos[1]]
        board[R_pos[0]][R_pos[1]] = "--"
        board[R_pos[0]][r_val] = old
        old = board[K_pos[0]][K_pos[1]]
        board[K_pos[0]][K_pos[1]] = "--"
        board[K_pos[0]][k_val] = old
        
        return king, board,piece
    return king, board, 0

def check(wking, bking, WhiteList ,BlackList, piece_return=False):
    for king in [wking,bking]:
        if king == None:
            break
        king_movs = king.get_info()[1]
        k_pos = king.get_position()
        for mov in king_movs:
            mov_num = mov*np.arange(1,8).reshape(7,1) + k_pos
            mov_num = mov_num[(np.max(mov_num,axis=1)<8) & (np.min(mov_num,axis=1)>-1)]
            for each in mov_num:
                output = piece_at_that_point(each,WhiteList,BlackList)
                if output != 0 and output.get_colour() != king.get_colour():
                    if ((mov == output.get_info()[1]).all(axis=1)).any():
                        return king if not piece_return else output
                    elif output != 0  and output.get_name() == "p":
                        if ((mov == output.get_info()[2]).all(axis=1)).any():
                            return king if not piece_return else output
                        elif output.get_name() == "p" and ((mov == output.get_info()[2]).all(axis=1)).any():
                            return king if not piece_return else output
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
                    output = check(w_king,b_king,whitelist,blacklist)
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
        choosen_dir = np.nonzero(((check_array[0].get_position() == attacking_p_movs).all(axis= 2))*1)
        if choosen_dir[0].size == 0:
            return w_check_m,b_check_m
        attacking_p_movs = attacking_p_movs[choosen_dir[0][0], 0:choosen_dir[1][0]]
        attacking_p_movs = np.append(attacking_p_movs,attacking_p.get_position())
        attacking_p_movs = attacking_p_movs.reshape((int(attacking_p_movs.shape[0]/2),2))
        for piece in correct_self_list[0]:
            if piece.get_name() in ["p"] :
                continue
            piece_movs, skip = valueDefiner(piece)
            value_data = ((piece_movs - attacking_p_movs.reshape(attacking_p_movs.shape[0],1,1,attacking_p_movs.shape[1]) == 0).all(axis=3))
            to = piece_movs[value_data.any(axis=0)]
            if value_data.any():
                if len(to.shape) == 1:
                    if check_line(piece,piece_movs,to,whitelist,blacklist):
                        if check_array[0] == w_king:
                            w_check_m = not w_check_m
                        elif check_array[0] == b_king:
                            b_check_m = not b_check_m
                        break
                elif len(to.shape) > 1:
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
        