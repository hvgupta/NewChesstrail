import random
from main_func import *
    

def randomPchooser(blacklist):
    return (random.choice(blacklist)).get_position()

def randomMovchooser(all_possible):
    return random.choice(all_possible)

def check_mov_chooser(w_king, b_king, whiteList, blackList):
    piece = check(w_king,b_king,whiteList,blackList,True)
    reduced_possible = []
    if piece == False:
        for b_piece in blackList:
            possible = False
            p_movs = b_piece.get_info()[1]
            p_pos = b_piece.get_position()
            for movs in p_movs:
                if np.max(movs+p_pos)>7 or np.min(movs+p_pos)<0:
                    continue
                output = piece_at_that_point(movs+p_pos,whiteList,blackList)
                if (output == 0 or output.get_colour() == Colour.w.value) and b_piece.get_name() != "p":
                    possible = True
                    break
                elif b_piece.get_name() == "p" and output == 0:
                    possible = True
                    break
            if b_piece.get_name() == "p":
                p_attacks = b_piece.get_info()[2]
                for atts in p_attacks:
                    if np.max(movs+p_pos)>7 or np.min(movs+p_pos)<0:
                        break
                    output = piece_at_that_point(atts+p_pos,whiteList,blackList)
                    if output != 0:
                        possible = True
                        break
            if possible:
                reduced_possible.append(b_piece)
    else:
        all_movs,skip = valueDefiner(piece)
        for b_piece in blackList:
            attacked_pos = get_attack_phile(b_king,all_movs,piece.get_position())
            if attacked_pos.any != False:
                pass
            else:
                continue
            to,p_pos = move_to_attack_line(b_piece,attacked_pos,True)
            if to.size > 0:
                for mov in to:
                    if check_line(b_piece,p_pos,mov,whiteList,blackList):
                        reduced_possible.append(b_piece)
                        break
    return randomPchooser(reduced_possible)