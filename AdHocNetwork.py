import random
import os
import ParameterConfig
from ParameterConfig import *
from Gateway import myBS
from Node import myNode
from TransmissionProcess import *


def Establishment():
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
    
    '''Gateway AskJoin process'''
    ParameterConfig.env.process(transmit_JoinAsk(ParameterConfig.env,ParameterConfig.GW)) # Initiate the AskJoin process for the gateway
    ParameterConfig.env.run(until=AskJoinTime)
    # Clear the process after running
    ParameterConfig.env = simpy.Environment() 
    
    if ParameterConfig.JoinReqNodeSet:
        for node in ParameterConfig.JoinReqNodeSet:
            ParameterConfig.env.process(transmit_JoinReq(ParameterConfig.env,node))
        ParameterConfig.JoinConfirmNodeSet = []   
        ParameterConfig.env.run(until=JoinReqTime)
        ParameterConfig.env = simpy.Environment() 
        
        '''Node JoinConfirm process'''
        if ParameterConfig.JoinConfirmNodeSet:
            for node in ParameterConfig.JoinConfirmNodeSet:
                ParameterConfig.env.process(transmit_JoinConfirm(ParameterConfig.env,node)) 
            ParameterConfig.env.run(until=JoinConfirmTime)
            ParameterConfig.env = simpy.Environment() 
    
    iteration = 0
    while True:
        print("Size of JoinAskNodeSet:",len(ParameterConfig.JoinAskNodeSet))
        iteration += 1
        
        if ParameterConfig.JoinAskNodeSet: # if there are nodes in JoinAskNodeSet
            '''Node AskJoin process'''
            for node in ParameterConfig.JoinAskNodeSet:
                ParameterConfig.env.process(transmit_JoinAsk(ParameterConfig.env,node))
            ParameterConfig.JoinAskNodeSet = []
            ParameterConfig.JoinReqNodeSet = []
            ParameterConfig.env.run(until=AskJoinTime)
            ParameterConfig.env = simpy.Environment() 
            
            print("AskJoin process finishes. Size of JoinAskNodeSet:",len(ParameterConfig.JoinAskNodeSet),"| Size of JoinReqNodeSet:",len(ParameterConfig.JoinReqNodeSet))
            
            '''Node JoinReq process'''
            if ParameterConfig.JoinReqNodeSet:
                for node in ParameterConfig.JoinReqNodeSet:
                    ParameterConfig.env.process(transmit_JoinReq(ParameterConfig.env,node))
                ParameterConfig.JoinConfirmNodeSet = []   
                ParameterConfig.env.run(until=JoinReqTime)
                ParameterConfig.env = simpy.Environment() 
                
                print("JoinReq process finished. Size of JoinConfirmNodeSet:",len(ParameterConfig.JoinConfirmNodeSet))
                
                '''Node JoinConfirm process'''
                if ParameterConfig.JoinConfirmNodeSet:
                    for node in ParameterConfig.JoinConfirmNodeSet:
                        ParameterConfig.env.process(transmit_JoinConfirm(ParameterConfig.env,node)) 
                    ParameterConfig.env.run(until=JoinConfirmTime)
                    ParameterConfig.env = simpy.Environment() 
                    
                    print("JoinConfirm process finished. Size of JoinConfirmNodeSet:",len(ParameterConfig.JoinConfirmNodeSet))

            print("---Iteration ", iteration, " finishes.---")
            
        elif not ParameterConfig.JoinAskNodeSet and ParameterConfig.UnconnectedNodes:
            #print("UnconnectedNodes:",len(UnconnectedNodes))
            '''if there are no nodes in JoinAskNodeSet but there are still unconnected nodes'''
            while ParameterConfig.UnconnectedNodes:
                for node in ParameterConfig.UnconnectedNodes:
                    if node.sf < 12:
                        pass
                    else:
                        ParameterConfig.UnconnectedNodes.remove(node)  # remove nodes that have reached the maximum spreading factor                    
                if ParameterConfig.UnconnectedNodes:
                    ParameterConfig.JoinReqNodeSet = ParameterConfig.UnconnectedNodes
                    '''Unconnected Nodes JoinReq process'''
                    for node in ParameterConfig.JoinReqNodeSet:
                        if node.sf < 12:
                            node.sf += 1 # increase the spreading factor for unconnected nodes
                        ParameterConfig.env.process(Unconnected_transmit_JoinReq(ParameterConfig.env,node))
                    ParameterConfig.JoinConfirmNodeSet = []
                    ParameterConfig.env.run(until=JoinReqTime)
                    ParameterConfig.env = simpy.Environment() 
                    '''Node JoinConfirm process'''
                    if ParameterConfig.JoinConfirmNodeSet:
                        for node in ParameterConfig.JoinConfirmNodeSet:
                            ParameterConfig.env.process(Unconnected_transmit_JoinConfirm(ParameterConfig.env,node)) 
                        ParameterConfig.env.run(until=JoinConfirmTime)
                        ParameterConfig.env = simpy.Environment()
                    
        elif not ParameterConfig.JoinAskNodeSet and not ParameterConfig.UnconnectedNodes:  
            # print("Size of JoinAskNodeSet:",len(JoinAskNodeSet)) 
            break
    
    print("AdHoc Network Established with {} nodes.".format(len(ParameterConfig.nodes)))
    
    for node in ParameterConfig.Devices:
        parent_ids = [Parent.ID for Parent in node.ParentSet]  # Collect Parent IDs
        child_ids = [Child.ID for Child in node.ChildSet]  # Collect Parent IDs
        print("Node ID:", node.ID, "Parent IDs:", parent_ids, "Child IDs:", child_ids, "Hop Count:", node.HopCount)
    
    #prepare show
    if (graphics == 1):
        # graphics for node
        for node in ParameterConfig.nodes:
            if node.HopCount == 1:
                color = 'red'
            elif node.HopCount == 2:
                color = 'green'
            elif node.HopCount == 3:
                color = 'blue'
            else:
                color = 'gray'  # Default color for other hop counts
            
            ax.add_artist(plt.Circle((node.x, node.y), 40, fill=True, color=color))
            ax.text(node.x + 5, node.y + 5, str(node.ID), fontsize=9, ha='left', va='bottom')  # Add node ID above the node
            
            if link_line:
                # Draw dashed lines to parent nodes
                for parent in node.ParentSet:
                    ax.plot([node.x, parent.x], [node.y, parent.y], 'k--', linewidth=1)  # Dashed line to parent

        # graphics for base station
        ax.scatter(ParameterConfig.GW.x, ParameterConfig.GW.y,
                   marker='^', color='red', s=100, zorder=10, label="Gateway")
        ax.text(ParameterConfig.GW.x + 5, ParameterConfig.GW.y + 5, str(ParameterConfig.GW.ID), fontsize=9, ha='left', va='bottom')  # Add GW ID

        plt.xlim([-radius, radius])
        plt.ylim([-radius, radius])
        plt.draw()
        plt.pause(0.001)  # Add a short pause to allow the plot to update

        plt.show(block=True)  # Keep the plot window open until it is closed by the user
        
    ParameterConfig.Routing_Flag = 1


            






    