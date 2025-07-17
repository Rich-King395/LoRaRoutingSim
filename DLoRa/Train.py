import os
import matplotlib.pyplot as plt
from tensorboardX import SummaryWriter
from ParameterConfig import *
import ParameterConfig
from Node import *
from Gateway import *
from DLoRa.Agent import *
from Plot.TopologyGraphics import Topology_Graphics, Mesh_Topology
import random

def DLoRa_Run(nodes):
    # generate BS
    ParameterConfig.GW = myBS(0) # create a gateway with ID 0

    Devices.append(ParameterConfig.GW) # add BS to the list of devices
    
    # generate node
    id = 1
    
    # Set a random number generator for node IDs
    random.seed(42)  # Initialize the random number generator
    
    while len(ParameterConfig.nodes) < nrNodes:
        # myNode takes period (in ms), base station id packetlen (in Bytes)
        # 1000000 = 16 min
        x = random.randint(-radius, radius)
        y = random.randint(-radius, radius)
        # make sure the nodes are inside the circle
        if (x ** 2 + y ** 2) > (radius ** 2):
            continue

        # create nrNodes for each base station
        node = myNode(id,x,y,avgSendTime) # For different BS, same node has different id
        
        node.HopCount = 1
        node.ParentSet = [ParameterConfig.GW]
        
        ParameterConfig.nodes.append(node)
        ParameterConfig.UnconnectedNodes.append(node)
        ParameterConfig.Devices.append(node) # add node to the list of devices
        id += 1

    '''Location recording'''
    # store nodes and basestation locations
    Location_Record = os.path.join(ParameterConfig.Project_Path, "Location_Record")
    os.makedirs(Location_Record, exist_ok=True)  # Create Location_Record folder if it doesn't exist
    
    node_path = os.path.join(Location_Record, "node.txt")  # Save node file in Location_Record
    with open(node_path, 'w') as nfile:
        for node in ParameterConfig.nodes:
            nfile.write('{x} {y} {ID}\n'.format(**vars(node)))

    basestation_path = os.path.join(Location_Record, "gateway.txt")  # Save basestation file in Location_Record
    with open(basestation_path, 'w') as bfile:
        bfile.write('{x} {y} {ID}\n'.format(**vars(ParameterConfig.GW)))  # Use ParameterConfig.GW for basestation
    
    Mesh_Topology() 
    
    ParameterConfig.Routing_Flag = 1
    
    random.seed(13)
    
    '''Initialize the DLoRa agent for each node'''
    for node in nodes:
        node.agent = UCB(DLoRa_Config.coef)
    
    # set_seed(random_seed)
    for episode in range(DLoRa_Config.num_episode):
        DLoRa_Train(nodes, episode)

    # Training_Chart(DLoRa_Config)
    
    # Topology_Graphics(nodes)

    DLoRa_Eval(nodes)

    # Result_Record(DLoRa_Config.NetPDR, DLoRa_Config.NetEnergyEfficiency)              

def DLoRa_Eval(nodes):
    ParameterConfig.Eval_Flag = 1
    
    sorted_nodes = sorted(nodes, key=lambda node: node.DisttoGW)
    
    for index, node in enumerate(sorted_nodes):
        node.DistID = index
    
    print("Start evaluation of DLoRa")
    
    writer = SummaryWriter(log_dir='./logs/DLoRa_run')
    
    while True:
        min_capacity = min(node.BatteryCapacity for node in nodes)
        
        for index, node in enumerate(sorted_nodes):
            writer.add_scalar(f'Battery/Node{node.DistID}/Distance{node.DisttoGW:.1f}m', node.BatteryCapacity, DLoRa_Config.eval_eposide)
        
        writer.add_scalar('Network/Min_Battery_Capacity', min_capacity, DLoRa_Config.eval_eposide)
        
        if min_capacity <= 0:
            Surival_Time = DLoRa_Config.eval_eposide * DLoRa_Config.eposide_duration / 1000
            print("Network survial time is",Surival_Time,"s" )
            break  
            
        DLoRa_Config.eval_eposide += 1
        
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
            env.process(transmit_single_hop_packet(env,node))

        env.run(until=DLoRa_Config.eposide_duration)

        for node in nodes:
            node.PDR = float((node.NumReceived)/(node.NumSent))

        NetPDR = float(ParameterConfig.NumReceived/ParameterConfig.NumSent) 
        NetEnergyEfficiency = float(8*ParameterConfig.RecPacketSize / ParameterConfig.TotalEnergyConsumption)

    writer.close()


