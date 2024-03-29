from __future__ import annotations
import math
from Helper_func import *
from type_enum import *
from board import *
from game import *

class Node():
    def __init__(self,game:Game ,args:dict , parent:Node = None, action:int = None, prior:int = 0, visit_count: int = 0) -> None:
        
        self.game:Game = game
        self.args:dict = args
        
        self.parent:Node = parent
        self.action_taken:int = action
        self.children:list[Node] = []
        self.prior:int = prior
        
        self.visit_count:int = visit_count
        self.value_sum:int = 0
    
    def isFullyExpanded(self)->bool:
        return len(self.children) > 0 

    def select(self)->Node:
        ''' upper confidence bound'''
        bestChild = None
        bestUCB = -np.inf
        
        for child in self.children:
            ucb = self.get_ucb(child)
            if ucb > bestUCB:
                bestChild = child
                bestUCB = ucb
        
        return bestChild
    
    def get_ucb(self,child:Node):
        if child.visit_count == 0:
            q_value = 0
        else:
            q_value = 1 - ((child.value_sum / child.visit_count) + 1) / 2
        return q_value + self.args['C'] * (math.sqrt(self.visit_count) / (child.visit_count + 1)) * child.prior
    
    def expand(self, policy):
        arrayActionIndex:np.ndarray = np.nonzero(policy)[0]
        for actionIndex in range(len(arrayActionIndex)):
            action:int = arrayActionIndex[actionIndex]
            prob = policy[action]
            WKing, BKing, newBoard = self.game.move_piece(action)
            child_colour = self.game.turn*-1
            child = Node(Game(WKing, BKing,child_colour, newBoard),self.args, self, action,prob)
            self.children.append(child)
            
    def backpropagate(self, value):
        self.value_sum += value
        self.visit_count += 1
        
        value *= -1 
        if self.parent is not None:
            self.parent.backpropagate(value)  

    def printDetail(self):
        for index in range(len(self.game.allowedPiece)):
            allowedP = self.game.allowedPiece[index]
            print(f"{allowedP.name} {allowedP.get_position()}: {str(self.game.allowedActions[index].tolist())}")
        
        for len8 in self.game.board.board:
            print(len8)