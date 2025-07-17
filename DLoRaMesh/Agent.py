import ParameterConfig
from ParameterConfig import *
import numpy as np
class DLoRaAgent:
    def __init__(self,ParentSet):
        self.Parent_Ids = [Parent.ID for Parent in ParentSet]
        self.SF_arms = ParameterConfig.SF
        self.Parent_arms = self.Parent_Ids
        self.TP_arms = ParameterConfig.Transmission_Power
        
        # each agent has three bandits
        self.K_SF = len(self.SF_arms)
        self.K_Parent = len(self.Parent_arms)
        self.K_TP = len(self.TP_arms)

        # intialize the expected reward of the handles of each bandit as 0
        self.Q_SF = np.zeros(self.K_SF, dtype=float)
        self.Q_Parent = np.zeros(self.K_Parent, dtype=float)
        self.Q_TP = np.zeros(self.K_TP, dtype=float)
        
        # Number of the choices of each handdle of each bandit
        self.counts_SF = np.zeros(self.K_SF)
        self.counts_Parent = np.zeros(self.K_Parent)
        self.counts_TP = np.zeros(self.K_TP)
        
        self.SF_index = 0
        self.Parent_index = 0
        self.TP_index = 0

        # reward for each step
        self.rewards = [0,0,0]
        
        self.action = []
        # record the action chosen by the agent for each step
        self.actions = []

    def actions_choose(self):
        # the agent pull three handles for each step
        raise NotImplementedError
    
    def Expected_Reward_Update(self):
        self.rewards[0] = self.rewards[0] + 5*float((self.SF_arms[self.SF_index]/(2^self.SF_arms[self.SF_index]))/SF_SUM)
        self.Q_SF[self.SF_index] += (self.rewards[0] - self.Q_SF[self.SF_index]) / (self.counts_SF[self.SF_index] + 1)
        
        self.Q_Parent[self.Parent_index] += (self.rewards[1] - self.Q_Parent[self.Parent_index]) / (self.counts_Parent[self.Parent_index] + 1)
        
        self.rewards[2] = self.rewards[2] - float(ParameterConfig.Transmission_Power[self.TP_index]/TP_SUM)*1.8
        self.Q_TP[self.TP_index] += (self.rewards[2] - self.Q_TP[self.TP_index]) / (self.counts_TP[self.TP_index] + 1)

""" UCB(Upper Confidence Boundary) algorithm, inherit from DLoRa"""
class UCB(DLoRaAgent):
    def __init__(self, ParentSet):
        super(UCB, self).__init__(ParentSet)
        self.total_count = 0
        self.coef = DLoRaMesh_Config.coef

    def actions_choose(self):
        self.total_count += 1
        '''SF choose'''
        ucb_sf = self.Q_SF + self.coef * np.sqrt(
            np.log(self.total_count) / (2 * (self.counts_SF + 1)))  # calculate ucb of sf
        k_sf = np.argmax(ucb_sf)
        self.counts_SF[k_sf] += 1
        '''relay choose'''
        ucb_parent = self.Q_Parent + self.coef * np.sqrt(
            np.log(self.total_count) / (2 * (self.counts_Parent + 1)))  # calculate ucb of parent
        k_parent = np.argmax(ucb_parent)
        self.counts_Parent[k_parent] += 1
        '''Transmission power choose'''
        ucb_tp = self.Q_TP + self.coef * np.sqrt(
            np.log(self.total_count) / (2 * (self.counts_TP + 1)))  # calculate ucb of parent
        k_tp = np.argmax(ucb_tp)
        self.counts_TP[k_tp] += 1

        self.SF_index = k_sf
        self.Parent_index = k_parent
        self.TP_index = k_tp
        
        sf = self.SF_arms[k_sf]
        parentid = self.Parent_arms[k_parent]
        tp = self.TP_arms[k_tp]
        
        return sf, parentid, tp