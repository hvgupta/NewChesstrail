from Helper_func import *
from board import *

# implement array which is changed only when needed, no need the redundancy

c:dict = {'C':2, "numberOfRuns": 100}

DEPTH = 3

def original_state(White_pList: list[Piece],Black_pList: list[Piece], WhiteK: Piece, BlackK: Piece, colour: Colour)-> tuple:
    # initialise the Piece_can_move and moves (based on the each turn)
    Piece_can_move = []
    moves = []
    colour_choosen_list = White_pList if colour == Colour.w.value else Black_pList
    for piece in colour_choosen_list:
        if piece.isDestroyed():
            continue
        all_moves,all_attack = movesReturn(piece)   
        legal_moves = returnValidPos(all_moves,White_pList,Black_pList,None,piece,[WhiteK,BlackK],all_attack if piece.get_name() == "p" else None,True)
        if legal_moves.size > 0:
            Piece_can_move.append(piece)
            moves.append(legal_moves)
    return Piece_can_move, moves

def PieceArray(P_list: list[Piece]): # returns encoded array of that colour (Piece list has the colour indication)
    informationArray = np.zeros((8,8))
    for piece in P_list:
        if piece.isDestroyed(): continue
        informationArray[tuple(piece.get_position())] = piece.get_info()["points"]
    return informationArray

"""
how to update
I) loop for initial position 
    1) check if the position is not empty, otherwise continue
    2) check if it is not a pawn
        i) only update if the basic move condition is satisfied
    3) check colour
        if same colour (if statement implies can only be pawn) 
        i) only update when move condition is satisfied
        if opposite colour
        ii) update when en passant, attack or move condition is satisfied
    4) knight loop
        i) if it is a knight, then update
        
II) loop for final position
    the same loop as (I) but also make sure of duplicates 
"""

def PieceUpdate(selected_p: Piece, move: np.ndarray, white_pList: list[Piece], black_pList: list[Piece])->list:
    pieceToUpdate = []
    direction_move = PieceType.K.value["moves"]
    direction_move = np.expand_dims(direction_move,axis=1)
    multiple = np.arange(1,8).reshape((7,1))
    
    p_old = selected_p.get_position()
    for case in [selected_p.get_position(), move]: # 2 cases to check for pieces to update, at the pos of the piece and at the position the piece is being moved to
        selected_p.change_pos(case) # move the piece to that position 
        moves_to_consider = (direction_move*multiple) + case # all the 8 directions check
        knightMoves = PieceType.N.value["moves"] + case # knight check
        knightMoves = knightMoves[(np.max(knightMoves,axis=1)<8) & (np.min(knightMoves,axis=1)>-1)] # since there are no multiples, knight moves can already be simplified 
        
        for moves in moves_to_consider: # first the 8 directions test 
            moving = moves[(np.max(moves,axis=1)<8) & (np.min(moves,axis=1)>-1)] # remove the coords which are outside the board
            for move in moving:
                
                whichPiece = piece_at_that_pos(move, white_pList, black_pList)
                if whichPiece == EMPTY_POS: # if the piece is empty then continue
                    continue
                
                elif whichPiece.get_name() != "p":
                    if (((moves[0]-case) == whichPiece.get_info()["moves"]).all(axis=1)).any(): # if the piece has the same basic movement as how it was approached, (can the piece move the in the same direction as the base move)
                        pieceToUpdate.append(whichPiece)
                
                elif whichPiece.get_colour() == selected_p.get_colour(): # if the piece is a pawn and of the same colour
                    if ((-1*(moves[0]-case) == whichPiece.get_info()["moves"]).all(axis=1)).any(): # only if the movement is in the same direction
                        pieceToUpdate.append(whichPiece)
                
                else: # if a pawn and not the same colour
                    if ((-1*(moves[0]-case) == whichPiece.get_info()["moves"]).all(axis=1)).any(): # check if the way is it approached is opposite to pawn's moves
                        pieceToUpdate.append(whichPiece)
                    elif ((-1*(moves[0]-case) == whichPiece.get_info()["attack"]).all(axis=1)).any(): # check if the way it is approached is opposite to pawn's attack
                        pieceToUpdate.append(whichPiece)
                    if (((moves[0]-case) == [ [0,1], [0,-1] ]).all(axis=1)).any(): # check for en PAAAAAASSSSSSSSSSSSSAAAAAAAAAAAAAANNNNNNNNTTTT
                        pieceToUpdate.append(whichPiece)
                break
        
        for Nmoves in knightMoves: # check for knight moves
            whichPiece = piece_at_that_pos(Nmoves, white_pList, black_pList)
            if whichPiece.get_name() == "N":
                pieceToUpdate.append(whichPiece)
    
    selected_p.change_pos(p_old)
    
    return list(dict.fromkeys(pieceToUpdate)) # remove duplicates and return
    
