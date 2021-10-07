'''
'''

import logging
import datetime


import game as game_module
from spy_catcher import SpyCatcher19800483
from random_agent import RandomAgent
from reflex_agent import ReflexAgent




def run_test():

    r_win = 0
    r_loss = 0

    for i in range(0, 1000):    

        logging.debug("\n\nNEW GAME {}".format(i))
        
        success = play_single_agent_game(8)
        if success:
            r_win += 1
        else:
            r_loss += 1
        
        #print(success)
    
    print("WINS: ", r_win)
    print("LOSSES: ", r_loss)
    



def play_single_agent_game(agent_count):
    '''Play a game using a single agent_type with varying numbers
    of resistance members'''

    agents = []

    for i in range(0, agent_count):

        agent_id = 'X_{}'.format(i)
        agents.append(ReflexAgent(name=agent_id))

    game = game_module.Game(agents)
        
    game.play()
    #print(game)

    return game.missions_lost < 3

def debug_log_setup():

    logging.basicConfig(filename='debug.log', level=logging.DEBUG)


if __name__ == '__main__':

    #debug_log_setup()

    run_test()
    #play_single_agent_game(7)
