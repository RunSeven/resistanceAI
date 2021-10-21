"""
Bayesian Agent

Gameplay:

    Resistance: Rates spies on votes, proposals and mission outcomes.
                Votes for trusted players.
                

    Spy:        Increases likeliness of killing mission as rounds progress.
                Increase negative votes as rounds progress.
                Supports spies in votes
"""

import random

from genetics import AgentPenalties, AgentPredisposition
from agent import Agent


class BayesianAgent(Agent):
    '''Bayesian Opponent Model Agent
    '''

    # New Game Variables
    name = None
    missions_failed = None
    number_of_players = None
    player_number = None
    spies = None
    agent_assessments = None

    # Custom Variables
    spy = None
    voting_round = None
    current_round = None
    collusion = False

    # Probabilities
    genetics = None
    penalties = None

    # Resistance Members to Frame
    target_resistance = None

    # Post game analysis data
    winner = None
    correctly_identified_spies = 0

    def __init__(self, name='BayesianOpponentModelAgent_19800483', genetics=None, penalties=None):
        '''Assign Name and clear missions failed'''

        self.name = name
        self.spy = False
        self.missions_failed = 0
        self.current_round = 0

        # Assign Penalties/Bonuses for adverse/positive actions
        if isinstance(penalties, AgentPenalties):
            self.penalties = penalties
        else:
            self.penalties = AgentPenalties()

        # Spy Variables
        self.target_resistance = list()

    def new_game(self, number_of_players, player_number, spies):
        '''New game setup'''

        # Reset information
        self.missions_failed = 0
        self.current_round = 0
        self.voting_round = 0
        self.winner = None
        self.correctly_identified_spies = 0

        # Play Information
        self.number_of_players = number_of_players
        self.player_number = player_number
        self.spies = spies

        self.spy = self.player_number in spies

        # Set initial
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
    
    def _get_agents_sorted_by_trust(self):
        '''Sorts the agents based on their distrust assessment and returns
        the most distrusted player'''

        sorted_assessment = dict(sorted(self.agent_assessments.items(), key=lambda item: item[1].distrust_level))
        return sorted_assessment

    def propose_mission(self, team_size, betrayals_required=1):
        '''Create a team based on role'''

        team = None
        proposition = TeamBuilder(self,
                                  self.number_of_players,
                                  self.agent_assessments)

        # Resistance team selection
        if not self.is_spy():

            team = proposition.resistance_mission_proposal(
                team_size,
                self.spy_count[self.number_of_players]
            )

            return team

        # Spy team selection 
        team = proposition.spy_mission_proposal(team_size,
                                                self.spies,
                                                betrayals_required)

        return team

    def vote(self, mission, proposer):
        '''Determine vote based on player model'''

        self.voting_round += 1

        voting = Vote(self,
                      proposer,
                      mission)

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
        if self.voting_round != 5 and any([agent for agent in mission if agent in self._get_burnt_spies()]):

            self.agent_assessments[proposer].distrust_level = 2.0
            self.agent_assessments[proposer].burnt = True

        # Award or penalise based on failing a round with the vote
        if self.voting_round == 5 and not mission_go_ahead:

            for agent in self.agent_assessments:
                
                # Trust agents more if they pass the final vote
                if agent not in votes:
                    self.agent_assessments[agent].vote_distrust -= self.penalties.vote_fail
                
                # Penalise more as the rounds progress for killing vote on final
                else:
                    self.agent_assessments[agent].vote_distrust += self.penalties.vote_fail * self.current_round

        # If the proposer includes the most suspect agent but isn't them trust them less
        agent_trust = list(self._get_agents_sorted_by_trust())[-1]
        if agent_trust in mission and proposer != agent_trust:
            self.agent_assessments[proposer].proposal_distrust += self.penalties.propose_suspect


    def _get_burnt_spies(self):
        '''A burnt spy is one that has been on a mission where the number of betrayals
        is equal to the number of agents on the mission'''

        burnt_spies = [agent
                       for agent in self.agent_assessments.values()
                       if agent.burnt]

        return burnt_spies


    def betray(self, mission, proposer):
        '''Determine whether to betray the mission'''

        # STANDARD LOGIC
        # PLAYABLE WITHOUT RISK UNDER ANY CIRCUMSTANCES

        # Ensure that resistance don't accidentally betray the mission
        if not self.is_spy():
            return False

        # Setup betrayal space
        spies_on_mission = [agent for agent in mission if agent in self.spies]
        betrayals_required = self.fails_required[self.number_of_players][self.current_round]

        # Do not betray mission that can't fail
        if len(spies_on_mission) < betrayals_required:
            return False

        # Metric for determining how hard a spy should work to stop the resistance
        time_pressure = self.current_round / 4

        # Zero risk for betraying on last round or to win
        if time_pressure == 1 or self.missions_failed == 2:
            return True


        # COLLUSION MODULE : WARNING PLAY OUTSIDE THE SPIRIT OF THE GAME USING
        #                    EX ANTE COLLUSION. SHOULD BE SWITCHED ON PRIOR TO THE
        #                    GAME BEING STARTED. DOESN'T WORK WITH 2 BETRAYAL MISSIONS
        #                    ATM.
        if self.collusion and len(spies_on_mission) > 1 and self.fails_required[self.number_of_players][self.current_round] == 1:
            
            # Lead spy (spy with max player number) will sabotage
            if self.player_number == max(spies_on_mission):
                return True
            # All other spies may avoid sabotage as they know the lead spy will sabotage
            else:
                return False

        # If player is burnt then unlikely on the mission but will always sabotage
        # Placed here to prevent intereference with COLLUSION MODULE
        if self.agent_assessments[self.player_number].burnt:
            return True

        # Always betray the mission in the last two rounds
        if len(spies_on_mission) == 1 and time_pressure > 0.5:
            return True

        # Determine actions when multiple spies on mission
        if len(spies_on_mission) > 1:

            # If a mission has failed and spy is in the second round lay low to avoid suspicion
            if time_pressure <= 0.5 and self.missions_failed == 1:
                return False
            
            elif len(spies_on_mission) == len(mission):

                if self.current_round <= 1:

                    # Based on number of rounds
                    if random.random() > 0.85 ** self.current_round:
                        return True
                    else:
                        return False

        # When in doubt, betray the mission
        return True

    def mission_outcome(self, mission, proposer, betrayals, mission_success):
        '''Update world understanding based on mission outcome'''
        
        # Add minor suspicion to proposer higher weighted in later rounds
        # self.agent_assessments[proposer].proposal_distrust += self.penalties.p_failed_mission

        # If all agents betray the mission they have burned themselves
        if len(mission) == betrayals:

            for agent in mission:
                self.agent_assessments[agent].distrust_level = 2.0
                self.agent_assessments[agent].burnt = True

            return
        
        # Update agent assessments
        for agent in mission:

            # Never change trust of burnt agents
            if self.agent_assessments[agent].burnt:
                continue

            if mission_success:
                self._sucessful_mission_trust_adjustment(agent, mission, betrayals)
            else:
                self._failed_mission_trust_adjustment(agent, mission, betrayals)
        
        # Update role dependent behaviours
        if self.is_spy():
            self._spy_mission_outcome(mission, betrayals, mission_success)
        else:
            self._resistance_mission_outcome(mission, betrayals)

    def _sucessful_mission_trust_adjustment(self, agent, mission, betrayals):
        '''Trust players more on success'''

        # We use the agents existing probability of being 
        # a spy to allow a mission to succeed in conjunction with the 
        # current round.  
        p_success_spy = 1 - self.agent_assessments[agent].distrust_level
        trust_adjustment = p_success_spy * self.penalties.failed_mission
        self.agent_assessments[agent].mission_distrust -= trust_adjustment

    def _failed_mission_trust_adjustment(self, agent, mission, betrayals):
        '''Trus agents less on failure'''

        # Use our initial distrust as a weight against further trust
        # If we trust them more the penalty will be less

        #Likelihood the agent is a spy as seen by the agent
        p_spy = self.agent_assessments[agent].distrust_level

        # Probability the agent in question betrayed the mission
        p_betrayal = (betrayals / len(mission)) * p_spy

        # Trus adjustment calculation
        trust_adjustment = p_betrayal * self.penalties.failed_mission
        self.agent_assessments[agent].mission_distrust += trust_adjustment

    def _spy_mission_outcome(self, mission, betrayals, mission_success):
        '''Update information for spy player where mision has failed''' 

        # Target a resistance member for vote blocking if
        # they could be suspect
        if not mission_success:
            targets = [resistance for resistance in mission if resistance not in self.spies]
            self.target_resistance.extend(targets)

    def _resistance_mission_outcome(self, mission, betrayals):
        '''Update information for resistance player where mission has failed'''

        # Spies become known to a single resistance agent if all other players sabotage
        if self.player_number in mission and betrayals == len(mission) - 1:
            known_spies = [spy for spy in mission if spy != self.player_number]

            for agent in known_spies:
                self.agent_assessments[agent].distrust_level = 2.0

    def round_outcome(self, rounds_complete, missions_failed):
        '''Update rounds and mission failures'''

        # Update agent status information
        self.current_round = rounds_complete
        self.missions_failed = missions_failed

        # Reset vote counter
        self.voting_round = 0

        # Trust levels aggregated at the end of each round
        for agent in self.agent_assessments:

            if self.agent_assessments[agent].distrust_level != 2.0:
                self.agent_assessments[agent].distrust_level = sum((self.agent_assessments[agent].mission_distrust,
                                                                    self.agent_assessments[agent].vote_distrust,
                                                                    self.agent_assessments[agent].proposal_distrust))
     
    def game_outcome(self, spies_win, spies):
        '''Assign data to variables for post game analysis'''

        # Post play metric information
        if (self.is_spy() and spies_win) or (not self.is_spy() and not spies_win):
            self.winner = True
        else:
            self.winner = False
        
        agent_trust = self._get_agents_sorted_by_trust()

        correctly_identified_spies = 0
        incorrectly_identified_spies = 0
        for i in range(1, len(spies)):
            
            if list(agent_trust.keys())[-i] in spies:
                correctly_identified_spies += 1
            else:
                incorrectly_identified_spies += 1

        self.correctly_identified_spies = correctly_identified_spies


