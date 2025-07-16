"""
    LoRaWAN Parameters
"""
import numpy as np
import math
import simpy
import matplotlib.pyplot as plt
# turn on/off graphics
graphics = 1

# do the full collision check
full_collision = False

# RSSI global values for antenna
dir_30 = 4
dir_90 = 2
dir_150 = -4
dir_180 = -3

# this is an array with measured values for sensitivity
# [SF,125KHz,250kHz,500kHz]
sf7 = np.array([7,-126.5,-124.25,-120.75])
sf8 = np.array([8,-127.25,-126.75,-124.0])
sf9 = np.array([9,-131.25,-128.25,-127.5])
sf10 = np.array([10,-132.75,-130.25,-128.75])
sf11 = np.array([11,-134.5,-132.75,-128.75])
sf12 = np.array([12,-133.25,-132.25,-132.25])

# receiver sensitivities of different SF and Bandwidth combinations
sensi = np.array([sf7,sf8,sf9,sf10,sf11,sf12])

# minimum SNR required for demodulation at different spreading factors
SNR_Req = np.array([-7.5,-10,-12.5,-15,-17.5,-20])


SF = np.array([7,8,9,10,11,12])
Carrier_Frequency = np.array([867100000,867300000,867500000,867700000,
                       867900000,868100000,868300000,868500000])
Transmission_Power = np.array([2,4,6,8,10,12,14])

TP_SUM = 2 + 4 + 6 + 8 + 10 + 12 + 14
SF_SUM = float(7/(2^7)+8/(2^8)+9/(2^9)+10/(2^10)+11/(2^11)+12/(2^12))

# adaptable LoRaWAN parameters to users
nrNodes = 100
radius = 5000
PayloadSize = 20
avgSendTime = 4000
nrNetworks = 1
simtime = 3600000 * 24
full_collision = 1

# allocation_method = "Random"
# allocation_method = "EXP3"
allocation_method = "DLoRaMesh"           

# allocation_method = "DLoRa"               

network_topology = "Mesh"
# network_topology = "Star"

AskJoinTime = 160000
JoinReqTime = 160000
JoinConfirmTime = 160000

Routing_Flag = 0

# global stuff
GW = None # global variable for the gateway
nodes = [] # list of nodes
UnconnectedNodes = [] # list of nodes that are not connected to the AdHocNetwork
Devices = [] # list of devices, including GW and nodes
env = simpy.Environment() # simulation environment

JoinAskNodeSet = [] # list of nodes that sent AskJoin packets
JoinReqNodeSet = [] # list of JoinReq packets sent by nodes
JoinConfirmNodeSet = [] # list of JoinConfirm packets sent by nodes

# max distance: 300m in city, 3000 m outside (5 km Utz experiment)
# also more unit-disc like according to Utz

NumSent = 0
NumReceived = 0
NumLost = 0

NumCollided = 0
NumPathlost = 0

TotalPacketSize =0 
RecPacketSize = 0 # size of received packets
TotalEnergyConsumption = 0 # total energy consumption of the network
TotalPacketAirtime  = 0 # total airtime of packets in the network

# list of received packets
recPackets=[]
# list of collided packets
collidedPackets=[]
# list of lost packets
lostPackets = []

# global value of packet index numbers
PacketIndex = 0

Ptx = 14 # packet transmission power
gamma = 2.32
d0 = 1000
std = 7.8           
Lpld0 = 128.75
GL = 0

# prepare graphics and add sink
if (graphics == 1):
    plt.ion()
    plt.figure()
    ax = plt.gcf().gca()

link_line = 1


# list of base stations
NodeInTransmission = [] # list of nodes in transmission at the same time

NodeInTransmissionToNode = []

packetsRecBS = [] # Packets received by GW

Project_Path = "D:\Files\IoT\LoRa\LoRa Simulator\LoRaRoutingSim"

class LoRaParameters:
    sf = 9
    cr = 1
    bw = 125
    tp = 14
    cf = 868000000
    PayloadSize = PayloadSize

class EXP3_Config:
    eposide_duration = 1600000  
    eval_duration = 12000000

    num_episode = 100
        
    NetworkEnergyEfficiency = []
    NetworkPDR = []

    NetPDR = 0
    NetThroughput = 0
    NetEnergyEfficiency = 0

    result_folder_path = f"D:\Files\IoT\LoRa\LoRa Simulator\LoRaRoutingSim\EXP3\Results"
    
class DLoRaMesh_Config:
    eposide_duration = 1600000  
    eval_duration = 12000000

    num_episode = 10
        
    NetworkEnergyEfficiency = []
    NetworkPDR = []

    NetPDR = 0
    NetThroughput = 0
    NetEnergyEfficiency = 0

    result_folder_path = f"D:\Files\IoT\LoRa\LoRa Simulator\LoRaRoutingSim\MAB\Results"

class DLoRa_Config:
    DLoRa_Variant = 2 # 0: epsilon-greedy, 1: decaying-greedy, 2: UCB
    
    coef = 2 # coefficient of UCB
    initialize_flag = 1

    initialize_duration = 12000000
    eposide_duration =  1600000
    eval_duration = 12000000

    num_episode = 10
    
    NetworkEnergyEfficiency = []
    NetworkPDR = []

    NetPDR = 0
    NetThroughput = 0
    NetEnergyEfficiency = 0

    result_folder_path = f"D:\Files\IoT\LoRa\LoRa Simulator\LoRaRoutingSim\DLoRa\Results"

class Random_Config:
    eposide_duration = 1600000  
    eval_duration = 12000000

    num_episode = 10
        
    NetworkEnergyEfficiency = []
    NetworkPDR = []

    NetPDR = 0
    NetThroughput = 0
    NetEnergyEfficiency = 0

    result_folder_path = f"D:\Files\IoT\LoRa\LoRa Simulator\LoRaRoutingSim\Random\Results"
            