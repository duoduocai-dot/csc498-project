#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
from breakout import Breakout
import matplotlib.pyplot as plt
import pickle


# In[2]:



# In[143]:


# ep = 0.9*1000
# for e in range(1,10000):
#     ep = ep/e*200
#     print(e, ep)


# In[154]:


class DoubleQLearning():

    def __init__(self, ballSpeeds, gamma=0.9, epsilon=1, decay=-0.0001, steps=1000):
        self.paddleXLocations, self.ballXLocations, self.ballYLocations =  self.discretizeStateSpaceAllStates(800, 600)

        self.ballSpeeds = ballSpeeds

        # policy estimate for each state
        self.policy = {}

        # Q-value estimate in each state
        self.q_values1  = {}
        self.q_values2  = {}

        for px in self.paddleXLocations:
            for bx in self.ballXLocations:
                for by in self.ballYLocations:
                    for ballSpeed in self.ballSpeeds:
                        # default action is to do nothing
                        self.policy[(px, bx, by, ballSpeed[0], ballSpeed[1])] = 2
                        for action in range(3):
                            self.q_values1[((px, bx, by, ballSpeed[0], ballSpeed[1]), action)] = 0
                            self.q_values2[((px, bx, by, ballSpeed[0], ballSpeed[1]), action)] = 0

        self.alpha = 0.9
        self.gamma = gamma
        self.epsilon = epsilon
        self.decay = decay
        self.k = 1
        self.steps = steps


    def double_q_learning(self, states, actions, rewards):
        # self.epsilon = 0.9*1000

        for t in range(len(states)):
            state = tuple(states[t])
            reward = rewards[t]
            action = actions[t]
            # print(state)
            # print(reward)
            # print(action)
            # break



            if t < len(states) - 1:
                nextState = tuple(states[t+1])

                currentQValue1 = self.q_values1[(state, action)]
                currentQValue2 = self.q_values2[(state, action)]

                nextQValue1Action0 = self.q_values1[(nextState, 0)]
                nextQValue1Action1 = self.q_values1[(nextState, 1)]
                nextQValue1Action2 = self.q_values1[(nextState, 2)]

                nextQValue2Action0 = self.q_values2[(nextState, 0)]
                nextQValue2Action1 = self.q_values2[(nextState, 1)]
                nextQValue2Action2 = self.q_values2[(nextState, 2)]

                rand_prob_for_q_func_choice = np.random.random()

                if rand_prob_for_q_func_choice < 0.5:
                    QValueActionsForNextStateForQ2 = [nextQValue2Action0, nextQValue2Action1, nextQValue2Action2]
                    bestActionForNextState = max(enumerate(QValueActionsForNextStateForQ2), key=lambda x: x[1])[0]
                    nextQValue = self.q_values1[(nextState, bestActionForNextState)]
                    self.q_values1[(state, action)] = currentQValue1 + self.alpha * (reward + self.gamma*nextQValue - currentQValue1)
                else:
                    QValueActionsForNextStateForQ1 = [nextQValue1Action0, nextQValue1Action1, nextQValue1Action2]
                    bestActionForNextState = max(enumerate(QValueActionsForNextStateForQ1), key=lambda x: x[1])[0]
                    nextQValue = self.q_values2[(nextState, bestActionForNextState)]
                    self.q_values2[(state, action)] = currentQValue2 + self.alpha * (reward + self.gamma*nextQValue - currentQValue2)


            Q1Action0 = self.q_values1[(state, 0)]
            Q1Action1 = self.q_values1[(state, 1)]
            Q1Action2 = self.q_values1[(state, 2)]

            Q2Action0 = self.q_values2[(state, 0)]
            Q2Action1 = self.q_values2[(state, 1)]
            Q2Action2 = self.q_values2[(state, 2)]

            QValueActionsForState = [Q1Action0 + Q2Action0, Q1Action1 + Q2Action1, Q1Action2 + Q2Action2]

            bestAction = max(enumerate(QValueActionsForState), key=lambda x: x[1])[0]

            random_probability = np.random.random()
            at = 0

            if random_probability < 1 - self.epsilon:
                # evaluate best action
                self.policy[state] = bestAction
            else:
                # explore random action
                self.policy[state] = np.random.randint(3)


        # self.epsilon = self.epsilon/t*100



    def epsilon_greedy_policy(self, obs):
        """
        obs: integer representing state

        returns integer representing action for current state,
        according to epsilon-greedy policy (see handout)

        epsilon is stored in self.epsilon

        Hint:
        act = random_agent(obs) #obtains a random action for obs
        act = self.__call__(obs) #obtains action according to self.policy
        """

        # get next action
        random_probability = np.random.random()
        at = 0

        if random_probability < 1 - self.epsilon:
            # evaluate best action
            at = self.policy[obs]
        else:
            # explore random action
            at = np.random.randint(3)

        # update epsilon, it goes to 0
        # so we eventually stop exploring and instead start evaluating
