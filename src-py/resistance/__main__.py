'''
'''

from spy_catcher import SpyCatcher19800483
from random_agent import RandomAgent
from reflex_agent import ReflexAgent

from game import Game

agents = [ReflexAgent(name='r1'),
          ReflexAgent(name='r2'),
          ReflexAgent(name='r3'),
          ReflexAgent(name='r4'),
          ReflexAgent(name='r5'),
          ReflexAgent(name='r6'),
          ReflexAgent(name='r7')]

game = Game(agents)
game.play()
print(game)
