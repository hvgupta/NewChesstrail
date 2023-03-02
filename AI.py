import random
from Helper_func import *
from board import *

# stockfish = Stockfish(r'V:\Harsh\Python\Chess\NewChesstrail\stockfish-11-win\Windows\stockfish_20011801_x64', depth=18, parameters={"Threads": 2, "Minimum Thinking Time": 30})

def randomchooser(blacklist):
    if blacklist == None:
        return None
    return random.choice(blacklist)
    
def check_mov_chooser(w_king, b_king, whiteList, blackList):
    piece = check(w_king,b_king,whiteList,blackList,True)
    reduced_possible, to_array = possible_movs_array(piece,blackList,whiteList,b_king)
    if reduced_possible ==None:
        return None,None
    piece_choosen = randomchooser(reduced_possible)
    piece_index = reduced_possible.index(piece_choosen)
    move_array = to_array[piece_index]
    mov_choosen = randomchooser(move_array) + piece_choosen.get_position()
    if len(mov_choosen.shape) == 2:
        mov_choosen = mov_choosen.reshape((2))
    return piece_choosen,mov_choosen 

def possible_movs_array(piece_checking,piece_list,enemy_list,p_king):
    reduced_possible = []
    to_array = []
    if piece_checking == False:
        for b_piece in piece_list:
            if (b_piece.get_position() == np.array([-100,-100])).all():
                continue
            possible = False
            p_movs = b_piece.get_info()[1]
            p_pos = b_piece.get_position()
            piece_array = []
            for movs in p_movs:
                if np.max(movs+p_pos)>7 or np.min(movs+p_pos)<0:
                    continue
                output = piece_at_that_pos(movs+p_pos,enemy_list,piece_list)
                b_piece.change_pos(movs+p_pos)
                returned = check(None,p_king,enemy_list,piece_list)
                b_piece.change_pos(p_pos)
                if (output == 0 or output.get_colour() == Colour.w.value) and b_piece.get_name() != "p" and returned == False:
                    possible = True
                    piece_array.append(movs)
                elif b_piece.get_name() == "p" and output == 0 and returned == False:
                    possible = True
                    piece_array.append(movs)
            if b_piece.get_name() == "p":
                p_attacks = b_piece.get_info()[2]
                for atts in p_attacks:
                    if np.max(atts+p_pos)>7 or np.min(atts+p_pos)<0:
                        break
                    output = piece_at_that_pos(atts+p_pos,enemy_list,piece_list)
                    b_piece.change_pos(atts+p_pos)
                    returned = check(None,p_king,enemy_list,piece_list)
                    b_piece.change_pos(p_pos)
                    if output != 0 and returned == False:
                        possible = True
                        piece_array.append(atts)
            if possible:
                reduced_possible.append(b_piece)
                to_array.append(piece_array)
    else:
        all_movs,skip = movesReturn(piece_checking)
        if piece_checking.get_name() !="p":
            attacked_pos = get_attack_line(p_king,all_movs,piece_checking.get_position())
        else:
            attacked_pos = get_attack_line(p_king,np.expand_dims(skip,axis=1),piece_checking.get_position())
        if (attacked_pos != np.array([-100,-100])).all():
            for b_piece in piece_list:
                if b_piece.get_name() == "K":
                    there = False
                    piece_array = []
                    bK_movs = b_piece.get_info()[1] + b_piece.get_position()
                    bK_movs = bK_movs[(np.max(bK_movs,axis=1)<8)&(np.min(bK_movs,axis=1)>-1)]
                    for movs in bK_movs:
                        if (movs == piece_checking.get_position()).all():
                            a_old = piece_checking.get_position()
                            k_pos = p_king.get_position()
                            destroyed_p(piece_checking)
                            p_king.change_pos(movs)
                            isCheck = check(None,p_king,piece_list,enemy_list)
                            p_king.change_pos(k_pos)
                            piece_checking.change_pos(a_old)
                            if isCheck != p_king:
                                there = True
                                piece_array.append(movs-p_king.get_position())
                        else:
                            moving_to = piece_at_that_pos(movs,enemy_list,piece_list)
                            if moving_to != 0 and moving_to.get_colour() == p_king.get_colour():
                                continue
                            k_attack_p = False
                            if moving_to != 0  and moving_to.get_colour() != p_king.get_colour():
                                a_old = moving_to.get_position()
                                destroyed_p(moving_to)
                                k_attack_p = True
                            old = b_piece.get_position()
                            b_piece.change_pos(movs)
                            isCheck = check(None,p_king,enemy_list,piece_list)
                            b_piece.change_pos(old)
                            if k_attack_p:
                                moving_to.change_pos(a_old)
                                    
                            if isCheck != p_king:
                                there = True
                                piece_array.append(movs-p_king.get_position())
                    if there:
                        reduced_possible.append(b_piece)
                        to_array.append(piece_array)
                else:   
                    to,p_pos = move_to_attack_line(b_piece,attacked_pos,True)
                    if b_piece.get_name() == "p":
                        there = False
                        move_array = []
                        for movs in to:
                            p_at_point = piece_at_that_pos(movs,enemy_list,piece_list)
                            if p_at_point != 0  and p_at_point.get_colour() == Colour.w.value and ((movs-b_piece.get_position() - b_piece.get_info()[2] == 0).all(axis=1).any()) == True:
                                move_array.append(movs-b_piece.get_position())
                                there = True
                            elif p_at_point == 0 and ((movs-b_piece.get_position() - b_piece.get_info()[2] == 0).all(axis=1).any()) == False:
                                move_array.append(movs-b_piece.get_position())
                                there = True
                        if there:
                            to_array.append(move_array)
                            reduced_possible.append(b_piece)

                    elif to.size > 0:
                        for mov in to:
                            if len(mov.shape) == 2:
                                mov = mov.reshape((2))
                            if check_line(b_piece,p_pos,mov,enemy_list,piece_list):
                                reduced_possible.append(b_piece)
                                to_array.append([mov-b_piece.get_position()])
    if len(reduced_possible) == 0:
        # possible_movs_array(piece_checking,piece_list,enemy_list,p_king)
        return None,None
    return reduced_possible,to_array
             
def board2fen(board, w_castle, b_castle):
    empty = 0
    fen = ""
    for row in board:
        for column in row:
            if column[0] == Colour.b.name:
                if empty != 0:
                    fen = fen + str(empty)
                    empty = 0
                fen = fen + column[1].lower()
            elif column[0] == Colour.w.name:
                if empty != 0:
                    fen = fen + str(empty)
                    empty = 0
                fen = fen + column[1].upper()
            elif column == '--':
                empty += 1
        if empty != 0:
            fen = fen + str(empty)
            empty = 0
        fen = fen + "/"
    fen = fen[:-1] + " b {castle} - 1 1" .format(castle= w_castle+b_castle)
    
    return fen

# def fen2move(fen):
#     stockfish.set_fen_position(fen)
#     move = stockfish.get_best_move()
#     return move

# c_board = Board()
# fen_string = board2fen(c_board.board, "","")
# print(fen2move(fen_string))