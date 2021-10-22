'''
Evolution 

'''

import logging

from custom_games import AllocatedAgentsGame

from genetics import AgentOriginator
from assignment import AgentTester, SquadCreator

from agent.bayesian_agent import BayesianAgent
from agent.deterministic_agent import DeterministicAgent

class AgentWorld():
    '''Starts off the cycle of evolution'''

    def __init__(self):

        self.agents = dict()


    def genesis(self, agent_generator, number_of_players, agents=dict()):
        '''Genesis uses an agent generator to generate new agents based on the
        number of players.  Agents can be brought into the world using the agents
        input but defaults to a new world empty of agents'''

        self.agents = dict()

        if number_of_players < 5 or number_of_players > 10:
            raise Exception("Invalid Player Range")

        while len(self.agents) < number_of_players:
            self.agents[agent_generator.create(BayesianAgent)] = {'resistance': 0, 'spy': 0, 'spies_found': 0}
    
    def training_ground(self, agent_count, agent_class, number_of_games=1000):
        '''Train agent against Bayesian non-collusion'''

        wins = 0
        squad_creator = SquadCreator()
        for i in range(0, self.number_of_games):

            game = AllocatedAgentsGame(self.agents)
            game.test_classes_by_selected_spy()

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins
    def run_single_game(self):
        '''Run a single instance of a game'''

        game = AllocatedAgentsGame(list(self.agents.keys()))
        game.allocate_spies_randomly()
        game.play()

        for agent in self.agents:
            
            if agent.winner:

                if agent.is_spy():
                    self.agents[agent]['spy'] += 1
                    continue
                
                self.agents[agent]['resistance'] += 1
            
            self.agents[agent]['spies_found'] += agent.correctly_identified_spies

               
    
    def trial_of_the_champions(self, number=1000):
        '''Run number of games and select the player with the most wins'''

        for simulation in range(0, number):
            self.run_single_game()

        #print("\n", "#" * 50)

        agent_superior_1 = None
        agent_superior_2 = None
        for agent in self.agents:
            if not agent_superior_1:
                agent_superior_1 = agent
            elif (self.agents[agent]['spy'] + self.agents[agent]['resistance'] ) > (self.agents[agent_superior_1]['spy'] + self.agents[agent_superior_1]['resistance'] ):
                agent_superior_2 = agent_superior_1
                agent_superior_1 = agent
            else:
                agent_superior_2 = agent
                

        #print("\n", "#" * 50, "\n")
        total_wins_1 = self.agents[agent_superior_1]['resistance'] + self.agents[agent_superior_1]['spy']
        #print("#2: ", agent_superior_1, " : ", total_wins_1)
        total_wins_2 = self.agents[agent_superior_2]['resistance'] + self.agents[agent_superior_2]['spy']
        #print("#2: ", agent_superior_2, " : ", total_wins_2)

        return total_wins_1, self.agents[agent_superior_1]['resistance'], self.agents[agent_superior_1]['spy'], self.agents[agent_superior_1]['spies_found'], agent_superior_1


        
def debug_log_setup():

    logging.basicConfig(
        filename='./logs/debug.log',
        level=logging.DEBUG,
        filemode='w')


def brute_force_selection():

    #debug_log_setup()

    agent_generator = AgentOriginator()

    world = AgentWorld()

    prev_best_agent = None
    prev_best_catcher = None
    last_total_wins = 0
    total_wins = 0
    resistance_wins = 0
    agent = None
    last_spies_found = 0
    spies_found = 0
    while total_wins < 80:

        agents = dict()
        if prev_best_agent != None:
            agents[prev_best_agent] = {'resistance': 0, 'spy': 0, 'spies_found': 0}
            agents[prev_best_catcher] = {'resistance': 0, 'spy': 0, 'spies_found': 0}

        world.genesis(agent_generator, 5, agents)

        total_wins, resistance_wins, spy_wins, spies_found, agent = world.trial_of_the_champions(100)

        if last_total_wins < total_wins:
            last_total_wins = total_wins            
            prev_best_agent = agent
            print("\nWINNER UPDATE")
        
        if last_spies_found < spies_found:
            last_spies_found = spies_found      
            prev_best_catcher = agent
            print("\nSPY CATCHER UPDATE")
        
def main():
    '''Starter function'''

    debug_log_setup()

    agent_generator = AgentOriginator()

    world = AgentWorld()
    world.genesis(agent_generator, 5)
    world.trial_of_the_champions(100)


if __name__ == '__main__':
    brute_force_selection()
