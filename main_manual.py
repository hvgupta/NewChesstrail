import pygame as p
from board import *
from main_func import *
        
def main():
    # initialising pygame ...
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    screen.fill(p.Color("white"))
    
    #creating the chess board array
    c_board = Board()
    White_pList, Black_pList = c_board.initialise(c_board.board)
    
    #inseting images on to the pygame window 
    loadImages()
    
    #declaring variables for later use
    running = True
    current_turn = Colour.w.value
    sqSelected = ()
    player_click = []
    moves = []
    whiteKing = White_pList[12]
    blackKing = Black_pList[4]
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
            
            all_possible, all_attack = valueDefiner(selected_p)
            
            if selected_p != 0 and selected_p.get_name() != "p":
                position_shower(all_possible,White_pList,Black_pList,screen,selected_p,[whiteKing,blackKing])
            elif selected_p != 0 and selected_p.get_name() == "p":
                position_shower(all_possible.reshape((all_possible.shape[1],all_possible.shape[0],2)),White_pList,Black_pList,screen,selected_p,[whiteKing,blackKing],all_attack)
        
        elif len(player_click) == 2:

            attacked_p = piece_at_that_pos(player_click[1],White_pList,Black_pList)
            
            condition = not (attacked_p != 0  and attacked_p.get_colour() == selected_p.get_colour())
                    
            if not condition:
                moves = []
                sqSelected,player_click = reset(sqSelected,player_click)
                continue
            p_name = selected_p.get_name()
                
            conditions = (
                (((all_possible[(np.max(all_possible,axis=2) < 8) & (np.min(all_possible,axis=2)>-1)] == player_click[1]).all(axis=1)).any())
                or
                (
                    p_name == "p" and ((all_attack[(np.max(all_attack,axis=1) < 8) & (np.min(all_attack,axis=1)>-1)] == player_click[1]).all(axis=1)).any()
                    and
                    (attacked_p != 0 and attacked_p.get_colour() != selected_p.get_colour())
                    )
                )
                    
            if not conditions:
                moves = []
                sqSelected,player_click = reset(sqSelected,player_click)
                continue
            
            output = None
            if p_name != "p":
                output = check_line(selected_p,all_possible,player_click[1],White_pList,Black_pList)
            else:
                test = np.expand_dims(all_possible if attacked_p == 0 else all_attack ,axis=0)
                output = check_line(selected_p,np.expand_dims(all_possible if attacked_p == 0 else all_attack ,axis=0),player_click[1],White_pList,Black_pList)
            
            if not output:
                sqSelected, player_click = reset(sqSelected,player_click) #check if the move is blocked by any other piece
                continue
            
            if selected_p.get_name() == "K" and abs(player_click[1][1] - player_click[0][1]) == 2:
                castle_valid = castle_checker(selected_p, np.array(player_click[1]),White_pList,Black_pList)
                if not castle_valid:
                    continue
                rook_xcoord = 0 if player_click[1][1] - player_click[0][1] == -2 else 7
                rook = piece_at_that_pos(np.array([player_click[1][0],rook_xcoord]),White_pList,Black_pList)
                rook_old_pos = rook.get_position()
                rook_to_pos = np.array([player_click[1][0],3]) if player_click[1][1] - player_click[0][1] == -2 else np.array([player_click[1][0],5])
                c_board.move_piece(selected_p,np.array(np.array(player_click[1])))
                c_board.move_piece(rook,rook_to_pos)
                moves.append([selected_p, player_click[0]])
                moves.append([rook, rook_old_pos])

            elif attacked_p == 0:
                c_board.move_piece(selected_p, np.array(sqSelected))
                moves.append([selected_p,player_click[0]])

            elif attacked_p != 0:
                c_board.move_piece(selected_p,np.array(sqSelected))
                destroyed_p(attacked_p)
                moves.append([selected_p,player_click[0]])
                moves.append([attacked_p, player_click[1]])
            
            isCheck = check(whiteKing,blackKing,White_pList,Black_pList)  
            if isCheck != False and isCheck.get_colour() == selected_p.get_colour():
                for move in moves:
                    c_board.move_piece(move[0],np.array(move[1]))
            else:
                gameState(screen,c_board.board)
                selected_p.change_castle()
                current_turn *= -1
                pawn_promotion(selected_p,screen,c_board.board)
            
            moves = []
            sqSelected,player_click = reset(sqSelected,player_click)
        
        if isCheck != False:
            k_pos = isCheck.get_position()
            screen.blit(
                p.transform.scale(
                    p.image.load("chess_pngs/cm_c.png"),(SQ_SIZE,SQ_SIZE)),p.Rect(k_pos[1]*SQ_SIZE,k_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE)
                )
        
        p.display.update()
            
        if w_checkMated or b_checkMated:
            running = False
            continue
        
        p.display.flip()

if __name__ == "__main__":    
    main()