#         self.epsilon = self.epsilon/self.k*100

        return at


    # given state [paddle x-location, ball x-location, ball y-location, ball x-speed, ball y-speed, bricks left] from environment
    # descretize state space for each variable and remove bricks left
    # so paddle x-locations are split into 10 possible locations (because paddle is 80 pixels wide and game screen is 800)
    # ball x-locations are split into 40 possible locations, ball y-location into 20
    def discretizeStateSpace(self, state):
        paddleXLocation = state[0]
        ballXLocation = state[1]
        ballYLocation = state[2]
        ballSpeed = [state[3], state[4]]

        stateToReturn = [0,0,0,ballSpeed[0], ballSpeed[1]]

        for px in self.paddleXLocations:
            if paddleXLocation <= px:
                stateToReturn[0] = px
                break

        for bx in self.ballXLocations:
            if ballXLocation <= bx:
                stateToReturn[1] = bx
                break

        for by in self.ballYLocations:
            if ballYLocation <= by:
                stateToReturn[2] = by
                break

        return stateToReturn




    # get all possible paddle x-locations, ball x-locations, and ball y-locations
    # so paddle x-locations are split into 10 possible locations (because paddle is 80 pixels wide and game screen is 800)
    # ball x-locations are split into 40 possible locations, ball y-location into 20
    # def discretizeStateSpaceAllStates(self, screenWidth, screenHeight):
    #     # for paddle x-locations, split screenWidth by 80 (800/80 = 10 locations)
    #     paddleXLocations = []
    #     for i in range(0, screenWidth, 80):
    #         paddleXLocations.append(i)
    #
    #
    #     # for ball x-locations, split screenWidth by 20 (800/20 = 40 locations)
    #     ballXLocations = []
    #     for i in range(0, screenWidth, 20):
    #         ballXLocations.append(i)
    #
    #     # for ball y-locations, split screenWidth by 30 to get 20 locations (600/30 = 20 locations)
    #     ballYLocations = []
    #     for i in range(0, screenHeight, 30):
    #         ballYLocations.append(i)
    #
    #     return paddleXLocations, ballXLocations, ballYLocations

    # get all possible paddle x-locations, ball x-locations, and ball y-locations
    # so paddle x-locations are split into 10 possible locations (because paddle is 80 pixels wide and game screen is 800)
    # ball x-locations are split into 40 possible locations, ball y-location into 20
    # more states
    # def discretizeStateSpaceAllStates(self, screenWidth, screenHeight):
    #     # for paddle x-locations, split screenWidth by 80 (800/80 = 10)
    #     paddleXLocations = []
    #     for i in range(0, screenWidth, 80):
    #         paddleXLocations.append(i)
    #
    #
    #     # for ball x-locations, split screenWidth by 10 (800/10 = 80 locations)
    #     ballXLocations = []
    #     for i in range(0, screenWidth, 10):
    #         ballXLocations.append(i)
    #
    #     # for ball y-locations, split screenWidth by 20 to get 30 locations (600/20 = 30 locations)
    #     ballYLocations = []
    #     for i in range(0, screenHeight, 20):
    #         ballYLocations.append(i)
    #
    #     return paddleXLocations, ballXLocations, ballYLocations

    # even more states
    def discretizeStateSpaceAllStates(self, screenWidth, screenHeight):
        # for paddle x-locations, split screenWidth by 80 (800/40 = 20)
        paddleXLocations = []
        for i in range(0, screenWidth, 40):
            paddleXLocations.append(i)


        # for ball x-locations, split screenWidth by 10 (800/10 = 80 locations)
        ballXLocations = []
        for i in range(0, screenWidth, 10):
            ballXLocations.append(i)

        # for ball y-locations, split screenWidth by 20 to get 30 locations (600/20 = 30 locations)
        ballYLocations = []
        for i in range(0, screenHeight, 20):
            ballYLocations.append(i)

        return paddleXLocations, ballXLocations, ballYLocations



    def collect_data(self, env):
        obs = self.discretizeStateSpace(env.reset())

        rewards = []
        states = []
        actions = []
