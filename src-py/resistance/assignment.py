'''
Assignement Test Bed

This module holds the comparative analysis of squads of different types 
playing against each other.  This involves
'''

# Standard Modules
import logging
import random

# Custom Game Modules
from game import Game
from custom_games import AllocatedAgentsGame

# Custom Agents
from agent import Agent
from agent.random_agent import RandomAgent
from agent.deterministic_agent import DeterministicAgent
from agent.bayesian_agent import BayesianAgent

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
    squad_creator = None

    def __init__(self, number_of_games=100):

        self.number_of_games = number_of_games
        self.squad_creator = SquadCreator()

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
            agents = self.squad_creator.create_with_agent_defined_roles(agent_count, agent_class, agent_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(game_type.__name__, i))

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_randomly()

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")


    def test_classes_by_type(self, game_type, resistance_class, spy_class):

        wins = 0
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_with_agent_defined_roles(agent_count, resistance_class, spy_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(game_type.__name__, i))

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_by_type(spy_class)

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")


    def test_classes_by_selected_spy(self, custom_class, is_spy, resistance_class, spy_class):

        wins = 0

        player_type = "RES"
        if is_spy:
            player_type = "SPY"

        for i in range(0, self.number_of_games):
            custom_agent = custom_class(name="{}_PLANTED_IN_RANDOM_POOL".format(player_type))
            agents = self.squad_creator.replace_single_agent_in_squad(custom_agent, agent_count, is_spy, resistance_class, spy_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(AllocatedAgentsGame.__name__, i))

            game = AllocatedAgentsGame(agents)

            if is_spy:
                game.allocate_single_spy(custom_agent.name)
            else:
                game.allocate_single_resistance(custom_agent.name)

            wins += self._play_game(game, agents)

        logging.info("RESISTANCE SUCCESS RATE: " + str(round((wins/self.number_of_games) * 100, 3)) + "%")
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

        for i in range(0, SPY_COUNT[agent_count]):
            agent_id = 'SPY_{}_{}'.format(spy_agent.__name__, i)
            agents.append(spy_agent(name=agent_id))

        while len(agents) < agent_count:

            agent_id = 'RES_{}_{}'.format(resistance_agent.__name__, i)
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

    def replace_single_agent_in_squad(self, custom_agent, agent_count, is_spy, resistance_agent=RandomAgent, spy_agent=RandomAgent):
        '''Replaces either a single spy or a single resistance member in a previously
        defined squad'''

        agents = self.create_with_agent_defined_roles(agent_count, resistance_agent, spy_agent)

        search_term = 'RES'
        if is_spy:
            search_term = 'SPY'

        replacement_agent_index = None
        for agent in agents:
            if search_term in agent.name:
                replacement_agent_index = agents.index(agent)

        agents[replacement_agent_index] = custom_agent

        return agents


def debug_log_setup():

    logging.basicConfig(
        filename='./logs/debug.log',
        level=logging.DEBUG,
        filemode='w')


class InvalidAgentException(Exception):
    '''Raise when something is passed to an agent creator that is not derived
    from the Agent class'''

if __name__ == '__main__':

    debug_log_setup()
    tester = AgentTester(1000)

    print("\n" + "#" * 50 + "\n")

    for agent_count in range(5, 11):

        print("\nRUNNING GAMES OF {} PLAYERS".format(agent_count))
        logging.debug("\n\nRUNNING GAMES OF {} PLAYERS".format(agent_count))

        '''# Test RandomAgent Success/Fail
        print("\nALL RANDOM AGENTS")
        logging.debug("\nALL RANDOM AGENTS")
        tester.test_single_class(Game, RandomAgent)

        # Test RandomAgent Success/Fail
        print("\nALL DETERMINISTIC AGENTS")
        logging.debug("\nALL DETERMINISTIC AGENTS")
        tester.test_single_class(Game, DeterministicAgent)

        # Test DeterministicAgent vs RandomAgent Success/Fail
        print("\nDETERMINISTIC (RES) VS RANDOM (SPY) AGENTS")
        logging.debug("\nDETERMINISTIC (RES) VS RANDOM (SPY) AGENTS")
        tester.test_classes_by_type(Game, DeterministicAgent, RandomAgent)

        # Test RandomAgent vs DeterministicAgent Success/Fail
        print("\nRANDOM (RES) VS DETERMINISTIC (SPY) AGENTS")
        logging.debug("\nRANDOM (RES) VS DETERMINISTIC (SPY) AGENTS")
        tester.test_classes_by_type(Game, RandomAgent, DeterministicAgent)

        # Single DETERMINISTIC Spy Amongst Random Agents
        print("\nSINGLE DETERMINISTIC SPY IN RANDOM")
        logging.debug("\nSINGLE DETERMINISTIC SPY IN RANDOM")
        tester.test_classes_by_selected_spy(DeterministicAgent, True, RandomAgent, RandomAgent)

        # Single DETERMINISTIC Spy Amongst Random Agents
        print("\nSINGLE DETERMINISTIC RESISTANCE IN RANDOM")
        logging.debug("\nSINGLE DETERMINISTIC RESISTANCE IN RANDOM")
        tester.test_classes_by_selected_spy(DeterministicAgent, False, RandomAgent, RandomAgent)'''

        # Test BayesianAgent vs DeterministicAgent Success/Fail
        print("\nBAYESIAN (RES) VS DETERMINISTIC (SPY) AGENTS")
        logging.debug("\nBAYESIAN (RES) VS DETERMINISTIC (SPY) AGENTS")
        tester.test_classes_by_type(Game, BayesianAgent, DeterministicAgent)

        # Test BayesianAgent vs DeterministicAgent Success/Fail
        print("\nDETERMINISTIC (RES) VS BAYESIAN (SPY) AGENTS")
        logging.debug("\nDETERMINISTIC (RES) VS BAYESIAN (SPY) AGENTS")
        tester.test_classes_by_type(Game, DeterministicAgent, BayesianAgent)


        print("\n\n" + "#" * 50 + "\n")
