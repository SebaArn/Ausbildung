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



ap.add_argument('Source', type=str, nargs=1)
ap.add_argument('-s', dest='StartPoint', default="None", type=str, nargs='?')
ap.add_argument('--start', dest='StartPoint', default="None", type=str, nargs='?')
ap.add_argument('-p', dest='ProjectName', default="", type=str, nargs='?')
ap.add_argument('--project', dest='ProjectName', default="", type=str, nargs='?')
ap.add_argument('--min', dest='Minimum', default="", type=float, nargs='?')
ap.add_argument('Minimum', dest='Minimum', default="", type=float, nargs='?')
ap.add_argument('--max', dest='Maximum', default="", type=float, nargs='?')
ap.add_argument('Maximum', dest='Maximum', default="", type=float, nargs='?')


parameter = parser.parse_args()
min = parser.Minimum
max = parser.Maximum
projectname = parser.ProjectName
startpoint = parameter.StartPoint
#print("Parameter:",parameter)
#print("Original:",parameter.original)
original = parameter.Source
data_type = np.dtype(
    [('JobID', '|S256'), ('Account', '|S256'),('ReqCPUS', 'i4'), ('ReqMem', '|S256'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
     ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
     ('End', '|S256'),('TotalCPU', '|S256'),('UserCPU', '|S256'),('SystemCPU', '|S256')])
Data = np.loadtxt(original, dtype=data_type, delimiter='|', skiprows=0, usecols=(0, 1, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27,15,17,16))
Data = Data[(Data[::]['End']).argsort()]
sp = 0
for i in range(len(Data)):
    if datetime.datetime.strptime(Data[i]["End"], "%Y-%m-%d-%H-%M-%S").timestamp() >= startpoint.timestamp():
        sp = i
        continue


joblist = []

for i in range(len(Data)):
    if translate_date_to_sec(Data[i]['End']) > 0 and projectname in Data[i]['Account']:
        start_t = datetime.datetime.strptime(str(Data[i]['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        end_t = datetime.datetime.strptime(str(Data[i]['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        if (end_t-start_t).seconds < 1:
            continue
        formated = Data[i]['TotalCPU']
        #print("totalCPU:",formated)
        formated = str(formated)[2:]
        #print("seconds:",translate_time_to_sec(formated))
        efficiency = translate_time_to_sec(formated) / (Data[i]['AllocCPUS']*(end_t-start_t).seconds)
        if efficiency <= max and efficiency >= min:
            id = str(Data[i]['JobID'])
            id = id[2::]
            joblist.append(id)
            #print("efficiency",efficiency)

print(joblist)

