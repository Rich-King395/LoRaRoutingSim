import ParameterConfig
from ParameterConfig import *
import numpy as np
import itertools
class NaiveMABAgent:
    def __init__(self, ParentSet):
        self.Parent_Ids = [Parent.ID for Parent in ParentSet]
        
        self.arms = list(itertools.product(ParameterConfig.Transmission_Power, ParameterConfig.SF, self.Parent_Ids))
        
        # self.arms = list(itertools.product(ParameterConfig.SF, self.Parent_Ids))
        
        self.arms = list(itertools.product(ParameterConfig.Transmission_Power, self.Parent_Ids))
        
        # number of actions
        self.K = len(self.arms)

        # intialize the expected reward of the base arms of each bandit as 0
        self.T = np.zeros(self.K, dtype=float)
        self.Q = np.zeros(self.K, dtype=float)

        self.l_EXP = 5
        
        self.round_robin_index = 0

        self.action_index = 0
        
        self.t = 0
        # rewards for each step
        self.reward = 0

        self.explore_flag = True

    def actions_choose(self):
        if self.T.min() <= self.l_EXP:
            arm_index = self.round_robin_index
            self.round_robin_index += 1
            if self.round_robin_index > (self.K-1) :
                self.round_robin_index = 0
        else:
            # print("开始学习：")
            self.t += 1
            
            if self.explore_flag == True:
                self.T = np.zeros(self.K, dtype=float)
                self.explore_flag = False
            ucb = self.Q + 2 * np.sqrt(np.log(self.t) / (2 * (self.T + 1)))
            arm_index = np.argmax(ucb)
        
        self.action_index = arm_index
        tp, parentid = self.arms[arm_index]
        #sf, parentid = self.arms[arm_index]
        # return tp, sf, parentid
        # return sf, parentid
        return tp, parentid

    def Expected_Reward_Update(self):
        # self.reward = self.reward + (1-float(self.arms[self.action_index][0]/14)) + (self.arms[self.action_index][1]/(2 ** self.arms[self.action_index][1])) / SF_SUM
        if self.reward == 1:
            # self.reward = (1-float(self.arms[self.action_index][0]/14)) + (self.arms[self.action_index][1]/(2 ** self.arms[self.action_index][1])) / SF_SUM
            
            self.reward = 1 + (1-float(self.arms[self.action_index][0]/14))
        
        self.T[self.action_index] += 1 
        self.Q[self.action_index] += (self.reward - self.Q[self.action_index]) / (self.T[self.action_index] + 1)