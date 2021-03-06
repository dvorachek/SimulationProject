#!/usr/bin/env python
import os
import random
from queue import Queue
import itertools
import json

# pip install simpy
import simpy

# for single queue single server variant
SINGLE_QUEUE_VARIANT = False  # change to true to use a single queue
FIFO_QUEUE = Queue(10000)  # 10MB / 1000 Byte packets

# "Constants" although some are reset
SEEDS = [seed for seed in range(13, 18)]  # (multiple runs) - currently set for 5 runs
TRAFFIC_GENERATION_RATE = 750  # number of packets per second generated by source node
TRANSMITION_SPEED_SOURCE = 10  # in Mbps
TRANSMITION_SPEED_ROUTER = 15  # in Mbps
PACKET_DATA_LENGTH = 1000  # in Bytes (1 Byte = 8 bits)
ROUTER_DEST_DELAY = 50  # in ms
HIGH_PRIORITY_QUEUE = Queue(10000)  # 10 MB / 1000 Byte packets
LOW_PRIORITY_QUEUE = Queue(10000)  # 10 MB / 1000 Byte packets
SIM_DURATION = 100  # length of simulation in ticks

# for normal distribution (starting values)
X = 250  # init value
Y = 2  # init value

# const index for data collection
TOTAL_NUM_PACKETS = 0
TOTAL_PACKET_TIME = 1
TOTAL_OUT_ORDER_PACKETS = 2
TOTAL_PACKETS_DROPPED = 3

run_data = [0 for _ in range(4)]  # holds data for each run
total_data = []  # data summary


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
        self.router_has_value = simpy.Store(env)

    def router_send(self, packet):
        '''sorts the packets into high/low priority queues
        or single queue if that mode it toggled'''
        if SINGLE_QUEUE_VARIANT:
            if FIFO_QUEUE.full():
                run_data[TOTAL_PACKETS_DROPPED] += 1
            else:
                if packet.seq_num > self.current_seq:
                    self.current_seq = packet.seq_num
                FIFO_QUEUE.put(packet)
                self.router_put(1)

        else:
            if packet.seq_num < self.current_seq:
                if HIGH_PRIORITY_QUEUE.full():
                    run_data[TOTAL_PACKETS_DROPPED] += 1
                else:
                    HIGH_PRIORITY_QUEUE.put(packet)
                    self.router_put(1)

            else:
                if LOW_PRIORITY_QUEUE.full():
                    run_data[TOTAL_PACKETS_DROPPED] += 1
                else:
                    LOW_PRIORITY_QUEUE.put(packet)
                    self.current_seq = packet.seq_num
                    self.router_put(1)
                    

    def router_latency(self, p):
        '''simulates the random normal dist latency unique to each packet'''
        yield self.env.timeout((p.delay) / 1000.0)  # Normal distribution delay
        self.router_send(p)

    def put_router(self, p):
        '''called to send packets to router from source node'''
        self.env.process(self.router_latency(p))

    def fixed_latency(self, p):
        '''simulates the fixed latency from router to dest node'''
        yield self.env.timeout((ROUTER_DEST_DELAY / 1000.0))  # Fixed delay
        self.to_dest.put(p)

    def put_dest(self, p):
        '''called to send packets to dest node from router'''
        self.env.process(self.fixed_latency(p))

    def get(self):
        '''used by the destination node to receive packets'''
        return self.to_dest.get()

    def router_put(self, v):
        '''sends signal to router'''
        self.router_has_value.put(v)

    def router_trigger(self):
        '''dequeues item that work up router'''
        return self.router_has_value.get()


def source_node(env, pipe):
    '''generates packets'''
    for i in itertools.count():
        yield env.timeout(exponential() / 1000)  # poisson process
        p = Packet(env, i)
        yield env.timeout(1250**-1)  # transmission speed
        pipe.put_router(p)   

def router(env, pipe):
    '''checks both queues and sends packets from queues to dest node'''
    while True:
        yield pipe.router_trigger()

        if SINGLE_QUEUE_VARIANT:
            if not FIFO_QUEUE.empty():
                packet = FIFO_QUEUE.get()
                yield env.timeout(1250**-1)  # transmission speed
                pipe.put_dest(packet)

        else:
            if not HIGH_PRIORITY_QUEUE.empty():
                packet = HIGH_PRIORITY_QUEUE.get()
                yield env.timeout(1250**-1)  # transmission speed
                pipe.put_dest(packet)

            if HIGH_PRIORITY_QUEUE.empty() and not LOW_PRIORITY_QUEUE.empty():
                packet = LOW_PRIORITY_QUEUE.get()
                yield env.timeout(1250**-1)  # transmission speed
                pipe.put_dest(packet)

