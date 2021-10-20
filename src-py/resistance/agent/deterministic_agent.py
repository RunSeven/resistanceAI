"""
Deterministic Agent

Gameplay:

    Resistance: Remembers known spies and works against them.
                Votes for players not known to have failed a mission.
                Has equality counter for failed missions.

    Spy:        Increases likeliness of killing mission as rounds progress.
                Increase negative votes as rounds progress.
                Supports spies in votes more as
"""

import random

from agent import Agent


from genetics import AgentGenetics, AgentPenalties, AgentPredisposition


class DeterministicAgent(Agent):
    '''Deterministic Agent has minimal understanding of the world.  Only remembers
    major game events.  Uses a mix of deterministic logic and randomness
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
    collusion = False
    winner = None

    # Probabilities
    agent_assessment = None
    genetics = None
    penalties = None

    # Resistance Members to Frame
    target_resistance = None

    def __init__(self, name='BayesianOpponentModelAgent_19800483', genetics=None, penalties=None):
        '''Assign Name and clear missions failed'''

        self.name = name
        self.spy = False
        self.missions_failed = 0
        self.current_round = 0

        # Set values on how the agent reacts to events
        if isinstance(genetics, AgentGenetics):            
            self.genetics = genetics
        else:
            self.genetics = AgentGenetics()

        if isinstance(penalties, AgentPenalties):
            self.penalties = penalties
        else:
            self.penalties = AgentPenalties()

        # Spy Variables
        self.target_resistance = list()


    def new_game(self, number_of_players, player_number, spies):
        '''New game setup'''

        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spies = spies
        self.winner = None

        # Set Play Status
        self.spy = self.player_number in spies

        trust_level = self._calculate_initial_spy_probability()
        self.agent_assessments = {player: AgentPredisposition(player)
                                  for player in range(0, self.number_of_players)}

    def is_spy(self):
        '''return spy status'''
        return self.spy

    def collusion_mode_on(self):
        '''Switch for setting collusion mode on'''
        self.collusion = True

    def collusion_mode_off(self):
        '''Switch for setting collusion mode off'''
        self.collusion = False

    def _calculate_initial_spy_probability(self):
        '''Calculates and initiates trust levels in spies'''

        number_of_spies = self.spy_count[self.number_of_players]
        spy_probability = number_of_spies / (self.number_of_players - 1)

        return spy_probability

    def propose_mission(self, team_size, betrayals_required=1):
        '''Create a team based on role'''
        team = None

        proposition = TeamBuilder(self.player_number,
                                      self.number_of_players,
                                      self._get_confirmed_spies())

        # If it's the first round spies just lay low
        # and resistance have no reason to object
        if self.current_round == 0 or not self.is_spy():

            team = proposition.resistance_mission_proposal(
                team_size,
                self.spy_count[self.number_of_players],
                betrayals_required
            )

            return team

        team = proposition.spy_mission_proposal(team_size,
                                                self.spies,
                                                betrayals_required)

        return team

    def vote(self, mission, proposer):
        '''Determine vote based on player model'''

        voting = Vote(proposer,
                      mission,
                      self.player_number,
                      self.current_round,
                      self.spies,
                      self.agent_assessments)

        # Accept any vote in the first round
        if self.current_round == 0:
            return True

        if self.is_spy():

            # If self is burnt default to fail the vote
            if self.player_number in self._get_burnt_spies():
                return False

            return voting.spy_vote(self.missions_failed,
                                   self.target_resistance)

        return voting.resistance_vote()

    def vote_outcome(self, mission, proposer, votes):
        '''Reflex agent cannot deal with '''

        mission_go_ahead = len(votes) >= self.number_of_players / 2

        # Anyone that votes for burnt agents is a spy
        if any([agent for agent in mission if agent in self._get_burnt_spies()]):
            self.agent_assessments[proposer].distrust_level = 1.0
            self.agent_assessments[proposer].burnt = True

    def _get_burnt_spies(self):
        '''A burnt spy is one that has been on a mission where the number of betrayals
        is equal to the number of agents on the mission'''

        burnt_spies = [agent
                       for agent in self.agent_assessments.values()
                       if agent.burnt]

        return burnt_spies

    def _get_confirmed_spies(self):
        '''A confirmed spy is one that the agent knows to be a spy but cannot assume other
        players know to be a spy'''

        confirmed_spies = [agent.number for agent in self.agent_assessments.values() if agent.distrust_level == 1.0]
        return confirmed_spies

    def betray(self, mission, proposer):
        '''Determine whether to betray the mission'''

        # STANDARD LOGIC
        # PLAYABLE WITHOUT RISK UNDER ANY CIRCUMSTANCES

        # Ensure that resistance don't accidentally betray the mission
        if not self.is_spy():
            return False

        # Setup betrayal space
        spies_on_mission = [agent for agent in mission if agent in self.spies]        
        betrayals_required = self.fails_required[self.number_of_players][self.current_round - 1]

        # Do not betray mission that can't fail
        if len(spies_on_mission) < betrayals_required:
            return False

        time_pressure = self.current_round / 4

        # Zero risk for betraying on last round or to win
        if time_pressure == 1 or self.missions_failed == 2:
            return True
        

        # COLLUSION MODULE : WARNING PLAY OUTSIDE THE SPIRIT OF THE GAME USING
        #                    EX ANTE COLLUSION. MUS BE SWITCHED ON PRIOR TO THE
        #                    GAME BEING STARTED
        if self.collusion and len(spies_on_mission) > 1 and self.fails_required[self.number_of_players][self.current_round] == 1:
            
            # If player is 'max(spies_on_mission)' they will sabotage otherwise they won't
            if self.player_number == max(spies_on_mission):
                return True
            else:
                return False

        # RANDOM MODULE
        # USES RANDOMISATION AND 'TIME PRESSURE' BASED ON THE CURRENT
        # ROUND TO DETERMINE ACTIONS

        # If player is burnt then unlikely on the mission but will always sabotage
        # Inside random module to prevent intereference with COLLUSION MODULE
        if self.agent_assessments[self.player_number].burnt:
            return True

        # Betray because agent is the only spy on the mission 
        # and it is late in the game
        if len(spies_on_mission) == 1 and time_pressure >= 0.5:
            return True

        # Determine actions when multiple spies on mission
        if len(spies_on_mission) > 1:

            # If it is an early round and a mission has already failed 
            # we want to lay low to build trust
            if time_pressure <= 0.5 and self.missions_failed == 1:
                return False
            
            # If we need to risk it then we will use a probability
            elif len(spies_on_mission) == len(mission):
                
                if self.current_round <= 1: 
                    
                    # Increase likelihood of failing mission for subsequent rounds
                    if random.random() > 0.85 * (self.current_round + 1):
                        return True
                    else:
                        return False

        # When in doubt sabotage the mission
        return True

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''Update world understanding based on mission outcome'''

        # If all agents betray the mission they have burned themselves
        if len(mission) == betrayals:

            for agent in mission:
                self.agent_assessments[agent].distrust_level = 1.0
                self.agent_assessments[agent].burnt = True

            return

        # Update the agent depending on role
        if self.is_spy():
            self._spy_mission_outcome(mission, betrayals, mission_success)
        else:
            self._resistance_mission_outcome(mission, betrayals)

    def _spy_mission_outcome(self, mission, betrayals, mission_success):

        # Target a resistance member for vote blocking if
        # they could be suspect
        if not mission_success:
            targets = [resistance for resistance in mission if resistance not in self.spies]
            self.target_resistance.extend(targets)

    def _resistance_mission_outcome(self, mission, betrayals):

        # Spies become known to the agent if he is the only one not to sabotage
        if self.player_number in mission and betrayals == len(mission) - 1:
            known_spies = [spy for spy in mission if spy != self.player_number]

            for agent in known_spies:
                self.agent_assessments[agent].distrust_level = 1.0

    def round_outcome(self, rounds_complete, missions_failed):
        '''Update rounds and mission failures'''
        self.current_round = rounds_complete
        self.missions_failed = missions_failed

    def game_outcome(self, spies_win, spies):
        '''Provide feedback to testing functions'''

        if (self.is_spy() and spies_win) or (not self.is_spy() and not spies_win):
            self.winner = True
        else:
            self.winner = False


