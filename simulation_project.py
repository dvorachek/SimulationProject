#!/usr/bin/python
import random
from Queue import Queue
import itertools

import simpy

# for single queue single server variant
SINGLE_QUEUE_VARIANT = False  # change to true to use a single queue
FIFO_QUEUE = Queue(10000)  # 10MB / 1000 Byte packets

# values may need to change for unit conversions
SEEDS = [seed for seed in range(13, 14)]  # change as desired (multiple runs)
TRAFFIC_GENERATION_RATE = 20  # number of packets per second from source node
TRANSMITION_SPEED_SOURCE = 10  # in Mbps
TRANSMITION_SPEED_ROUTER = 15  # in Mbps
PACKET_DATA_LENGTH = 1000  # in Bytes (1 Byte = 8 bits)
ROUTER_DEST_DELAY = 50  # in ms
HIGH_PRIORITY_QUEUE = Queue(10000)  # 10 MB / 1000 Byte packets
LOW_PRIORITY_QUEUE = Queue(10000)  # 10 MB / 1000 Byte packets
SIM_DURATION = 100  # length of simulation in ticks

# for normal distribution
X = 1  # change as needed
Y = 1  # change as needed

# data struct for stats collection
total_num_packets = 0
total_packet_time = 0
total_out_of_order_packets = 0
total_packets_dropped = 0
# will need to reset for each run
# these results will need to be summed in anot



class Packet(object):
    """class for containing event information"""
    def __init__(self, env, seq_num):
        self.start_time = env.now
        self.seq_num = seq_num
        self.delay = normal()  # we assume the delay is in seconds


class Pipes(object):
    '''This class sends packets between source node, router and dest node'''
    def __init__(self, env):
        self.env = env
        self.to_dest = simpy.Store(env)
        self.current_seq = -1

    def router_send(self, packet):
        '''sorts the packets into high/low priority queues
        or single queue if that mode it toggled'''
        if SINGLE_QUEUE_VARIANT:
            FIFO_QUEUE.put(packet)

        else:
            if packet.seq_num < self.current_seq:
                HIGH_PRIORITY_QUEUE.put(packet)
            else:
                LOW_PRIORITY_QUEUE.put(packet)
                self.current_seq = packet.seq_num

    def router_latency(self, p):
        '''simulates the random normal dist latency unique to each packet'''
        yield self.env.timeout(p.delay + (1250**-1))
        self.router_send(p)

    def put_router(self, p):
        '''called to send packets to router from source node'''
        self.env.process(self.router_latency(p))

    def fixed_latency(self, p):
        '''simulates the fixed latency from router to dest node'''
        yield self.env.timeout((ROUTER_DEST_DELAY / 1000.0) + (1875**-1))
        self.to_dest.put(p)

    def put_dest(self, p):
        '''called to send packets to dest node from router'''
        self.env.process(self.fixed_latency(p))

    def get(self):
        '''used by the destination node to receive packets'''
        return self.to_dest.get()


def source_node(env, pipe):
    '''generates packets

    need to add poisson rate of arrival'''
    for i in itertools.count():
        yield env.timeout(1.0 / TRAFFIC_GENERATION_RATE)  # poisson process
        p = Packet(env, i)

        pipe.put_router(p)

def router(env, pipe):
    '''checks both queues and sends packets from queues to dest node
    
    print statements are for testing'''

    while True:
        if SINGLE_QUEUE_VARIANT:
            if not FIFO_QUEUE.empty():
                packet = FIFO_QUEUE.get()
                pipe.put_dest(packet)

        else:
            if not HIGH_PRIORITY_QUEUE.empty():
                packet = HIGH_PRIORITY_QUEUE.get()
                '''print 'high priority'
                print "do something with {}".format(packet.seq_num)'''
                pipe.put_dest(packet)
            if HIGH_PRIORITY_QUEUE.empty() and not LOW_PRIORITY_QUEUE.empty():
                packet = LOW_PRIORITY_QUEUE.get()
                '''print 'low priority'
                print "do something with {}".format(packet.seq_num)
                print "{0:.3f}".format(env.now)'''
                pipe.put_dest(packet)
        yield env.timeout(0.0001)

def destination_node(env, pipe):
    '''process that consumes values from router'''
    while True:
        packet = yield pipe.get()
        
        print "packet {} arrived at dest".format(packet.seq_num)

def normal():
    delay = -1
    while delay < 0:
        delay = random.normalvariate(X, Y)
    return delay


if __name__=="__main__":

    for s in SEEDS:

        random.seed(s)

        print 'creating env and pipes'
        env = simpy.Environment()
        pipe = Pipes(env)

        print 'init source node process'
        env.process(source_node(env, pipe))

        print 'init router process'
        env.process(router(env, pipe))

        print 'init dest node process'
        env.process(destination_node(env, pipe))

        print 'start simulation'
        env.run(until=SIM_DURATION)

