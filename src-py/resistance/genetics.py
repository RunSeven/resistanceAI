'''

Genetics

Holds the code for kick starting the genetic algorithm that
will update the Reference Data.

'''

import datetime
import logging
import random


class AgentGenetics():
    '''Holds values for which a player will either trust another player
    vote against a mission or betray a mission'''

    def __init__(self, distrust=0.65, vote=0.65, betray=0.65):

        self.distrust = distrust
        self.vote = vote
        self.betray = betray
    
    def __repr__(self):

        return "Distrust {} | Vote {} | Betray {}".format(round(self.distrust, 4),
                                                          round(self.vote, 4),
                                                          round(self.betray, 4))


class AgentPenalties():
    '''Holds the penalty values for actions taken by players'''

    def __init__(self, failed_mission=0.1, p_failed_mission=0.05, vote_fail=0.3, vote_spy=0.05):
        '''Penalties for 
           Participiating in a Failed Mission: failed_mission
           Proposing a Failed Mission: p_failed_mission
           Aborting a mission through votes: vote_fail
           Voting for a suspected spy: vote_spy'''

        self.failed_mission = failed_mission
        self.p_failed_mission = p_failed_mission
        self.vote_fail = vote_fail
        self.vote_spy = vote_spy
    
    def __repr__(self):

        return "On Failed: {} | Propose Failed: {} | Aborting Vote: {} | Suspect Vote: {}".format(self.failed_mission, self.p_failed_mission, self.vote_fail, self.vote_spy)


class AgentOriginator():

    def __init__(self):
        '''NA'''
        pass

    def create(self, seed_agent):
        '''Seed agents based on the number of players'''

        genetics = self._seed_genetics()
        penalties = self._seed_penalties()
        return seed_agent('X', genetics, penalties)

    def _seed_genetics(self):
        '''Creates the initial values of the AgentGenetics'''

        distrust = random.random()
        vote = random.random()
        betray = random.random()

        genetics = AgentGenetics(distrust, vote, betray)

        return genetics
    
    def _seed_penalties(self):
        '''Seed the penalty values for association with subversive actions'''

        failed_mission = random.random()
        p_failed_mission = random.random()
        vote_fail = random.random()
        vote_spy = random.random()

        penalties = AgentPenalties(failed_mission, p_failed_mission, vote_fail, vote_spy)

        return penalties

    def evolve(self, agent):
        '''Takes each of the values in genetics and muttes them slightly
        using the mutations to build a new agent'''

        genetics = agent.genetics

        distrust = self._mutate_gene(genetics.distrust)
        vote = self._mutate_gene(genetics.vote)
        betray = self._mutate_gene(genetics.betray)

        mutations = AgentGenetics(distrust, vote, betray)

        mutation_time = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
        mutation_id = 'M_{}'.format(mutation_time)

        return self.seed_agent(mutation_id, mutations)

    def _mutate_gene(self, gene):

        mutation = random.randrange(gene - 0.1, gene + 0.1)
        return mutation


