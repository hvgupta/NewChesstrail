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
    

def castle_checker(king,to, board,Whitelist,Blacklist):
    K_pos = king.get_position()
    dif = to[1] - K_pos[1]
    if not king.get_info()[2]:
        return king, board
    if dif > 0:
        R_pos = to+np.array([0,1])
    else:
        R_pos = to + np.array([0,-2])

    there  = False
    piece = piece_at_that_point(R_pos,Whitelist,Blacklist)
    if piece.get_name() == "R" and piece.get_colour() == king.get_colour():
        there = True
    
    if there:
        if not piece.get_info()[2]:
            return king,board
        
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
        
        
    # R_pos = rook.get_position()
    # K_pos = king.get_position()
    # if rook.get_info()[2] and king.get_info()[2]:
    #     dif = R_pos[1] - K_pos[1]
    #     if dif < 0:
    #         r_val = 3
    #         k_val = 2
    #         rook.change_pos(np.array([R_pos[0],r_val]))
    #         king.change_pos(np.array([K_pos[0],k_val]))
    #     elif dif > 0:
    #         r_val = 5
    #         k_val = 6
    #         rook.change_pos(np.array([R_pos[0],r_val]))
    #         king.change_pos(np.array([K_pos[0],k_val]))
        
    #     old = board[R_pos[0]][R_pos[1]]
    #     board[R_pos[0]][R_pos[1]] = "--"
    #     board[R_pos[0]][r_val] = old
    #     old = board[K_pos[0]][K_pos[1]]
    #     board[K_pos[0]][K_pos[1]] = "--"
    #     board[K_pos[0]][k_val] = old
    
    # return rook, king, board


def check(wking, bking, WhiteList ,BlackList):
    for king in [wking,bking]:
        king_movs = king.get_info()[1]
        k_pos = king.get_position()
        for mov in king_movs:
            mov_num = mov*np.arange(1,8).reshape(7,1) + k_pos
            mov_num = mov_num[(np.max(mov_num,axis=1)<8) & (np.min(mov_num,axis=1)>-1)]
            for each in mov_num:
                output = piece_at_that_point(each,WhiteList,BlackList)
                if output != 0 and output.get_colour() != king.get_colour():
                    if ((mov == output.get_info()[1]).all(axis=1)).any():
                        return king
                    elif output != 0  and output.get_name() == "p":
                        if ((mov == output.get_colour()).all(axis=1)).any():
                            return king
                        elif output.get_name() == "p" and ((mov == output.get_info()[2]).all(axis=1)).any():
                            return king
                elif output !=0 and output.get_colour() == king.get_colour():
                    break
            
    return False

def check_mate(king, whitelist, blacklist):
    # old_pos = king.get_position()
    # all_possible = valueDefiner(king)
    # all_possible = all_possible[(np.max(all_possible,axis=2)<8)&(np.min(all_possible,axis=2)>-1)]
    # for moves in all_possible:
    #     output = piece_at_that_point(moves,whitelist,blacklist)
    #     king.change_pos(moves[0])
    pass
        