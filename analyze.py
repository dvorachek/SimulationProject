import json
import os

import matplotlib.pyplot as plt
import math
import numpy as np
import scipy.stats as st


def confidence_interval(mean, n, std, confidence=.95, z=1.96):
    return (mean + (z * (std / math.sqrt(n))), mean - (z * (std / math.sqrt(n))))

def ci(data, confidence=.95, z=1.96):
    n = len(data)
    mean = float(sum(data)) / n
    sd = std(data, mean)
    return (mean + (z * (sd / math.sqrt(n))), mean - (z * (sd / math.sqrt(n))))

def std(data, mean):
    return math.sqrt(sum([(item - mean)**2 for item in data])/len(data))


if __name__=="__main__":
    os.chdir('data')
    data_files = os.listdir(os.getcwd())

    match_data = dict()

    green_diamond = dict(markerfacecolor='g', marker='D')
    red_square = dict(markerfacecolor='r', marker='s')

    for file in data_files:

        with open(file) as f:
            data = json.load(f)

        print '='*60
        print("file:{}".format(file))

        #print("header:{}".format(data[0]))
        #print data

        key = file[6:]
        index = int(file[5:6]) - 1
        print key
        print index

        if key not in match_data:
            match_data[key] = [0 for _ in range(2)]

        num_packet = [item[0] for item in data[1:]]
        packet_time = [item[1] for item in data[1:]]
        out_order = [item[2] for item in data[1:]]
        dropped = [item[3] for item in data[1:]]

        all_data = [num_packet, packet_time, out_order, dropped]
      
        match_data[key][index] = all_data #, means, stds, confidence_intervals]


    for k, v in match_data.iteritems():
        single_q = v[0]
        two_q = v[1]

        combined_packet_time = [single_q[1]] + [two_q[1]]
        print combined_packet_time

        fig1, ax1 = plt.subplots()
        ax1.set_title("comparing packet times {}".format(key))
        ax1.boxplot(combined_packet_time, conf_intervals=[ci(combined_packet_time[0]), ci(combined_packet_time[1])])
        plt.show()


        combined_out_order = [single_q[2]] + [two_q[2]]
        print combined_packet_time

        fig2, ax2 = plt.subplots()
        ax2.set_title("comparing out of order rates {}".format(key))
        ax2.boxplot(combined_out_order, conf_intervals=[ci(combined_out_order[0]), ci(combined_out_order[1])], flierprops=green_diamond)
        plt.show()


        combined_dropped = [single_q[3]] + [two_q[3]]
        print combined_dropped

        fig3, ax3 = plt.subplots()
        ax3.set_title("comparing packet drop rates {}".format(key))
        ax3.boxplot(combined_dropped, conf_intervals=[ci(combined_dropped[0]), ci(combined_dropped[1])], flierprops=red_square)
        plt.show()

        