'''
Evolution 

'''

import logging

from custom_games import AllocatedAgentsGame

from genetics import AgentGenetics
from genetics import AgentOriginator

from agent.bayesian_agent import BayesianAgent

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
                
    
    def trial_of_the_champions(self, n=1000):
        '''Run 'n' games and select the player with the most wins'''

        for simulation in range(0, n):
            self.run_single_game()

        print("\n", "#" * 50)

        agent_superior = None
        for agent in self.agents:
            if not agent_superior:
                agent_superior = agent
            elif (self.agents[agent]['spy'] + self.agents[agent]['resistance'] ) > (self.agents[agent_superior]['spy'] + self.agents[agent_superior]['resistance'] ):
                agent_superior = agent
            
            print("\n")
            print(agent, "\n", agent.genetics, "\n", agent.penalties, "\n", self.agents[agent]['resistance'], "\n", self.agents[agent]['spy'])
        
        print("\n", "#" * 50, "\n")

        
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
    world.trial_of_the_champions()

    


if __name__ == '__main__':
    main()
