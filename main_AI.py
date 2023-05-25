import pygame as p
from board import *
from AI import *

def main(fen = ""):
    screen = p.display.set_mode((WIDTH,HEIGHT))
    screen.fill(p.Color("white"))
    c_board = Board()
    White_pList, Black_pList = c_board.initialise(c_board.board)
    loadImages()
    running = True
    current_turn = Colour.w.value
    sqSelected = ()
    player_click = []
    def reset(sqSelected,player_click): # resets the sqSelected and player_click
        sqSelected = ()
        player_click = []
        return sqSelected,player_click

    whiteKing = White_pList[12]
    blackKing = Black_pList[4]
    HUMAN = Colour.w.value
    AI = Colour.b.value
    selected_p = Piece
    w_checkMated = False
    b_checkMated = False
    
    while running:
        
        if current_turn == HUMAN:
            for e in p.event.get():
                
                if e.type == p.QUIT:
                    running = False
                
                elif e.type == p.MOUSEBUTTONDOWN :
                    
                    p.display.update()
                    location = p.mouse.get_pos()
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col):
                        sqSelected,player_click=reset(sqSelected,player_click)
                    else:   
                        sqSelected = (row,col)
                        player_click.append(sqSelected)
            
        elif current_turn == AI:

            move = move_decider(White_pList,Black_pList, whiteKing, blackKing)
            player_click = [tuple(move["piece"].get_position()),tuple(move["move"])]
            selected_p = piece_at_that_pos(player_click[0],White_pList, Black_pList)
            sqSelected = tuple(move["move"])
            print("{piece} : {From} -> {to}".format(piece= selected_p.get_name(), From= player_click[0], to= player_click[1]))
        
        gameState(screen,c_board.board)
        isCheck = check(whiteKing,blackKing,White_pList,Black_pList)
        if isCheck != False:
            if isCheck.get_colour() == Colour.w.value:
                w_checkMated = check_mate(isCheck, White_pList, Black_pList)
            else:
                b_checkMated = check_mate(isCheck, White_pList, Black_pList)
                
        if len(player_click) == 1:
            
            selected_p = piece_at_that_pos(player_click[0],White_pList,Black_pList) 
            if selected_p == EMPTY_POS or selected_p.get_colour() != current_turn:
                sqSelected,player_click=reset(sqSelected,player_click) # resets player click if the clicked tile is empty or of the wrong colour
                continue
            
            all_possible, all_attack = movesReturn(selected_p) #gives all the moves possible legal and illegal
            #shows those positions accoring to all the legal moves
            if selected_p == EMPTY_POS:
                continue
            elif selected_p.get_name() != "p":
                legal_moves = position_shower(all_possible,White_pList,Black_pList,screen,selected_p,[whiteKing,blackKing]) 
            else:
                legal_moves = position_shower(all_possible.reshape((all_possible.shape[1],all_possible.shape[0],2)),White_pList,Black_pList,screen,selected_p,[whiteKing,blackKing],all_attack)
        
        elif len(player_click) == 2:

            if not (legal_moves.size != 0 and (legal_moves == player_click[1]).all(axis=1).any()) and current_turn != AI:
                sqSelected,player_click = reset(sqSelected,player_click)
                continue
            attacked_p = piece_at_that_pos(player_click[1],White_pList,Black_pList) #gives the positon information for the position being moved 
            if selected_p.get_name() == "p" and abs(player_click[0][0] - player_click[1][0]) == 2:
                selected_p.change_en_passant(True) 
            elif selected_p.get_name() == "p" and abs(player_click[0][0] - player_click[1][0]) == 1:
                selected_p.change_en_passant(False)
            
            if selected_p.get_name() == "K" and abs(player_click[1][1] - player_click[0][1]) == 2: #checks for the castle condition
                castle_valid = castle_checker(selected_p, np.array(player_click[1]),White_pList,Black_pList)
                if not castle_valid:
                    continue
                rook_xcoord = 0 if player_click[1][1] - player_click[0][1] == -2 else 7
                rook = piece_at_that_pos(np.array([player_click[1][0],rook_xcoord]),White_pList,Black_pList)
                rook_to_pos = np.array([player_click[1][0],3]) if player_click[1][1] - player_click[0][1] == -2 else np.array([player_click[1][0],5])
                c_board.move_piece(selected_p,np.array(np.array(player_click[1])))
                c_board.move_piece(rook,rook_to_pos)

            elif attacked_p == EMPTY_POS: #if the piece is moving to an empty space
                c_board.move_piece(selected_p, np.array(sqSelected))
                check_for_en_passant = piece_at_that_pos(np.array([sqSelected]) - np.array([selected_p.get_colour(),0]), White_pList, Black_pList)
                if check_for_en_passant != 0 and selected_p.get_name() == "p":
                    destroyed_p(check_for_en_passant)
                    c_board.move_piece("--",( np.array([sqSelected]) - np.array([selected_p.get_colour(),0])).reshape((2)))

            elif attacked_p != EMPTY_POS:# if the piece is moving to a space which is occupied by the opposite team
                c_board.move_piece(selected_p,np.array(sqSelected))
                destroyed_p(attacked_p)
            
            isCheck = check(whiteKing,blackKing,White_pList,Black_pList) #checks if the moves result into the self king being checked  
            gameState(screen,c_board.board)
            selected_p.change_castle()
            current_turn *= -1
            pawn_promotion(selected_p,screen,c_board.board)

            sqSelected,player_click = reset(sqSelected,player_click)
        
        if isCheck != False:
            k_pos = isCheck.get_position()
            screen.blit(
                p.transform.scale(
                    p.image.load("chess_pngs/cm_c.png"),(SQ_SIZE,SQ_SIZE)),p.Rect(k_pos[1]*SQ_SIZE,k_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE)
                )
        if draw_check(White_pList,Black_pList,[whiteKing,blackKing]):
            game_end(0,screen)
            running = False
            break
        p.display.update()
            
        if w_checkMated or b_checkMated:
            game_end(1 if w_checkMated else 2,screen)
            running = False
            break
        
        p.display.flip()
    
        
    while True:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                raise SystemExit
            
            elif e.type == p.MOUSEBUTTONDOWN:
                p.quit()
                raise SystemExit

if __name__ == "__main__":
    p.init()
    p.font.init()
    start_screen = p.display.set_mode((WIDTH,HEIGHT))
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
                # elif e.key == p.K_v and e.mod & p.KMOD_CTRL:
                #     input_fen = p.scrap.get(p.SCRAP_TEXT)
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
        

    main(input_fen)