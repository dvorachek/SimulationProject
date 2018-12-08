import json
import os

'''import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, m-h, m+h
'''


if __name__=="__main__":
    os.chdir('data')
    data_files = os.listdir(os.getcwd())

    for file in data_files:


        with open(file) as f:
            data = json.load(f)

        print '='*60
        print("file:{}".format(file))
        print("header:{}".format(data[0]))
        
        avg_num_packets = float(sum([num_packets[0] for num_packets in data[1:]])) / len(data)
        sum_packet_time = float(sum([num_packets[1] for num_packets in data[1:]])) / len(data)
        sum_out_order = float(sum([num_packets[2] for num_packets in data[1:]])) / len(data)
        sum_dropped = float(sum([num_packets[3] for num_packets in data[1:]])) / len(data)

        
        print avg_num_packets
        print sum_packet_time
        print sum_out_order
        print sum_dropped
        #for item in data[1:]:
            #print item[0]
            #avg_num_packets = sum([num_packets[0] for num_packets in item[0]) / len(data)
            
            #print avg_num_packets
            #avg_num_packets += item[0]
            #sum_packet_time += item[1]
            #sum_out_order += item[2]
            #sum_dropped += item[3]
        
        




        
    