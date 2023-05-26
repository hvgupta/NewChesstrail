from click_handle import *
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
        isCheck = check(whiteKing,blackKing,White_pList,Black_pList) # checks if a king is checked
        if isCheck != False: # verifies if it is a checkmate
            if isCheck.get_colour() == Colour.w.value:
                w_checkMated = check_mate(isCheck, White_pList, Black_pList)
            else:
                b_checkMated = check_mate(isCheck, White_pList, Black_pList)
                
        if w_checkMated or b_checkMated: # if there is a checkmate then end the game
            game_end(1 if w_checkMated else 2,screen)
            running = False
            break
                
        if len(player_click) == 1: # check if the first click is valid, makes sure if a piece and the correct turn piece is choosen
            legal, selected_p, legal_moves = first_click(White_pList, Black_pList, current_turn, screen, whiteKing, blackKing, sqSelected, player_click) 
            if not legal: 
                sqSelected,player_click = reset(sqSelected,player_click)
                continue
        
        elif len(player_click) == 2: # handles the second click, which is the movement of the piece. makes sure if the piece can move to that position and so if it doesnt cause checks
            
            if second_click(c_board, legal_moves, White_pList, Black_pList, selected_p,sqSelected,player_click):
                
                isCheck = check(whiteKing,blackKing,White_pList,Black_pList) #checks if the moves result into the self king being checked  
                gameState(screen,c_board.board)
                selected_p.change_castle()
                current_turn *= -1
                pawn_promotion(selected_p,screen,c_board.board)

                sqSelected,player_click = reset(sqSelected,player_click)
            else:
                sqSelected,player_click = reset(sqSelected,player_click)
                continue
        
        if isCheck != False: # turns the king red when checked
            k_pos = isCheck.get_position()
            screen.blit(
                p.transform.scale(
                    p.image.load("chess_pngs/cm_c.png"),(SQ_SIZE,SQ_SIZE)),p.Rect(k_pos[1]*SQ_SIZE,k_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE)
                )

        elif draw_check(White_pList,Black_pList,[whiteKing,blackKing]):
            game_end(0,screen)
            running = False
            break
        p.display.update()
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
    input_fen = FenInitialisation() # checks if a special fen start is needed 
    main(input_fen)