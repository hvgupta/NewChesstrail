import pygame as p
from board import *
from AI import *

def main():
    
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    c_board = Board()
    WhiteList, BlackList = c_board.initialise(c_board.board)
    loadImages()
    running = True
    current_turn = Colour.w.value
    sqSelected = ()
    player_click = []
    def reset(sqSelected,player_click): # resets the sqSelected and player_click
        sqSelected = ()
        player_click = []
        return sqSelected,player_click

    whiteKing = WhiteList[12]
    blackKing = BlackList[4]
    HUMAN = Colour.w.value
    AI = Colour.b.value
    player_click_index = 0
    count = 0
    
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
            fen = board2fen(c_board.board,"KQ","kq")
            print(fen)
            # print(fen2move(fen))
            if player_click_index == 0:
                selected_p,p_move = check_mov_chooser(whiteKing,blackKing,WhiteList,BlackList)
                try:
                    print(selected_p.get_name(),selected_p.get_position(),p_move)
                except:
                    pass
                if selected_p != None:
                    all_possible,all_attack = valueDefiner(selected_p)
                    player_click.append(tuple(selected_p.get_position()))
                    player_click.append(tuple(p_move))
                else:
                    game_end(0)

        gameState(screen,c_board.board)
        isCheck = check(whiteKing,blackKing,WhiteList,BlackList)
        w_check,b_check = check_mate(whiteKing,blackKing,WhiteList,BlackList)
                
        if len(player_click) == 1:
            
            selected_p = piece_at_that_point(player_click[0],WhiteList,BlackList) 
            if selected_p == 0 or selected_p.get_colour() != current_turn:
                sqSelected,player_click=reset(sqSelected,player_click)
                continue
            
            all_possible, all_attack = valueDefiner(selected_p)
            
            if selected_p != 0 and selected_p.get_name() != "p":
                position_shower(all_possible,WhiteList,BlackList,screen,selected_p,[whiteKing,blackKing])
            elif selected_p != 0 and selected_p.get_name() == "p":
                position_shower(all_possible.reshape((all_possible.shape[1],all_possible.shape[0],2)),WhiteList,BlackList,screen,selected_p,[whiteKing,blackKing],all_attack)
        
        elif len(player_click) == 2:

            attacked_p = piece_at_that_point(player_click[1],WhiteList,BlackList)
            
            condition = not (attacked_p != 0  and attacked_p.get_colour() == selected_p.get_colour())
                    
            if condition and selected_p != 0:
                p_info = selected_p.get_info()
                p_name = selected_p.get_name()
                    
                if ((all_possible[(np.max(all_possible,axis=2) < 8) & (np.min(all_possible,axis=2)>-1)] == player_click[1]).all(axis=1)).any():
                    output = None
                    if p_name != "p":
                        output = check_line(selected_p,all_possible,player_click[1],WhiteList,BlackList)
                    else:
                        if attacked_p != 0:
                            sqSelected,player_click=reset(sqSelected,player_click)
                            break
                        output = check_line(selected_p,np.expand_dims(all_possible,axis=0),player_click[1],WhiteList,BlackList)
                    
                    if not output:
                        sqSelected, player_click = reset(sqSelected,player_click)
                        continue
                    
                    all_possible = all_possible[(np.max(all_possible,axis=2) < 8) & (np.min(all_possible,axis=2)>-1)]    

                    if attacked_p == 0:
                        move_piece(selected_p, np.array(player_click[1]),c_board.board)
                        isCheck = check(whiteKing,blackKing,WhiteList,BlackList)
                        if isCheck != False and isCheck.get_colour() == selected_p.get_colour():
                            move_piece(selected_p,np.array(player_click[0]),c_board.board)
                            sqSelected,player_click = reset(sqSelected,player_click)
                            continue
                    elif attacked_p != 0:
                        move_piece(selected_p,np.array(player_click[0]),c_board.board)
                        a_old = attacked_p.get_position()
                        destroyed_p(attacked_p)
                        isCheck = check(whiteKing,blackKing,WhiteList,BlackList)
                        if isCheck != False and isCheck.get_colour() == selected_p.get_colour():
                            move_piece(selected_p,np.array(player_click[0]),c_board.board)
                            attacked_p.position = a_old
                            sqSelected,player_click = reset(sqSelected,player_click)
                            continue
                        
                    selected_p.change_castle()

                    current_turn = current_turn*-1

                elif p_name == "K" and attacked_p == 0:
                    selected_p,c_board.board,attacked_p = castle_checker(selected_p,player_click[1],c_board.board,WhiteList,BlackList)
                    if attacked_p != 0:
                        selected_p.change_castle()
                        attacked_p.change_castle()
                        current_turn = current_turn*-1
                    
                elif p_info == getattr(type,"p").value and player_click[1] in all_attack:
                    attacked_p = piece_at_that_point(player_click[1],WhiteList,BlackList)
                    if attacked_p != 0 and current_turn != attacked_p.get_colour():
                        move_piece(selected_p,np.array(player_click[1]),c_board.board)
                        attacked_p.change_pos(np.array([-1,-1]))
                        current_turn = current_turn*-1
                            
            sqSelected,player_click=reset(sqSelected,player_click)

        # pawn_promotion(selected_p,screen,c_board.board)
        
        if w_check or isCheck == whiteKing:
            k_pos = whiteKing.get_position()
            screen.blit(
                p.transform.scale(
                    p.image.load("chess_pngs/cm_c.png"),(SQ_SIZE,SQ_SIZE)),p.Rect(k_pos[1]*SQ_SIZE,k_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE)
                )
            
        elif b_check or isCheck == blackKing:
            k_pos = blackKing.get_position()
            screen.blit(
                p.transform.scale(
                    p.image.load("chess_pngs/cm_c.png"),(SQ_SIZE,SQ_SIZE)),p.Rect(k_pos[1]*SQ_SIZE,k_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE)
                )
        
        p.display.update()
            
        if w_check:
            game_end(-1)
        elif b_check:
            game_end(1)

        clock.tick(15)
        p.display.flip()

        

if __name__ == "__main__":    
    main()