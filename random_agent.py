from actions import Action
from agent import AgentInterface
from cards import Cards
from exceptions import IllegalActionException
from state import PlayerState
from typing import Optional
from random import randrange
import sys

class RandomAgent(metaclass=AgentInterface):
	def __init__(self):
		self.current = None
		self.index = None

	def new_round(self, start:PlayerState):
		self.current = start
		self.index = start.index

	def see(self, action:Action, results:PlayerState):
		self.current = results

	def play_card(self, card:Cards) ->Optional[Action]:
		rv = None
		play = None
		while not self.current.legal_action(rv, card):
			if(randrange(2) == 1):
				play = card
			else:
				play = self.current.hand
			print(self.current.hand, card, play)
			target = randrange(self.current.num_players)
			try:
				if(play == Cards.GUARD):
					rv = self.play_guard(self.index, target, list(Cards)[randrange(len(list(Cards)))])
				elif(play == Cards.PRIEST):
					rv = self.play_priest(self.index, target)
				elif(play == Cards.BARON):
					rv = self.play_baron(self.index, target)
				elif(play == Cards.HANDMAID):
					rv = self.play_handmaid(self.index)
				elif(play == Cards.PRINCE):
					rv = self.play_prince(self.index, target)
				elif(play == Cards.KING):
					rv = self.play_king(self.index, target)
				elif(play == Cards.COUNTESS):
					rv = self.play_countess(self.index)
				else:
					rv = None
			except IllegalActionException as e:
				pass
		return rv
