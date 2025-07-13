import random
import ParameterConfig
from ParameterConfig import *
from Propagation import checkcollision, rssi, snr
from Node import get_distance
from datetime import datetime

'''
In AskJoin process, gateway and nodes broadcast packets to each other.
Fro gateway, we don't need to check for collisions, because the packets 
are not sent at the same time. For nodes, collsions may happens but they 
do not matter. As long as the AskJoin packet can be received by the node, 
the node can join the network.    
'''
def transmit_JoinAsk(env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        # print("Number of nodes", len(ParameterConfig.nodes))
        
        yield env.timeout(random.expovariate(1.0/float(node.period)))

        node.Generate_AskJoin()
           
        '''Check which node can receive the AskJoin packet.'''
        #print("Number of nodes", len(ParameterConfig.nodes))
        for n in ParameterConfig.nodes:
            if n.ID != node.ID: 
                distance = get_distance(node.x, node.y, n) # distance between node and gateway
                # print("distance:",distance)
                RSSI = rssi(node.packet, distance) # received signal strength indicator
                SNR = snr(RSSI) # signal to noise ratio

                if RSSI > node.packet.minisensi and SNR > node.packet.miniSNR:
                    '''The node can receive the packet, add the source node to the parent set.'''
                    # print("Node %d received AskJoin packet from Node %d" %(n.ID, node.ID))
                    if node.ID == 0 and n.HopCount == 0: # Parent node is the Gateway
                        n.HopCount = 1
                        if node not in n.ParentSet:   
                            n.ParentSet.append(node)
                            if n in ParameterConfig.UnconnectedNodes: # if the node is not connected to the network
                                ParameterConfig.UnconnectedNodes.remove(n)
                            if n not in ParameterConfig.JoinAskNodeSet:
                                ParameterConfig.JoinAskNodeSet.append(n) # add the node to the JoinAskNodeSet
                        
                    elif node.ID != 0:
                        if n.HopCount == 0: # child node receive the AskJoin packet from the parent node for the first time
                            n.HopCount = node.HopCount + 1                             
                            n.ParentSet.append(node)
                            
                            if n in ParameterConfig.UnconnectedNodes: # if the node is not connected to the network
                                ParameterConfig.UnconnectedNodes.remove(n)
                            if n not in ParameterConfig.JoinReqNodeSet: # 1st layer nodes don't need to send JoinReq packets
                                ParameterConfig.JoinReqNodeSet.append(n) # add the node to the JoinReqSet
                            if n not in ParameterConfig.JoinAskNodeSet:
                                ParameterConfig.JoinAskNodeSet.append(n) # add the node to the JoinAskNodeSet                    
                        
                        elif n.HopCount == node.HopCount + 1:
                            if node not in n.ParentSet:   
                                n.ParentSet.append(node)
                                if n in ParameterConfig.UnconnectedNodes: # if the node is not connected to the network
                                    ParameterConfig.UnconnectedNodes.remove(n)
                                if n not in ParameterConfig.JoinReqNodeSet: # 1st layer nodes don't need to send JoinReq packets
                                    ParameterConfig.JoinReqNodeSet.append(n) # add the node to the JoinReqSet
                                if n not in ParameterConfig.JoinAskNodeSet:
                                    ParameterConfig.JoinAskNodeSet.append(n) # add the node to the JoinAskNodeSet
                            
                    
            # take first packet rectime, stop for rectime        
            yield env.timeout(node.packet.rectime)

'''
In JoinReq process, child nodes send directional packets to their potential parent nodes. 
When the parent nodes receive the JoinReq packets, they add the child nodes to their ChildSet.
Parent nodes allocate each of its child node a unique channel.
'''
def transmit_JoinReq(env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        yield env.timeout(random.expovariate(1.0/float(node.period)))
       
        node.Generate_JoinReq()
        
        '''Check whether the parent nodes can receive the JoinReq packet.'''
        for packet in node.JoinReqSet:
            if packet.lost == False:
                if node not in Devices[packet.TargetID].ChildSet and len(Devices[packet.TargetID].ChildSet) < 8: 
                    Devices[packet.TargetID].ChildSet.append(node) # add the node to the parent node's ChildSet
                    if Devices[packet.TargetID] not in ParameterConfig.JoinConfirmNodeSet:
                        ParameterConfig.JoinConfirmNodeSet.append(Devices[packet.TargetID])
            else:
                continue   
                
            '''Check collisions for JoinReq packets.'''
            node.packet = packet # assign the packet to the node's packet
            if (node in NodeInTransmission):
                pass
                # print ("ERROR: packet already in")
            else:
                # adding packet if no collision
                if (checkcollision(packet) == 1):
                    packet.collided = 1
                else:
                    packet.collided = 0
                NodeInTransmission.append(node)
                packet.addTime = env.now
                    
            # take first packet rectime, stop for rectime        
            yield env.timeout(packet.rectime)

            # can remove the node for next transmission                  
            if (node in NodeInTransmission):
                NodeInTransmission.remove(node)


'''
In JoinConfirm process, parent nodes send directional packets to their child nodes. 
JoinConfirm packets include the channel information for each child node. 
'''
def transmit_JoinConfirm(env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        yield env.timeout(random.expovariate(1.0/float(node.period)))
       
        node.Generate_JoinConfirm()
        
        '''Check whether the parent nodes can receive the JoinConfirm packet.'''
        for packet in node.JoinConfirmSet:
            if packet.lost == False:
               if node in Devices[packet.TargetID].ParentSet: 
                    Devices[packet.TargetID].ParentFreSet[node.ID] = packet.cf  # allocate channel to the child node
            else:
                continue   
                
            '''Check collisions for JoinReq packets.'''
            if (node in NodeInTransmission):
                pass
                # print ("ERROR: packet already in")
            else:
                # adding packet if no collision
                if (checkcollision(packet) == 1):
                    packet.collided = 1
                else:
                    packet.collided = 0
                NodeInTransmission.append(node)
                packet.addTime = env.now
                    
            # take first packet rectime, stop for rectime        
            yield env.timeout(packet.rectime)

            # can remove the node for next transmission                  
            if (node in NodeInTransmission):
                NodeInTransmission.remove(node)

'''
    This function is used to transmit JoinReq packets for unconnected nodes.
    Unconnected nodes will increase their spreading factor and try to connect to the network.
'''
def Unconnected_transmit_JoinReq(env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        yield env.timeout(random.expovariate(1.0/float(node.period)))

        node.Generate_AskJoin()
        
        '''Check which node can receive the unconnected JoinReq packet.'''
        for n in ParameterConfig.nodes:
            if n.ID != node.ID: 
                distance = get_distance(node.x, node.y, n) # distance between node and gateway
                RSSI = rssi(node.packet, distance) # received signal strength indicator
                SNR = snr(RSSI) # signal to noise ratio
                if RSSI < node.packet.minisensi or SNR < node.packet.miniSNR:
                    '''The node cannot receive the packet, it is lost.'''
                    pass
                else:
                    '''The node can receive the packet, add the source node to the parent set.'''
                    n.sf = node.sf
                    if node.HopCount == 0:
                        node.HopCount = n.HopCount + 1
                    else:
                        if n.HopCount+1 < node.HopCount:
                            node.HopCount = n.HopCount + 1
                        else:
                            pass
                        
                    if node not in n.ChildSet and len(n.ChildSet) < 8:
                        n.ChildSet.append(node) # add the node to the parent node's ChildSet
                        if node in ParameterConfig.UnconnectedNodes: # if the node is not connected to the network
                            ParameterConfig.UnconnectedNodes.remove(node)
                        if n not in ParameterConfig.JoinConfirmNodeSet:
                            ParameterConfig.JoinConfirmNodeSet.append(n)    
        
        yield env.timeout(node.packet.rectime)


'''
    This function is used to transmit JoinConfirm packets for unconnected nodes.
    Unconnected nodes will increase their spreading factor and try to connect to the network.
'''
def Unconnected_transmit_JoinConfirm(env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        yield env.timeout(random.expovariate(1.0/float(node.period)))
       
        node.Generate_JoinConfirm()
        
        '''Check whether the parent nodes can receive the JoinConfirm packet.'''
        for packet in node.JoinConfirmSet:
            if packet.lost == False:
               Devices[packet.TargetID].cf = packet.cf # allocate channel to the child node
               if Devices[packet.SouceID] not in node.ParentSet:
                   node.ParentSet.append(Devices[packet.TargetID])   
            else:
                continue   
                
            '''Check collisions for JoinReq packets.'''
            if (node in NodeInTransmission):
                pass
                # print ("ERROR: packet already in")
            else:
                # adding packet if no collision
                if (checkcollision(packet) == 1):
                    packet.collided = 1
                else:
                    packet.collided = 0
                NodeInTransmission.append(node)
                packet.addTime = env.now
                    
            # take first packet rectime, stop for rectime        
            yield env.timeout(packet.rectime)

            # can remove the node for next transmission                  
            if (node in NodeInTransmission):
                NodeInTransmission.remove(node)
    


'''
After the Ad-Hoc network is established, nodes start to transmit packets to the gateway.
'''
def transmit_packet(self,env,node):
    while True:
        # time before sending anything (include prop delay)
        # send up to 2 seconds earlier or later
        # simulate the time interval of discrete events happened in a system
        yield env.timeout(random.expovariate(1.0/float(node.period)))

        # time sending and receiving
        # packet arrives -> add to base station
        node.sent = node.sent + 1 # number of packets sent by the node       
        global packetSeq
        packetSeq += 1 # total number of packet of the network

        node.Generate_Packet()

        if (node in NodeInTransmission):
                print ("ERROR: packet already in")
        else:
                # adding packet if no collision
                if (checkcollision(node.packet)==1):
                    node.packet.collided = 1
                else:
                    node.packet.collided = 0
                NodeInTransmission.append(node)
                node.packet.addTime = env.now
                node.packet.seqNr = packetSeq
        self.TotalPacketSize += node.packet.PS
        self.TotalEnergyConsumption += float(node.packet.tx_energy / 1000)
        self.TotalPacketAirtime += float(node.packet.rectime / 1000)            
            
        # take first packet rectime, stop for rectime        
        yield env.timeout(node.packet[0].rectime)

        # if packet did not collide, add it in list of received packets
        # unless it is already in

        if node.packet.lost:
            lostPackets.append(node.packet.seqNr)
        else:
            if node.packet.collided == 0:               
                packetsRecBS.append(node.packet.seqNr)

                # recPackets is a global list of received packets
                # not updated for multiple networks        
                if (recPackets):
                    if (recPackets[-1] != node.packet.seqNr):
                        recPackets.append(node.packet.seqNr)
                        self.RecPacketSize += node.packet.PS
                else:
                    recPackets.append(node.packet.seqNr)
                    self.RecPacketSize += node.packet.PS
            else:
                # XXX only for debugging
                collidedPackets.append(node.packet.seqNr)

        # complete packet has been received by base station
        # can remove it for next transmission
                        
        if (node in NodeInTransmission):
            NodeInTransmission.remove(node)

            
