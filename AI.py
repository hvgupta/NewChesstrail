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
        for b_piece in blackList:
            attacked_pos = get_attack_phile(b_king,all_movs,piece.get_position())
            if attacked_pos.any != False:
                pass
            else:
                continue
            if b_piece.get_name() == "K":
                there = False
                piece_array = []
                bK_movs = b_piece.get_info()[1] + b_piece.get_position()
                bK_movs = bK_movs[(np.max(bK_movs,axis=1)<8)&(np.min(bK_movs,axis=1)>-1)]
                for movs in bK_movs:
                    moving_to = piece_at_that_point(movs,whiteList,blackList)
                    if (moving_to == 0 or moving_to.get_colour() != Colour.b.value) and check(None,b_king,whiteList,blackList) != b_king:
                        there = True
                        piece_array.append([movs-b_king.get_position()])
                if there:
                    reduced_possible.append(b_piece)
                    to_array.append(piece_array)   
            to,p_pos = move_to_attack_line(b_piece,attacked_pos,True)
            if to.size > 0:
                for mov in to:
                    if check_line(b_piece,p_pos,mov,whiteList,blackList):
                        reduced_possible.append(b_piece)
                        to_array.append([mov-b_piece.get_position()])
    piece_choosen = randomchooser(reduced_possible)
    # print(piece_choosen.get_name(), piece_choosen.get_position())
    piece_index = reduced_possible.index(piece_choosen)
    move_array = to_array[piece_index]
    mov_choosen = randomchooser(move_array) + piece_choosen.get_position()
    # print(mov_choosen)
    return piece_choosen,mov_choosen 