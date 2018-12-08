import json
import os

#import matplotlib.pyplot as plt
import math
import numpy as np
import scipy.stats as st


def confidence_interval(mean, n, std, confidence=.95, z=1.96):
    return (mean + (z * (std / math.sqrt(n))), mean - (z * (std / math.sqrt(n))))

def std(data, mean):
    return math.sqrt(sum([(item - mean)**2 for item in data])/len(data))


if __name__=="__main__":
    os.chdir('data')
    data_files = os.listdir(os.getcwd())

    for file in data_files:

        with open(file) as f:
            data = json.load(f)

        print '='*60
        print("file:{}".format(file))
        #print("header:{}".format(data[0]))

        num_packet = [item[0] for item in data[1:]]
        packet_time = [item[1] for item in data[1:]]
        out_order = [item[2] for item in data[1:]]
        dropped = [item[2] for item in data[1:]]
        
        mean_num_packets = float(sum(num_packet)) / len(data[1:])
        mean_packet_time = float(sum(packet_time)) / len(data[1:])
        mean_out_order = float(sum(out_order)) / len(data[1:])
        mean_dropped = float(sum(dropped)) / len(data[1:])

        std_num_packets = std(num_packet, mean_num_packets)
        std_packet_time = std(packet_time, mean_packet_time)
        std_out_order = std(out_order, mean_out_order)
        std_dropped = std(dropped, mean_dropped)

        ci_num_packets = confidence_interval(mean_num_packets, len(data[1:]), std_num_packets)
        ci_packet_time = confidence_interval(mean_packet_time, len(data[1:]), std_packet_time)
        ci_out_order = confidence_interval(mean_out_order, len(data[1:]), std_out_order)
        ci_dropped = confidence_interval(mean_dropped, len(data[1:]), std_dropped)
        
        print("mean_num_packets={}, std_num_packets={}, ci_num_packets={}".format(mean_num_packets, std_num_packets, ci_num_packets))
        print("mean_packet_time={}, std_packet_time={}, ci_packet_time={}".format(mean_packet_time, std_packet_time, ci_packet_time))
        print("mean_out_order={}, std_out_order={}, ci_out_order={}".format(mean_out_order, std_out_order, ci_out_order))
        print("mean_dropped={}, std_dropped={}, ci_dropped={}".format(mean_dropped, std_dropped, ci_dropped))

