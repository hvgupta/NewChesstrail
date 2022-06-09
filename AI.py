import random
from main_func import *
    

def randomPchooser(blacklist):
    return (random.choice(blacklist)).get_position()

def randomMovchooser(all_possible):
    return random.choice(all_possible)
            