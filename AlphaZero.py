from MCTS import *
from game import *
from SPG import *
import random

class AlphaZero():
    def __init__(self, model, optimizer, game, args)->None:
        self.model: ResNet = model
        self.optimizer = optimizer
        self.game:Game = game
        self.args = args
        self.mcts = MCTS(game, args, model)
        
    def selfPlay(self):
        memory= []
        player = Colour.w.value
        
        game = self.game
        while True:
            neutral_state = game
            action_probs = self.mcts.search()
            
            memory.append((neutral_state, action_probs, player))
            
            temperature_action_probs = action_probs ** (1 / self.args['temperature'])
            temperature_action_probs /= np.sum(temperature_action_probs)
            
            if self.game.validMovesNum  != 0:
                
                action = np.random.choice(3288, p=temperature_action_probs) # Divide temperature_action_probs with its sum in case of an error
                
                state = self.game.move_piece(action)
                
            value, is_terminal = self.game.valueAndterminated()
            
            if is_terminal:
                returnMemory = []
                for hist_neutral_state, hist_action_probs, hist_player in memory:
                    hist_outcome = value if hist_player == player else -value
                    returnMemory.append((
                        hist_neutral_state.get_encodedState(),
                        hist_action_probs,
                        hist_outcome
                    ))
                return returnMemory
            
            player *= -1
            game = Game(state[0],state[1],game.WhiteK, game.BlackK, player, game.board)
            
    def train(self, memory):
        games:Game
        random.shuffle(memory)
        for batchIdx in range(0, len(memory), self.args['batch_size']):
            sample = memory[batchIdx:min(len(memory) - 1, batchIdx + self.args['batch_size'])] # Change to memory[batchIdx:batchIdx+self.args['batch_size']] in case of an error
            games, policy_targets, value_targets = zip(*sample)
            
            policy_targets, value_targets = np.array(policy_targets), np.array(value_targets).reshape(-1, 1)
            
            games = torch.tensor(games.get_encodedState(), dtype=torch.float32, device=self.model.device)
            policy_targets = torch.tensor(policy_targets, dtype=torch.float32, device=self.model.device)
            value_targets = torch.tensor(value_targets, dtype=torch.float32, device=self.model.device)
            
            out_policy, out_value = self.model(games.get_encodedState())
            
            policy_loss = F.cross_entropy(out_policy, policy_targets)
            value_loss = F.mse_loss(out_value, value_targets)
            loss = policy_loss + value_loss
            
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

    def learn(self):
        for iteration in range(self.args['num_iterations']):
            memory = []
            
            self.model.eval()
            for selfPlay_iteration in range(self.args['num_selfPlay_iterations']):
                memory += self.selfPlay()
                
            self.model.train()
            for epoch in range(self.args['num_epochs']):
                self.train(memory)
            
            torch.save(self.model.state_dict(), f"model_{iteration}_{self.game}.pt")
            torch.save(self.optimizer.state_dict(), f"optimizer_{iteration}_{self.game}.pt")


class AlphaZeroParallel:
    def __init__(self, model, optimizer, game, args):
        self.model: ResNet = model
        self.optimizer = optimizer
        self.game:Game = game
        self.args = args
        self.mcts = MCTSParallel(game, args, model)
        
    def selfPlay(self):
        return_memory = []
        player = 1
        spGames = [SPG() for spg in range(self.args['num_parallel_games'])]
        
        while len(spGames) > 0:
            # states = np.stack([[spg.game.white_pList, spg.game.black_pList] for spg in spGames])
            
            self.mcts.search(spGames)
            
            for i in range(len(spGames))[::-1]:
                spg = spGames[i]
                
                action_probs = np.zeros(3288)
                for child in spg.root.children:
                    action_probs[child.action_taken] = child.visit_count
                action_probs /= np.sum(action_probs)

                spg.memory.append((spg.root.game, action_probs, player))

                temperature_action_probs = action_probs ** (1 / self.args['temperature'])
                action = np.random.choice(3288, p=temperature_action_probs) # Divide temperature_action_probs with its sum in case of an error

                white_pList, black_pList, WhiteK, BlackK, board = spg.game.move_piece(action)
                spg.game = Game(white_pList,black_pList,WhiteK,BlackK, spg.game.turn*-1, board)

                value, is_terminal = self.game.valueAndterminated()

                if is_terminal:
                    for hist_neutral_state, hist_action_probs, hist_player in spg.memory:
                        hist_outcome = value if hist_player == player else -value
                        return_memory.append((
                            hist_neutral_state.get_encodedState(),
                            hist_action_probs,
                            hist_outcome
                        ))
                    del spGames[i]
                    
            player *= -1
            
        return return_memory
                
    def train(self, memory):
        games:Game
        random.shuffle(memory)
        for batchIdx in range(0, len(memory), self.args['batch_size']):
            sample = memory[batchIdx:min(len(memory) - 1, batchIdx + self.args['batch_size'])] # Change to memory[batchIdx:batchIdx+self.args['batch_size']] in case of an error
            games, policy_targets, value_targets = zip(*sample)
            
            policy_targets, value_targets = np.array(policy_targets), np.array(value_targets).reshape(-1, 1)
            
            games = torch.tensor(games.get_encodedState(), dtype=torch.float32, device=self.model.device)
            policy_targets = torch.tensor(policy_targets, dtype=torch.float32, device=self.model.device)
            value_targets = torch.tensor(value_targets, dtype=torch.float32, device=self.model.device)
            
            out_policy, out_value = self.model(games.get_encodedState())
            
            policy_loss = F.cross_entropy(out_policy, policy_targets)
            value_loss = F.mse_loss(out_value, value_targets)
            loss = policy_loss + value_loss
            
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()
    
    def learn(self):
        for iteration in range(self.args['num_iterations']):
            memory = []
            
            self.model.eval()
            for selfPlay_iteration in range(self.args['num_selfPlay_iterations'] // self.args['num_parallel_games']):
                memory += self.selfPlay()
                
            self.model.train()
            for epoch in range(self.args['num_epochs']):
                self.train(memory)
            
            torch.save(self.model.state_dict(), f"model_{iteration}_{self.game}.pt")
            torch.save(self.optimizer.state_dict(), f"optimizer_{iteration}_{self.game}.pt")