import random
from Queue import Queue
import itertools

import simpy


# values may need to change for unit conversions (converting to ms might be best)
SEEDS = [seed for seed in range(13, 43)]  # change as desired (multiple runs)
TRAFFIC_GENERATION_RATE = 20  # number of packets per second from source node
TRANSMITION_SPEED_SOURCE = 10  # in Mbps
PACKET_DATA_LENGTH = 1000  # in Bytes (1 Byte = 8 bits)
ROUTER_DEST_DELAY = 50  # in ms
HIGH_PRIORITY_QUEUE = Queue()  # need to set size
LOW_PRIORITY_QUEUE = Queue()  # need to set size
SIM_DURATION = 100  # for testing
X = 1  # change as needed
Y = 1  # change as needed


class Packet(object):
    """class for containing event information
    """
    def __init__(self, env, seq_num):
        self.start_time = env.now
        self.seq_num = seq_num
        self.delay = 0  # need to change to normal dist random delay


class Pipes(object):  # maybe replace by simpy.Store(env)
    def __init__(self, env):
        self.env = env
        self.to_router = []
        self.from_router = []
        self.current_seq = -1

    def router_send(self, packet):
        if packet.seq_num < self.current_seq:
            HIGH_PRIORITY_QUEUE.put(packet)
        else:
            LOW_PRIORITY_QUEUE.put(packet)
            self.current_seq = packet.seq_num


def router(env, in_pipe):
    while True:
        if not HIGH_PRIORITY_QUEUE.empty():
            print 'high priority'
            packet = HIGH_PRIORITY_QUEUE.get()
            print "do something with {}".format(packet)
        if HIGH_PRIORITY_QUEUE.empty() and not LOW_PRIORITY_QUEUE.empty():
            print 'low priority'
            packet = LOW_PRIORITY_QUEUE.get()
            print "do something with {}".format(packet)

def source_node(env, pipe):
    for i in itertools.count():
        yield env.timeout(1.0 / TRAFFIC_GENERATION_RATE)  # poisson
        packet = Packet(env, i)
        pipe.router_send(packet)


def destination_node(env):
    print 'TODO'

if __name__=="__main__":
    random.seed(SEEDS[0])  # just take the first until we need multiple runs
    
    env = simpy.Environment()
    router_pipe = Pipes(env)



    env.run(until=SIM_DURATION)

