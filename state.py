from cards import Cards
from collections import Counter
from actions import Action
from exceptions import IllegalActionException
from typing import List, Tuple, Set, Optional
import typing
from random import randrange

class PlayerState(object):
	def __init__(self, num_players:int, index:int, scores:List[int], discards:List[List[Cards]], known:List[Tuple[int,Cards]], eliminated:Set[int]):
		self.num_players = num_players
		self.index = index
		self.scores = scores
		self.discards = discards
		self.known = known
		self.eliminated = eliminated
		self.hand = None
		for i in range(len(known)):
			if known[i][0] == self.index:
				self.hand = known[i][1]
		if self.hand == None:
			raise ValueError('known did not contain hand of player %d' % index)

	def legal_action(self, action:Action, drawn:Cards) ->bool:
		if action is None:
			return False
		try:
			if self.hand != action.card and drawn != action.card:
				raise IllegalActionException('Player does not hold the played card')
			if (self.hand == Cards.COUNTESS or drawn == Cards.COUNTESS) and (action.card == Cards.KING or action.card == Cards.PRINCE):
				raise IllegalActionException('Player must play the countess')
			if action.target != -1:
				if action.target in self.eliminated:
					raise IllegalActionException('Target is already eliminated')
				if action.target == self.index and action.card == Cards.PRINCE:
					pass
				elif self.handmaid(action.target) and ((not self.all_handmaid(action.player)) or action.card == Cards.PRINCE):
					raise IllegalActionException('Target is protected by the handmaid')
		except IllegalActionException as e:
			print(e)
			return False
		return True

	def handmaid(self, player:int) ->bool:
		if (not 0 <= player < self.num_players) or len(self.discards[player]) == 0:
			return False
		return self.discards[player][-1] == Cards.HANDMAID

	def all_handmaid(self, player:int) ->bool:
		rv = True
		for i in range(self.num_players):
			rv = rv and (i in self.eliminated or self.handmaid(i) or i == player)
		return rv

	def unseen_cards(self) ->List[Cards]:
		counter: typing.Counter[Cards] = Counter()
		for i in range(self.num_players):
			for card in self.discards[i]:
				counter[card] += 1
		for i in range(len(self.known)):
			counter[self.known[i][1]] += 1
		rv = []
		for card in Cards:
			for _ in range(counter[card], card.value[2]):
				rv.append(card)
		return rv


