import random
from main_func import *
    

def randomchooser(blacklist):
    return random.choice(blacklist)
    
def check_mov_chooser(w_king, b_king, whiteList, blackList):
    piece = check(w_king,b_king,whiteList,blackList,True)
    reduced_possible = []
    to_array = []
    if piece == False:
        for b_piece in blackList:
            if (b_piece.get_position() == np.array([-1,-1])).all():
                continue
            possible = False
            p_movs = b_piece.get_info()[1]
            p_pos = b_piece.get_position()
            piece_array = []
            for movs in p_movs:
                if np.max(movs+p_pos)>7 or np.min(movs+p_pos)<0:
                    continue
                output = piece_at_that_point(movs+p_pos,whiteList,blackList)
                if (output == 0 or output.get_colour() == Colour.w.value) and b_piece.get_name() != "p":
                    possible = True
                    piece_array.append(movs)
                elif b_piece.get_name() == "p" and output == 0:
                    possible = True
                    piece_array.append(movs)
            if b_piece.get_name() == "p":
                p_attacks = b_piece.get_info()[2]
                for atts in p_attacks:
                    if np.max(movs+p_pos)>7 or np.min(movs+p_pos)<0:
                        break
                    output = piece_at_that_point(atts+p_pos,whiteList,blackList)
                    if output != 0:
                        possible = True
                        piece_array.append(atts)
            if possible:
                reduced_possible.append(b_piece)
                to_array.append(piece_array)
    else:
        all_movs,skip = valueDefiner(piece)
        if piece.get_name() !="p":
            attacked_pos = get_attack_phile(b_king,all_movs,piece.get_position())
        else:
            attacked_pos = get_attack_phile(b_king,np.expand_dims(skip,axis=1),piece.get_position())
        if (attacked_pos != np.array([-1,-1])).all():
            for b_piece in blackList:
                if b_piece.get_name() == "K":
                    there = False
                    piece_array = []
                    bK_movs = b_piece.get_info()[1] + b_piece.get_position()
                    bK_movs = bK_movs[(np.max(bK_movs,axis=1)<8)&(np.min(bK_movs,axis=1)>-1)]
                    for movs in bK_movs:
                        if (movs == piece.get_position()).all():
                            a_old = piece.get_position()
                            destroyed_p(piece)
                            moving_to = piece_at_that_point(movs,whiteList,blackList)
                            piece.change_pos(a_old)
                        else:
                            moving_to = piece_at_that_point(movs,whiteList,blackList)
                            isCheck = check(None,b_king,whiteList,blackList)
                            if (moving_to == 0 or moving_to.get_colour() != Colour.b.value) and isCheck != b_king:
                                there = True
                                piece_array.append(movs-b_king.get_position())
                    if there:
                        reduced_possible.append(b_piece)
                        to_array.append(piece_array)   
                to,p_pos = move_to_attack_line(b_piece,attacked_pos,True)
                if b_piece.get_name() == "p":
                    there = False
                    move_array = []
                    for movs in to:
                        p_at_point = piece_at_that_point(movs,whiteList,blackList)
                        if p_at_point != 0  and p_at_point.get_colour() == Colour.w.value:
                            move_array.append(movs-b_piece.get_position())
                            there = True
                        elif p_at_point == 0 and ((movs-b_piece.get_position() - b_piece.get_info()[2] == 0).all(axis=1).any()) == False:
                            move_array.append(movs-b_piece.get_position())
                            there = True
                    if there:
                        to_array.append(move_array)
                        reduced_possible.append(b_piece)

                if to.size > 0 and not b_piece.get_name() in ["K","p"]:
                    for mov in to:
                        if len(mov.shape) == 2:
                            mov = mov.reshape((2))
                        if check_line(b_piece,p_pos,mov,whiteList,blackList):
                            reduced_possible.append(b_piece)
                            to_array.append([mov-b_piece.get_position()])
    if len(reduced_possible) == 0:
        return None,None
    piece_choosen = randomchooser(reduced_possible)
    piece_index = reduced_possible.index(piece_choosen)
    move_array = to_array[piece_index]
    mov_choosen = randomchooser(move_array) + piece_choosen.get_position()
    if len(mov_choosen.shape) == 2:
        mov_choosen = mov_choosen.reshape((2))
    return piece_choosen,mov_choosen 