class Vote():
    '''Vote makes role dependent votes'''

    def __init__(self, voter, proposer, mission):

        self.voter = voter
        
        self.proposer = proposer
        self.mission = mission

        self.confirmed_spies = {agent: voter.agent_assessments[agent].distrust_level
                                for agent in voter.agent_assessments
                                if voter.agent_assessments[agent].distrust_level == 2.0}

    def spy_vote(self, missions_failed, target_resistance):
        '''Decide on voting if player is a spy'''

        # Spies shouldn't vote for burnt assets
        if any([agent in self.mission
                for agent in self.voter.agent_assessments
                if self.voter.agent_assessments[agent].burnt]):

            return False

        # We are trying to frame someone so we should vote against them
        no_targets = all([target in self.mission for target in target_resistance])
        if (len(target_resistance) != 0 and no_targets) or self.proposer in target_resistance :
            
            return False

        # No spies in mission
        if all([team_member not in self.voter.spies for team_member in self.mission]):

            # If we can still win without this mission then allow it
            if 4 - self.voter.current_round >= 3 - missions_failed:
                return True
            else:
                return False

        # If no reason not to vote yes then allow it
        return True

    def resistance_vote(self):
        '''Decide on voting if player is resistance'''

        if self.voter.voting_round == 5:
            return True

        # Proposer is known spy so don't trust them
        if self.voter.agent_assessments[self.proposer].distrust_level == 2.0:
            return False
       
        # Only vote against a player if we think are a spy.
        # we assume trust in the first two rounds
        agent_trust = list(self.voter._get_agents_sorted_by_trust())
        if any([agent in self.mission
                for agent in self.voter.agent_assessments
                if (agent_trust[-1] in self.mission 
                or agent_trust[-2] in self.mission)
                and self.voter.current_round != 1]):
            
            # If we think the mission contains spies then trust
            # the proposer less
            trust_adjustment = self.voter.penalties.propose_suspect
            self.voter.agent_assessments[self.proposer].proposal_distrust += trust_adjustment

            return False

        # If we have no suspicion vote yes
        return True