class GameState(object):
	def __init__(self, num_players: int):
		if not(2 <= num_players <= 4):
			raise ValueError('Number of agents out of range')
		self.num_players = num_players
		self.scores = [0 for _ in range(self.num_players)]
		self.new_round()
		self.next_player = 0

	def __str__(self):
		return 'GameState: {{num_players: {0}, next_player: {1}, scores: {2}}}'.format(self.num_players, self.next_player, self.scores)

	def __repr__(self):
		return self.__str__()

	def new_round(self):
		self.new_deck()
		self.deck_top = 0
		self.discards = [[] for _ in range(self.num_players)]
		self.hand = []
		self.known = [[False for _ in range(self.num_players)] for _ in range(self.num_players)]
		for i in range(self.num_players):
			self.hand.append(self.deck[self.deck_top])
			self.deck_top += 1
			self.known[i][i] = True

	def new_deck(self):
		self.deck = []
		for card in Cards:
			for _ in range(card.value[2]):
				self.deck.append(card)
		for _ in range(200):
			i1 = randrange(len(self.deck))
			i2 = randrange(len(self.deck))
			card_buf = self.deck[i1]
			self.deck[i1] = self.deck[i2]
			self.deck[i2] = card_buf

	def get_player_state(self, player_index:int) ->Optional[PlayerState]:
		if not (0 <= player_index < self.num_players):
			raise ValueError('index out of range')
		if(self.hand[player_index] == None):
			return None
		known = []
		for i in range(len(self.known[player_index])):
			if self.known[player_index][i]:
				known.append((i, self.hand[i]))
		eliminated = set()
		for i in range(self.num_players):
			if self.hand[i] == None:
				eliminated.add(i)
		return PlayerState(self.num_players, player_index, self.scores, self.discards, known, eliminated)

	def legal_action(self, action:Action, drawn:Cards) ->bool:
		if action is None:
			return False
		try:
			if self.hand[action.player] != action.card and drawn != action.card:
				raise IllegalActionException('Player does not hold the played card')
			if self.next_player != action.player:
				raise IllegalActionException('Wrong player in action')
			if (self.hand[action.player] == Cards.COUNTESS or drawn == Cards.COUNTESS) and (action.card == Cards.KING or action.card == Cards.PRINCE):
				raise IllegalActionException('Player must play the countess')
			if(action.target != -1):
				if self.hand[action.target] == None:
					raise IllegalActionException('Target is already eliminated')
				if self.handmaid(action.target) and ((not self.all_handmaid(action.player)) or action.card == Cards.PRINCE):
					raise IllegalActionException('Target is protected by the handmaid')
		except IllegalActionException as e:
			print(e)
			return False
		return True

	def handmaid(self, player:int) ->bool:
		if (not 0 <= player < self.num_players) or len(self.discards[player]) == 0:
			return False
		return self.discards[player][-1] == Cards.HANDMAID

	def all_handmaid(self, player:int) ->bool:
		rv = True
		for i in range(self.num_players):
			rv = rv and (self.hand[i] is None or self.handmaid(i) or i == player)
		return rv

	def draw_card(self):
		rv = self.deck[self.deck_top]
		self.deck_top += 1
		return rv

	def update(self, action:Action, card:Cards):
		self.discards[action.player].append(action.card)
		try:
			self.legal_action(action, card)
		except IllegalActionException as e:
			#undo action
			self.discards[action.player].pop()
			raise e
		if action.card == self.hand[action.player]:
			self.hand[action.player] = card
			for i in range(self.num_players):
				if(i != action.player):
					self.known[i][action.player] = False
		if action.card == Cards.GUARD:
			self.guard_action(action)
		elif action.card == Cards.PRIEST:
			self.priest_action(action)
		elif action.card == Cards.BARON:
			self.baron_action(action)
		elif action.card == Cards.HANDMAID:
			pass
		elif action.card == Cards.PRINCE:
			self.prince_action(action)
		elif action.card == Cards.KING:
			self.king_action(action)
		elif action.card == Cards.COUNTESS:
			pass
		elif action.card == Cards.PRINCESS:
			self.princess_action(action)
		else:
			raise IllegalActionException('Illegal Action? Something\'s gone very wrong')

		if(self.round_over()):
			for i in range(self.num_players):
				for j in range(self.num_players):
					self.known[i][j] = True
			winner = self.round_winner()
			self.scores[winner] += 1
			self.next_player = winner
		else:
			self.next_player = (self.next_player + 1) % self.num_players
			while (self.hand[self.next_player] is None):
				self.next_player = (self.next_player + 1) % self.num_players

	def guard_action(self, action:Action):
		if(self.all_handmaid(action.player)):
			print('Player %d is protected by the handmaid' % action.target)
			return
		elif(action.guess == self.hand[action.target]):
			self.discards[action.target].append(self.hand[action.target])
			self.hand[action.target] = None
			for p in range(self.num_players):
				self.known[p][action.target] = True
			print('Player %d had the %s and is eliminated from the round' %(action.target, action.card.value[1]))
			return
		print('Player %d does not have the %s' %(action.target, action.card.value[1]))

	def priest_action(self, action:Action):
		if(self.all_handmaid(action.player)):
			print('Player %d is protected by the handmaid' % action.target)
		else:
			self.known[action.player][action.target] =True
			print('Player %d sees player %d\'s card' % (action.player, action.target))

	def baron_action(self, action:Action):
		if(self.all_handmaid(action.player)):
			print('Player %d is protected by the handmaid' % action.target)
		elim = -1
		if(self.hand[action.player].value[0] > self.hand[action.target].value[0]):
			elim = action.target
		elif(self.hand[action.player].value[0] > self.hand[action.target].value[0]):
			elim = action.player

		if elim != -1:
			self.discards[elim].append(self.hand[elim])
			self.hand[elim] = None
			for p in range(self.num_players):
				self.known[p][elim] = True
			print('Player %d holds the lesser card: %s and is eliminated' % (elim, self.discards[elim][-1].value[1]))
		else:
			self.known[action.player][action.target] = True
			self.known[action.target][action.player] = True
			print('Both players hold the same card, and neither is eliminated')

	def prince_action(self, action:Action):
		self.discards[action.target].append(self.hand[action.target])
		if(self.hand[action.target] == Cards.PRINCESS):
			self.hand[action.target] = None
			for p in range(self.num_players):
				self.known[p][action.target] = True
			print('Player %d discarded the princess and is eliminated' % action.target)
		else:
			self.hand[action.target] = self.deck[self.deck_top]
			self.deck_top += 1
			for p in range(self.num_players):
				self.known[p][action.target] = True
			print('Player %d discards the %s' % (action.target, self.discards[action.target][-1].value[1]))

	def king_action(self, action:Action):
		if(self.all_handmaid(action.player)):
			print('Player %d is protected by the handmaid' % action.target)
		self.known[action.player][action.target] = True
		self.known[action.target][action.player] = True
		card_buf = self.hand[action.player]
		self.hand[action.player] = self.hand[action.target]
		self.hand[action.target] = card_buf
		print('Player %d and player %d swap cards' %(action.player, action.target))

	def princess_action(self, action:Action):
		self.hand[action.player] = None
		for p in range(self.num_players):
			self.known[p][action.player] = True
		print('Player %d played the princess and is eliminated' % (action.player))

	def round_over(self) ->bool:
		remaining = 0
		for i in range(self.num_players):
			if self.hand[i] is not None:
				remaining += 1
		return remaining == 1 or (len(self.deck) - self.deck_top < 2)

	def round_winner(self):
		winner = 1
		top_card = -1
		discard_val = -1
		for i in range(self.num_players):
			if(self.hand[i] is not None):
				dv = 0
				for j in range(len(self.discards[i])):
					dv += self.discards[i][j].value[0]
				if(self.hand[i].value[0] > top_card or (self.hand[i].value[0] == top_card and dv > discard_val)):
					winner = i
					top_card = self.hand[i].value[0]
					discard_val = dv
		return winner

	def game_over(self) ->bool:
		return self.game_winner() != -1

	def game_winner(self) ->int:
		threshold = 0
		if(self.num_players == 4):
			threshold = 4
		elif(self.num_players == 3):
			threshold = 5
		elif(self.num_players == 2):
			threshold = 7
		for i in range(self.num_players):
			if(self.scores[i] == threshold):
				return i
		return -1