#         self.k = 0

        # for step in range(15000): # A
        for step in range(self.steps):
            states.append(obs)
            act = self.epsilon_greedy_policy(tuple(obs))
#             act = self.policy[tuple(obs)]
            obs, rew, done = env.step(act)
            obs = self.discretizeStateSpace(obs)
            rewards.append(rew)
            actions.append(act)
#             self.k+=1

        states[-1] = obs

        return states, actions, rewards

    def train(self):

        breakout_env = Breakout()
        breakout_env.make()

        breakout_env.reset()

        ballspeeds = list(breakout_env.speeds.values())
        doubleQLearningAgent = DoubleQLearning(ballspeeds, decay=self.decay, steps=self.steps)

        episodes = 40000
        rewards_ = []

        for e in range(episodes):
            breakout_env.reset()
            states, actions, rewards = doubleQLearningAgent.collect_data(breakout_env)
            doubleQLearningAgent.double_q_learning(states, actions, rewards )
            doubleQLearningAgent.epsilon = doubleQLearningAgent.epsilon + doubleQLearningAgent.decay
            doubleQLearningAgent.k+=1
            if doubleQLearningAgent.epsilon < 0:
                doubleQLearningAgent.epsilon = 0

            rewards_.append(sum(rewards))
            print("episode =", e, " epsilon =", doubleQLearningAgent.epsilon, " rewards in episode = ", sum(rewards), "steps = ", str(self.steps))

        plt.plot(rewards_)
        plt.ylabel('rewards')
        plt.xlabel('episodes')
        plt.title("rewards for tabular double q learnging, episodes = "+str(episodes) + ", epsilon decay = 0.0.00005, steps = " +str(self.steps)+ ", brickLayout = " + str(breakout_env.brickLayout))
        plt.savefig('Rewards_Double_Q_Learning.png', bbox_inches='tight')

        with open('saved_double_q_learning_policy.pkl', 'wb') as f:
            pickle.dump(doubleQLearningAgent.policy, f)

        with open('saved_double_q_learning_q_values1.pkl', 'wb') as f:
            pickle.dump(doubleQLearningAgent.q_values1, f)

        with open('saved_double_q_learning_q_values2.pkl', 'wb') as f:
            pickle.dump(doubleQLearningAgent.q_values2, f)


# training code
# breakout_env = Breakout()
# breakout_env.make()
#
# breakout_env.reset()
#
# ballspeeds = list(breakout_env.speeds.values())
# doubleQLearningAgent = DoubleQLearning(ballspeeds, decay=-0.000026, steps=20000)
# doubleQLearningAgent.train()

# In[155]:


# max(enumerate([1,2,3]), key=lambda x: x[1])[0]


# In[ ]:

#
