import random
import os
import ParameterConfig
from ParameterConfig import *
from Propagation import checkcollision
from Gateway import myBS
from Node import myNode
from datetime import datetime

class Simulation:
    def __init__(self):
        self.sum = 0
        self.sumSent = 0
        self.sent = []
        self.der = []
        self.simstarttime = 0
        self.simendtime = 0
        self.avgDER = 0
        self.derALL = 0
        self.RecPacketSize = 0
        self.TotalPacketSize = 0
        self.TotalPacketAirtime = 0
        self.TotalEnergyConsumption = 0
        self.throughput = 0
        self.EffectEnergyConsumPerByte = 0
        self.file_name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.folder_path = os.path.join(os.getcwd(), "results")
        self.folder_path = os.path.join(self.folder_path,self.file_name)
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def run(self):
        # generate BS

        ParameterConfig.GW = myBS(0)

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
            
            env.process(Simulation.transmit(self,env,node)) # create a transmission process for each node
            id += 1

            # store nodes and basestation locations
        node_path = os.path.join(self.folder_path, self.file_name+"-node.txt")
        with open(node_path, 'w') as nfile:
            for node in nodes:
                nfile.write('{x} {y} {id}\n'.format(**vars(node)))

        basestation = os.path.join(self.folder_path, self.file_name+"-basestation.txt")
        with open(basestation, 'w') as bfile:
            bfile.write('{x} {y} {id}\n'.format(**vars(basestation)))

        #prepare show
        if (graphics == 1):
            plt.xlim([-radius, radius])
            plt.ylim([-radius, radius])
            plt.draw()
            plt.show()  
            
        # start simulation
        env.run(until=simtime)

    def results_calculation(self):
        self.sum = self.sum + len(packetsRecBS) # calculate total received packets
        self.sent.append(0)
        for i in range(0,nrNodes):
            self.sumSent = self.sumSent + nodes[i].sent
            #print ("id for node ", nodes[i].id, "BS:", nodes[i].bs.id, " sent: ", nodes[i].sent)
            self.sent[nodes[i].bs.id] = self.sent[nodes[i].bs.id] + nodes[i].sent

        # der = []
        # data extraction rate = Packet Dilvery Rate PDR
        self.PDR = 100*(len(recPackets)/float(self.sumSent))
        self.throughput = 8 * float(self.RecPacketSize) / self.TotalPacketAirtime
        self.EffectEnergyConsumPerByte = float(self.TotalEnergyConsumption) / self.RecPacketSize
    
    def results_show(self):
        # print stats and save into file
        print ("Number of received packets (independent of right base station)", len(recPackets))
        print ("Number of collided packets", len(collidedPackets))
        print ("Number of lost packets (not correct)", len(lostPackets))
        print ("Total number of packets sent: ", self.sumSent)

        print ("PDR: {:.2f}".format(self.PDR))
        print ("Network throughput: {:.3f} bps".format(self.throughput))
        print ("Effective energy consumption per byte: {:.3e} Joule".format(self.EffectEnergyConsumPerByte))

        # this can be done to keep graphics visible
        if (graphics == 1):
            input('Press Enter to continue ...')
    
    def simulation_record(self):
        result_file_name = self.file_name+"-result.txt"
        file_path = os.path.join(self.folder_path, result_file_name)
        with open(file_path, 'w') as file:
            file.write('Simulation start at {}'.format(self.simstarttime))
            file.write(' and end at {}\n'.format(self.simendtime))
            file.write('--------Parameter Setting--------\n')
            file.write('Nodes per base station: {}\n'.format(nrNodes))
            file.write('Packet generation interval: {} ms\n'.format(avgSendTime))
            file.write('LoRa parameters allocation method: {}\n'.format(allocation_method))
            file.write('Simulation duration: {} h\n'.format(int(simtime/3600000)))

            if full_collision == 1:
                file.write('Collision check mode: Full Collision Check\n')
            else:
                file.write('Collision check mode: Simple Collision Check\n')
            
            file.write('Number of networks: {}\n'.format(nrNetworks))
            file.write('Network topology radius: {} m\n'.format(radius))
            file.write('Packet payload size: {}\n\n'.format(PayloadSize))

            file.write('--------Simulation Results--------\n')
            file.write("Total number of packets sent: {}\n".format(self.sumSent))
            file.write("Number of received packets: {}\n".format(len(recPackets)))
            file.write("Number of collided packets: {}\n".format(len(collidedPackets)))
            file.write("Number of lost packets: {}\n".format(len(lostPackets)))
              
            file.write("Total payload size: {} bytes\n".format(self.TotalPacketSize))
            file.write("Received payload size: {} bytes\n".format(self.RecPacketSize))
            file.write("Network throughput: {:.3f} bps\n".format(self.throughput))
            file.write("Effective energy consumption per byte: {:.3e} Joule\n".format(self.EffectEnergyConsumPerByte))




    