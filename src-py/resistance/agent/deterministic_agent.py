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

import logging
import random

from agent import Agent


class AgentAssessment():

    def __init__(self, player_number, spy_probability):

        self.number = player_number

        self.distrust_level = spy_probability
        self.burnt = False



class AgentThreshold():
    '''Holds values for which a player will either trust another player
    vote against a mission or betray a mission'''

    def __init__(self, distrust=0.65, vote=0.65, betray=0.65):

        self.distrust = distrust
        self.vote = vote
        self.betray = betray


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

    # Probabilities
    agent_assessment = None
    agent_threshold = None

    # Resistance Members to Frame
    target_resistance = None

    def __init__(self, name='BayesianOpponentModelAgent_19800483', agent_threshold=None):
        '''Assign Name and clear missions failed'''

        self.name = name
        self.spy = False
        self.missions_failed = 0
        self.current_round = 0

        #
        if isinstance(agent_threshold, AgentThreshold):
            logging.debug("AGENT: {} USING THRESHOLDS | DISTRUST {} | VOTE {} | BETAYAL {}".format(self.name, agent_threshold.distrust, agent_threshold.vote, agent_threshold.betray))
            self.agent_threshold = agent_threshold
        else:
            logging.debug("AGENT: {} USING DEFAULT AGENT THRESHOLD".format(self.name))
            self.agent_threshold = AgentThreshold()

        # Spy Variables
        self.target_resistance = list()



    def new_game(self, number_of_players, player_number, spies):
        '''New game setup'''

        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spies = spies

        # Set Play Status
        self.spy = self.player_number in spies
        logging.debug("{} ({}) IS A SPY {}".format(self.player_number, self.__class__.__name__, self.spy))

        trust_level = self._calculate_initial_spy_probability()
        self.agent_assessments = {player: AgentAssessment(player, trust_level)
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
                logging.debug("{} IS VOTING AGAINST THE MISSION AS THEY ARE BURNT AND SABOTAGING VIA VOTE".format(self.player_number))
                return False

            return voting.spy_vote(self.missions_failed,
                                   self.target_resistance)

        return voting.resistance_vote()

    def vote_outcome(self, mission, proposer, votes):
        '''Reflex agent cannot deal with '''

        mission_go_ahead = len(votes) >= self.number_of_players / 2

        if self.player_number == 0:
            logging.debug("MISSION GO AHEAD: {} | {}".format(mission_go_ahead, mission))

        # Anyone that votes for burnt agents is a spy
        if any([agent for agent in mission if agent in self._get_burnt_spies()]):

            self.agent_assessments[proposer].distrust_level = 1.0
            self.agent_assessments[proposer].burnt = True

            logging.debug("BURNT AGENT {} FOUND IN MISSION {} PROPOSED BY {}".format(str(mission),
                                                                                     str(self._get_burnt_spies()),
                                                                                     proposer))

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
            logging.debug("NOT A SPY: ", self.player_number)
            return False

        # Setup betrayal space
        spies_on_mission = [agent for agent in mission if agent in self.spies]
        betrayals_required = self.fails_required[self.number_of_players][self.current_round]

        # Do not betray mission that can't fail
        if len(spies_on_mission) < betrayals_required:
            logging.debug("ROUND {} BETRAYAL UNACHIEVABLE AGENT {} LAYING LOW".format(self.current_round, self.player_number))
            return False

        logging.debug("BETRAYALS REQUIRED: {} SPIES AVAILABLE: {} BETRAYAL ACHIEVABLE".format(betrayals_required,
                                                                                                 len(spies_on_mission)))

        time_pressure = self.current_round / 4

        # Always betray last round as zero risk
        if time_pressure == 1:
            logging.debug("LAST ROUND BETRAYAL: {}".format(self.player_number))
            return True
        elif self.missions_failed == 2:
            logging.debug("WINNING BETRAYAL: {}".format(self.player_number))
            return True


        # COLLUSION MODULE : WARNING PLAY OUTSIDE THE SPIRIT OF THE GAME USING
        #                    EX ANTE COLLUSION. MUS BE SWITCHED ON PRIOR TO THE
        #                    GAME BEING STARTED
        if self.collusion and len(spies_on_mission) > 1 and self.fails_required[self.number_of_players][self.current_round] == 1:

            if self.player_number == max(spies_on_mission):
                logging.debug("COLLUSIVE BETRAYAL BY LEAD SPY ROUND: {} AGENT: {}".format(self.current_round, self.player_number))
                return True
            else:
                logging.debug("COLLUSIVE BETRAYAL BY LEAD SPY ({}) ROUND {}: AGENT {} LAYING LOW".format(max(spies_on_mission), self.current_round, self.player_number))
                return False

        # RANDOM MODULE
        # USES RANDOMISATION AND 'TIME PRESSURE' BASED ON THE CURRENT
        # ROUND TO DETERMINE ACTIONS

        # If player is burnt then unlikely on the mission but will always sabotage
        # Inside random module to prevent intereference with COLLUSION MODULE
        if self.agent_assessments[self.player_number].burnt:
            return True

        if len(spies_on_mission) == 1 and time_pressure >= 0.5:
            logging.debug("BETRAYAL OF OPPORTUNITY ROUND: {} AGENT: {}".format(self.current_round, self.player_number))
            return True

        # Determine actions when multiple spies on mission
        if len(spies_on_mission) > 1:

            if time_pressure <= 0.5 and self.missions_failed == 1:
                logging.debug("ASSESSING RISK ROUND {}: AGENT {} LAYING LOW".format(max(spies_on_mission), self.current_round, self.player_number))
                return False
            elif len(spies_on_mission) == len(mission):
                
                if self.current_round <= 1: 
                    
                    # TODO - Replace Manual Calc for single round option Nash Eq. Calculator
                    # Based on number of rounds
                    if random.random() > 0.85:
                        return True
                    else:
                        return False

        logging.debug("BETRAYAL OF OPPORTUNITY ROUND: {} AGENT: {}".format(self.current_round, self.player_number))
        return True

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''Update world understanding based on mission outcome'''

        if self.player_number == 0:
            logging.debug("MISSION SUCCESS: {}".format(mission_success))

        # If all agents betray the mission they have burned themselves
        if len(mission) == betrayals:

            for agent in mission:
                self.agent_assessments[agent].distrust_level = 1.0
                self.agent_assessments[agent].burnt = True

            logging.debug("SPIES BURNED THEMSELVES in ROUND {} : {}".format(self.current_round, str(self._get_burnt_spies())))
            return

        # Update probabilities
        for agent in mission:

            # Never change trust of burnt agents
            if self.agent_assessments[agent].distrust_level == 1.0:
                continue

            if mission_success:

                # P(spy | success) = P(success | spy) * P(spy) / P(success)

                p_success_spy = 0.3
                p_spy = self.agent_assessments[agent].distrust_level

                p_success_resistance = 1.0
                p_resistance = 1.0 - p_spy

                p_success = p_success_spy * p_spy + p_success_resistance + p_success_resistance * p_resistance

                distrust_level = (p_success_spy * p_spy) / p_success

                if distrust_level < 0.0 or distrust_level > 1.0:
                    message = "P(PASS g. RESISTANCE) : {} | P(RESISTANCE) : {} | P(PASS) : {}".format(p_success_spy, p_spy, p_success)
                    raise BadProbabilityException(message)

                self.agent_assessments[agent].distrust_level = distrust_level

            else:

                p_fail_spy = 0.7
                p_spy = self.agent_assessments[agent].distrust_level
                p_fail = p_fail_spy * p_spy

                distrust_level = (p_fail_spy * p_spy) / p_fail

                if distrust_level < 0.0 or distrust_level > 1.0:
                    message = "ROUND {}  |  P(FAIL g. SPY) : {} | P(SPY) : {} | P(FAIL) : {} ==> {}".format(self.current_round, p_fail_spy, p_spy, p_fail, distrust_level)
                    raise BadProbabilityException(message)

                self.agent_assessments[agent].distrust_level = (0.7 * self._calculate_initial_spy_probability()) / ((self.current_round + 1) / 5)


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

            logging.debug("AGENT(S) ({}) CONFIRMED AS SPIES in ROUND {} TO PLAYER: {}".format(str(known_spies), self.current_round, self.player_number))

    def round_outcome(self, rounds_complete, missions_failed):
        '''Update rounds and mission failures'''
        self.current_round = rounds_complete
        self.missions_failed = missions_failed

        logging.debug("AGENT {} ASSESSMENTS: {}".format(self.player_number, str({agent_number: self.agent_assessments[agent_number].distrust_level for agent_number in self.agent_assessments})))

    def game_outcome(self, spies_win, spies):
        '''This shouldn't matter to Reflex Agent'''

        if self.player_number == 0:
            logging.debug("SPIES WIN: {}  SPIES WERE: {}\n".format(spies_win, str(spies)))







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
            self._vote_logging("(SPY) VOTING AGAINST BURNT ASSET ")
            return False

        # We are trying to frame someone so we should vote against them
        no_targets = all([target in self.mission for target in target_resistance])
        if (len(target_resistance) != 0 and no_targets) or self.proposer in target_resistance :
            self._vote_logging("(SPY) VOTING NO TO FRAME TARGET")
            return False

        # No spies in mission
        if all([team_member not in self.spies for team_member in self.mission]):

            # If we have breathing room then allow it
            if 4 - self.current_round >= 3 - missions_failed:
                self._vote_logging("(SPY) VOTING YES AS {} ROUNDS LEFT AND ONLY {} FAILS REQUIRED".format(4 - self.current_round, 3 - missions_failed))
                return True
            else:
                self._vote_logging("(SPY) VOTING NO DUE TO NUMBER OF ROUNDS LEFT")
                return False

        self._vote_logging("(SPY) VOTING YES AS NO REASON NOT TO ")
        return True

    def resistance_vote(self):
        '''Decide on voting if player is resistance'''

        # Proposer is inherently untrustworthy
        if self.agent_assessments[self.proposer].distrust_level == 1.0:
            return False

        # Only vote against a player if we know they are a spy
        if any([agent in self.mission for agent in self.agent_assessments if self.agent_assessments[agent].distrust_level == 1.0]):
            self._vote_logging("(RESISTANCE) VOTING AGAINST KNOWN SPY")

            return False

        self._vote_logging("(RESISTANCE) VOTING YES AS NO INFORMATION NOT TO")
        return True

    def _vote_logging(self, reason):

        log_output = "ROUND: {} PROPOSER: {} VOTING PLAYER: {} MISSION: {} {} {}"
        log_output = log_output.format(self.current_round,
                                       self.proposer,
                                       self.player_number,
                                       str(self.mission),
                                       reason,
                                       str(self.confirmed_spies))
        logging.debug(log_output)


class TeamBuilder():

    def __init__(self, player_number, number_of_players, confirmed_spies):

        self.player_number = player_number
        self.number_of_players = number_of_players
        self.confirmed_spies = confirmed_spies

    def resistance_mission_proposal(self, team_size, number_of_spies, betrayals_required):

        team = []

        # Without adding ourself the mission will fail
        if (self.number_of_players - 1) - team_size < number_of_spies:
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

        # If agent is burnt add self to poison vote
        if self.player_number in self.confirmed_spies:
            team.append(self.player_number)

        # Without adding ourself the mission will succeed/fail
        elif (self.number_of_players - 1) - team_size < number_of_spies:
            team.append(self.player_number)

        #If self not already in the team random spies until we have enough
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


class BadProbabilityException(Exception):
    '''Raise when an exception is calculated that does not fall
    between 0.0 and 1.0 incluseively'''
