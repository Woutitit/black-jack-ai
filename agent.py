from game import *

#Init global vars
EPISODES 	= 5000000
EPSILON 	= 0.1
ACTIONS 	= ["hit", "stand"]

state_action_pair_rewards = {} #Holds all average reward values for all state-action pairs
state_action_pair_encounters = {} #Holds encounters count for each state-action pair. Used to calculate the average reward.

def get_reward_values(state):
	#Note: We won't get all reward values for each action but only the ones for current state
	#Rewards are 0 when no values known
	hit_reward = 0
	stand_reward = 0

	if (state, "hit") in state_action_pair_rewards:
		hit_reward = state_action_pair_rewards[(state, "hit")]

	if (state, "stand") in state_action_pair_rewards:
		stand_reward = state_action_pair_rewards[(state, "stand")]

	return np.array([hit_reward, stand_reward])

def choose_action(state):
	if np.random.random() < EPSILON:
		return np.random.choice(ACTIONS)
	else:
		#Get Q (= average reward) values for each action in current state
		state_action_rewards = get_reward_values(state)
		
		best_action = np.argmax(state_action_rewards) #Select action with highest avg reward value for current state
		return ACTIONS[best_action] 

def execute_action(action, agent):
	if action == "hit":
		agent.hit()
	if action == "stand":
		agent.stand()

def get_reward(agent_hand_status):
	#Check if the agent won, drawed or lost and give +1, 0 and -1 to each state-action pair accordingly
	if agent_hand_status == "win":
		return 1
	elif agent_hand_status == "loss":
		return -1
	else:
		return 0

def update_q_table(sa_pairs, reward):
	#Assign new encounter and reward values to each state-action from current episode
	for sa_pair in sa_pairs:
		avg_sa_reward = 0 #We put 0 so that we have a value when key does not exist yet
		sa_count = 0

		#If state-action pair exists (and thus also the encounter count for it) assign these values to local vars
		if sa_pair in state_action_pair_rewards and sa_pair in state_action_pair_encounters:
			avg_sa_reward = state_action_pair_rewards[sa_pair]
			sa_count = state_action_pair_encounters[sa_pair]

		#Calculate new encounter count and average reward value for state-action
		new_sa_count = sa_count + 1
		new_avg_reward = (avg_sa_reward * sa_count + reward) / new_sa_count

		#Override old encounter and reward values
		state_action_pair_rewards[sa_pair] = new_avg_reward
		state_action_pair_encounters[sa_pair] =  new_sa_count


#Main training loop
for i in range(EPISODES):

	#Init game
	game = Game()
	game.set_players(("Agent", "Dealer"))
	game.run()

	#Init local vars
	agent 				= game.players[0]
	dealer 				= game.players[1]
	deck 				= game.deck
	state_action_pairs 	= [] #Holds all state-action pairs of this episode

	#Keep playing until we bust or stand
	while game.turn == 0: #0 = player 1's (the agent's) turn

		while agent.hand.total_value < 11: #Always hit under hand value of 11. 
			agent.hit()

		#After above loop has end we will need to decide which action to take. This means we now need to observe the state.
		#The full state consists of our cards, the value of it and one dealer card we know about and the value of that card.
		#state = (tuple(agent.hand.cards), agent.hand.total_value, dealer.hand.cards[0], dealer.hand.cards[0][2])

		#However, we will use a simplified state space so we don't need to so many episodes to get good reward values for each state-action pair
		#and we can print it out because it does not excee memory.
		state = (agent.hand.total_value, dealer.hand.cards[0][2])

		#Choose random action or pick action with the highest value for current observed state.
		action = choose_action(state)

		#Add state-action pair to temporary/episodal state-action pairs list
		state_action_pairs.append((state, action)) #Reward is default 0 

		#Now obviously execute our chosen action
		execute_action(action, agent)

	#After episode get reward based on whether we won, drawed or lost
	reward = get_reward(agent.hand.status)

	#Add reward to global average reward value of each state-action that was in this episode
	update_q_table(state_action_pairs, reward)
	print(agent.hand.status)

print("Training done.")

#Instead of printing out a graph, print out the simplified reward values for all the pairs and see if it makes sense. 
#For example you know it works if it has a very low reward value to hit when you have 21 you know it works.
print(state_action_pair_rewards)