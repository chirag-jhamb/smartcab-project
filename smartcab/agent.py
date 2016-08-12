import random
import operator
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.a = 0.5
        self.gamma = 0.5
        self.qvalue = {}   #set qtable as empty dict
        self.future_q_max = 0  # Max(Q',a') start at 0

        #starting values for current state and action;State_0
        self.current_action = random.choice(Environment.valid_actions[1:])
        self.current_qvalue = 0
        self.current_state = ('green',None,None,None,'forward')
        self.current_reward = 0

        self.counter = 0   # counter for epsilon

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.counter = self.counter + 1  # counter for epsilon
        print "Below is the counter value"
        if self.counter == 90:
            print self.qvalue

    def q_table(self,state,action,reward):         # TODO: Learn policy based on state, action, reward

        for move in Environment.valid_actions:
            if (self.state,move) not in self.qvalue:
                self.qvalue[(state,move)] = 0

        self.future_q_max = self.qvalue[(state,action)]     #current state sensed is recorded as the future state in the simulation world, state 1
        self.qvalue[(self.current_state,self.current_action)] = ((1-self.a)*self.current_qvalue) + (self.a*(self.current_reward+(self.gamma*self.future_q_max)))
        #'future' state value is assigned to current state variable to be used in the next iteration
        self.current_state = state
        self.current_action = action
        self.current_qvalue = self.qvalue[(self.current_state,self.current_action)]
        self.current_reward = reward


    def update(self, t):
        # Gather inputs

        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        self.state = (inputs['light'],inputs['oncoming'],inputs['left'],self.next_waypoint)


        # TODO: Select action according to your policy, either random or from q-table
        epsilon = self.counter / 80.0

        if epsilon >= random.random():
            baseline = None

            for move in Environment.valid_actions:
                if (self.state,move) not in self.qvalue:
                    self.qvalue[(self.state,move)] = 0
                if self.qvalue[(self.state,move)] > baseline:
                    action = move
                    baseline = self.qvalue[(self.state,move)]

        # Execute action and get reward
            reward = self.env.act(self, action)
            self.gamma = 0.5
            self.q_table(self.state,action,reward)  #update Q table

        # Execute random action
        else:
            action = random.choice(Environment.valid_actions[1:])
            reward = self.env.act(self, action)
            self.gamma = 0
            self.q_table(self.state,action,reward) #update Q table

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline= True )  # set agent to track

    # Now simulate it
    sim = Simulator(e, update_delay=0.5)  # reduce update_delay to speed up simulation
    sim.run(n_trials=100)  # press Esc or close pygame window to quit


if __name__ == '__main__':
    run()
