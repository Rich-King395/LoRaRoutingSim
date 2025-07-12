#
# this function creates a BS, base station
#
import matplotlib.pyplot as plt
from ParameterConfig import *
from BroadcastingPacket import BroadcastingPacket

class myBS:
    def __init__(self, id):
        self.ID = id
        # two-dimensional location 
        self.x = 0
        self.y = 0
        self.HopCount = 0
        
        
        self.cf = 868000000
        self.sf = 7
        self.bw = 500
        self.tp = 14
        
        self.ChildSet = []  # list of child nodes
           
        global graphics
        if (graphics):
            global ax
            # XXX should be base station position
            # deaw different BSs according to their ids
            if (self.id == 0):
                ax.add_artist(plt.Circle((self.x, self.y), 10, fill=True, color='red'))
                # ax.add_artist(plt.Circle((self.x, self.y), maxDist, fill=False, color='blue'))

    def Generate_AskJoin(self):
        PacketPara = LoRaParameters()
        PacketPara.cf = self.cf
        PacketPara.sf = self.sf
        PacketPara.bw = self.bw
        PacketPara.tp = self.tp
        BroadcastingPacket(self.id, PacketPara)
        
