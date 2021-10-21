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
    '''Tests Agents by running games of various sizes against with preconfigured setups
    to determine the how well agents work in different scenarios.'''

    number_of_games = None
    squad_creator = None

    def __init__(self, number_of_games=1000):

        self.number_of_games = number_of_games
        self.squad_creator = SquadCreator()

    def _play_game(self, game, agents):
        '''Play a game with a preconfigured agent'''

        game.play()
        success = game.missions_lost < 3

        if success:
            return 1

        return 0

    def test_single_class(self, agent_class):
        '''Play a game using a single agent type as both spies and resistance'''

        wins = 0
        squad_creator = SquadCreator()
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_with_agent_defined_roles(agent_count, agent_class, agent_class)

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_randomly()

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins
    

    def test_colluding_single_class(self, agent_class):
        '''Play a game with a single agent type in which the spies have implemented collusion'''

        wins = 0
        squad_creator = SquadCreator()
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_collusive_single_agent_squad(agent_count, agent_class)

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_randomly()

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins
    
    def test_randomly_colluding_single_class(self, collusion_probability, agent_class):
        '''Play a game where collusion is on only for some of the agents depending on the provided probability that they
        will collude'''

        wins = 0
        squad_creator = SquadCreator()
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_random_collusion_with_agent_defined_roles(agent_count, collusion_probability, agent_class, agent_class)

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_randomly()

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins
    

    def test_colluding_classes_by_type(self, resistance_class, spy_class):

        wins = 0
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_collusion_with_agent_defined_roles(agent_count, resistance_class, spy_class)

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_by_type(spy_class)

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins
    
    def test_randomly_colluding_classes_by_type(self, collusion_probability, resistance_class, spy_class):

        wins = 0
        
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_random_collusion_with_agent_defined_roles(agent_count, collusion_probability, resistance_class, spy_class)

            logging.debug("\n\nNEW GAME ({}) {}".format(game_type.__name__, i))

            game = AllocatedAgentsGame(agents)
            game.allocate_spies_by_type(spy_class)

            wins += self._play_game(game, agents)

        print("RESISTANCE SUCCESS RATE: ", round((wins/self.number_of_games) * 100, 3), "%")

        return wins


    def test_classes_by_type(self, resistance_class, spy_class):

        wins = 0
        for i in range(0, self.number_of_games):
            agents = self.squad_creator.create_with_agent_defined_roles(agent_count, resistance_class, spy_class)

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
        '''Create a squad with a single agent type.  Spies can be assigned randomly'''

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
        '''Create a squad of a single agent type in which the spies collude'''

        agents = self.create_single_agent_squad(agent_count, single_agent)

        for agent in agents:

            if 'collusion' in agent.__class__.__dict__:
                agent.collusion_mode_on()

        return agents
    
    def create_collusion_with_agent_defined_roles(self, agent_count, resistance_agent=DeterministicAgent, spy_agent=DeterministicAgent):
        '''Create a squad where each agent type is allocated a specific type, either resistance or spy'''

        agents = self.create_with_agent_defined_roles(agent_count, resistance_agent, spy_agent)

        for agent in agents:

            if 'collusion' in agent.__class__.__dict__:
                agent.collusion_mode_on()

        return agents
    
    def create_random_collusion_with_agent_defined_roles(self, agent_count, collusion_probability, resistance_agent=DeterministicAgent, spy_agent=DeterministicAgent):
        '''Create a squad with collusive spies in which the spies only act collusively with a pre-defined probability'''

        agents = self.create_with_agent_defined_roles(agent_count, resistance_agent, spy_agent)

        for agent in agents:

            if 'collusion' in agent.__class__.__dict__:

                if random.random() < collusion_probability:
                    agent.collusion_mode_on()
                else:
                    agent.collusion_mode_off()

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
        collusion_probabilities = [0.95, 0.8, 0.65, 0.5, 0.25]

        print("\nALL {} AGENTS".format(primary_agent))
        homogenous_label = "all_{}".format(primary_agent) 
        agent_type_outcomes[homogenous_label] = tester.test_single_class(Game, agent_models[primary_agent])

        for secondary_agent in agent_models.keys():

            if primary_agent != secondary_agent:
            
                a_vs_b = "{} Resistance vs {} Spies".format(primary_agent, secondary_agent) 
                print("\n{} RESISTANCE VS {} SPIES".format(
                    primary_agent,
                    secondary_agent
                ))
                agent_type_outcomes[a_vs_b] = tester.test_classes_by_type(Game, agent_models[primary_agent], agent_models[secondary_agent])

                single_spy = "Single {} Spy amongst {} Spies".format(primary_agent, secondary_agent)
                print("\nSINGLE {} SPY AMONGST {} AGENTS".format(primary_agent, secondary_agent))            
                agent_type_outcomes[single_spy] = tester.test_classes_by_selected_spy(agent_models[primary_agent], True, RandomAgent, RandomAgent)

                single_resistance = "Single {} Resistance amongst {} Agents".format(primary_agent, secondary_agent)
                print("\nSINGLE {} RESISTANCE AMONGST {} AGENTS".format(primary_agent, secondary_agent))            
                agent_type_outcomes[single_resistance] = tester.test_classes_by_selected_spy(DeterministicAgent, False, RandomAgent, RandomAgent)

                # Random can't collude
                if secondary_agent == 'RANDOM':
                    continue
                
                resistance_vs_colluding = "{} Resistance amongst Colluding {} Spies".format(primary_agent, secondary_agent)
                print("\n{} RESISTANCE VS COLLUDING {} SPIES".format(primary_agent, secondary_agent))            
                agent_type_outcomes[resistance_vs_colluding] = tester.test_colluding_classes_by_type(
                    agent_models[primary_agent], 
                    agent_models[secondary_agent])


                for collusion_probability in collusion_probabilities:
                    resistance_vs_randomly_colluding = "{} Resistance amongst ({}%) Colluding {} Spies".format(primary_agent, collusion_probability * 100, secondary_agent)
                    print("\n{} RESISTANCE VS  ({}%) COLLUDING {} SPIES".format(primary_agent, collusion_probability * 100, secondary_agent))            
                    agent_type_outcomes[resistance_vs_randomly_colluding] = tester.test_randomly_colluding_classes_by_type(
                        collusion_probability,
                        agent_models[primary_agent], 
                        agent_models[secondary_agent])
            
            else:

                # Random can't collude
                if secondary_agent == 'RANDOM':
                    continue

                resistance_vs_colluding = "{} Resistance amongst Colluding {} Spies".format(primary_agent, secondary_agent)
                print("\n{} RESISTANCE VS COLLUDING {} SPIES".format(primary_agent, secondary_agent))            
                agent_type_outcomes[resistance_vs_colluding] = tester.test_colluding_single_class(
                    agent_models[primary_agent])
                

                for collusion_probability in collusion_probabilities:
                    resistance_vs_randomly_colluding = "{} Resistance amongst ({}%) Colluding {} Spies".format(primary_agent, collusion_probability * 100, secondary_agent)
                    print("\n{} RESISTANCE VS  ({}%) COLLUDING {} SPIES".format(primary_agent, collusion_probability * 100, secondary_agent))            
                    agent_type_outcomes[resistance_vs_randomly_colluding] = tester.test_randomly_colluding_single_class(
                        collusion_probability,
                        agent_models[primary_agent])
        
        n_player_outcomes.append(agent_type_outcomes)
        
    return n_player_outcomes


if __name__ == '__main__':
    '''The main function plays games under various pre-configured setups as discussed
    in the project report.  The data is then saved into a CSV file foranalysis in the report.
    '''

    # Set up testing functions with the number of games to play
    number_of_games = 100
    tester = AgentTester(number_of_games)

    # Mission Outcomes holds the information relating to each mission
    # in terms of which Agents were involved and what the results were.
    # Wins are considered as resistance wins
    mission_outcomes = dict()

    # Run through missions for the specified number of players
    for agent_count in range(5, 11):

        print("\n\nPLAYING GAMES OF SIZE {}".format(agent_count))

        # Okay, so we aren't passing agent_outcome to anything...
        # I admit it is a global variable and I realised it too late
        # to fix without risking everything else.
        mission_outcomes[agent_count] = summarise()

    # Write to CSV for analysis
    with open("./logs/summary.csv", 'w', newline="\n") as file:

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

        for key in table.keys():
            
            row = table[key].copy()
            row.insert(0, key)            
            csv_writer.writerow(row)


            