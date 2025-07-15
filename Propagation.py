# check for collisions at base station
# Note: called before a packet (or rather node) is inserted into the list
import math
from ParameterConfig import *
import ParameterConfig

# check for collisions at base station
# Note: called before a packet (or rather node) is inserted into the list
def checkcollision(packet):
    col = 0 # flag needed since there might be several collisions for packet
    # lost packets don't collide
    if packet.lost: 
       return 0
    if NodeInTransmission:
        for other in NodeInTransmission:
            if other.ID != packet.SourceID: # nodes that donnot send this packet
               if frequencyCollision(packet, other.packet) \
                   and sfCollision(packet, other.packet):
                   if full_collision:
                       if timingCollision(packet, other.packet):
                           # check who collides in the power domain
                           c = powerCollision(packet, other.packet)
                           # mark all the collided packets
                           # either this one, the other one, or both
                           for p in c:
                               p.collided = 1
                               if p == packet:
                                   col = 1
                       else:
                           # no timing collision, all fine
                           pass
                   else:
                       packet.collided = 1
                       other.packet.collided = 1  # other also got lost, if it wasn't lost already
                       col = 1
        return col
    return 0


def multihop_checkcollision(packet):
    col = 0 # flag needed since there might be several collisions for packet
    # lost packets don't collide
    if packet.lost: 
       return 0
    if ParameterConfig.NodeInTransmissionToNode[packet.TargetID]:
        for OtherSourceID in ParameterConfig.NodeInTransmissionToNode[packet.TargetID]:
            if OtherSourceID != packet.SourceID: # nodes that donnot send this packet
               if frequencyCollision(packet, Devices[OtherSourceID].packet) \
                   and sfCollision(packet, Devices[OtherSourceID].packet):
                   if full_collision:
                       if timingCollision(packet, Devices[OtherSourceID].packet):
                           # check who collides in the power domain
                           c = powerCollision(packet, Devices[OtherSourceID].packet)
                           # mark all the collided packets
                           # either this one, the other one, or both
                           for p in c:
                               p.collided = 1
                               if p == packet:
                                   col = 1
                       else:
                           # no timing collision, all fine
                           pass
                   else:
                       packet.collided = 1
                       Devices[OtherSourceID].packet.collided = 1  # other also got lost, if it wasn't lost already
                       col = 1
        return col
    return 0


# 
# frequencyCollision, conditions
# 120kHz,60kHz,30kHz are the minimum tlerable frequency offsets
#        |f1-f2| <= 120 kHz if f1 or f2 has bw 500 
#        |f1-f2| <= 60 kHz if f1 or f2 has bw 250 
#        |f1-f2| <= 30 kHz if f1 or f2 has bw 125 
def frequencyCollision(p1,p2):
    if (abs(p1.cf-p2.cf)<=120 and (p1.bw==500 or p2.cf==500)):#Bandwodth=500kHz
        return True
    elif (abs(p1.cf-p2.cf)<=60 and (p1.bw==250 or p2.cf==250)):#Bandwidth=200kHz
        return True
    else:
        if (abs(p1.cf-p2.cf)<=30):
            return True
    return False

# SF Collision
def sfCollision(p1, p2):
    if p1.sf == p2.sf:
        # p2 may have been lost too, will be marked by other checks
        return True
    return False

# Capture Effect
def powerCollision(p1, p2):
    powerThreshold = 6 # dB
    if abs(p1.RSSI - p2.RSSI) < powerThreshold:
        # packets are too close to each other, both collide
        # return both packets as casualties 
        return (p1, p2)
    elif p2.RSSI - p1.RSSI > powerThreshold:
        # p2 overpowered p1, return p1 as casualty
        return (p1,)
    # p2 was the weaker packet, return it as a casualty  
    return (p2,)

def timingCollision(p1, p2):
    # assuming p1 is the freshly arrived packet and this is the last check
    # we've already determined that p1 is a weak packet, so the only
    # way we can win is by being late enough (only the first n - 5 preamble symbols overlap)
    # at least 5 symbols are left intact in the preamble, otherwise the packet would be damaged
    # assuming 8 preamble symbols
    Npream = 8
    
    # we can lose at most (Npream - 5) * Tsym of our preamble
    Tpreamb = 2**p1.sf/(1.0*p1.bw) * (Npream - 5) # 2^SF/BW = Ts  
    
    # check whether p2 ends in p1's critical section
    p2_end = p2.addTime + p2.rectime
    p1_cs = env.now + Tpreamb
    if p1_cs < p2_end:
        # p1 collided with p2 and lost
        return True
    return False

def rssi(packet,distance):
    if ParameterConfig.Routing_Flag == 0:
        Lpl = Lpld0+10*gamma*math.log10(distance/d0)
    else:
        Lpl = Lpld0+10*gamma*math.log10(distance/d0) + np.random.normal(0,std)

    Prx = packet.tp + GL - Lpl
    return Prx

def snr(rss):
    # TODO make a better noise assumption
    noise_floor = -174 + 10 * np.log10(125e3)
    return rss - noise_floor

def get_distance(x,y,Target):
     dist = np.sqrt((x-Target.x)*(x-Target.x)+(y-Target.y)*(y-Target.y)) # distance between node and gateway
     return dist
