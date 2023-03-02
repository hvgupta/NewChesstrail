import pygame as p
from board import *
from Helper_func import *
         
def main(fen = ""):
    # initialising pygame ...
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    screen.fill(p.Color("white"))
    
    #creating the chess board array
    c_board = Board(fen)
    White_pList, Black_pList = c_board.initialise(c_board.board)
    
    #inseting images on to the pygame window 
    loadImages()
    
    #declaring variables for later use
    running = True
    current_turn = c_board.Turn.value
    sqSelected = ()
    player_click = []
    legal_moves = []
    whiteKing, blackKing = getKing(White_pList, Black_pList)
    selected_p = Piece
    
    def reset(sqSelected,player_click): # resets the sqSelected and player_click
        sqSelected = ()
        player_click = []
        return sqSelected,player_click

    while running: # the main function
        
        for e in p.event.get():
            
            if e.type == p.QUIT:
                p.quit()
                raise SystemExit
            
            elif e.type == p.MOUSEBUTTONDOWN:
                
                p.display.update()
                location = p.mouse.get_pos() #get the coordinate of the mouse click
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row,col): #checks if the same box is clicked twice, if yes then it resets the position storers
                    sqSelected,player_click=reset(sqSelected,player_click)
                else:   
                    sqSelected = (row,col)
                    player_click.append(sqSelected)
        
        gameState(screen,c_board.board)
        
        isCheck = check(whiteKing,blackKing,White_pList,Black_pList)
        w_checkMated,b_checkMated = check_mate(whiteKing,blackKing,White_pList,Black_pList)
                
        if len(player_click) == 1:
            
            selected_p = piece_at_that_pos(player_click[0],White_pList,Black_pList) 
            if selected_p == 0 or selected_p.get_colour() != current_turn:
                sqSelected,player_click=reset(sqSelected,player_click) # resets player click if the clicked tile is empty or of the wrong colour
                continue
            
            all_possible, all_attack = movesReturn(selected_p) #gives all the moves possible legal and illegal
            #shows those positions accoring to all the legal moves
            if selected_p != 0 and selected_p.get_name() != "p":
                legal_moves = position_shower(all_possible,White_pList,Black_pList,screen,selected_p,[whiteKing,blackKing]) 
            elif selected_p != 0 and selected_p.get_name() == "p":
                legal_moves = position_shower(all_possible.reshape((all_possible.shape[1],all_possible.shape[0],2)),White_pList,Black_pList,screen,selected_p,[whiteKing,blackKing],all_attack)
        
        elif len(player_click) == 2:
            
            if not (legal_moves.size != 0 and (legal_moves == player_click[1]).all(axis=1).any()):
                sqSelected,player_click = reset(sqSelected,player_click)
                continue
            attacked_p = piece_at_that_pos(player_click[1],White_pList,Black_pList) #gives the positon information for the position being moved to
            
            if selected_p.get_name() == "K" and abs(player_click[1][1] - player_click[0][1]) == 2: #checks for the castle conditoin
                castle_valid = castle_checker(selected_p, np.array(player_click[1]),White_pList,Black_pList)
                if not castle_valid:
                    continue
                rook_xcoord = 0 if player_click[1][1] - player_click[0][1] == -2 else 7
                rook = piece_at_that_pos(np.array([player_click[1][0],rook_xcoord]),White_pList,Black_pList)
                rook_to_pos = np.array([player_click[1][0],3]) if player_click[1][1] - player_click[0][1] == -2 else np.array([player_click[1][0],5])
                c_board.move_piece(selected_p,np.array(np.array(player_click[1])))
                c_board.move_piece(rook,rook_to_pos)

            elif attacked_p == 0: #if the piece is moving to an empty space
                c_board.move_piece(selected_p, np.array(sqSelected))

            elif attacked_p != 0:# if the piece is moving to a space which is occupied by the opposite team
                c_board.move_piece(selected_p,np.array(sqSelected))
                destroyed_p(attacked_p)
            
            isCheck = check(whiteKing,blackKing,White_pList,Black_pList) #checks if the moves result into the self king being checked  
            gameState(screen,c_board.board)
            selected_p.change_castle()
            current_turn *= -1
            pawn_promotion(selected_p,screen,c_board.board)
            
            # PastMoves = []
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