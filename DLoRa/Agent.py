import ParameterConfig
from ParameterConfig import *
import numpy as np
class DLoRaAgent:
    def __init__(self):
        self.SF_arms = ParameterConfig.SF
        self.Fre_arms = ParameterConfig.Carrier_Frequency
        self.TP_arms = ParameterConfig.Transmission_Power
        
        # each agent has three bandits
        self.K_SF = len(self.SF_arms)
        self.K_Fre = len(self.Fre_arms)
        self.K_TP = len(self.TP_arms)

        # intialize the expected reward of the handles of each bandit as 0
        self.Q_SF = np.zeros(self.K_SF, dtype=float)
        self.Q_Fre = np.zeros(self.K_Fre, dtype=float)
        self.Q_TP = np.zeros(self.K_TP, dtype=float)
        
        # Number of the choices of each handdle of each bandit
        self.counts_SF = np.zeros(self.K_SF)
        self.counts_Fre = np.zeros(self.K_Fre)
        self.counts_TP = np.zeros(self.K_TP)
        
        self.SF_index = 0
        self.Fre_index = 0
        self.TP_index = 0

        # reward for each step
        self.rewards = [0,0,0]
        
        # cumulative rewards of each LoRa resource of each agent
        self.cumulative_reward_SF = 0
        self.cumulative_reward_Fre = 0
        self.cumulative_reward_TP = 0

        self.action = []
        # record the action chosen by the agent for each step
        self.actions = []

    def actions_choose(self):
        # the agent pull three handles for each step
        raise NotImplementedError
    
    def Expected_Reward_Update(self):
        self.Q_SF[self.SF_index] += (self.rewards[0] - self.Q_SF[self.SF_index]) / (self.counts_SF[self.SF_index] + 1)
        
        self.Q_Fre[self.Fre_index] += (self.rewards[1] - self.Q_Fre[self.Fre_index]) / (self.counts_Fre[self.Fre_index] + 1)
        
        self.rewards[2] = self.rewards[2] - float(ParameterConfig.Transmission_Power[self.TP_index]/TP_SUM)*1.8
        self.Q_TP[self.TP_index] += (self.rewards[2] - self.Q_TP[self.TP_index]) / (self.counts_TP[self.TP_index] + 1)

""" UCB(Upper Confidence Boundary) algorithm, inherit from DLoRa"""
class UCB(DLoRaAgent):
    def __init__(self,coef):
        super(UCB, self).__init__()
        self.total_count = 0
        self.coef = coef

    def actions_choose(self):
        self.total_count += 1
        '''SF choose'''
        ucb_sf = self.Q_SF + self.coef * np.sqrt(
            np.log(self.total_count) / (2 * (self.counts_SF + 1)))  # calculate ucb of sf
        k_sf = np.argmax(ucb_sf)
        self.counts_SF[k_sf] += 1
        '''Carrier frequency choose'''
        ucb_fre = self.Q_Fre + self.coef * np.sqrt(
            np.log(self.total_count) / (2 * (self.counts_Fre + 1)))  # calculate ucb of fre
        k_fre = np.argmax(ucb_fre)
        self.counts_Fre[k_fre] += 1
        '''Transmission power choose'''
        ucb_tp = self.Q_TP + self.coef * np.sqrt(
            np.log(self.total_count) / (2 * (self.counts_TP + 1)))  # calculate ucb of fre
        k_tp = np.argmax(ucb_tp)
        self.counts_TP[k_tp] += 1

        self.SF_index = k_sf
        self.Fre_index = k_fre
        self.TP_index = k_tp
        
        sf = self.SF_arms[k_sf]
        fre = self.Fre_arms[k_fre]
        tp = self.TP_arms[k_tp]
        
        return sf, fre, tp