class Vote():

    def __init__(self, proposer, mission, player_number, current_round, spies, agent_assessments):

        self.proposer = proposer
        self.mission = mission

        self.player_number = player_number
        self.current_round = current_round
        self.spies = spies
        self.agent_assessments = agent_assessments

        self.confirmed_spies = [agent
                                for agent in self.agent_assessments
                                if self.agent_assessments[agent].distrust_level == 1.0]

    def spy_vote(self, missions_failed, target_resistance):
        '''Decide on voting if player is a spy'''

        # Spies shouldn't vote for burnt assets
        if any([agent in self.mission for agent in self.agent_assessments if self.agent_assessments[agent].burnt]):
            return False

        # We are trying to frame someone so we should vote against them
        no_targets = all([target in self.mission for target in target_resistance])
        if (len(target_resistance) != 0 and no_targets) or self.proposer in target_resistance :
            return False

        # No spies in mission
        if all([team_member not in self.spies for team_member in self.mission]):

            # If we can still win without this mission then allow it
            if 4 - self.current_round >= 3 - missions_failed:
                return True
            else:
                return False

        # If no reason not to vote yes then allow it
        return True

    def resistance_vote(self):
        '''Decide on voting if player is resistance'''

        # Proposer is inherently untrustworthy
        if self.agent_assessments[self.proposer].distrust_level == 1.0:
            return False

        # Only vote against a player if we know they are a spy
        if any([agent in self.mission for agent in self.agent_assessments if self.agent_assessments[agent].distrust_level == 1.0]):
            return False

        # If no reason not to vote yes then allow it
        return True



class TeamBuilder():

    def __init__(self, player_number, number_of_players, confirmed_spies):

        self.player_number = player_number
        self.number_of_players = number_of_players
        self.confirmed_spies = confirmed_spies

    def resistance_mission_proposal(self, team_size, number_of_spies, betrayals_required):

        team = []

        # Add self to mission
        team.append(self.player_number)

        while len(team) < team_size:

            agent = random.randrange(self.number_of_players)

            # Don't include confirmed spies
            if agent not in team and agent not in self.confirmed_spies:
                team.append(agent)

        # Hide any evidence of selection order
        random.shuffle(team)
        return team

    def spy_mission_proposal(self, team_size, spies, betrayals_required):

        team = []
        number_of_spies = len(spies)

        # Always add self
        team.append(self.player_number)

        #Add random spies until we have enough to kill the mission
        while len(team) < betrayals_required:

            if len(self.confirmed_spies) - number_of_spies < betrayals_required:
                break

            viable_spies = [spy for spy in self.spies if spy not in self.confirmed_spies]

            spy = random.choice(viable_spies)

            if spy not in team:
                team.append()

        while len(team) < team_size:

            agent = random.randrange(self.number_of_players)

            # Don't include burnt agents
            if agent not in team and agent not in self.confirmed_spies:
                team.append(agent)

        random.shuffle(team)
        return team