def pieces_which_can_move(White_pList: list[Piece],Black_pList: list[Piece], piece: Piece, whiteK:Piece, blackK: Piece, original: np.ndarray, pieceCanMove:list, moves:list):
    pieceToUpdate = PieceUpdate(piece,original,White_pList,Black_pList)
    for piece in pieceToUpdate:
        if piece in pieceCanMove:
            piece_index = pieceCanMove.index(piece)
            all_possible, all_attack = movesReturn(piece)
            moves[piece_index] = returnValidPos(all_possible,White_pList, Black_pList, None, piece, [whiteK, blackK], all_attack if piece.get_name() == "p" else None, True)
        else:
            pieceCanMove.append(piece)
            moves.append(returnValidPos(all_possible,White_pList, Black_pList, None, piece, [whiteK, blackK], all_attack if piece.get_name() == "p" else None, True))
    # choosen_list = White_pList if colour == Colour.w.value else Black_pList
    # p_pos = np.array([])
    # for choosen_piece in choosen_list:
    #     p_pos = np.concatenate((p_pos, choosen_piece.get_position()))
    # p_pos = p_pos.reshape((int(p_pos.size/2),2))
    # p_pos= p_pos.astype(int)
    # diff_from_original = p_pos - original
    # diff_from_new = p_pos - piece.get_position()
    # all_moves_to_consider = np.concatenate((PieceType.K.value["moves"], PieceType.N.value["moves"]))
    # # all_moves_to_consider = np.expand_dims(all_moves_to_consider,axis=1)
    # shape = all_moves_to_consider.shape
    # test = np.broadcast_to(all_moves_to_consider, (shape[0],diff_from_original.shape[0],2))
    
    # divided_array = (np.dot(diff_from_original, all_moves_to_consider)*np.dot(diff_from_original, all_moves_to_consider) == np.dot(diff_from_original, diff_from_original)* np.dot(all_moves_to_consider, all_moves_to_consider))
    # divided_array = divided_array.astype(int)
    # divided_array
    
    # colour_choosen_list = White_pList if colour == Colour.w.value else Black_pList
    # for piece in colour_choosen_list:
    #     if piece.isDestroyed():
    #         continue
    #     all_moves,all_attack = movesReturn(piece)   
    #     legal_moves = position_shower(all_moves,White_pList,Black_pList,None,piece,[WhiteK,BlackK],all_attack if piece.get_name() == "p" else None,True)
    #     if legal_moves.size > 0:
    #         Piece_can_move.append(piece)
    #         moves.append(legal_moves)
    # return Piece_can_move, moves
    
def eval_func(W_position_array, B_position_array, W_allowed_piece:list, B_allowed_piece:list, colour:Colour):
    score = 0
    W_move_array = np.array([val for lst in W_allowed_piece[1] for val in lst])
    B_move_array = np.array([val for lst in B_allowed_piece[1] for val in lst])
    (cur_side, cur_moves, enemy_side, enemy_moves) = (W_position_array, W_move_array, B_position_array, B_move_array) if colour == Colour.w.value else (B_position_array, B_move_array, W_position_array, W_move_array)
    cur_moves = cur_moves.astype(int)
    cur_side_sum = enemy_side[tuple(cur_moves.T)]
    score += np.sum(cur_side_sum)
    enemy_moves = enemy_moves.astype(int)
    enemy_side_sum = cur_side[tuple(enemy_moves.T)]
    score -= np.sum(enemy_side_sum)
    return score
    
