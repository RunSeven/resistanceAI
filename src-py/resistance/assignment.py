'''
Assignement Test Bed

This module holds the comparative analysis of squads of different types 
playing against each other.  This involves
'''

# Standard Modules
import csv
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

        return wins
    

    def test_colluding_single_class(self, game_type, agent_class):

        wins = 0
        squad_creator = SquadCreator()
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_collusive_single_agent_squad(agent_count, agent_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(game_type.__name__, i))

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_randomly()

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins
    

    def test_colluding_classes_by_type(self, game_type, resistance_class, spy_class):

        wins = 0
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_collusion_with_agent_defined_roles(agent_count, resistance_class, spy_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(game_type.__name__, i))

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_by_type(spy_class)

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins


    def test_classes_by_type(self, game_type, resistance_class, spy_class):

        wins = 0
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_with_agent_defined_roles(agent_count, resistance_class, spy_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(game_type.__name__, i))

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_by_type(spy_class)

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins


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

        return wins


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

        return self.create_with_agent_defined_roles(agent_count, single_agent, single_agent)

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

    def create_collusive_single_agent_squad(self, agent_count, single_agent=DeterministicAgent):

        agents = self.create_single_agent_squad(agent_count, single_agent)

        for agent in agents:

            if 'collusion' in agent.__class__.__dict__:
                agent.collusion_mode_on()

        return agents
    
    def create_collusion_with_agent_defined_roles(self, agent_count, resistance_agent=DeterministicAgent, spy_agent=DeterministicAgent):

        agents = self.create_with_agent_defined_roles(agent_count, resistance_agent, spy_agent)

        for agent in agents:

            if 'collusion' in agent.__class__.__dict__:
                agent.collusion_mode_on()

        return agents


def debug_log_setup():

    logging.basicConfig(
        filename='./logs/debug.log',
        level=logging.DEBUG,
        filemode='w')


class InvalidAgentException(Exception):
    '''Raise when something is passed to an agent creator that is not derived
    from the Agent class'''


def summarise():

    agent_models = {
        "RANDOM": RandomAgent, 
        "DETERMINISTIC": DeterministicAgent, 
        "BAYESIAN": BayesianAgent
        }
    
    n_player_outcomes = list()
    
    for primary_agent in agent_models.keys():

        agent_type_outcomes = dict()

        print("\nALL {} AGENTS".format(primary_agent))
        homogenous_label = "all_{}".format(primary_agent) 
        agent_type_outcomes[homogenous_label] = tester.test_single_class(Game, agent_models[primary_agent])

        for secondary_agent in agent_models.keys():

            if primary_agent == secondary_agent:
                continue
            
            a_vs_b = "{}_resistance_vs_{}_spies".format(primary_agent, secondary_agent) 
            print("\n{} RESISTANCE VS {} SPIES".format(
                primary_agent,
                secondary_agent
            ))
            agent_type_outcomes[a_vs_b] = tester.test_classes_by_type(Game, agent_models[primary_agent], agent_models[secondary_agent])

            single_spy = "single_{}_spy_amongst_{}_agents".format(primary_agent, secondary_agent)
            print("\nSINGLE {} SPY AMONGST {} AGENTS".format(primary_agent, secondary_agent))            
            agent_type_outcomes[single_spy] = tester.test_classes_by_selected_spy(agent_models[primary_agent], True, RandomAgent, RandomAgent)

            single_resistance = "single_{}_resistance_amongst_{}_agents".format(primary_agent, secondary_agent)
            print("\nSINGLE {} RESISTANCE AMONGST {} AGENTS".format(primary_agent, secondary_agent))            
            agent_type_outcomes[single_resistance] = tester.test_classes_by_selected_spy(DeterministicAgent, False, RandomAgent, RandomAgent)

            # Random can't collude
            if secondary_agent == 'RANDOM':
                continue
            
            single_resistance_vs_colluding = "single_{}_resistance_amongst_colluding_{}_agents".format(primary_agent, secondary_agent)
            print("\n{} RESISTANCE VS COLLUDING {} SPIES".format(primary_agent, secondary_agent))            
            agent_type_outcomes[single_resistance_vs_colluding] = tester.test_colluding_classes_by_type(
                Game, 
                agent_models[primary_agent], 
                agent_models[secondary_agent])
        
        n_player_outcomes.append(agent_type_outcomes)
        
    return n_player_outcomes


