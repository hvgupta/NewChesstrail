from ResNet import *
from Node import *
from SPG import *

class MCTS():
    def __init__(self,game:Game, args, model:ResNet):
        self.game:Game = game
        self.args = args
        self.model = model
        
    @torch.no_grad()
    def search(self):
        root = Node(self.game, self.args, visit_count=1)
        
        policy, _ = self.model(
            torch.tensor(self.game.get_encodedState(), device=self.model.device).unsqueeze(0)
        )
        policy = torch.softmax(policy, axis=1).squeeze(0).cpu().numpy()
        policy = (1 - self.args['dirichlet_epsilon']) * policy + self.args['dirichlet_epsilon'] \
            * np.random.dirichlet([self.args['dirichlet_alpha']] * 3288)
        
        valid_moves, _ = self.game.get_validMoves()
        policy *= valid_moves
        policy /= np.sum(policy)
        root.expand(policy)
        
        for search in range(self.args['num_searches']):
            node = root
            
            while node.isFullyExpanded():
                node = node.select()
                
            value, is_terminal = node.game.valueAndterminated()
            value *= -1
            
            if not is_terminal:
                policy, value = self.model(
                    torch.tensor(node.game.get_encodedState(), device=self.model.device).unsqueeze(0)
                )
                policy = torch.softmax(policy, axis=1).squeeze(0).cpu().numpy()
                valid_moves, _ = node.game.get_validMoves()
                policy *= valid_moves
                policy /= np.sum(policy)
                
                value = value.item()
                
                node.expand(policy)
                
            node.backpropagate(value)    
            
            
        action_probs = np.zeros(3288)
        for child in root.children:
            action_probs[child.action_taken] = child.visit_count
        action_probs /= np.sum(action_probs)
        return action_probs


# MCTSParallel plays many games at once

class MCTSParallel():
    def __init__(self,game:Game, args, model:ResNet):
        self.game:Game = game
        self.args = args
        self.model = model

    @torch.no_grad()
    def search(self, spGames: list[SPG]):
        f"""
        in this version of search of MCTS, many games are ran parallelly (all the games listed in {spGames})
        """
        for spGame in spGames:
            state = spGame.game.get_encodedState()
            policy, _ = self.model(torch.tensor(state,device= self.model.device).unsqueeze(0))
            policy = torch.softmax(policy, axis=1).squeeze(0).cpu().numpy()
            policy = (1 - self.args['dirichlet_epsilon']) * policy + self.args['dirichlet_epsilon'] \
                * np.random.dirichlet([self.args['dirichlet_alpha']] * 3288)
                
            valid_moves,_ = spGame.game.get_validMoves()
            policy *= valid_moves
            policy /= np.sum(policy)

            spGame.root = Node(self.game, self.args, visit_count=1)
            spGame.root.expand(policy)
       
        for search in range(self.args['num_searches']):
            expandable_spGames:list[int] = []
            index:int = 0
            policiesValues = []
            for spg in spGames:
                spg.node = None
                node = spg.root

                while node.isFullyExpanded():
                    node = node.select()

                value, is_terminal = node.game.valueAndterminated()
                value *= -1
                
                if is_terminal:
                    node.backpropagate(value)
                    
                else:
                    spg.node = node
                    expandable_spGames.append(index)
                    policy,value = self.model(torch.tensor(node.game.get_encodedState(), device=self.model.device).unsqueeze(0))
                    policy = torch.softmax(policy, axis=1).squeeze(0).cpu().numpy()
                    value = value.cpu().numpy()
                    policiesValues.append((policy,value))
                    
                index += 1       
                
            for i, mappingIdx in enumerate(expandable_spGames):
                node = spGames[mappingIdx].node
                spg_policy, spg_value = policiesValues[i]
                
                valid_moves, _ = node.game.get_validMoves()
                spg_policy *= valid_moves
                spg_policy /= np.sum(spg_policy)

                node.expand(spg_policy)
                node.backpropagate(spg_value)