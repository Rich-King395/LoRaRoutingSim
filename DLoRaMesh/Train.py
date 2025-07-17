import os
import matplotlib.pyplot as plt
from tensorboardX import SummaryWriter
from ParameterConfig import *
import ParameterConfig
from Node import *
from Gateway import *
from DLoRaMesh.Agent import UCB
from Plot.TopologyGraphics import Topology_Graphics
from Plot.Plot import sf_distribution, tp_distribution
import random

def DLoRaMesh_Run(nodes):
    '''Initialize the DLoRaMesh agent for each node'''
    for node in nodes:
        node.agent = UCB(ParentSet = node.ParentSet)
    
    # set_seed(random_seed)
    DLoRaMesh_Train(nodes)

    # Training_Chart(DLoRaMesh_Config)
    
    # Topology_Graphics(nodes)

    DLoRaMesh_Eval(nodes)
    
    # Result_Record(DLoRaMesh_Config.NetPDR, DLoRaMesh_Config.NetEnergyEfficiency)              


def DLoRaMesh_Train(nodes):
    for episode in range(DLoRaMesh_Config.num_episode):
        # initialize simulation environment current time for each episode
        env = simpy.Environment()

        ''' initialize the environment at the beginning of episode '''
        reset_simulation_stats()
        
        ''' Initialize the data of nodes and their transmission processes for each episode '''
        for node in nodes:
            node.NumSent = 0
            node.NumLost = 0
            node.NumReceived = 0

            ''' Before simulation, initialize each node's transmission process '''
            env.process(transmit_multi_hop_packet(env,node))

        env.run(until=DLoRaMesh_Config.eposide_duration)


        for node in nodes:
            node.PDR = float((node.NumReceived)/(node.NumSent))

        NetPDR = float(ParameterConfig.NumReceived/ParameterConfig.NumSent) 
        NetEnergyEfficiency = float(8*ParameterConfig.RecPacketSize / ParameterConfig.TotalEnergyConsumption)

        DLoRaMesh_Config.NetworkEnergyEfficiency.append(NetEnergyEfficiency)
        DLoRaMesh_Config.NetworkPDR.append(NetPDR)

        # print(f"episode={episode} | PDR={NetPDR*100:.2f} | Network EE={NetEnergyEfficiency:.2f}")
        print(f"episode={episode} | PDR={NetPDR*100:.2f} | EE = {NetEnergyEfficiency:.2f} | Number of packet sent = {ParameterConfig.NumSent} | "
            f"Number of packet received = {ParameterConfig.NumReceived} | "
            f"Number of path lost packet = {ParameterConfig.NumPathlost} | "
            f"Number of packet collided = {ParameterConfig.NumCollided}")

def DLoRaMesh_Eval(nodes):
    ParameterConfig.Eval_Flag = 1
    
    sorted_nodes = sorted(nodes, key=lambda node: node.DisttoGW)
    
    for index, node in enumerate(sorted_nodes):
        node.DistID = index
    
    print("Start evaluation of DLoRaMesh")
    
    writer = SummaryWriter(log_dir='./logs/DLoRaMesh_run')
    
    while True:
        min_capacity = min(node.BatteryCapacity for node in nodes)
        
        for index, node in enumerate(sorted_nodes):
            writer.add_scalar(f'Battery/Node{node.DistID}/Distance{node.DisttoGW:.1f}m', node.BatteryCapacity, DLoRaMesh_Config.eval_eposide)
        
        writer.add_scalar('Network/Min_Battery_Capacity', min_capacity, DLoRaMesh_Config.eval_eposide)
        
        if min_capacity <= 0:
            Surival_Time = DLoRaMesh_Config.eval_eposide * DLoRaMesh_Config.eposide_duration / 1000
            print("Network survial time is",Surival_Time,"s" )
            break  
            
        DLoRaMesh_Config.eval_eposide += 1
        
        # initialize simulation environment current time for each episode
        env = simpy.Environment()

        ''' initialize the environment at the beginning of episode '''
        reset_simulation_stats()
        
        ''' Initialize the data of nodes and their transmission processes for each episode '''
        for node in nodes:
            node.NumSent = 0
            node.NumLost = 0
            node.NumReceived = 0

            ''' Before simulation, initialize each node's transmission process '''
            env.process(transmit_multi_hop_packet(env,node))

        env.run(until=DLoRaMesh_Config.eposide_duration)

        for node in nodes:
            node.PDR = float((node.NumReceived)/(node.NumSent))

        NetPDR = float(ParameterConfig.NumReceived/ParameterConfig.NumSent) 
        NetEnergyEfficiency = float(8*ParameterConfig.RecPacketSize / ParameterConfig.TotalEnergyConsumption)

    writer.close()
    
    sf_distribution(DLoRaMesh_Config.result_folder_path)
    tp_distribution(DLoRaMesh_Config.result_folder_path)
      
