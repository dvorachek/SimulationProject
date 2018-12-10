#!/usr/bin/env python
import json
import os
import matplotlib.pyplot as plt
import math
from scipy import stats


def ci(data, confidence=.95, z=1.96):
    n = len(data)
    mean = float(sum(data)) / n
    sd = std(data, mean)
    return (mean + (z * (sd / math.sqrt(n))), mean - (z * (sd / math.sqrt(n))))

def std(data, mean):
    return math.sqrt(sum([(item - mean)**2 for item in data])/len(data))


if __name__=="__main__":
    match_data = dict()
    green_diamond = dict(markerfacecolor='g', marker='D')
    red_square = dict(markerfacecolor='r', marker='s')

    os.chdir('data')

    for file in os.listdir(os.getcwd()):
        with open(file) as f:
            data = json.load(f)

        print("reading file: {}".format(file))

        key = file[6:]
        index = int(file[5:6]) - 1

        if key not in match_data:
            match_data[key] = [0 for _ in range(2)]

        num_packet = [item[0] for item in data[1:]]
        packet_time = [item[1] for item in data[1:]]
        out_order = [item[2] for item in data[1:]]
        dropped = [item[3] for item in data[1:]]

        all_data = [num_packet, packet_time, out_order, dropped]
        match_data[key][index] = all_data

    for k, v in match_data.iteritems():
        single_q = v[0]
        two_q = v[1]

        combined_packet_time = [single_q[1]] + [two_q[1]]
        combined_out_order = [single_q[2]] + [two_q[2]]
        combined_dropped = [single_q[3]] + [two_q[3]]

        combined = [combined_packet_time, combined_out_order, combined_dropped]
        header = ['Packet Time in System', 'Out-of-order Rate', 'Rate of Packets Dropped']

        rate, mean, var = k.split('_')[1:]
        mean = mean[4:]
        var = var[3:].split('.')[0]
        
        for i in range(3):

            # print raw data
            title =("\n{}: Generation Rate = {} Mean = {} Var = {}".format(header[i], rate, mean, var))
            print(title)
            d = combined[i][0]
            print('\nSingle Queue System Stats')
            #print("5 run data: {}".format(d))
            print("mean: {}".format(float(sum(d))/len(d)))
            print("CI: {}".format(ci(d)))

            d = combined[i][1]
            print('\nPriority Queueing System Stats')
            #print("5 run data: {}".format(d))
            print("mean: {}".format(float(sum(d))/len(d)))
            print("CI: {}".format(ci(d)))

            # save plot
            fig, ax = plt.subplots()
            ax.set_title("{}\nGeneration Rate = {} Mean = {} Var = {}".format(header[i], rate, mean, var))
            ax.boxplot(combined[i],
                       conf_intervals=[ci(combined[i][0]),
                       ci(combined[i][1])],
                       flierprops=green_diamond)
            plt.xticks([1, 2], ['Single Queue', 'Two Priority Queues'])
            fig.savefig('../graphs/{}_generationRate{}.png'.format(header[i].replace(' ', '_'), k[1:]))

