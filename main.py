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
    sqSelected = ()
    player_click = []
    current_turn = Colour.w.value
    
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
                   sqSelected = ()
                   player_click = []
                else:   
                    sqSelected = (row,col)
                    player_click.append(sqSelected)
                
                selected_p = None

                if current_turn == Colour.w.value:
                    for piece in WhiteList:
                        if len(player_click) and (piece.get_position() == player_click[0]).all():
                            selected_p = piece   
                else:
                    for piece in BlackList:
                        if len(player_click) and (piece.get_position() == player_click[0]).all():
                            selected_p = piece             
                
                if selected_p  == None:
                    sqSelected = ()
                    player_click = []
                    break
                
                if selected_p.get_name() == "p":
                    all_possible, all_attack = valueDefiner(selected_p)
                else:
                    all_possible = valueDefiner(selected_p)
                
                if len(player_click) == 2:
                    condition = True
                    
                    for w_piece, b_piece in zip(WhiteList,BlackList):
                        if (w_piece.get_position() == player_click[1]).all() and selected_p.get_colour() == -1:
                            condition = False
                        if (b_piece.get_position() == player_click[1]).all() and selected_p.get_colour() == 1:
                            condition = False
                    
                    if selected_p == None:
                        break
                    
                    if selected_p.get_name() == "R":
                        king = piece_at_that_point(player_click[1],WhiteList,BlackList)
                        if king != 0 and king.get_name() == "K" and king.get_info()[2] and selected_p.get_info()[2]:
                            condition = True
                            
                    if condition and selected_p != None:
                        p_info = selected_p.get_info()
                        p_name = selected_p.get_name()
                            
                        output = check_line(all_possible,player_click[1],WhiteList,BlackList)
                        all_possible = all_possible[(np.max(all_possible,axis=2) < 8) & (np.min(all_possible,axis=2)>-1)]
                        
                        if ((all_possible == player_click[1]).all(axis=1)).any() and output:
                            attacked_p = piece_at_that_point(player_click[1],WhiteList,BlackList)
                            if (p_name == "R" and attacked_p.get_name() == "K") or (p_name == "K" and attacked_p.get_name() == "R"):
                                selected_p,attacked_p,c_board.board = castle_checker(selected_p,attacked_p,c_board.board,WhiteList,BlackList)
                                selected_p.piece_type = (p_info[0],p_info[1],False)
                                a_info = attacked_p.get_info()
                                attacked_p.piece_type = (a_info[0],a_info[1],False)
                                attacked_p = 0
                            elif p_name == "p":
                                if attacked_p != 0:
                                    sqSelected = ()
                                    player_click = []
                                    break
                                else:
                                    move_piece(selected_p,np.array(player_click[1]),c_board.board)
                            else:                            
                                move_piece(selected_p,np.array(player_click[1]),c_board.board)
                                
                            current_turn = current_turn*-1
                            if attacked_p != 0:
                                attacked_p.change_pos(np.array([-1,-1]))
                                
                            
                        elif p_info == getattr(type,"p").value and player_click[1] in all_attack:
                            attacked_p = piece_at_that_point(player_click[1],WhiteList,BlackList)
                            if attacked_p != 0 and current_turn != attacked_p.get_colour():
                                move_piece(selected_p,np.array(player_click[1]),c_board.board)
                                attacked_p.change_pos(np.array([-1,-1]))
                                current_turn = current_turn*-1
                                    
                    sqSelected = ()
                    player_click = []
                        
        gameState(screen,c_board.board)
        try:
            for turn_set in all_possible:                  
                for pos in turn_set:
                    if (pos[0] > 7 or pos[0] <0) or (pos[1] > 7 or pos[1] < 0):
                        break
                    # print(len(player_click))
                    # print(player_click[0] == player_click[1])
                    if len(player_click) == 0 or selected_p == None:
                        break
                    surface1 = p.Surface((512,512),p.SRCALPHA)
                    surface1.set_colorkey(p.Color("white"))  # use `(0,0,0)` (black color) as transparent color
                    surface1.set_alpha(128)  # transparency 50% for other colors
                    output = piece_at_that_point(pos,WhiteList,BlackList)
                    if output == 0:
                        p.draw.circle(surface1, (0,0,0), (32 + (64*pos[1]),32 + (64*pos[0])), DIMENSION*1.5) 
                    elif output.get_colour() != selected_p.get_colour() and selected_p.get_name() != "p":
                        # p.draw.circle(surface1, (255,0,0), (32 + (SQ_SIZE*pos[1]),32 + (SQ_SIZE*pos[0])), DIMENSION*1.5)
                        p.draw.rect(surface1,(255,0,0),p.Rect(pos[1]*SQ_SIZE,pos[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
                        screen.blit(surface1,(0,0))
                        break
                    elif output.get_colour() == selected_p.get_colour():
                        break
                    screen.blit(surface1,(0,0))
            
            if selected_p.get_name() == "p":
                for attack in all_attack:
                    surface1 = p.Surface((512,512),p.SRCALPHA)
                    surface1.set_colorkey(p.Color("white"))
                    surface1.set_alpha(128)
                    output = piece_at_that_point(attack,WhiteList,BlackList)
                    if output == 0:
                        pass
                    elif output.get_colour() != selected_p.get_colour():
                        p.draw.rect(surface1,(255,0,0),p.Rect(attack[1]*SQ_SIZE,attack[0]*SQ_SIZE,SQ_SIZE,SQ_SIZE))
                        screen.blit(surface1,(0,0))        
                
        except:
            pass
        clock.tick(15)
        p.display.flip()
        # selected_p = None
    

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
                
                
if __name__ == "__main__":    
    main()