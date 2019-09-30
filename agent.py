from actions import Action
from cards import Cards
from exceptions import IllegalActionException

class AgentInterface(type):
	def __new__(metaclass, name, bases, attrs):
		expected_methods = {'new_round':2, 'see':3, 'play_card':2}
		for method in expected_methods:
			if method not in attrs:
				raise TypeError('method %s missing from AgentInterface class' % method)
			if attrs[method].__code__.co_argcount != expected_methods[method]:
				raise TypeError('method %s requires exactly %d arguments (self inclusive)' %(method, expected_methods[method]))
		return super().__new__(metaclass, name, bases, attrs)

	def __call__(self, *args, **kwargs):
		cls = type.__call__(self, *args, **kwargs)
		for func in dir(type(self)):
			if func[:2] == '__':
				continue
			setattr(cls, func, getattr(self, func))
		return cls

	def play_guard(self, player:int, target:int,  guess:Cards) ->Action:
		print('player: {0}, target: {1}, guess: {2}'.format(player, target, guess))
		if(target == -1): raise IllegalActionException('Target myst be specified')
		if(player == target): raise IllegalActionException('Player cannot target themself')
		if(guess == None): raise IllegalActionException('Player must guess a card')
		if(guess == Cards.GUARD): raise IllegalActionException('Player cannot guess a guard')
		return Action(Cards.GUARD, player, target, guess)

	def play_priest(self, player:int, target:int) ->Action:
		if(target == -1): raise IllegalActionException('Target must be specified')
		if(player == target): raise IllegalActionException('Player cannot target themself')
		return Action(Cards.PRIEST, player, target, None)

	def play_baron(self, player:int, target:int) ->Action:
		if(target == -1): raise IllegalActionException('Target must be specified')
		if(player == target): raise IllegalActionException('Player cannot target themself')
		return Action(Cards.BARON, player, target, None)

	def play_handmaid(self, player:int) ->Action:
		return Action(Cards.HANDMAID, player, -1, None)

	def play_prince(self, player:int, target:int) ->Action:
		if(target == -1): raise IllegalActionException('Target must be specified')
		return Action(Cards.PRINCE, player, target, None)

	def play_king(self, player:int, target:int) ->Action:
		if(target == -1): raise IllegalActionException('Target must be specified')
		if(player == target): raise IllegalActionException('Player cannot target themself')
		return Action(Cards.KING, player, target, None)

	def play_countess(self, player:int) ->Action:
		return Action(Cards.COUNTESS, player, -1, None)

	def play_princess(self, player:int) ->Action:
		return Action(Cards.PRINCESS, player, -1, None)