def AI_logic(White_pList: list[Piece], Black_pList: list[Piece], WhiteK: Piece, BlackK: Piece, depth: int, current_turn: Colour):
    if depth == 2:
        return 0
    move_array = pieces_which_can_move(White_pList,Black_pList,WhiteK,BlackK,current_turn)
    move_list = np.array([])
    ScoreList = np.array([])
    for piece,moves in zip(move_array[0],move_array[1]):
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

def move_chooser(piece:Piece, all_moves: np.ndarray[int], White_pList: list[Piece], Black_pList: list[Piece], WhiteK: Piece, Black: Piece, current_turn: int, cur_turn_piece_move):
    index = -1
    val = -np.inf
    p_old_pos = piece.get_position()
    for i in range(all_moves.shape[0]):
        move = all_moves[i]
        piece.change_pos(move)
        W_move = PieceArray(White_pList)
        B_move = PieceArray(Black_pList)
        if current_turn == Colour.w.value:
            B_P_list = pieces_which_can_move(White_pList, Black_pList, WhiteK, Black, Colour.w.value,piece, p_old_pos)
            score = eval_func(W_move, B_move, cur_turn_piece_move, B_P_list, current_turn)
        else:
            W_P_list = pieces_which_can_move(White_pList, Black_pList, WhiteK, Black, Colour.b.value,piece, p_old_pos)
            score = eval_func(W_move, B_move, W_P_list, cur_turn_piece_move, current_turn)
        if score > val:
            index = i
            val = score
    piece.change_pos(p_old_pos)
    return all_moves[index]

def alpha_beta(White_pList: list[Piece], Black_pList: list[Piece], whiteK:Piece, blackK:Piece, current_turn: int, alpha:int, beta:int, depth:int):
    cur_colour_p = original_state(White_pList, Black_pList, whiteK, blackK, current_turn) 
    if depth == 0 or len(cur_colour_p[0]) == 0:
        W_array = PieceArray(White_pList)
        B_array = PieceArray(Black_pList)
        opposite_colour_p = pieces_which_can_move(White_pList, Black_pList, whiteK, blackK, current_turn*-1)
        score = eval_func(W_array, B_array, cur_colour_p if current_turn == Colour.w.value else opposite_colour_p, cur_colour_p if current_turn == Colour.b.value else opposite_colour_p, current_turn)
        return score

    move_array = []
    # in this case black will be the maximiser and white will be the minimiser 
    for index in range(len(cur_colour_p[0])):
        piece: Piece = cur_colour_p[0][index]
        piece_old_pos = piece.get_position()
        cur_moves = cur_colour_p[1][index]
        move = move_chooser(piece, cur_moves,White_pList, Black_pList, whiteK, blackK,current_turn, cur_colour_p)
        move_array.append(move)
        piece.change_pos(move)
        score = alpha_beta(White_pList, Black_pList, whiteK, blackK, current_turn*-1, alpha, beta, depth-1)
        returnScore = 0
        
        if current_turn == Colour.b.value: # checks if currently it is black's turn
            returnScore = max(-np.inf, score)
            alpha = max(alpha, score)
        else: # otherwise it is white's turn
            returnScore = min(np.inf, score)
            beta = min(beta, score)
            
        piece.change_pos(piece_old_pos)
        if beta <= alpha:
            break
    return returnScore if depth != DEPTH else [cur_colour_p[0][index], move_array[index]]       

def move_decider(White_pList, Black_pList, WhiteK, BlackK):
    output = alpha_beta(White_pList, Black_pList, WhiteK, BlackK, Colour.b.value, -np.inf, np.inf, DEPTH)
    # moveList, scoreList = AI_logic(White_pList,Black_pList, WhiteK,BlackK,0,Colour.b.value)
    # max_num = np.sum(scoreList)
    # rand_num = random.random()*max_num
    # truth_array = ((np.cumsum(scoreList) - rand_num) >= 0) == False
    # index = np.count_nonzero(truth_array)
    return {"piece": output[0], "move": output[1]}
    