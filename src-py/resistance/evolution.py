'''
Evolution 

'''

import logging

from genetics import AgentGenetics
from genetics import AgentOriginator

from agent.bayesian_agent import BayesianAgent

class AgentWorld():
    '''Starts off the cycle of evolution'''

    agents = None

    def __init__(self):

        self.agents = list()

    def genesis(self, agent_generator, number_of_players):

        if number_of_players < 5 or number_of_players > 10:
            raise Exception("Invalid Player Range")

        while len(self.agents) < number_of_players:
            self.agents.append(agent_generator.create(BayesianAgent))
        
        for agent in self.agents:
            logging.debug(agent.genetics)
        
def debug_log_setup():

    logging.basicConfig(
        filename='./logs/debug.log',
        level=logging.DEBUG,
        filemode='w')

def main():
    '''Starter function'''

    debug_log_setup()

    agent_generator = AgentOriginator()

    world = AgentWorld()
    world.genesis(agent_generator, 5)


if __name__ == '__main__':
    main()
