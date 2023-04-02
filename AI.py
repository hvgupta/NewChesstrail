import random
from Helper_func import *
from board import *

def pieces_which_can_move(White_pList,Black_pList, WhiteK, BlackK, colour):
    Piece_can_move = []
    for piece in (White_pList if colour == Colour.w.value else Black_pList):
        if piece.isDestroyed():
            continue
        all_moves,all_attack = movesReturn(piece)   
        legal_moves = position_shower(all_moves,White_pList,Black_pList,None,piece,[WhiteK,BlackK],all_attack if piece.get_name() == "p" else None,True)
        if legal_moves.size > 0:
            Piece_can_move.append([piece,legal_moves])
    return np.array(Piece_can_move)

def eval_func(w_allowed_piece_move_array, b_allowed_piece_move_array, White_pList, Black_pList) -> int:
    score = 0
    piece:Piece
    for piece, moves in b_allowed_piece_move_array:
        for move in moves:
            if piece_at_that_pos(move,White_pList,Black_pList) == 0:
                score += 0.5
            else:
                score += piece.get_info()["points"]
    for piece, moves in w_allowed_piece_move_array:
        for move in moves:
            if piece_at_that_pos(move,White_pList,Black_pList) != 0:
                score -= piece.get_info()["points"]
    
    return score

def AI_logic(White_pList, Black_pList, WhiteK, BlackK, depth, current_turn):
    if depth == 2:
        return 0
    move_array = pieces_which_can_move(White_pList,Black_pList,WhiteK,BlackK,current_turn)
    move_list = np.array([])
    ScoreList = np.array([])
    for piece,moves in move_array:
        old_p = piece.get_position()
        for move in moves:
            check_for_piece = piece_at_that_pos(move,White_pList if current_turn == Colour.b.value else Black_pList,None)
            if check_for_piece == 0:
                piece.change_pos(move)
            elif check_for_piece != 0:
                old = check_for_piece.get_position()
                piece.change_pos(move)
                destroyed_p(check_for_piece)
            score = eval_func(pieces_which_can_move(White_pList,Black_pList,WhiteK,BlackK,current_turn),move_array,White_pList,Black_pList)
            if check_for_piece != 0:
                check_for_piece.change_pos(old)
            move_list = np.append(move_list,{"piece": piece, "move": move})
            ScoreList = np.append(ScoreList, score)
        piece.change_pos(old_p)
    ind = np.argsort(ScoreList)
    if current_turn == Colour.w.value:
        ind = ind[:3]
    else:
        ind = ind[-3:]
    move_list = move_list[ind]
    ScoreList = ScoreList[ind]
    for move,Score in zip(move_list, ScoreList):
        any_piece = piece_at_that_pos(move["move"],White_pList, Black_pList)
        old = None
        p_old = move["piece"].get_position()
        if any_piece == 0:
            move["piece"].change_pos(move["move"])
        elif any_piece.get_name() != "K":
            move["piece"].change_pos(move["move"])
            old = any_piece.get_position()
            destroyed_p(any_piece)
        Score += AI_logic(White_pList,Black_pList,WhiteK,BlackK, depth+1, current_turn*-1)
        move["piece"].change_pos(p_old)
        if any_piece != 0:
            any_piece.change_pos(old)
        
    if depth == 0:
        return move_list,ScoreList
    return Score


def move_decider(White_pList, Black_pList, WhiteK, BlackK):
    moveList, scoreList = AI_logic(White_pList,Black_pList, WhiteK,BlackK,0,Colour.b.value)
    max_num = np.sum(scoreList)
    rand_num = random.random()*max_num
    truth_array = ((np.cumsum(scoreList) - rand_num) >= 0) == False
    index = np.count_nonzero(truth_array)
    return moveList[index]
    