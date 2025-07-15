import os
import matplotlib.pyplot as plt
from ParameterConfig import *
import ParameterConfig
from Node import *
from Gateway import *
from EXP3.Agent import EXP3Agent
import random

def EXP3_Run(nodes):
    '''Initialize the EXP3 agent for each node'''
    for node in nodes:
        node.agent = EXP3Agent(ParentSet = node.ParentSet)
    
    # set_seed(random_seed)
    for episode in range(EXP3_Config.num_episode):
        EXP3_Train(nodes, episode)

    # Training_Chart(EXP3_Config)

    # EXP3_Eval(nodes)

    # Result_Record(EXP3_Config.NetPDR, EXP3_Config.NetEnergyEfficiency)              


def EXP3_Train(nodes, episode):
    
    # initialize simulation environment current time for each episode
    env = simpy.Environment()
    
    ParameterConfig.NodeInTransmissionToNode = [[] for _ in range(len(Devices))]

    ''' initialize the environment at the beginning of episode '''
    reset_simulation_stats()
    
    ''' Initialize the data of nodes and their transmission processes for each episode '''
    for node in nodes:
        node.NumSent = 0
        node.NumLost = 0
        node.NumReceived = 0

        ''' Before simulation, initialize each node's transmission process '''
        env.process(transmit_multi_hop_packet(env,node))

    env.run(until=EXP3_Config.eposide_duration)


    for node in nodes:
        node.PDR = float((node.NumReceived)/(node.NumSent))

    NetPDR = float(ParameterConfig.NumReceived/ParameterConfig.NumSent) 
    # NetEnergyEfficiency = float(8*ParameterConfig.RecPacketSize / ParameterConfig.TotalEnergyConsumption)

    # EXP3_Config.NetworkEnergyEfficiency.append(NetEnergyEfficiency)
    EXP3_Config.NetworkPDR.append(NetPDR)

    # print(f"episode={episode} | PDR={NetPDR*100:.2f} | Network EE={NetEnergyEfficiency:.2f}")
    print(f"episode={episode} | PDR={NetPDR*100:.2f}")

