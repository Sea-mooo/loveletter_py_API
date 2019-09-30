from typing import Optional
from cards import Cards
from exceptions import IllegalActionException

class Action(object):
	def __init__(self, card:Cards, player:int, target:int, guess:Optional[Cards]):
		if not (0 <= player < 4):
			raise IllegalActionException('Player out of range')
		if card == None:
			raise IllegalActionException('No card specified')
		if not (-1 <= target < 4):
			raise IllegalActionException('Player out of range')
		self.card = card
		self.player = player
		self.target = target
		self.guess = guess
