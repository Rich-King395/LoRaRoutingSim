#
# this function creates a BS, base station
#
import matplotlib.pyplot as plt
from ParameterConfig import *
from BroadcastingPacket import BroadcastingPacket

class myBS:
    def __init__(self, id):
        self.id = id
        # two-dimensional location 
        self.x = 0
        self.y = 0
        
        self.cf = 868000000
        self.sf = 7
        self.bw = 500
        self.tp = 14

        # create gateways and initialize their positions
        if nrBS == 1 and self.id == 0:
            self.x = 0
            self.y = 0
        elif nrBS == 2:
            a = radius/2.0 # radius/2
            if self.id == 0:
                self.x = a
                self.y = 0
            elif self.id == 1:
                self.x = -a
                self.y = 0
        elif nrBS == 3:
            a = radius/(2.0 + math.sqrt(3)) # radius/11
            b = math.sqrt(3) * a # (9*radius)/11
            c = 2 * a # (2*radius)/11
            if self.id == 0:
                self.x = -b
                self.y = -a
            if self.id == 1:
                self.x = b
                self.y = -a
            if self.id == 2:
                self.x = 0
                self.y = c
        elif nrBS == 4:
            a = radius/(1.0 + math.sqrt(2)) # radius/5
            if self.id == 0:
                self.x = a
                self.y = a
            if self.id == 1:
                self.x = a
                self.y = -a
            if self.id == 2:
                self.x = -a
                self.y = a
            if self.id == 3:
                self.x = -a
                self.y = -a
                
        global graphics
        if (graphics):
            global ax
            # XXX should be base station position
            # deaw different BSs according to their ids
            if (self.id == 0):
                ax.add_artist(plt.Circle((self.x, self.y), 10, fill=True, color='red'))
                # ax.add_artist(plt.Circle((self.x, self.y), maxDist, fill=False, color='blue'))
            if (self.id == 1):
                ax.add_artist(plt.Circle((self.x, self.y), 10, fill=True, color='red'))
                # ax.add_artist(plt.Circle((self.x, self.y), maxDist, fill=False, color='red'))
            if (self.id == 2):
                ax.add_artist(plt.Circle((self.x, self.y), 10, fill=True, color='green'))
                # ax.add_artist(plt.Circle((self.x, self.y), maxDist, fill=False, color='green'))
            if (self.id == 3):
                ax.add_artist(plt.Circle((self.x, self.y), 10, fill=True, color='brown'))
                # ax.add_artist(plt.Circle((self.x, self.y), maxDist, fill=False, color='brown'))
    
    def Generate_AskJoin(self):
        PacketPara = LoRaParameters()
        PacketPara.cf = self.cf
        PacketPara.sf = self.sf
        PacketPara.bw = self.bw
        PacketPara.tp = self.tp
        BroadcastingPacket(self.id, PacketPara)
        
