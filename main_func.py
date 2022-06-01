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
    for w,b in zip(w_list,b_list):
        if (w.get_position() == coord).all():
            piece = w
            break
        elif (b.get_position() == coord).all():
            piece = b
            break
    if piece !=None:
        return piece
    else:
        return 0

def check_line(all_possible, to,w_list,b_list):
    choosen_dir = np.nonzero(((to == all_possible).all(axis= 2))*1)
    if choosen_dir[0].size == 0:
        return False
    for pos in all_possible[choosen_dir[0][0], 0: choosen_dir[1][0]]:
        output = piece_at_that_point(list(pos),w_list,b_list)
        if output != 0:
            return False
        else:
            continue
    return True


def valueDefiner(piece):
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
        return all_possible
    else:
        all_possible = p_pos + np.expand_dims(p_info[1],axis=1)*np.arange(1,8).reshape(7,1)*p_colour
        return all_possible
    

def castle_checker(rook, king, board, w_list, b_list):
    R_pos = rook.get_position()
    K_pos = king.get_position()
    if rook.get_info()[2] and king.get_info()[2]:
        dif = R_pos[1] - K_pos[1]
        if dif < 0:
            r_val = 3
            k_val = 2
            rook.change_pos(np.array([R_pos[0],r_val]))
            king.change_pos(np.array([K_pos[0],k_val]))
        elif dif > 0:
            r_val = 5
            k_val = 6
            rook.change_pos(np.array([R_pos[0],r_val]))
            king.change_pos(np.array([K_pos[0],k_val]))
        
        old = board[R_pos[0]][R_pos[1]]
        board[R_pos[0]][R_pos[1]] = "--"
        board[R_pos[0]][r_val] = old
        old = board[K_pos[0]][K_pos[1]]
        board[K_pos[0]][K_pos[1]] = "--"
        board[K_pos[0]][k_val] = old
    
    return rook, king, board

            