def DLoRa_Train(nodes, episode):
    
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
        env.process(transmit_single_hop_packet(env,node))

    env.run(until=DLoRa_Config.eposide_duration)

    for node in nodes:
        node.PDR = float((node.NumReceived)/(node.NumSent))

    NetPDR = float(ParameterConfig.NumReceived/ParameterConfig.NumSent) 
    NetEnergyEfficiency = float(8*ParameterConfig.RecPacketSize / ParameterConfig.TotalEnergyConsumption)

    # DLoRa_Config.NetworkEnergyEfficiency.append(NetEnergyEfficiency)
    DLoRa_Config.NetworkPDR.append(NetPDR)

    # print(f"episode={episode} | PDR={NetPDR*100:.2f} | Network EE={NetEnergyEfficiency:.2f}")
    print(f"episode={episode} | PDR={NetPDR*100:.2f} | EE = {NetEnergyEfficiency:.2f} | Number of packet sent = {ParameterConfig.NumSent} | "
          f"Number of packet received = {ParameterConfig.NumReceived} | "
          f"Number of path lost packet = {ParameterConfig.NumPathlost} | "
          f"Number of packet collided = {ParameterConfig.NumCollided}")
        
'''
After the Ad-Hoc network is established, nodes start to transmit packets to the gateway.
'''
def transmit_single_hop_packet(env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        yield env.timeout(random.expovariate(1.0/float(node.period)))
        
        DLoRa_Generate_Single_Hop_Packet(node)
        
        ParameterConfig.TotalEnergyConsumption += node.packet.tx_energy
          
        ParameterConfig.PacketIndex += 1
        
        '''Check collisions with the packets having the same target node'''
        if node in ParameterConfig.NodeInTransmission:
            pass
        else:
            # adding packet if no collision
            if checkcollision(node.packet) == 1:    
                node.packet.collided = 1
            else:
                node.packet.collided = 0
            ParameterConfig.NodeInTransmission.append(node)
            node.packet.addTime = env.now
            node.packet.Index = ParameterConfig.PacketIndex
        
        yield env.timeout(node.packet.rectime)
        
        '''Agent observe reward'''
        if node.packet.lost == True or node.packet.collided == 1:
            node.agent.rewards = [-1,-1,-1] 
        else:
            node.agent.rewards = [1,1,1] # successully received, positive reward
  
        '''Weight update of the DLoRa agent'''
        node.agent.Expected_Reward_Update()
                                   
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
def DLoRa_Generate_Single_Hop_Packet(node):
    node.packet = None

    TargetID = 0 # nodes transmit packets to the gateway directly
    
    node.dist = get_distance(node.x, node.y, Devices[TargetID]) # distance between node and gateway
    
    PacketPara = LoRaParameters()
    
    PacketPara.sf, PacketPara.cf, PacketPara.tp = node.agent.actions_choose()

    node.packet = DirectionalPacket(node.ID, TargetID, PacketPara, node.dist)
    
    if ParameterConfig.Eval_Flag == 1:
        node.BatteryCapacity -= node.packet.tx_energy*0.001
    # print('node %d' %id, "x", node.x, "y", node.y, "dist: ", node.dist, "my BS:", node.bs.id)


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
    ParameterConfig.NodeInTransmission = []
    ParameterConfig.NumSent = 0
    ParameterConfig.NumReceived = 0
    ParameterConfig.NumLost = 0
    ParameterConfig.NumCollided = 0
    ParameterConfig.NumPathlost = 0
    ParameterConfig.TotalPacketSize =0 
    ParameterConfig.RecPacketSize = 0 # size of received packets
    ParameterConfig.TotalEnergyConsumption = 0 # total energy consumption of the network
    ParameterConfig.TotalPacketAirtime  = 0 # total airtime of packets in the network