class TeamBuilder():
    '''Proposes teams to undertake missions'''

    def __init__(self, proposer, number_of_players, agent_assessments):

        self.proposer = proposer        
        self.number_of_players = number_of_players
        self.agent_assessments = agent_assessments

        self.confirmed_spies = [agent
                                for agent in self.agent_assessments
                                if self.agent_assessments[agent].distrust_level == 2.0]

    def resistance_mission_proposal(self, team_size, number_of_spies):
        '''Propose teams as a resistance member.  Tries to minimise risk and maximise information
        found out about other players'''

        team = []
        agent_trust = list(self.proposer._get_agents_sorted_by_trust())

        # Always include self except choke missions of size 2
        if team_size > 2 and self.proposer.player_number not in team:
            team.append(self.proposer.player_number)

        while len(team) < team_size:

            agent = random.randrange(self.number_of_players)

            # Don't include confirmed spies
            if agent in team or agent in self.confirmed_spies:
                continue

            # Don't include the most untrusted
            if agent in team or agent in agent_trust[-number_of_spies:]:
                continue

            # Two player missions are choke points so we want to test other players here
            if team_size == 2 and agent == self.proposer.player_number:
                continue

            team.append(agent)

        # Hide any evidence of selection order
        random.shuffle(team)
        return team

    def spy_mission_proposal(self, team_size, spies, betrayals_required):
        '''Propose mission as a spy.  Tries to minimise the overall suspicion of
        the mission by selecting the least likely spies alongside the 
        least suspicious resistance members.'''

        team = []
        number_of_spies = len(spies)

        agent_trust = list(self.proposer._get_agents_sorted_by_trust())
        
        # Always add self
        team.append(self.proposer.player_number)

        # Get a list of spies that haven't been burnt
        viable_spies = [spy for spy in spies if spy not in self.confirmed_spies]
        
        #If self not already in the team spies by lowest suspicion until we have enough
        while len(team) < betrayals_required:
            
            # Get a subset of these that are least suspect
            best_spies = [spy for spy in viable_spies if spy not in agent_trust[-number_of_spies:] and spy not in team]

            # Choose the best option available
            if len(viable_spies) < betrayals_required:
                spy = random.choice(spies)                
            elif len(best_spies) > 0:         
                spy = random.choice(best_spies)
            else:
                spy = random.choice(viable_spies)

            if spy not in team:
                team.append(spy)

        # Fill in the remaining positions
        agent_number = 0        
        while len(team) < team_size:

            agent = random.randrange(self.number_of_players)

            # Don't include burnt agents
            if agent not in team and agent not in self.confirmed_spies:
                continue

            # Add the least suspect team members in order
            # TODO - Ensure minimum spies are included        
            team.append(agent_trust[agent_number])
            agent_number += 1

        # Hide any evidence of selection order
        random.shuffle(team)
        return team
