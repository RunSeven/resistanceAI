'''
Assignement Test Bed

This module holds all of the code to play agents, setup squads of agents
to play Resistance.  It also setups logging and create output for analysis
'''

# Standard Modules
import logging
import random

# Custom Game Modules
from game import Game
from custom_games import AllocatedAgentsGame

# Custom Agents
from agent import Agent
from random_agent import RandomAgent
from reflex_agent import ReflexAgent
from bom_agent import BayesianAgent

# Global Variables
MISSION_SIZES = {
    5: [2, 3, 2, 3, 3],
    6: [2, 3, 4, 3, 4],
    7: [2, 3, 3, 4, 4],
    8: [3, 4, 4, 5, 5],
    9: [3, 4, 4, 5, 5],
    10: [3, 4, 4, 5, 5]
}

SPY_COUNT = {5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4}


FAILS_REQUIRED = {
    5: [1, 1, 1, 1, 1],
    6: [1, 1, 1, 1, 1],
    7: [1, 1, 1, 2, 1],
    8: [1, 1, 1, 2, 1],
    9: [1, 1, 1, 2, 1],
    10: [1, 1, 1, 2, 1]
}


class AgentTester():
    '''Tests Agents in various ways by runnings tests, allocating
    agents to different roles etc.'''

    number_of_games = None

    def __init__(self, number_of_games=100):

        self.number_of_games = number_of_games

    def _play_game(self, game, agents):

        game.play()
        success = game.missions_lost < 3

        if success:
            return 1

        return 0

    def test_single_class(self, game_type, agent_class):

        wins = 0
        squad_creator = SquadCreator()
        for i in range(0, self.number_of_games):
            agents = squad_creator.create_with_agent_defined_roles(agent_count, agent_class, agent_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(game_type.__name__, i))

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_randomly()

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")


    def test_classes_by_type(self, game_type, resistance_class, spy_class):

        wins = 0
        squad_creator = SquadCreator()
        for i in range(0, self.number_of_games):
            agents = squad_creator.create_with_agent_defined_roles(agent_count, resistance_class, spy_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(game_type.__name__, i))

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_by_type(spy_class)

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")


class SquadCreator():
    '''Creates the group of agents to undertake resistance work'''

    def __init__(self):
        pass

    def create_with_agent_defined_roles(self, agent_count, resistance_agent=RandomAgent, spy_agent=RandomAgent):
        '''Create a squad where resistance and spy roles are pre-determined
        by their agent type.  This is equivalent to random selections
        when both agent types are the same'''

        agents = []
        #print("GENERATING SQUAD OF {} RESISTANCE MEMBERS".format(agent_count))
        #logging.info("GENERATING SQUAD OF {} RESISTANCE MEMBERS".format(agent_count))

        for i in range(0, SPY_COUNT[agent_count]):
            agent_id = 'SPY_{}_{}'.format(spy_agent.__name__, i)
            #print("ADDING {} TO SQUAD".format(agent_id))
            agents.append(spy_agent(name=agent_id))

        while len(agents) < agent_count:

            agent_id = 'RES_{}_{}'.format(resistance_agent.__name__, i)
            #print("ADDING {} TO SQUAD".format(agent_id))
            agents.append(resistance_agent(name=agent_id))

        return agents

    def create_single_agent_squad(self, agent_count, single_agent):

        agents = []

        if RandomAgent().__class__.__bases__[0].__name__ != 'Agent':
            message = "{} does not appear to be a valid Agent".format(single_agent)
            raise InvalidAgentException(message)

        for i in range(0, agent_count):

            agent_id = 'X_{}'.format(i)
            agents.append(single_agent(name=agent_id))

        return agents




def debug_log_setup():

    logging.basicConfig(
        filename='./logs/debug.log', level=logging.DEBUG)


class InvalidAgentException(Exception):
    '''Raise when something is passed to an agent creator that is not derived
    from the Agent class'''

if __name__ == '__main__':

    debug_log_setup()
    tester = AgentTester(1000)

    for agent_count in range(5, 11):

        print("\nRUNNING GAMES OF {} PLAYERS".format(agent_count))
        logging.debug("\n\nRUNNING GAMES OF {} PLAYERS".format(agent_count))

        # Test RandomAgent Success/Fail
        print("\nALL RANDOM AGENTS")
        logging.debug("\nALL RANDOM AGENTS")        
        tester.test_single_class(Game, RandomAgent)

        # Test RandomAgent vs ReflexAgent Success/Fail
        print("\nREFLEX (RES) VS RANDOM (SPY) AGENTS")
        logging.debug("\nREFLEX (RES) VS RANDOM (SPY) AGENTS")        
        tester.test_classes_by_type(Game, BayesianAgent, RandomAgent)

        # Test RandomAgent vs ReflexAgent Success/Fail
        print("\nRANDOM (RES) VS REFLEX (SPY) AGENTS")
        logging.debug("\nRANDOM (RES) VS REFLEX (SPY) AGENTS")        
        tester.test_classes_by_type(Game, RandomAgent, BayesianAgent)

