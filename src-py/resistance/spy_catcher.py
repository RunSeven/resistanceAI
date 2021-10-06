'''
Author:             Simon McGee
Student Number:     19800483

As the name would suggest the purpose of this agent is to work primarily as a
resistance player and determine who spies are.  Effort to include play as a
spy is minimal
'''


from agent import Agent
import random


class SpyCatcher19800483(Agent):
    '''Agent with a focus on determining who is a spy. Plays a spy poorly'''

    #Default Inputs
    number_of_players = None
    player_number = None
    spy_list = list()

    #Holds info on whether a player is likely to be a spy
    players = None

    def __init__(self, name='SpyCatcher19800483'):
        '''Assign name and set play mode to non-spy as a default setting'''

        self.name = name
        self.spy = False

    def new_game(self, number_of_players, player_number, spies):
        '''Different play numbers might require different methods'''

        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spy_list = spies

        self.determine_play_mode()

    def determine_play_mode(self):
        '''Sets up the play mode as either a resistance member or spy with initial
        stats accordingly'''

        spies = self.spy_count[self.number_of_players]
        spy_probability = spies / (self.number_of_players - 1)

        self.players = {player: spy_probability for player in range(0, self.number_of_players)}
        self.is_spy()

    def is_spy(self):
        '''Set the play mode of the Agent as either resistance or spy
        '''

        if self.player_number in self.spy_list:
            self.spy = True
        
        return self.spy

    def propose_mission(self, team_size, betrayals_required=1):
        '''
        expects a team_size list of distinct agents with id between 0 (inclusive)
        and number_of_players (exclusive) to be returned.
        betrayals_required are the number of betrayals required for the mission to fail.
        '''
        team = []
        while len(team) < team_size:
            agent = random.randrange(team_size)
            if agent not in team:
                team.append(agent)
        return team

    def vote(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the
        player who proposed the mission.
        The function should return True if the vote is for the mission, and False if
        the vote is against the mission.
        '''
        print("PROPOSER: ", proposer)
        return random.random() < 0.5

    def vote_outcome(self, mission, proposer, votes):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player
        who proposed the mission.
        votes is a dictionary mapping player indexes to Booleans (True if they voted for
        the mission, False otherwise).
        No return value is required or expected.
        '''
        print("VOTING OUTCOMES: ", votes)

    def betray(self, mission, proposer):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_
        of_players, and include this agent.
        proposer is an int between 0 and number_of_players and is the index of the
        player who proposed the mission.
        The method should return True if this agent chooses to betray the mission,
        and False otherwise.
        By default, spies will betray 30% of the time.
        '''
        if self.is_spy():
            return random.random() < 0.3

        return False

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''
        mission is a list of agents to be sent on a mission.
        The agents on the mission are distinct and indexed between 0 and number_of_players.
        proposer is an int between 0 and number_of_players and is the index of the player
        who proposed the mission. Betrayals is the number of people on the mission who
        betrayed the mission, and mission_success is True if there were not enough
        betrayals to cause the mission to fail, False otherwise. It is not expected or
        required for this function to return anything.
        '''
        # nothing to do here


    def round_outcome(self, rounds_complete, missions_failed):
        '''
        basic informative function, where the parameters indicate:
        rounds_complete, the number of rounds (0-5) that have been completed
        missions_failed, the numbe of missions (0-3) that have failed.
        '''
        # nothing to do here


    def game_outcome(self, spies_win, spies):
        '''
        basic informative function, where the parameters indicate:
        spies_win, True iff the spies caused 3+ missions to fail
        spies, a list of the player indexes for the spies.
        '''
        # nothing to do here