if __name__ == '__main__':

    #debug_log_setup()
    tester = AgentTester(1000)

    print("\n" + "#" * 50 + "\n")

    mission_outcomes = dict()

    for agent_count in range(5, 11):

        print("\nRUNNING GAMES OF {} PLAYERS".format(agent_count))
        logging.debug("\n\nRUNNING GAMES OF {} PLAYERS".format(agent_count))

        mission_outcomes[agent_count] = summarise()
        

        '''# Test RandomAgent Success/Fail
        print("\nALL RANDOM AGENTS")
        logging.debug("\nALL RANDOM AGENTS")
        tester.test_single_class(Game, RandomAgent)

        # Test RandomAgent Success/Fail
        print("\nALL DETERMINISTIC AGENTS")
        logging.debug("\nALL DETERMINISTIC AGENTS")
        tester.test_single_class(Game, DeterministicAgent)

        # Test RandomAgent Success/Fail
        print("\nALL BAYESIAN AGENTS")
        logging.debug("\nALL BAYESIAN AGENTS")
        tester.test_single_class(Game, BayesianAgent)

        # Test DeterministicAgent vs RandomAgent Success/Fail
        print("\nDETERMINISTIC (RES) VS RANDOM (SPY) AGENTS")
        logging.debug("\nDETERMINISTIC (RES) VS RANDOM (SPY) AGENTS")
        tester.test_classes_by_type(Game, DeterministicAgent, RandomAgent)

        # Test RandomAgent vs DeterministicAgent Success/Fail
        print("\nRANDOM (RES) VS DETERMINISTIC (SPY) AGENTS")
        logging.debug("\nRANDOM (RES) VS DETERMINISTIC (SPY) AGENTS")
        tester.test_classes_by_type(Game, RandomAgent, DeterministicAgent)

        # Test BayesianAgent vs RandomAgent Success/Fail
        print("\nBAYESIAN (RES) VS RANDOM (SPY) AGENTS")
        logging.debug("\nBAYESIAN (RES) VS RANDOM (SPY) AGENTS")
        tester.test_classes_by_type(Game, BayesianAgent, RandomAgent)

        # Test RandomAgent vs BayesianAgent Success/Fail
        print("\nRANDOM (RES) VS BAYESIAN (SPY) AGENTS")
        logging.debug("\nRANDOM (RES) VS nBAYESIAN (SPY) AGENTS")
        tester.test_classes_by_type(Game, RandomAgent, BayesianAgent)

        # Single DETERMINISTIC Spy Amongst Random Agents
        print("\nSINGLE DETERMINISTIC SPY IN RANDOM")
        logging.debug("\nSINGLE DETERMINISTIC SPY IN RANDOM")
        tester.test_classes_by_selected_spy(DeterministicAgent, True, RandomAgent, RandomAgent)

        # Single DETERMINISTIC Spy Amongst Random Agents
        print("\nSINGLE DETERMINISTIC RESISTANCE IN RANDOM")
        logging.debug("\nSINGLE DETERMINISTIC RESISTANCE IN RANDOM")
        tester.test_classes_by_selected_spy(DeterministicAgent, False, RandomAgent, RandomAgent)

        # Single Bayesian Spy Amongst Random Agents
        print("\nSINGLE BAYESIAN SPY IN RANDOM")
        logging.debug("\nSINGLE BAYESIAN SPY IN RANDOM")
        tester.test_classes_by_selected_spy(BayesianAgent, True, RandomAgent, RandomAgent)

        # Single Bayesian Spy Amongst Random Agents
        print("\nSINGLE BAYESIAN RESISTANCE IN RANDOM")
        logging.debug("\nSINGLE BAYESIAN RESISTANCE IN RANDOM")
        tester.test_classes_by_selected_spy(BayesianAgent, False, RandomAgent, RandomAgent)

        # Test BayesianAgent vs DeterministicAgent Success/Fail
        print("\nBAYESIAN (RES) VS DETERMINISTIC (SPY) AGENTS")
        logging.debug("\nBAYESIAN (RES) VS DETERMINISTIC (SPY) AGENTS")
        tester.test_classes_by_type(Game, BayesianAgent, DeterministicAgent)

        # Test BayesianAgent vs DeterministicAgent Success/Fail
        print("\nDETERMINISTIC (RES) VS BAYESIAN (SPY) AGENTS")
        logging.debug("\nDETERMINISTIC (RES) VS BAYESIAN (SPY) AGENTS")
        tester.test_classes_by_type(Game, DeterministicAgent, BayesianAgent)

        # Test RandomAgent Success/Fail
        print("\nALL DETERMINISTIC AGENTS")
        logging.debug("\nALL RANDOM AGENTS")
        tester.test_single_class(Game, DeterministicAgent)

        # Single Bayesian Spy Amongst Random Agents
        print("\nSINGLE BAYESIAN SPY IN DETERMINISTIC")
        logging.debug("\nSINGLE BAYESIAN SPY IN RANDOM")
        tester.test_classes_by_selected_spy(BayesianAgent, True, DeterministicAgent, DeterministicAgent)

        # Single Bayesian Spy Amongst Random Agents
        print("\nSINGLE BAYESIAN RESISTANCE IN DETERMINISTIC")
        logging.debug("\nSINGLE BAYESIAN RESISTANCE IN RANDOM")
        tester.test_classes_by_selected_spy(BayesianAgent, False, DeterministicAgent, DeterministicAgent)

        print("\nALL DETERMINISTIC AGENTS")
        logging.debug("\nALL RANDOM AGENTS")
        tester.test_single_class(Game, DeterministicAgent)

        # Test RandomAgent Success/Fail
        print("\nALL COLLUDING DETERMINISTIC AGENTS")
        logging.debug("\nALL COLLUDING DETERMINISTIC AGENTS")
        tester.test_colluding_single_class(Game, DeterministicAgent)

        # Test RandomAgent Success/Fail
        print("\nALL COLLUDING BAYESIAN AGENTS")
        logging.debug("\nALL COLLUDING BAYESIAN AGENTS")
        tester.test_colluding_single_class(Game, BayesianAgent)

        # Test RandomAgent Success/Fail
        print("\nBAYESIAN (RES) VS COLLUDING DETERMINISTIC (SPY) AGENTS")
        logging.debug("\nBAYESIAN (RES) VS COLLUDING DETERMINISTIC (SPY) AGENTS")
        tester.test_colluding_classes_by_type(Game, BayesianAgent, DeterministicAgent)

        # Test RandomAgent Success/Fail
        print("\nDETERMINISTIC (RES) VS COLLUDING BAYESIAN (SPY) AGENTS")
        logging.debug("\nDETERMINISTIC (RES) VS COLLUDING BAYESIAN (SPY) AGENTS")
        tester.test_colluding_classes_by_type(Game, DeterministicAgent, BayesianAgent)

        # Test RandomAgent Success/Fail
        print("\nBAYESIAN (RES) VS COLLUDING RANDOM (SPY) AGENTS")
        logging.debug("\nBAYESIAN (RES) VS COLLUDING RANDOM (SPY) AGENTS")
        tester.test_colluding_classes_by_type(Game, BayesianAgent, RandomAgent)

        # Test RandomAgent Success/Fail
        print("\nRANDOM (RES) VS COLLUDING BAYESIAN (SPY) AGENTS")
        logging.debug("\nRANDOM (RES) VS COLLUDING BAYESIAN (SPY) AGENTS")
        tester.test_colluding_classes_by_type(Game, RandomAgent, BayesianAgent)'''


        print("\n\n" + "#" * 50 + "\n")

    with open("./logs/summary.csv", 'w') as file:

        csv_writer = csv.writer(file)
        csv_writer.writerow("game_type,5_players,6_players,7_players,8_players,9_players,10_players".split(','))

        table = dict()
        print(mission_outcomes.keys())

        for agent_number in range(5, 11):
            round_number = mission_outcomes[agent_number]
            
            for agent_type in range(0,3):
                
                for key in round_number[agent_type].keys():

                    if key not in table:
                        table[key] = list()

                    table[key].append(round_number[agent_type][key])

        print(table)       
        for key in table.keys():
            
            row = table[key].copy()
            row.insert(0, key)            
            csv_writer.writerow(row)


            