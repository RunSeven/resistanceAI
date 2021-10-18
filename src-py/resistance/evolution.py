'''
Evolution 

'''

import logging

from custom_games import AllocatedAgentsGame

from genetics import AgentGenetics
from genetics import AgentOriginator

from agent.bayesian_agent import BayesianAgent
from agent.deterministic_agent import DeterministicAgent

class AgentWorld():
    '''Starts off the cycle of evolution'''

    def __init__(self):

        self.agents = dict()


    def genesis(self, agent_generator, number_of_players):

        if number_of_players < 5 or number_of_players > 10:
            raise Exception("Invalid Player Range")

        while len(self.agents) < number_of_players:
            self.agents[agent_generator.create(BayesianAgent)] = {'resistance': 0, 'spy': 0}
        
        for agent in self.agents:
            logging.debug("GENETICS: {}".format(str(agent.genetics)))

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
                
    
    def trial_of_the_champions(self, number=1000):
        '''Run number of games and select the player with the most wins'''

        for simulation in range(0, number):
            self.run_single_game()

        print("\n", "#" * 50)

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
                
            
            print("\n")
            print(agent, "\n", agent.genetics, "\n", agent.penalties, "\n", self.agents[agent]['resistance'], "\n", self.agents[agent]['spy'])
        
        print("\n", "#" * 50, "\n")

        print("#1: ", agent_superior_1)
        print("#2: ", agent_superior_2)


        
def debug_log_setup():

    logging.basicConfig(
        filename='./logs/debug.log',
        level=logging.DEBUG,
        filemode='w')

def main():
    '''Starter function'''

    #debug_log_setup()

    agent_generator = AgentOriginator()

    world = AgentWorld()
    world.genesis(agent_generator, 5)
    world.trial_of_the_champions(100)

    


if __name__ == '__main__':
    main()
