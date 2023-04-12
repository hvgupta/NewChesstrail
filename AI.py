import random
from Helper_func import *
from board import *

WEIGHT = 1
BIAS = 0.5

def PieceArray(P_list: list[Piece]):
    informationArray = np.zeros((8,8))
    for piece in P_list:
        if piece.isDestroyed(): continue
        informationArray[tuple(piece.get_position())] = piece.get_info()["points"]*WEIGHT
    return informationArray

def pieces_which_can_move(White_pList: list[Piece],Black_pList: list[Piece], WhiteK: Piece, BlackK: Piece, colour: Colour):
    Piece_can_move = []
    colour_choosen_list = White_pList if colour == Colour.w.value else Black_pList
    for piece in colour_choosen_list:
        if piece.isDestroyed():
            continue
        all_moves,all_attack = movesReturn(piece)   
        legal_moves = position_shower(all_moves,White_pList,Black_pList,None,piece,[WhiteK,BlackK],all_attack if piece.get_name() == "p" else None,True)
        if legal_moves.size > 0:
            Piece_can_move.append([piece,legal_moves])
    return Piece_can_move
    

def eval_func(W_position_array, B_position_array, W_allowed_piece, B_allowed_piece, colour:Colour):
    score = 0
    W_move_array = np.concatenate(np.array(W_allowed_piece).T[1])
    B_move_array = np.concatenate(np.array(B_allowed_piece).T[1]) 
    (cur_side, cur_moves, enemy_side, enemy_moves) = (W_position_array, W_move_array, B_position_array, B_move_array) if colour == Colour.w.value else (B_position_array, B_move_array, W_position_array, W_move_array)
    cur_moves = cur_moves.astype(int)
    cur_side_sum = enemy_side[tuple(cur_moves.T)] + BIAS
    score += np.sum(cur_side_sum)
    enemy_moves = enemy_moves.astype(int)
    enemy_side_sum = cur_side[tuple(enemy_moves.T)] + BIAS
    score -= np.sum(enemy_side_sum)
    return score
    
def AI_logic(White_pList: list[Piece], Black_pList: list[Piece], WhiteK: Piece, BlackK: Piece, depth: int, current_turn: Colour):
    if depth == 2:
        return 0
    move_array = pieces_which_can_move(White_pList,Black_pList,WhiteK,BlackK,current_turn)
    move_list = np.array([])
    ScoreList = np.array([])
    for piece,moves in move_array:
        old_p = piece.get_position()
        for move in moves:
            check_for_piece = piece_at_that_pos(move, White_pList if current_turn == Colour.b.value else Black_pList,None)
            if check_for_piece == EMPTY_POS:
                piece.change_pos(move)
            elif check_for_piece != EMPTY_POS:
                old = check_for_piece.get_position()
                piece.change_pos(move)
                destroyed_p(check_for_piece)
            W_position_array = PieceArray(White_pList)
            B_position_array = PieceArray(Black_pList)
            Cur_colour = pieces_which_can_move(White_pList, Black_pList, WhiteK, BlackK, current_turn)
            opposite_colour = pieces_which_can_move(White_pList,Black_pList,WhiteK,BlackK,current_turn*-1)
            score = eval_func(W_position_array, B_position_array, opposite_colour, Cur_colour, current_turn)
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
    move_list: np.ndarray[dict[str, Piece], dict[str,np.ndarray]]= move_list[ind]
    ScoreList: list[int] = ScoreList[ind]
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
    