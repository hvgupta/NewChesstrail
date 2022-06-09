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
            if player_click_index == 0:
                AI_select_p_pos = check_mov_chooser(whiteKing,blackKing,WhiteList,BlackList)
                player_click.append(tuple(AI_select_p_pos))
                player_click_index+=1
                
            elif player_click_index == 1:
                pos_selected = np.array([-1,-1])
                AI_move_array = np.copy(all_possible)
                if piece_at_that_point(AI_select_p_pos,WhiteList,BlackList).get_name() == "p":
                    AI_move_array = np.append(AI_move_array,all_attack)
                    AI_move_array = AI_move_array.reshape((int(AI_move_array.shape[0]/2),1,2))
                AI_move_array = AI_move_array[(np.max(AI_move_array,axis=2) < 8) & (np.min(AI_move_array,axis=2)>-1)]
                if AI_move_array.shape[0] != 0:
                    while np.max(pos_selected)>7 or np.min(pos_selected)<0:
                        pos_selected = np.array(randomMovchooser(AI_move_array))
                AI_move_array = np.expand_dims(AI_move_array,axis=1)
                player_click.append(tuple(pos_selected))
                player_click_index = 0
                
                
        if len(player_click) == 1:
            
            selected_p = piece_at_that_point(player_click[0],WhiteList,BlackList)
            
            if selected_p == 0 or selected_p.get_colour() != current_turn:
                sqSelected,player_click=reset(sqSelected,player_click)
                continue
            
            all_possible, all_attack = valueDefiner(selected_p)
        
        elif len(player_click) == 2:

                attacked_p = piece_at_that_point(player_click[1],WhiteList,BlackList)
                
                if attacked_p != 0  and attacked_p.get_colour() == selected_p.get_colour():
                    condition = False
                else:
                    condition = True
                        
                if condition and selected_p != None:
                    p_info = selected_p.get_info()
                    p_name = selected_p.get_name()
                        
                    output = check_line(selected_p,all_possible,player_click[1],WhiteList,BlackList)
                    all_possible = all_possible[(np.max(all_possible,axis=2) < 8) & (np.min(all_possible,axis=2)>-1)]
                    
                    if ((all_possible == player_click[1]).all(axis=1)).any() and output:
                        if p_name != "p":
                            move_piece(selected_p,np.array(player_click[1]),c_board.board)
                            if attacked_p != 0 :
                                a_old = attacked_p.get_position()
                                destroyed_p(attacked_p)
                            isCheck = check(whiteKing,blackKing,WhiteList,BlackList)
                            if isCheck != False and isCheck.get_colour() == selected_p.get_colour():
                                move_piece(selected_p,np.array(player_click[0]),c_board.board)
                                attacked_p.change_pos(a_old) if attacked_p != 0 else 0
                                sqSelected,player_click=reset(sqSelected,player_click)
                                break
                            
                            selected_p.change_castle()
                        else:
                            if attacked_p != 0:
                                sqSelected,player_click=reset(sqSelected,player_click)
                                break
                            else:
                                move_piece(selected_p,np.array(player_click[1]),c_board.board)
                                if attacked_p != 0:
                                    a_old = attacked_p.get_position()
                                destroyed_p(attacked_p)
                                if isCheck != False and isCheck.get_colour() == selected_p.get_colour():
                                    move_piece(selected_p,np.array(player_click[0]),c_board.board)
                                    attacked_p.change_pos(a_old) if attacked_p != 0 else 0
                                    sqSelected,player_click=reset(sqSelected,player_click)
                                    break

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
                    
        gameState(screen,c_board.board)
        isCheck = check(whiteKing,blackKing,WhiteList,BlackList)
        w_check,b_check = check_mate(whiteKing,blackKing,WhiteList,BlackList)
        if len(player_click) == 1 and selected_p != 0 and selected_p.get_name() != "p" and current_turn == HUMAN:
            position_shower(all_possible,WhiteList,BlackList,screen,selected_p,[whiteKing,blackKing])
        elif len(player_click) == 1 and selected_p != 0 and selected_p.get_name() == "p" and current_turn == HUMAN:
            position_shower(all_possible,WhiteList,BlackList,screen,selected_p,[whiteKing,blackKing],all_attack)
        c_m = False
        if w_check or isCheck == whiteKing:
            k_pos = whiteKing.get_position()
            c_m = True
        if b_check or isCheck == blackKing:
            k_pos = blackKing.get_position()
            c_m = True
        
        if c_m:
            screen.blit(p.transform.scale(p.image.load("chess_pngs/cm_c.png"),(SQ_SIZE,SQ_SIZE)),p.Rect(k_pos[1]*SQ_SIZE,k_pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
            
        if w_check or b_check:
            running = False
        clock.tick(15)
        p.display.flip()

        

if __name__ == "__main__":    
    main()