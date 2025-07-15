import ParameterConfig
from ParameterConfig import *
import numpy as np
import itertools
class EXP3Agent:
    def __init__(self, ParentSet):
        Parent_Ids = [Parent.ID for Parent in ParentSet]
        
        self.arms = list(itertools.product(Transmission_Power, Parent_Ids))
        

        # number of actions
        self.K = len(self.arms)

        # initialize the expected reward of the base arms of each bandit as 0
        self.N = np.zeros(self.K, dtype=float)
        self.P = np.zeros(self.K, dtype=float)
        self.W = np.ones(self.K, dtype=float)
        
        self.action_index = 0
               
        self.l_EXP = 5
        self.alpha = 1
        self.l_EE = 100

        self.round_robin_index = 0

        self.T = 0
        # rewards for each step
        self.reward = 0

    def actions_choose(self):
        self.T += 1
        self.gamma = min(1.0, math.sqrt((self.K * math.log2(self.K))/((math.e - 1) * self.T)))

        if self.N.min() <= self.l_EXP:
            arm_index = self.round_robin_index
            self.round_robin_index += 1
            if self.round_robin_index > (self.K - 1):
                self.round_robin_index = 0
                arm_index = self.round_robin_index
        else:
            arm_index = np.random.choice(np.arange(self.K), p=self.P)

        TP, TargetID = self.arms[arm_index]
        self.action_index = arm_index
        
        return TP, TargetID

    def Probability_Weight_Update(self):
        # Probaility Update
        U = self.W[self.action_index] / np.sum(self.W)
        self.P[self.action_index] = (1 - self.gamma) * U + self.gamma / self.K
        
        self.P /= np.sum(self.P)
        
        # Weight Update
        self.W[self.action_index] = self.W[self.action_index] * np.exp((self.gamma * self.reward) / (self.K * self.P[self.action_index]))

        self.N[self.action_index] += 1 
        if self.N[self.action_index] > self.l_EXP:
            if self.P[self.action_index] < 0.5*self.P.max():
                self.P[self.action_index] = 0
                self.P /= np.sum(self.P)
        if self.N[self.action_index] > self.alpha*self.l_EE:
            self.N = np.zeros(self.K, dtype=float)
            self.alpha += 1
        



    


        





