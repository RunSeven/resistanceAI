import logging

import game as game_module
from random_agent import RandomAgent
from reflex_agent import ReflexAgent
from bayesian_agent import BomAgent




def run_test(agent_count):

    r_win = 0
    r_loss = 0
    game_count = 1000

    for i in range(0, game_count):    

        logging.debug("\n\nNEW GAME {}".format(i))
        
        success = play_single_agent_game(agent_count)
        if success:
            r_win += 1
        else:
            r_loss += 1
        
        #print(success)
    
    print("WINS: ", r_win)
    print("LOSSES: ", r_loss)
    print("WIN PERCENT: ", round((r_win/game_count) * 100, 3), "%")
    

def run_test_on_all_game_types():

    for i in range(5, 11):

        print("RESISTANCE MEMBERS: {}".format(i))
        logging.debug("RESISTANCE MEMBERS: {}".format(i))
        run_test(i)


def play_single_agent_game(agent_count):
    '''Play a game using a single agent_type with varying numbers
    of resistance members'''

    agents = []

    for i in range(0, agent_count):

        agent_id = 'X_{}'.format(i)
        agents.append(BomAgent(name=agent_id))

    game = game_module.Game(agents)
        
    game.play()
    #print(game)

    return game.missions_lost < 3

def debug_log_setup():

    logging.basicConfig(filename='debug.log', level=logging.DEBUG)


if __name__ == '__main__':

    debug_log_setup()

    run_test_on_all_game_types()
    #play_single_agent_game(7)
