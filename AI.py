import random
from main_func import *
    

def randomPchooser(blacklist):
    return (random.choice(blacklist)).get_position()

def randomMovchooser(all_possible):
    return random.choice(all_possible)

# def check_mov_chooser(w_king, b_king, whiteList, blackList,all_possible,all_attack=None):
#     piece = check(w_king,b_king,whiteList,blackList,True)
#     if piece != False:
        