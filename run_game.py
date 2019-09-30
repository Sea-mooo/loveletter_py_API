from actions import Action
from cards import Cards
from agent import AgentInterface
from state import GameState, PlayerState
from exceptions import IllegalActionException
from typing import Optional, List
import sys

def run_game(agents:List[AgentInterface]) ->Optional[List[int]]:
	game_over = False
	winner = 0
	num_players = len(agents)
	game_state = GameState(num_players)
	player_states = [game_state.get_player_state(i) for i in range(num_players)]
	try:
		while not game_state.game_over():
			for i in range(num_players):
				player_states[i] = game_state.get_player_state(i)
				agents[i].new_round(player_states[i])
			while not game_state.round_over():
				print('Cards are:')
				for i in range(num_players):
					print('player %d:' % i, end='')
					curr_card = game_state.hand[i]
					if curr_card is None:
						print('None')
					else:
						print(curr_card.value[1])
				top_card = game_state.draw_card()
				print('Player %d draws the top card %s' % (game_state.next_player, top_card.value[1]))
				action = agents[game_state.next_player].play_card(top_card)
				try:
					game_state.update(action, top_card)
				except IllegalActionException as e:
					print('ILLEGAL ACTION PERFORMED BY PLAYER %d' % game_state.next_player)
					print(e)
					sys.exit(1)
				for i in range(num_players):
					agents[i].see(action, game_state.get_player_state(i))
			print('New Round, scores are:')
			for i in range(num_players):
				print('player %d:%d' % (i, game_state.scores[i]))
			game_state.new_round()
		print('Player %d wins the Princess\'s heart!' % game_state.game_winner())
		return game_state.scores
	except IllegalActionException as e:
		print('Something has gone wrong')
		print(e)
	return None

if __name__ == '__main__':
	from random_agent import RandomAgent
	agents = [RandomAgent() for _ in range(4)]
	foo = run_game(agents)
	if(foo != None):
		print('Scores')
		for i in range(len(foo)):
			print('\t%d: %d' % (i, foo[i]))