def destination_node(env, pipe):
    '''process that consumes values from router'''
    current_seq = -1
    while True:
        packet = yield pipe.get()
        
        run_data[TOTAL_NUM_PACKETS] += 1

        if packet.seq_num < current_seq:
            run_data[TOTAL_OUT_ORDER_PACKETS] += 1
        else:
            current_seq = packet.seq_num
        
        run_data[TOTAL_PACKET_TIME] += (env.now - packet.start_time)

def exponential():
    delay = -1
    while delay < 0:
        delay = random.expovariate(TRAFFIC_GENERATION_RATE)
    return delay

def normal():
    '''generates normal in ms'''
    delay = -1
    while delay < 0:
        delay = random.normalvariate(X, Y)
    return delay


if __name__=="__main__":
    os.chdir('data')

    for i in range(12):
        SINGLE_QUEUE_VARIANT = (i % 2 == 0)

        # Kinda sloppy, but it works
        if i > 1:
            TRAFFIC_GENERATION_RATE = 1125
        if i > 3:
            TRAFFIC_GENERATION_RATE = 750
            X = 50
            Y = 45
        if i > 5:
            TRAFFIC_GENERATION_RATE = 1125
        if i > 7:
            TRAFFIC_GENERATION_RATE = 750
            X = 50
            Y = 1
        if i > 9:
            TRAFFIC_GENERATION_RATE = 1125

        file_name = "Queue{}_{}_mean{}_var{}.json".format(i%2+1, TRAFFIC_GENERATION_RATE, X, Y)
        print(file_name)
        print('avg_num_packets, avg_packet_time, avg_out_order, avg_dropped')

        # Header for dataset
        param = "file_name={}, Seeds={}, TRAFFIC_GENERATION_RATE={}, SINGLE_QUEUE_VARIANT={}, X={}, Y={}".format(
            file_name, SEEDS, TRAFFIC_GENERATION_RATE, SINGLE_QUEUE_VARIANT, X, Y)
        total_data.append(param)

        for s in SEEDS:
            random.seed(s)

            #print 'creating env and pipes'
            env = simpy.Environment()
            pipe = Pipes(env)

            #print 'init source node process'
            env.process(source_node(env, pipe))

            #print 'init router process'
            env.process(router(env, pipe))

            #print 'init dest node process'
            env.process(destination_node(env, pipe))

            #print 'start simulation'
            env.run(until=SIM_DURATION)

            # get means
            run_data[TOTAL_PACKET_TIME] = float(run_data[TOTAL_PACKET_TIME]) / run_data[TOTAL_NUM_PACKETS]
            run_data[TOTAL_OUT_ORDER_PACKETS] = float(run_data[TOTAL_OUT_ORDER_PACKETS]) / run_data[TOTAL_NUM_PACKETS]
            run_data[TOTAL_PACKETS_DROPPED] = float(run_data[TOTAL_PACKETS_DROPPED]) / run_data[TOTAL_NUM_PACKETS]

            print(run_data)
            total_data.append(run_data)

            # reset run_data for next seed
            run_data = [0 for _ in range(4)]
            HIGH_PRIORITY_QUEUE = Queue(10000)  # 10 MB / 1000 Byte packets
            LOW_PRIORITY_QUEUE = Queue(10000)  # 10 MB / 1000 Byte packets
            FIFO_QUEUE = Queue(10000)  # 10MB / 1000 Byte packets

        avg_num_packets = float(sum([num_packets[0] for num_packets in total_data[1:]])) / len(total_data[1:])
        avg_packet_time = float(sum([num_packets[1] for num_packets in total_data[1:]])) / len(total_data[1:])
        avg_out_order = float(sum([num_packets[2] for num_packets in total_data[1:]])) / len(total_data[1:])
        avg_dropped = float(sum([num_packets[3] for num_packets in total_data[1:]])) / len(total_data[1:])

        avgs = [avg_num_packets, avg_packet_time, avg_out_order, avg_dropped]

        print(avgs)
        print('\n')

        with open(file_name, 'w') as outfile:
            json.dump(total_data, outfile)

        total_data = []

