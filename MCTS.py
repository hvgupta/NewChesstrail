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
        
        valid_moves, gg = self.game.get_validMoves()
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
                node.printDetail()
                valid_moves, gg = node.game.get_validMoves()
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



class MCTSParallel():
    def __init__(self,game:Game, args, model:ResNet):
        self.game:Game = game
        self.args = args
        self.model = model

    @torch.no_grad()
    def search(self, spGames: list[SPG]):
        policy, _ = self.model(
            torch.tensor(self.game.get_encodedState(), device=self.model.device)
        )
        policy = torch.softmax(policy, axis=1).cpu().numpy()
        policy = (1 - self.args['dirichlet_epsilon']) * policy + self.args['dirichlet_epsilon'] \
            * np.random.dirichlet([self.args['dirichlet_alpha']] * self.game.action_size, size=policy.shape[0])
        spg:SPG
        for i, spg in enumerate(spGames):
            spg_policy = policy[i]
            valid_moves = spg.game.get_validMoves()
            spg_policy *= valid_moves
            spg_policy /= np.sum(spg_policy)

            spg.root = Node(self.game, self.args, states[i], visit_count=1)
            spg.root.expand(spg_policy)
        
        for search in range(self.args['num_searches']):
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
                    
            expandable_spGames = [mappingIdx for mappingIdx in range(len(spGames)) if spGames[mappingIdx].node is not None]
                    
            if len(expandable_spGames) > 0:
                states = np.stack([spGames[mappingIdx].node.game.get_encodedState() for mappingIdx in expandable_spGames])
                states = np.swapaxes(states,0,1)
                policy, value = self.model(
                    torch.tensor(states, device=self.model.device)
                )
                policy = torch.softmax(policy, axis=1).cpu().numpy()
                value = value.cpu().numpy()
                
            for i, mappingIdx in enumerate(expandable_spGames):
                node = spGames[mappingIdx].node
                spg_policy, spg_value = policy[i], value[i]
                
                valid_moves = node.game.get_validMoves()
                spg_policy *= valid_moves
                spg_policy /= np.sum(spg_policy)

                node.expand(spg_policy)
                node.backpropagate(spg_value)