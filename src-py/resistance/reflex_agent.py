'''
Reflex Agent

Gameplay:

    Resistance: Remembers known spies and works against them.
                Votes for players not known to have failed a mission.
                Has equality counter for failed missions.

    Spy:        Increases likeliness of killing mission as rounds progress.
                Increase negative votes as rounds progress.
                Supports spies in votes more as
'''

from agent import Agent
import random


class ReflexAgent(Agent):
    '''Reflex Agent has minimal understanding of the world.  Only remembers
    major game events.
    '''

    # New Game Variables
    name = None
    missions_failed = None
    number_of_players = None
    player_number = None
    spies = None

    # Custom Variables
    spy = False
    current_round = 1
    confirmed_spies = list()

    # Resistance Member to Frame
    target_resistance = list()

    def __init__(self, name='Reflex'):
        '''Assign Name and zero missions failed'''
        self.name = name
        self.missions_failed = 0

    def new_game(self, number_of_players, player_number, spies):
        '''New game setup'''

        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spies = spies

        # Set Play Status
        self.spy = self.player_number in spies
        print("SPY STATUS: ", self.player_number, self.spy)

    def is_spy(self):
        '''return spy status'''

        return self.spy

    def propose_mission(self, team_size, betrayals_required=1):
        '''Create a team based on role'''
        team = None

        # If it's the first round we just lay low
        if self.current_round == 1 or not self.spy:
            team = self._resistance_mission_proposal(team_size,
                                                     betrayals_required)
            return team

        team = self._spy_mission_proposal(team_size, betrayals_required)

        return team

    def _resistance_mission_proposal(self, team_size, betrayals_required):

        team = []
        print("RESISTANCE MISSION PROPOSAL")

        while len(team) < team_size:

            agent = random.randrange(team_size)

            # Don't include burnt agents
            if agent not in team and agent not in self.confirmed_spies:
                team.append(agent)

        random.shuffle(team)
        return team

    def _spy_mission_proposal(self, team_size, betrayals_required):

        team = []
        print("SPY MISSION PROPOSAL")

        # If agent is burnt add self to poison vote
        # otherwise poison with someone randomly
        if self.player_number in self.confirmed_spies:
            team.append(self.player_number)
        else:
            viable_spies = [spy for spy in self.spies if spy not in self.confirmed_spies]
            team.append(random.choice(viable_spies))

        while len(team) < team_size:

            agent = random.randrange(team_size)

            # Don't include burnt agents
            if agent not in team and agent not in self.confirmed_spies:
                team.append(agent)

        random.shuffle(team)
        return team

    def vote(self, mission, proposer):
        '''Determine vote based on player model'''

        print("VOTE")

        # Accept any vote in the first round
        if self.current_round == 1:
            return True

        if self.spy:

            # If self is burnt default to fail the vote
            if self.player_number in self.confirmed_spies:
                self._is_burnt_asset_vote()

            return self._spy_vote(mission, proposer)

        return self._resistance_vote(mission, proposer)

    def _spy_vote(self, mission, proposer):
        '''Decide on voting if player is a spy'''

        # Spies shouldn't vote for burnt assets
        if not all([player in mission for player in self.confirmed_spies]):
            return False

        # We are trying to frame someone so we should vote against them
        no_targets = all([target in mission for target in self.target_resistance])
        if len(self.target_resistance) != 0 and no_targets:
            return False

        # No spies in mission
        if all([team_member not in self.spies for team_member in mission]):

            # If we have breathing room then allow it
            if self.current_round - self.missions_failed > 0:
                return True
            else:
                return False

        return True

    def _resistance_vote(self, mission, proposer):
        '''Decide on voting if player is resistance'''

        # Only vote against a player if we know they are a spy
        if not all([player in mission for player in self.confirmed_spies]):
            return False

        return True

    def _is_burnt_asset_vote(self):
        '''Decide how to vote if the player is a spy and burnt asset'''

        # Try to kill all other votes based on others suscpicion
        return False

    def vote_outcome(self, mission, proposer, votes):
        '''Reflex agent cannot deal with '''

        # Anyone that votes on burnt agents is a traitor???

    def betray(self, mission, proposer):
        '''Determine whether to betray the mission'''

        print("BETRAYAL START")

        # Ensure that resistance don't betray the mission
        # by a bad function call
        if not self.spy:
            print("NOT A SPY: ", self.player_number)            
            return False

        # Determine actions when all team members are spies
        if all([team_member in self.spies for team_member in mission]):

            # Don't burn spies on the first round
            if self.current_round == 1:
                return False

            # Spies have to risk a burning event because
            if len(mission) == 2 and self.missions_failed == 0:
                return random.random() < (1/len(mission)) + 0.1

            return random.random() < (1/len(mission)) - 0.1

        # Nothing to lose in the last round
        if self.current_round == 5:
            return True

        print("BETRAYAL END")
        return True


    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''Update world understanding based on mission outcome'''

        # If all agents betray the mission they have burned themselves
        if len(mission) == betrayals:
            self.confirmed_spies.extend(mission)
            return

        # Update the agent depending on role
        if self.spy:
            self._spy_mission_outcome(mission, mission_success)
        else:
            self._resistance_mission_outcome(mission, betrayals)

    def _spy_mission_outcome(self, mission, mission_success):

        # Target a resistance member for vote blocking if
        # they could be suspect
        if not mission_success:
            targets = [resistance for resistance in mission if resistance not in self.spies]
            self.target_resistance.extend(targets)

    def _resistance_mission_outcome(self, mission, betrayals):

        # Spies become burned for the player if we are resistance,
        # and the number of remaining members
        # on the team is equivalent to the number of betrayals
        if self.player_number in mission and betrayals == len(mission) - 1:
            known_spies = [spy for spy in mission if spy != self.player_number]
            self.confirmed_spies.extend(known_spies)

    def round_outcome(self, rounds_complete, missions_failed):
        '''Update rounds and mission failures'''
        self.current_round = rounds_complete + 1
        self.missions_failed = missions_failed

    def game_outcome(self, spies_win, spies):
        '''This shouldn't matter to Reflex Agent'''
        pass
