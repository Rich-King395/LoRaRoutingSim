import sys
from ParameterConfig import *
from AdHocNetwork import Establishment


if __name__ == "__main__":
    # get arguments
    if len(sys.argv) == 10:
        nrNodes = int(sys.argv[1]) # number of nodes                      
        avgSendTime = int(sys.argv[2]) # average sending interval in milliseconds
        allocation_method = int(sys.argv[4]) # allocation method for LoRa parameters
        simtime = int(sys.argv[5]) # total running time in milliseconds
        nrBS = int(sys.argv[6]) # number of base stations 1,2,3,4,6,8,24
        if len(sys.argv) > 6:
            full_collision = bool(int(sys.argv[7])) # 1 to enable full collision check, 0 for simplified check
        nrNetworks = int(sys.argv[9]) # number of networks
        radius = float(sys.argv[10]) # radius of network
        PayloadSize = int(sys.argv[11]) # payloadsize of packet
    else:
        print ("------Use the default config------")
    print ("Nodes per base station:", nrNodes) 
    print ("AvgSendTime (exp. distributed):",avgSendTime)
    print ("LoRa parameters allocation method: ", allocation_method)
    print ("Simtime: ", simtime)
    print ("Full Collision: ", full_collision)
    print ("nrNetworks: ", nrNetworks)
    print ("radius: ",radius)
    print ("PayloadSize: ",PayloadSize)

    
    Establishment()
    
    