'''
After the Ad-Hoc network is established, nodes start to transmit packets to the gateway.
'''
def transmit_multi_hop_packet(env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        yield env.timeout(random.expovariate(1.0/float(node.period)))
        
        DLoRaMesh_Generate_Multi_Hop_Packet(node)
        
        ParameterConfig.TotalEnergyConsumption += node.packet.tx_energy
        
        FormerSourceID = node.packet.SourceID
        SourceID = node.packet.SourceID
        TargetID = node.packet.TargetID
        
        ParameterConfig.PacketIndex += 1
        
        '''Check collisions with the packets having the same target node'''
        if node.ID in ParameterConfig.NodeInTransmissionToNode[node.packet.TargetID]:
            pass
        else:
            # adding packet if no collision
            if multihop_checkcollision(node.packet)==1:    
                node.packet.collided = 1
            else:
                node.packet.collided = 0
            ParameterConfig.NodeInTransmissionToNode[node.packet.TargetID].append(node.ID)
            node.packet.addTime = env.now
            node.packet.Index = ParameterConfig.PacketIndex
        
        yield env.timeout(node.packet.rectime)
        
        '''Agent observe reward'''
        if node.packet.lost == True or node.packet.collided == 1: 
            node.agent.rewards = [-1,-1,-1] 
        else: 
            node.agent.rewards = [1,1,1] 
        
        '''Weight update of the DLoRaMesh agent'''
        node.agent.Expected_Reward_Update()
        
        # complete packet has been received by base station
        # can remove it for next transmission                  
        if node.ID in ParameterConfig.NodeInTransmissionToNode[TargetID]:
            ParameterConfig.NodeInTransmissionToNode[TargetID].remove(node.ID)
        
        '''Whether the packet is lost or not'''
        if node.packet.lost:
            pass
        else:
            if node.packet.collided == 0: # Relay node receive the packet
                SourceID = TargetID
                if TargetID != 0:
                    TargetID = DLoRaMesh_Generate_Relay_Packet(Devices[SourceID], FormerSourceID)
                    
                    ParameterConfig.TotalEnergyConsumption += Devices[SourceID].RelayPackets[FormerSourceID].tx_energy      
            else:
                pass
        
        while SourceID != 0 and node.packet.collided == 0 and node.packet.lost == False:
            '''Check collisions with the packets having the same target node'''
            if SourceID in ParameterConfig.NodeInTransmissionToNode[TargetID]:
                pass
            else:
                # adding packet if no collision
                if multihop_checkcollision(Devices[SourceID].RelayPackets[FormerSourceID])==1:    
                    Devices[SourceID].RelayPackets[FormerSourceID].collided = 1
                else:
                    Devices[SourceID].RelayPackets[FormerSourceID].collided = 0

                ParameterConfig.NodeInTransmissionToNode[TargetID].append(SourceID)
                
                Devices[SourceID].RelayPackets[FormerSourceID].addTime = env.now
            
            yield env.timeout(node.packet.rectime)
            
            '''Agent observe reward'''
            if Devices[SourceID].RelayPackets[FormerSourceID].lost == True or Devices[SourceID].RelayPackets[FormerSourceID].collided == 1: 
                Devices[SourceID].agent.rewards = [-1,-1,-1] 
            else: 
                Devices[SourceID].agent.rewards = [1,1,1] 
            
            '''Weight update of the DLoRaMesh agent'''
            Devices[SourceID].agent.Expected_Reward_Update()
            
            # complete packet has been received by base station
            # can remove it for next transmission                  
            if SourceID in ParameterConfig.NodeInTransmissionToNode[TargetID]:
                ParameterConfig.NodeInTransmissionToNode[TargetID].remove(SourceID)
                      
            '''Whether the packet is lost or not'''
            if  Devices[SourceID].RelayPackets[FormerSourceID].lost:
                node.packet.lost = True
            else:
                if  Devices[SourceID].RelayPackets[FormerSourceID].collided == 0: # Relay node receive the packet
                    if TargetID != 0:
                        FormerSourceID = SourceID
                        SourceID = TargetID
                        TargetID = DLoRaMesh_Generate_Relay_Packet(Devices[SourceID], FormerSourceID)
                        
                        ParameterConfig.TotalEnergyConsumption += Devices[SourceID].RelayPackets[FormerSourceID].tx_energy
                        
                    else:
                        SourceID = 0
                else:
                    node.packet.collided = 1   
                    
                           
        '''Whether the packet is received by the gateway or not'''
        ParameterConfig.NumSent += 1
        node.NumSent += 1
        if node.packet.lost == True:
            ParameterConfig.NumPathlost += 1
        elif node.packet.collided == 1:
            ParameterConfig.NumCollided += 1
            
        if node.packet.collided == 0 and node.packet.lost == False:
            ParameterConfig.NumReceived += 1
            ParameterConfig.RecPacketSize += node.packet.PS
            node.NumReceived += 1
        else:
            ParameterConfig.NumLost += 1
            node.NumLost += 1
            
        
# node generate "virtul" packets for each gateway
def DLoRaMesh_Generate_Multi_Hop_Packet(node):
    node.packet = None

    '''Choose Target node and Transmission Power'''
    # tp, TargetID = node.agent.actions_choose()
    node.sf, TargetID, node.tp = node.agent.actions_choose()
    
    dist = get_distance(node.x, node.y, Devices[TargetID]) # distance between node and gateway
    
    PacketPara = LoRaParameters()
    
    PacketPara.sf = node.sf
    
    PacketPara.cf = node.ParentFreSet.get(TargetID, 868100000)
    # PacketPara.cf = random.choice(Carrier_Frequency)
    # PacketPara.tp = tp 
    PacketPara.tp = node.tp
    node.packet = DirectionalPacket(node.ID, TargetID, PacketPara, dist)
    
    if ParameterConfig.Eval_Flag == 1:
        node.BatteryCapacity -= node.packet.tx_energy*0.001
    # print('node %d' %id, "x", node.x, "y", node.y, "dist: ", node.dist, "my BS:", node.bs.id)

def DLoRaMesh_Generate_Relay_Packet(node, FormerNodeID):
    
    '''Choose Target node and Transmission Power'''
    # tp, TargetID = node.agent.actions_choose()
    node.sf, TargetID, node.tp = node.agent.actions_choose()
    
    dist = get_distance(node.x,node.y,Devices[TargetID]) # distance between node and gateway
    
    PacketPara = LoRaParameters()

    PacketPara.sf = node.sf
    PacketPara.cf = node.ParentFreSet.get(TargetID, 868100000)
    # PacketPara.cf = random.choice(Carrier_Frequency)
    # PacketPara.tp = tp
    PacketPara.tp = node.tp
    
    node.RelayPackets[FormerNodeID] = DirectionalPacket(node.ID, TargetID, PacketPara, dist)
    
    if ParameterConfig.Eval_Flag == 1:
        node.BatteryCapacity -= node.RelayPackets[FormerNodeID].tx_energy*0.001

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
    ParameterConfig.NodeInTransmissionToNode = [[] for _ in range(len(Devices))]
    ParameterConfig.NumSent = 0
    ParameterConfig.NumReceived = 0
    ParameterConfig.NumLost = 0
    ParameterConfig.NumCollided = 0
    ParameterConfig.NumPathlost = 0
    ParameterConfig.TotalPacketSize =0 
    ParameterConfig.RecPacketSize = 0 # size of received packets
    ParameterConfig.TotalEnergyConsumption = 0 # total energy consumption of the network
    ParameterConfig.TotalPacketAirtime  = 0 # total airtime of packets in the network


