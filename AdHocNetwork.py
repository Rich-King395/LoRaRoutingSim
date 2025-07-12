import random
import os
import ParameterConfig
from ParameterConfig import *
from Gateway import myBS
from Node import myNode
from TransmissionProcess import *

class AdHocNetwork:
    def __init__(self):
        self.avgDER = 0
        self.derALL = 0
        self.RecPacketSize = 0
        self.throughput = 0
        self.EffectEnergyConsumPerByte = 0

    def Establishment(self):
        # generate BS
        ParameterConfig.GW = myBS(0) # create a gateway with ID 0

        Devices.append(ParameterConfig.GW) # add BS to the list of devices
        
        # generate node
        id = 1
        while len(nodes) < nrNodes:
            # myNode takes period (in ms), base station id packetlen (in Bytes)
            # 1000000 = 16 min
            x = random.randint(-radius, radius)
            y = random.randint(-radius, radius)
            # make sure the nodes are inside the circle
            if (x ** 2 + y ** 2) > (radius ** 2):
                continue

            # create nrNodes for each base station
            node = myNode(id,x,y,avgSendTime) # For different BS, same node has different id
            nodes.append(node)
            Devices.append(node) # add node to the list of devices
            id += 1
            
        UnconnectedNodes = nodes

        '''Location recording'''
        # store nodes and basestation locations
        Location_Record = os.path.join(Project_Path, "Location_Record")
        os.makedirs(Location_Record, exist_ok=True)  # Create Location_Record folder if it doesn't exist
        
        node_path = os.path.join(Location_Record, self.file_name+"-node.txt")  # Save node file in Location_Record
        with open(node_path, 'w') as nfile:
            for node in nodes:
                nfile.write('{x} {y} {id}\n'.format(**vars(node)))

        basestation_path = os.path.join(Location_Record, self.file_name+"-gateway.txt")  # Save basestation file in Location_Record
        with open(basestation_path, 'w') as bfile:
            bfile.write('{x} {y} {id}\n'.format(**vars(ParameterConfig.GW)))  # Use ParameterConfig.GW for basestation
            
        '''Gateway AskJoin process'''
        env.process(transmit_JoinAsk(self,env,node)) # Initiate the AskJoin process for the gateway
        env.run(until=AskJoinTime)
        # Clear the process after running
        env._processes.clear() 
        
        while True:
            if JoinAskNodeSet: # if there are nodes in JoinAskNodeSet
                '''Node AskJoin process'''
                for node in JoinAskNodeSet:
                    env.process(transmit_JoinAsk(self,env,node))
                JoinAskNodeSet = []
                JoinReqNodeSet = []
                env.run(until=AskJoinTime)
                env._processes.clear() 
                '''Node JoinReq process'''
                if JoinReqNodeSet:
                    for node in JoinReqNodeSet:
                        env.process(transmit_JoinReq(self,env,node))
                    JoinConfirmNodeSet = []   
                    env.run(until=JoinReqTime)
                    env._processes.clear() 
                    '''Node JoinConfirm process'''
                    if JoinConfirmNodeSet:
                        for node in JoinConfirmNodeSet:
                            env.process(transmit_JoinConfirm(self,env,node)) 
                        env.run(until=JoinConfirmTime)
                        env._processes.clear() 
            elif not JoinAskNodeSet and UnconnectedNodes:
                '''if there are no nodes in JoinAskNodeSet but there are still unconnected nodes'''
                while UnconnectedNodes:                    
                    JoinReqNodeSet = UnconnectedNodes
                    '''Unconnected Nodes JoinReq process'''
                    for node in JoinReqNodeSet:
                        node.sf += 1 # increase the spreading factor for unconnected nodes
                        env.process(Unconnected_transmit_JoinReq(self,env,node))
                    env.run(until=JoinReqTime)
                    env._processes.clear() 
                    '''Node JoinConfirm process'''
                    if JoinConfirmNodeSet:
                        for node in JoinConfirmNodeSet:
                            env.process(transmit_JoinConfirm(self,env,node)) 
                        env.run(until=JoinConfirmTime)
                        env._processes.clear() 
                                           
            elif not JoinAskNodeSet and not UnconnectedNodes:    
                break
                
        #prepare show
        if (graphics == 1):
            plt.xlim([-radius, radius])
            plt.ylim([-radius, radius])
            plt.draw()
            plt.show()  
            






    