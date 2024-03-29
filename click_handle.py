import pygame as p
from board import *
from Helper_func import *
from Piece import *
from tkinter import Tk

#continue return 0
#else return 1

def FenInitialisation():
    p.init()
    p.font.init()
    start_screen = p.display.set_mode((IMGWIDTH,HEIGHT))
    start_screen.fill((0,0,0))
    base_font =  p.font.SysFont("monospace",16)
    input_fen = ''
    input_rect = p.Rect(0,200,500,50)
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                raise SystemExit
            elif e.type == p.KEYDOWN:
                if e.key == p.K_BACKSPACE:
                    input_fen = input_fen[:-1]
                elif e.key == p.K_RETURN:
                    running = False
                    break
                else:
                    if e.key == p.K_v and e.mod & p.KMOD_CTRL:
                        input_fen += Tk().clipboard_get()
                    else:
                        input_fen += e.unicode
        instruction_font = p.font.SysFont("monospace", 29)
        instruction_font.set_bold(5) 
        instruction1 = instruction_font.render("Enter a 'FEN' string", True, (255,255,255))
        instruction2 = instruction_font.render("or just enter to start a", True, (255,255,255))
        instruction3 = instruction_font.render("normal game", True, (255,255,255))
        p.draw.rect(start_screen, (255,255,255), input_rect)
        text_surface = base_font.render(input_fen, True, (0,0,0))
        start_screen.blit(text_surface, (input_rect.x+5, input_rect.y+5))
        start_screen.blit(instruction1, (0,50))
        start_screen.blit(instruction2, (0,90))
        start_screen.blit(instruction3, (0,130))
        p.display.update()
        
    return input_fen

def reset(sqSelected,player_click): # resets the sqSelected and player_click
    sqSelected = ()
    player_click = []
    return sqSelected,player_click

def first_click(cBoard:Board, current_turn, screen, whiteKing: Piece, blackKing: Piece,player_click):
    selected_p = cBoard.piece_at_that_pos(np.array(player_click[0])) 
    if selected_p == EMPTY_POS or selected_p.get_colour() != current_turn:
    # resets player click if the clicked tile is empty or of the wrong colour
        return False,0,0
    
    all_possible, all_attack = movesReturn(selected_p) #gives all the moves possible legal and illegal
    #shows those positions accoring to all the legal moves
    if selected_p.get_name() != "p":
        legal_moves = returnValidPos(all_possible,cBoard,screen,selected_p,[whiteKing,blackKing]) 
    elif selected_p.get_name() == "p":
        legal_moves = returnValidPos(all_possible.reshape((all_possible.shape[1],all_possible.shape[0],2)),cBoard,screen,selected_p,[whiteKing,blackKing],all_attack)
    
    return True, selected_p ,legal_moves

def second_click(c_board:Board,legal_moves: np.ndarray, selected_p: Piece, sqSelected,player_click):
    if not (legal_moves.size != 0 and (legal_moves == player_click[1]).all(axis=1).any()):
        return 0
            
    attacked_p: Piece = c_board.piece_at_that_pos(np.array(player_click[1])) #gives the positon information for the position being moved 
    if selected_p.get_name() == "p":
        if selected_p.K_from_en_passant:
            selected_p.change_en_passant(False)
        elif abs(player_click[0][0] - player_click[1][0]) == 2:
            selected_p.change_en_passant(True) 
        elif abs(player_click[0][0] - player_click[1][0]) == 1:
            selected_p.change_en_passant(False)
    
    if selected_p.get_name() == "K" and abs(player_click[1][1] - player_click[0][1]) == 2: #checks for the castle condition
        castle_valid = castle_checker(selected_p, np.array(player_click[1]),c_board)
        if not castle_valid:
            return 0
        rook_xcoord = 0 if player_click[1][1] - player_click[0][1] == -2 else 7
        rook = c_board.piece_at_that_pos(np.array([player_click[1][0],rook_xcoord]))
        rook_to_pos = np.array([player_click[1][0],3]) if player_click[1][1] - player_click[0][1] == -2 else np.array([player_click[1][0],5])
        c_board.move_piece(selected_p,np.array(np.array(player_click[1])))
        c_board.move_piece(rook,rook_to_pos)

    elif attacked_p == EMPTY_POS: #if the piece is moving to an empty space
        c_board.move_piece(selected_p, np.array(sqSelected))
        check_for_en_passant = c_board.piece_at_that_pos((np.array([sqSelected]) - np.array([selected_p.get_colour(),0]))[0])
        if check_for_en_passant != 0 and selected_p.get_name() == "p":
            change_pos(check_for_en_passant,None,c_board.PieceonBoard,True)
            c_board.move_piece("--",( np.array([sqSelected]) - np.array([selected_p.get_colour(),0])).reshape((2)))

    elif attacked_p != EMPTY_POS:# if the piece is moving to a space which is occupied by the opposite team
        c_board.move_piece(selected_p,np.array(sqSelected))
        change_pos(attacked_p,None,c_board.PieceonBoard,True)

    return 1
        