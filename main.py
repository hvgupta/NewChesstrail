import pygame as p
from board import *
from main_func import *

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
IMAGES = {}

def loadImages():
    pieces = ["wp","bp","wR","wB","wK","wQ","wN","bR","bB","bK","bQ","bN"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("chess_pngs/{piece}.png".format(piece= piece)),(SQ_SIZE,SQ_SIZE))
        
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
    
    while running:

        for e in p.event.get():
            
            if e.type == p.QUIT:
                running = False
            
            elif e.type == p.MOUSEBUTTONDOWN:
                
                p.display.update()
                location = p.mouse.get_pos()
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE
                if sqSelected == (row,col):
                    sqSelected,player_click=reset(sqSelected,player_click)
                else:   
                    sqSelected = (row,col)
                    player_click.append(sqSelected)
                
                if len(player_click) == 1:
                    
                    selected_p = piece_at_that_point(player_click[0],WhiteList,BlackList)
                    
                    if selected_p == 0 or selected_p.get_colour() != current_turn:
                        sqSelected,player_click=reset(sqSelected,player_click)
                        break
                    
                    if selected_p.get_name() == "p":
                        all_possible, all_attack = valueDefiner(selected_p)
                    else:
                        all_possible = valueDefiner(selected_p)
                
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
        if len(player_click) == 1 and selected_p != 0 and selected_p.get_name() != "p":
            position_shower(all_possible,WhiteList,BlackList,screen,selected_p,[whiteKing,blackKing])
        elif len(player_click) == 1 and selected_p != 0 and selected_p.get_name() == "p":
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

        

def gameState(screen, board):
    drawboard(screen)
    drawPieces(screen,board)
    
def drawboard(screen):
    colours = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[((r+c)%2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def position_shower(all_possible, WhiteList, BlackList, screen, selected_p,king_array,all_attack = None):
    p_name = selected_p.get_name()
    isCheck = check(king_array[0],king_array[1],WhiteList,BlackList,True)
    other_condition = True
    
    for turn_set in all_possible: 

        for pos in turn_set:
            
            if (pos[0] > 7 or pos[0] <0) or (pos[1] > 7 or pos[1] < 0):
                break
            surface = surface_creator()
            output = piece_at_that_point(pos,WhiteList,BlackList)
            if isCheck!= False and selected_p.get_name() != "K":
                checked_colour = king_array[0] if isCheck.get_colour() == Colour.b.value else king_array[1]
                if isCheck.get_name() != "p":
                    attacking_p_movs = valueDefiner(isCheck)
                else:
                    p_movs, attacking_p_movs = valueDefiner(isCheck)
                    attacking_p_movs = np.expand_dims(attacking_p_movs,axis=1)
                choosen_dir = np.nonzero(((checked_colour.get_position() == attacking_p_movs).all(axis=2))*1)
                if choosen_dir[0].size == 0:
                    break
                attacking_p_movs = attacking_p_movs[choosen_dir[0][0],0:choosen_dir[1][0]+1]
                attacking_p_movs = np.append(attacking_p_movs,isCheck.get_position())
                attacking_p_movs = attacking_p_movs.reshape((int(attacking_p_movs.shape[0]/2),2))
                other_condition = ((attacking_p_movs == pos).all(axis=1)).any()
                
            if output == 0 and other_condition:
                old = selected_p.get_position()
                selected_p.change_pos(pos)
                Check = check(king_array[0],king_array[1],WhiteList,BlackList)
                selected_p.change_pos(old)
                if Check != False and Check.get_colour() == selected_p.get_colour():
                    continue
                else:
                    draw(screen,surface,"c",pos)
                    
            elif output != 0 and output.get_colour() != selected_p.get_colour() and selected_p.get_name() != "p" and other_condition:
                old = selected_p.get_position()
                selected_p.change_pos(pos)
                if isCheck != False:
                    a_old = isCheck.get_position()
                    if (pos == isCheck.get_position()).all():
                        isCheck.change_pos(np.array([-1,-1]))
                Check = check(king_array[0],king_array[1],WhiteList,BlackList)
                selected_p.change_pos(old)
                if isCheck != False:
                    isCheck.change_pos(a_old)
                if Check != False and Check.get_colour() == selected_p.get_colour():
                    continue
                else:
                    draw(screen,surface,"r",pos)
                break
            elif output != 0 and output.get_colour() == selected_p.get_colour():
                break

    if p_name == "p":
        for attack in all_attack:
            surface = surface_creator()
            output = piece_at_that_point(attack,WhiteList,BlackList)
            if output == 0:
                pass
            elif output.get_colour() != selected_p.get_colour():
                old = selected_p.get_position()
                selected_p.change_pos(pos)
                Check = check(king_array[0],king_array[1],WhiteList,BlackList)
                selected_p.change_pos(old)
                if Check != False and Check.get_colour() == selected_p.get_colour():
                    continue
                else:
                    draw(screen,surface,"r",attack)
    
    if selected_p.get_name() == "K" and selected_p.get_castle():
        p_pos = selected_p.get_position()
        for pos in np.array([[0,-2],[0,2]]):
            new_pos = pos+p_pos
            if pos[1] == -2:
                output = check_line(selected_p,np.array([[[0,-1],[0,-2]]])+p_pos,new_pos,WhiteList,BlackList)
            else:
                output = check_line(selected_p,np.array([[[0,1],[0,2]]])+p_pos,new_pos,WhiteList,BlackList)
            if piece_at_that_point(new_pos,WhiteList,BlackList) == 0 and output:
                surface = surface_creator()
                draw(screen,surface,"c",new_pos)
                 
def surface_creator():
    surface = p.Surface((512,512),p.SRCALPHA)
    surface.set_colorkey(p.Color("White"))
    surface.set_alpha(25)
    return surface

def draw(screen,surface, r_or_c:str, pos):
    if r_or_c.lower() == "c":       
        p.draw.circle(surface,(0,0,0), (32 + (64*pos[1]),32 + (64*pos[0])), DIMENSION*1.5)
    else:
        p.draw.rect(surface,(255,0,0),p.Rect(pos[1]*SQ_SIZE,pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
    screen.blit(surface,(0,0))

def destroyed_p(attacked_p):
    if attacked_p != 0:
        attacked_p.change_pos(np.array([-1,-1]))

if __name__ == "__main__":    
    main()