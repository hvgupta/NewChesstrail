from click_handle import *
         
def main(fen = ""):
    # initialising pygame ...
    screen = p.display.set_mode((IMGWIDTH,HEIGHT))
    screen.fill(p.Color("white"))
    
    #creating the chess board array
    ChessBoard = Board(fen)
    ChessBoard.initialise()
    
    #inseting images on to the pygame window 
    loadImages()
    
    #declaring variables for later use
    running: bool = True
    current_turn = Colour.w.value
    sqSelected = ()
    player_click:list[tuple[int]] = []
    legal_moves = []
    whiteKing, blackKing = getKing(ChessBoard)
    selected_p = Piece
    w_checkMated = False
    b_checkMated = False
    
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
        gameState(screen,ChessBoard.board)
        isCheck = check(whiteKing,blackKing,ChessBoard) # checks if a king is checked
        if isCheck != False: # verifies if it is a checkmate
            if isCheck.get_colour() == Colour.w.value:
                w_checkMated = check_mate(isCheck, ChessBoard)
            else:
                b_checkMated = check_mate(isCheck, ChessBoard)
                
        if w_checkMated or b_checkMated: # if there is a checkmate then end the game
            game_end(1 if w_checkMated else 2,screen)
            running = False
            break
                
        if len(player_click) == 1: # check if the first click is valid, makes sure if a piece and the correct turn piece is choosen
            legal, selected_p, legal_moves = first_click(ChessBoard, current_turn, screen, whiteKing, blackKing, player_click) 
            if not legal: 
                sqSelected,player_click = reset(sqSelected,player_click)
                continue
        
        elif len(player_click) == 2: # handles the second click, which is the movement of the piece. makes sure if the piece can move to that position and so if it doesnt cause checks
            
            if second_click(ChessBoard, legal_moves, selected_p,sqSelected,player_click):
                
                gameState(screen,ChessBoard.board)
                selected_p.change_castle()
                current_turn *= -1
                pawn_promotion(selected_p,screen,ChessBoard.board)

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

        # elif draw_check(White_pList,Black_pList,[whiteKing,blackKing]):
        #     game_end(0,screen)
        #     running = False
        #     break
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