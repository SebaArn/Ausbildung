import numpy as np
import datetime
import matplotlib as mpl  # general matplotlib import
import matplotlib.pyplot as plt  # MATLAB-like plotting
import datetime, time
import struct
import csv
import sys
import string
import pandas
import argparse
import os.path


# %matplotlib inline


ap = argparse.ArgumentParser()
ap.add_argument('Source', type=str, nargs=1)
ap.add_argument('Output', type=str, nargs=1)
ap.add_argument('Quota', type=int, nargs='?')
parameter = ap.parse_args()
plt.rcParams['figure.figsize'] = [6, 4]  # set global parameters
# print ("please enter the name of a data to read or press enter for the default value")
# text = input("Dateiname:\n")
Thresholds = [(0.7, "#ADD8E6"), (1.1,), (1.5, '#FFFF00'), (100, '#FF0000')]
# Temporary
print(parameter.Source[0])
zieldatei = ap.parse_args()
Quote = ap.parse_args()

dtype1 = np.dtype(
    [('JobID', '|S256'), ('ReqCPUS', 'i4'), ('ReqMem', '|S256'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
     ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
     ('End', '|S256')])
job_record = np.dtype([('ReqCPUS', 'i4'), ('ReqMem', 'i4')])

original = parameter.Source[0]

mypath = os.path.abspath(".")
copy = mypath + "\copy.log-example"

test = mypath + '\Testinput.log-example'

# np.loadtxt(original, dtype={'names': ('ReqCPUS','ReqMem','ReqNodes','AllocNodes','AllocCPUS','NNodes','NCPUS','CPUTimeRAW','ElapsedRaw','Start','End'),
#                            'formats': ('i64',  'i64',    'i64',    'i64',       'i64',       'i64'   , 'i64'  'i64'     ,'i64'       ,'S256' ,'S256')}, delimiter = '|',
#           usecols = (                    3,    4,         5,         6,           7,          8,        9,      12,          13,        26,    27))

Data = np.loadtxt(original, dtype=dtype1, delimiter='|', skiprows=0, usecols=(1, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27))
CopyData = np.loadtxt(copy, dtype=dtype1, delimiter='|', skiprows=1, usecols=(1, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27))
fin_dtype = np.dtype(
    [('Corehours', 'uint64'), ('Endtime', 'S256')]
)


def translateDateToSec(YMDHMS):
    x_ = str(YMDHMS, 'utf-8')
    if x_ == 'Unknown':
        return -1
    else:
        temptime = datetime.datetime.strptime(str(YMDHMS, 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        return temptime.timestamp()
        # Year, Month, Day, Hour, Minute, Second = x.split("-")
        # print(int(float(Second))+ int(float(Minute))*60 +int(float(Hour))*3600 + (int(float(Day))-1)*3600*24 +(int(float(Month))-1)*3600*24*DaysByTheFirstOfMonth(Month) + (int(float(Year))-1)*3600*24*30*364)
        # return (int(float(Second)) + int(float(Minute)) * 60 + int(float(Hour)) * 3600 + (
        #            int(float(Day)) - 1) * 3600 * 24 + 3600 * 24 * DaysByTheFirstOfMonth(Month, Year) + (
        #                    int(float(Year)) - 1) * 3600 * 24 * 365) - temp


def Schaltjahr(Jahreszahl):
    x = (int(float(Jahreszahl)))
    if ((((x % 400) == 0) or ((x % 100) > 0)) and ((x % 4) == 0)):
        return 1
    else:
        return 0


# TODO adapt then 364 above to consider every 4th year, every 100 years, every 400 years, these are only aprox
def DaysByTheFirstOfMonth(month, year):
    my_dictionary = {
        '01': 0,
        '02': 31,
        '03': 59 + Schaltjahr(year),
        '04': 90 + Schaltjahr(year),
        '05': 120 + Schaltjahr(year),
        '06': 151 + Schaltjahr(year),
        '07': 181 + Schaltjahr(year),
        '08': 212 + Schaltjahr(year),
        '09': 243 + Schaltjahr(year),
        '10': 273 + Schaltjahr(year),
        '11': 304 + Schaltjahr(year),
        '12': 334 + Schaltjahr(year),
    }

    return my_dictionary[month]


#
# TODO fix DaysByTheFirstofMonth and the line that calls it (a set term for each of the 12 months?)
#

PlotArray = (np.zeros((Data.size, 3)))
x = 0
time_accumulator = 0
# Set a start date way in the future
x_start = datetime.datetime.strptime("3000-01-01-01-01-01", "%Y-%m-%d-%H-%M-%S")
x_end = datetime.datetime.strptime("2000-01-01-01-01-01", "%Y-%m-%d-%H-%M-%S")
# Set y max to the estmated total amount of core-hours in a year for the Lichtenberg (for max,min computation)
y_start1 = 1000000000000000000000000000000000
y_end1 = 0
for row in Data:
    # PlotArray[x][0] = (column[8] * column[5])
    if translateDateToSec(row[11]) > 0:
        end_t = datetime.datetime.strptime(str(row['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        start_t = datetime.datetime.strptime(str(row['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        x_start = min(end_t, x_start)
        x_end = max(end_t, x_end)
        # if row['AllocCPUS'] == 0:
        # print ('Element',row,' has Zero CPUs')
        if (end_t - start_t).seconds < 1:
            # print ('Element', row, ' has zero Runtime')
            continue
        y_start1 = min(y_start1, (row['AllocCPUS'] * (end_t - start_t).seconds))
        y_end1 = max(y_end1, (row['AllocCPUS'] * (end_t - start_t).seconds) / 3600)
        PlotArray[x, 0] = end_t.timestamp()
        PlotArray[x, 1] = (row['AllocCPUS'] * (end_t - start_t).seconds / 3600)
        #       PlotArray[x]=[x,x*x]
        x = x + 1

# min(PlotArray, key=lambda i: i[1] if isinstance(i[1],datetime) else datetime.max)
# print ('Array shape is ',PlotArray.shape)
# print ('x is ',x)
PlotArray = PlotArray[0:x][:]
# print ('Array shape is ',PlotArray.shape)
PlotArray = np.sort(PlotArray, axis=0)
# print ('Array shape is ',PlotArray.shape)
PlotArray[0, 2] = PlotArray[0][1]
# print ('Array shape is ',PlotArray.shape)
y_start2 = 0
y_end2 = 0
for x in range(1, PlotArray.shape[0]):
    #    PlotArray[x,0]=2
    PlotArray[x, 2] = PlotArray[x, 1] + PlotArray[x - 1, 2]  # /=3600+10#PlotArray[x-1,1]
    y_end2 = max(y_end2, PlotArray[x, 2])

SecondData = np.loadtxt(test, dtype='S256', delimiter='|', skiprows=0, usecols=(1, 14, 26, 27))
# print(SecondData)
# print(datetime.datetime.strptime(str(SecondData[0,3], 'utf-8'),"%Y-%m-%d-%H-%M-%S"))
file = open("writingfile.txt", "w")
file.close()
file = open("writingfile.txt", "a")
z = 0

for row in SecondData:
    file.write(SecondData[z][0].decode('UTF-8') + " " + SecondData[z][2].decode('UTF-8') + " " +
               SecondData[z][1].decode('UTF-8') + "\n")
    z = z + 1

file.close()

# TODO: set grid to 6 hour intervals, womöglich mit axis.set_xticks(21600)
#

print(x_start, y_start1, x_end, y_end1, ' ', y_start2, y_end2)
# plt.plot(PlotArray[:,0],PlotArray[:,1], '.')
tmp_x = [(datetime.datetime.fromtimestamp(i)) for i in PlotArray[:, 0]]
# tmp_y=[PlotArray[i][2] for i in range(0,10)]#.shape
tmp_y = PlotArray[:, 2]
tmp_array = PlotArray[:, (0, 2)]
# print (tmp_y)
# print (tmp_array)
# tmp_array= [PlotArray[i][0,2] for i in range(0,PlotArray.shape[0])]
# tmp_array= [(PlotArray[i][0],PlotArray[i][2]) for i in range(0,PlotArray.shape[0])]
# print(tmp_array)
plt.plot(tmp_x, tmp_y, )
axis = plt.gca()
#    axis.set_xticks()
# axis.set_yscale('log')
print(x_end)
temptimest = x_start.timestamp()
temptimest2 = x_end.timestamp()
#    axis.set_xlim([datetime.datetime.fromtimestamp(int(temptimest - 86400)),datetime.datetime.fromtimestamp(int(temptimest2+ 86400))])
# alternativ
axis.set_xlim([datetime.datetime.fromtimestamp(int(temptimest - (temptimest2 - temptimest) / 20)),
               datetime.datetime.fromtimestamp(int(temptimest2 + (temptimest2 - temptimest) / 20))])
axis.set_ylim([y_start2 - (0.05 * y_end2), y_end2 * 1.05])
# axis.set_xticks(21600, minor=False)
#
plt.grid(True)

# locs, labels = plt.xticks()
# axis.xaxis.set_ticks(np.arange(x_start,x_end,2628000))
# plt.plot(x,y, '.')
# plt.plot(times,coreseconds, '*')
# print(times)
# print (coreseconds)

plt.ylabel('Corehours')
plt.xlabel('Enddate of Process')
manager = plt.get_current_fig_manager()
#manager.resize(*manager.window.maxsize())
# plt.show()
fig = plt.gcf()
fig.set_size_inches((11, 8.5), forward=False)
fig.savefig(zieldatei.Output[0], dpi=500)
# plt.savefig("graph.png", bbox_inches='tight')
# testype = np.dtype(
#    [('A', '|S256'),('B', 'i4'), ('C', '|S256')])
# var1=np.array([('Foo',1,'a est'),('Goo',2,'more text'),('Hoo',3,'even more text')],dtype=testype)

