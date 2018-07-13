import sys
import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib.pyplot as plt  # MATLAB-like plotting
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import re


border = 0.08

def translate_date_to_sec(ymdhms):
    """
    :param ymdhms: the year-month-day-hour-minute-second data (datetime.datetime) to be translated into unix-seconds.
    :return: the amount of seconds passed since the first of january 1970 00:00 UTC, if invalid: "-1".
    """
    x_ = str(ymdhms, 'utf-8')
    if x_ == 'Unknown':
        return -1
    else:
        temp_time = datetime.datetime.strptime(str(ymdhms, 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # convert into datetime
        return temp_time.timestamp()  # then convert into unix-seconds (timestamp)


def translate_time_to_sec(time):
    seconds = 0
    flagdays = False
    if '-' in time:
        flagdays = True
    time = time.split('.')[0]
    if len(time) < 2:
        return 0
    subsplits = time.split('-')
    seconds = 0
    if flagdays:
        seconds += 24 * 3600 * int(''.join(c for c in subsplits[0] if c.isdigit()))
    timesplitseconds = subsplits[-1].split(':')
    for i in range(len(timesplitseconds)):
        seconds += int(''.join(c for c in (timesplitseconds[-(i + 1)]) if c.isdigit())) * int(math.pow(60, int(i)))
    return seconds


parser = argparse.ArgumentParser()
parser.add_argument('original')
parameter = parser.parse_args()
#print("Parameter:",parameter)
#print("Original:",parameter.original)
original = parameter.original
data_type = np.dtype(
    [('JobID', '|S256'), ('ReqCPUS', 'i4'), ('ReqMem', '|S256'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
     ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
     ('End', '|S256'),('TotalCPU', '|S256'),('UserCPU', '|S256'),('SystemCPU', '|S256')])
Data = np.loadtxt(original, dtype=data_type, delimiter='|', skiprows=0, usecols=(0, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27,15,17,16))


joblist = []

for row in Data:
    if translate_date_to_sec(row['End']) > 0:
        start_t = datetime.datetime.strptime(str(row['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        end_t = datetime.datetime.strptime(str(row['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        if (end_t-start_t).seconds < 1:
            continue
        formated = row['TotalCPU']
        #print("totalCPU:",formated)
        formated = str(formated)[2:]
        #print("seconds:",translate_time_to_sec(formated))
        efficiency = translate_time_to_sec(formated) / (row['AllocCPUS']*(end_t-start_t).seconds)
        if efficiency <= border:
            id = str(row['JobID'])
            id = id[2::]
            joblist.append(id)
            #print("efficiency",efficiency)

print(joblist)

