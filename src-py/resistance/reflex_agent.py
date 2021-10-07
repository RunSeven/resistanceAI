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

import logging
import random

from agent import Agent



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
    spy = None
    current_round = None
    number_of_spies = None
    confirmed_spies = None

    # Resistance Member to Frame
    target_resistance = None

    def __init__(self, name='Reflex'):
        '''Assign Name and zero missions failed'''
        self.name = name
        self.missions_failed = 0

        self.spy = False
        self.current_round = 1
        self.confirmed_spies = list()

        self.target_resistance = list()

    def new_game(self, number_of_players, player_number, spies):
        '''New game setup'''

        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spies = spies
        self.number_of_spies = self.spy_count[number_of_players]

        # Set Play Status
        self.spy = self.player_number in spies
        logging.debug("{} IS A SPY {}".format(self.player_number, self.spy))

    def is_spy(self):
        '''return spy status'''

        return self.spy

    def propose_mission(self, team_size, betrayals_required=1):
        '''Create a team based on role'''
        team = None

        proposition = Proposal(self.player_number, self.number_of_players, self.spies, self.confirmed_spies)

        # If it's the first round we just lay low
        if self.current_round == 1 or not self.spy:
            team = proposition.resistance_mission_proposal(team_size,
                                                            self.number_of_spies,
                                                            betrayals_required)
            return team

        team = proposition.spy_mission_proposal(team_size, self.number_of_spies, betrayals_required)

        return team

    

    def vote(self, mission, proposer):
        '''Determine vote based on player model'''

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
        if any([player in mission for player in self.confirmed_spies]):
            self._vote_logging(proposer, mission, "(SPY) VOTING AGAINST BURNT ASSET ")
            return False

        # We are trying to frame someone so we should vote against them
        no_targets = all([target in mission for target in self.target_resistance])
        if len(self.target_resistance) != 0 and no_targets:
            self._vote_logging(proposer, mission, "(SPY) VOTING NO TO FRAME TARGET")
            return False

        # No spies in mission
        if any([team_member not in self.spies for team_member in mission]):

            # If we have breathing room then allow it
            if self.current_round - self.missions_failed > 0:
                self._vote_logging(proposer, mission, "(SPY) VOTING YES FOR NUMBER OF ROUNDS")
                return True
            else:
                self._vote_logging(proposer, mission, "(SPY) VOTING NO AGAINST NUMBER OF ROUNDS")
                return False

        self._vote_logging(proposer, mission, "(SPY) VOTING YES AS NO REASON NOT TO ")
        return True

    def _resistance_vote(self, mission, proposer):
        '''Decide on voting if player is resistance'''

        # Proposer is inherently untrustworthy
        if proposer in self.confirmed_spies:
            return False

        # Only vote against a player if we know they are a spy
        if any([player in mission for player in self.confirmed_spies]):
            self._vote_logging(proposer, mission, "(RESISTANCE) VOTING AGAINST KNOWN SPY")
            logging.debug("PLAYER: {} {}".format(self.player_number, str({player: player in mission for player in self.confirmed_spies})))
            return False
        
        self._vote_logging(proposer, mission, "(RESISTANCE) VOTING YES AS NO INFORMATION NOT TO")
        return True

    def _is_burnt_asset_vote(self):
        '''Decide how to vote if the player is a spy and burnt asset'''

        # Try to kill all other votes based on others suscpicion
        return False
    
    def _vote_logging(self, proposer, mission, reason):

        log_output = "ROUND: {} PROPOSER: {} PLAYER: {} MISSION: {} {} {}"
        log_output = log_output.format(self.current_round, proposer, self.player_number, str(mission), reason, str(self.confirmed_spies))
        logging.debug(log_output)

    def vote_outcome(self, mission, proposer, votes):
        '''Reflex agent cannot deal with '''

        # Anyone that votes on burnt agents is a traitor???

    def betray(self, mission, proposer):
        '''Determine whether to betray the mission'''

        # Ensure that resistance don't betray the mission
        # by a bad function call
        if not self.spy:
            logging.debug("NOT A SPY: ", self.player_number)            
            return False

        # Determine actions when all team members are spies
        if all([team_member in self.spies for team_member in mission]):

            # Don't burn spies on the first round
            if self.current_round == 1:
                return False

            # Spies have to risk a burning event 
            if len(mission) == 2 and self.missions_failed == 0:
                betray = random.random() < (1/len(mission)) + 0.1

                if betray:
                    logging.debug("BETRAYING MISSION: {}".format(self.player_number))
                return betray

            betray = random.random() < (1/len(mission)) - 0.1
            if betray:
                logging.debug("BETRAYING MISSION: {}".format(self.player_number))
            return betray

        # Nothing to lose in the last round
        if self.current_round == 5:
            logging.debug("LAST ROUND BETRAYAL: {}".format(self.player_number))
            return True

        logging.debug("JUST BECAUSE BETRAYAL ROUND: {} BETRAYOR: ".format(self.current_round, self.player_number))
        return True


    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''Update world understanding based on mission outcome'''

        # If all agents betray the mission they have burned themselves
        if len(mission) == betrayals:
            self.confirmed_spies.extend(mission)
            self.confirmed_spies = list(set(self.confirmed_spies))
            logging.debug("SPIES BURNED THEMSELVES in ROUND {}".format(self.current_round, str(self.confirmed_spies)))
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
            self.confirmed_spies = list(set(self.confirmed_spies))
            logging.debug("BURNED THEMSELVES in ROUND {} ({}) TO PLAYER: {}".format(self.current_round,  str(known_spies), self.player_number))

    def round_outcome(self, rounds_complete, missions_failed):
        '''Update rounds and mission failures'''
        self.current_round = rounds_complete + 1
        self.missions_failed = missions_failed

    def game_outcome(self, spies_win, spies):
        '''This shouldn't matter to Reflex Agent'''
        pass




class Proposal():


    def __init__(self, player_number, number_of_players, spies, confirmed_spies):
        
        self.player_number = player_number
        self.number_of_players = number_of_players
        self.spies = spies
        self.confirmed_spies = confirmed_spies

    def resistance_mission_proposal(self, team_size, number_of_spies, betrayals_required):

        team = []        
        
        # Without adding ourself the mission will fail
        if (self.number_of_players -1) - team_size < number_of_spies:
            team.append(self.player_number)

        while len(team) < team_size:

            agent = random.randrange(self.number_of_players)
            
            # Don't include burnt agents
            if agent not in team and agent not in self.confirmed_spies:
                team.append(agent)
            
        random.shuffle(team)
        return team

    def spy_mission_proposal(self, team_size, number_of_spies, betrayals_required):

        team = []
        
        # If agent is burnt add self to poison vote        
        if self.player_number in self.confirmed_spies:
            team.append(self.player_number)
        
        # Without adding ourself the mission will succeed/fail
        elif (self.number_of_players -1) - team_size < number_of_spies:
            team.append(self.player_number)
        
        #If self not already in the team random spies until we have enough
        while len(team) < betrayals_required:

            if len(self.confirmed_spies) - number_of_spies < betrayals_required:
                break

            viable_spies = [spy for spy in self.spies if spy not in self.confirmed_spies]

            spy = random.choice(viable_spies)

            if spy not in team:
                team.append()

        proposal_string = ''
        while len(team) < team_size:

            agent = random.randrange(self.number_of_players)
            proposal_string += str(agent)

            # Don't include burnt agents
            if agent not in team and agent not in self.confirmed_spies:
                team.append(agent)
                            

        random.shuffle(team)
        return team