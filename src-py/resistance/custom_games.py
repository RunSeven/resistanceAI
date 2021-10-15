'''
Custom Games

The original Game class has a tightly coupled spy allocation and gming
system.  This module allows for greater diversity in selecting whether
and agent is randomly assigned a role or specifically assigned
to either the resistance or spy groups
'''

# Standard Modules
import logging
import random

# Game Play Modules
from game import Round
from agent import Agent


class AllocatedAgentsGame():
    '''Allocates Spies and Resistance using Agent Type
    to choose play type'''

    # Setup Game Space
    agents = None
    number_of_players = None
    spies = None

    def __init__(self, agents):

        if len(agents) < 5 or len(agents) > 10:
            raise Exception('Agent array out of range')

        self._setup_agents(agents)
        
    def _setup_agents(self, agents):

        self.agents = agents.copy()
        random.shuffle(self.agents)
        self.number_of_players = len(agents)
        self.spies = list()

    def allocate_spies_by_type(self, spy_class):
        '''Allocate spies and resistance randomly'''

        self.spies = [self.agents.index(agent) for agent in self.agents if isinstance(agent, spy_class)]
        
        if len(self.spies) != Agent.spy_count[self.number_of_players]:
            message = "Spy count does not match the number of spies required"
            raise SpyAllocationException(message)

        self._initialise_agents()
        self._initialise_rounds()
    
    def allocate_spies_randomly(self):
        '''Allocate spies and resistance randomly'''

        while len(self.spies) < Agent.spy_count[self.number_of_players]:
            spy = random.randrange(self.number_of_players)
            if spy not in self.spies:
                self.spies.append(spy)
        
        self._initialise_agents()
        self._initialise_rounds()
        
    def _initialise_agents(self):

        for player_number in range(self.number_of_players):
            spy_list = self.spies.copy() if player_number in self.spies else []
            self.agents[player_number].new_game(self.number_of_players, player_number, spy_list)
    
    def _initialise_rounds(self):

        self.rounds = list()
        self.missions_lost = 0


    def play(self):

        if len(self.spies) == 0:
            exception_message = "Spies have not been allocated"
            raise UnallocatedSpiesException(exception_message)

        leader_id = 0
        for i in range(5):
            logging.debug("STARTING ROUND {}".format(i))
            self.rounds.append(Round(leader_id, self.agents, self.spies, i))
            
            if not self.rounds[i].play():
                self.missions_lost += 1

            for a in self.agents:
                a.round_outcome(i+1, self.missions_lost)

            leader_id = (leader_id+len(self.rounds[i].missions)) % len(self.agents)

        for a in self.agents:
            a.game_outcome(self.missions_lost > 2, self.spies)


class UnallocatedSpiesException(Exception):
    '''Raise when the spies have not been allocated'''


class SpyAllocationException(Exception):
    '''Raise when the attempt number of spies created does not match the
    expected count
    '''