'''
After the Ad-Hoc network is established, nodes start to transmit packets to the gateway.
'''
def transmit_multi_hop_packet(env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        yield env.timeout(random.expovariate(1.0/float(node.period)))
        
        EXP3_Generate_Multi_Hop_Packet(node)
        
        FormerSourceID = node.packet.SourceID
        SourceID = node.packet.SourceID
        TargetID = node.packet.TargetID
        
        ParameterConfig.PacketIndex += 1
        
        '''Check collisions with the packets having the same target node'''
        if node in ParameterConfig.NodeInTransmissionToNode[node.packet.TargetID]:
            pass
        else:
            # adding packet if no collision
            if multihop_checkcollision(node.packet)==1:    
                node.packet.collided = 1
            else:
                node.packet.collided = 0
            ParameterConfig.NodeInTransmissionToNode[node.packet.TargetID].append(node)
            node.packet.addTime = env.now
            node.packet.Index = ParameterConfig.PacketIndex
        
        yield env.timeout(node.packet.rectime)
        
        '''Weight update of the EXP3 agent'''
        node.agent.Probability_Weight_Update()
        
        # complete packet has been received by base station
        # can remove it for next transmission                  
        if node in ParameterConfig.NodeInTransmissionToNode[node.packet.TargetID]:
            ParameterConfig.NodeInTransmissionToNode[node.packet.TargetID].remove(node)
        
        '''Whether the packet is lost or not'''
        if node.packet.lost:
            pass
        else:
            if node.packet.collided == 0: # Relay node receive the packet
                SourceID = TargetID
                if TargetID != 0:
                    TargetID = EXP3_Generate_Relay_Packet(Devices[TargetID], FormerSourceID)
                
            else:
                pass
        
        
        while SourceID != 0 and node.packet.collided == 0 and node.packet.lost == False:
            '''Check collisions with the packets having the same target node'''
            if Devices[SourceID] in ParameterConfig.NodeInTransmissionToNode[Devices[SourceID].RelayPackets[FormerSourceID].TargetID]:
                pass
            else:
                # adding packet if no collision
                if multihop_checkcollision(Devices[SourceID].RelayPackets[FormerSourceID])==1:    
                    Devices[SourceID].RelayPackets[FormerSourceID].collided = 1
                else:
                    Devices[SourceID].RelayPackets[FormerSourceID].collided = 0

                ParameterConfig.NodeInTransmissionToNode[Devices[SourceID].RelayPackets[FormerSourceID].TargetID].append(node)
                Devices[SourceID].RelayPackets[FormerSourceID].addTime = env.now
            
            yield env.timeout(node.packet.rectime)
            
            '''Weight update of the EXP3 agent'''
            Devices[SourceID].agent.Probability_Weight_Update()
            
            
            # complete packet has been received by base station
            # can remove it for next transmission                  
            if Devices[SourceID] in ParameterConfig.NodeInTransmissionToNode[Devices[SourceID].RelayPackets[FormerSourceID].TargetID]:
                ParameterConfig.NodeInTransmissionToNode[Devices[SourceID].RelayPackets[FormerSourceID].TargetID].remove(Devices[SourceID])
                      
            '''Whether the packet is lost or not'''
            if  Devices[SourceID].RelayPackets[FormerSourceID].lost:
                node.packet.lost = True
            else:
                if  Devices[SourceID].RelayPackets[FormerSourceID].collided == 0: # Relay node receive the packet
                    if TargetID != 0:
                        FormerSourceID = SourceID
                        SourceID = TargetID
                        TargetID = EXP3_Generate_Relay_Packet(Devices[TargetID], FormerSourceID)
                    else:
                        SourceID = 0
                else:
                    node.packet.collided = 1   
                    
                           
        '''Whether the packet is received by the gateway or not'''
        ParameterConfig.NumSent += 1
        node.NumSent += 1
        if node.packet.collided == 1 or node.packet.lost == True:
            ParameterConfig.NumLost += 1
            node.NumLost += 1
        else:
            ParameterConfig.NumReceived += 1
            node.NumReceived += 1
        
# node generate "virtul" packets for each gateway
def EXP3_Generate_Multi_Hop_Packet(node):
    node.packet = None

    '''Choose Target node and Transmission Power'''
    tp, TargetID = node.agent.actions_choose()
    
    node.dist = get_distance(node.x, node.y, Devices[TargetID]) # distance between node and gateway
    
    PacketPara = LoRaParameters()
    
    PacketPara.sf = node.sf
    PacketPara.cf = node.ParentFreSet.get(TargetID, 868100000)
    PacketPara.tp = tp 
    node.packet = DirectionalPacket(node.ID, TargetID, PacketPara, node.dist)
    # print('node %d' %id, "x", node.x, "y", node.y, "dist: ", node.dist, "my BS:", node.bs.id)

def EXP3_Generate_Relay_Packet(node, FormerNodeID):
    
    '''Choose Target node and Transmission Power'''
    tp, TargetID = node.agent.actions_choose()
    
    node.dist = get_distance(node.x,node.y,Devices[TargetID]) # distance between node and gateway
    
    PacketPara = LoRaParameters()

    PacketPara.sf = node.sf
    PacketPara.cf = node.ParentFreSet.get(TargetID, 868100000)
    PacketPara.tp = tp 
    
    node.RelayPackets[FormerNodeID] = DirectionalPacket(node.ID, TargetID, PacketPara, node.dist)

    return TargetID


def Training_Chart(Method_Config):
    '''Network Energy Efficiency'''
    plt.figure()
    x = range(1, Method_Config.num_episode+1)
    plt.plot(x, Method_Config.NetworkEnergyEfficiency, label='NetworkEnergyEfficiency', color='blue')

    plt.title('Network Energy Efficiency changes with increasing episode')
    plt.xlabel('Episode')
    plt.ylabel('Energy Efficiency/(bits/mJ)')
    plt.legend()

    fig1_name = 'NetworkEnergyEfficiency_plot.png'
    plt.savefig(os.path.join(Method_Config.result_folder_path, fig1_name))

    '''Network PDR'''
    plt.figure()
    plt.plot(x, Method_Config.Network_PDR, '-', color='b')
    plt.title('Network PDR changes with increasing episode')
    plt.xlabel('Episode')
    plt.ylabel('Network PDR')

    fig2_name = 'Network_PDR_plot.png'
    plt.savefig(os.path.join(Method_Config.result_folder_path, fig2_name))


def reset_simulation_stats():
    """重置仿真统计量，确保每次动作测试独立"""
    ParameterConfig.NumSent = 0
    ParameterConfig.NumReceived = 0
    ParameterConfig.NumLost = 0
    ParameterConfig.TotalPacketSize =0 
    ParameterConfig.RecPacketSize = 0 # size of received packets
    ParameterConfig.TotalEnergyConsumption = 0 # total energy consumption of the network
    ParameterConfig.TotalPacketAirtime  = 0 # total airtime of packets in the network


