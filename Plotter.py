import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib.pyplot as plt  # MATLAB-like plotting
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import sys
import re

# This program creates an image that visualizes a given log file in relation to a given quota.

# determines quota-durations, current default value: 6 hours
# suggested 30*24*60*60 for months, but that creates imprecise months, assumes 30 day per month
# TODO: adapt seconds_per_instance depending on timerange
seconds_per_instance = 365.25/12 * 24 * 60 * 60

thresholds = [0.7, 1.1, 1.5]  # If the usage this month is below thresholds times the quota,
colors = ['#81c478', "#008000", '#ffa500']  # the quota will be colored in the equally indexed color.
maximum = '#ff0000'  # if the usage is above the (highest threshold) * quota, the Quota will be colored in
#  the given color 'maximum'.
plt.rcParams['figure.figsize'] = [6, 4]  # set global parameters, plotter initialisation


# translate_date_to_sec receives a date and returns the date in unix-seconds, if it's a valid date,
# (i.e not "Unknown" otherwise returns -1)
# If there is more invalid inputs possible in the log-system, this has to be expanded.
def translate_date_to_sec(ymdhms):
    """
    :param ymdhms: the year-month-day-hour-minute-second data (datetime.datetime) to be translated into unix-seconds.
    :return: the amount of seconds passed since the first of january 1970 00:00 UTC, if invalid: "-1".
    """
    #print(ymdhms)
    x_ = str(ymdhms, 'utf-8')
    if x_ == 'Unknown':
        return -1
    else:
        temp_time = datetime.datetime.strptime(str(ymdhms, 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # convert into datetime
        return temp_time.timestamp()  # then convert into unix-seconds (timestamp)

def translate_time_to_sec(time):
    flagdays = False
    if '-' in time:
        flagdays = True
    time = time.split('.')[0]
    if len(time) < 2:
        return 0
    subsplits = time.split('-')
    seconds = 0
    if flagdays:  # days are present
        seconds += 24 * 3600 * int(''.join(c for c in subsplits[0] if c.isdigit()))
    timesplitseconds = subsplits[-1].split(':')
    for i in range(len(timesplitseconds)):
        seconds += int(''.join(c for c in (timesplitseconds[-(i + 1)]) if c.isdigit())) * int(math.pow(60, int(i)))
    return seconds

# separates the quotas into four categories, taking the ratios from thresholds and the results from colors
def colorisation(value, comp):
    """
    :param value: The difference between the beginning of the Instance and the end, in Corehours
    :param comp: the given Quota
    :return: A color based on the relationship of the two parameters, red for value >> comp, green
     for value ~~ (roughly equal) comp, blue for comp >> value and orange for value > comp
    """
    if value/comp < thresholds[0]:
        return colors[0]
    if value / comp < thresholds[1]:
        return colors[1]
    if value / comp < thresholds[2]:
        return colors[2]
    else:
        return maximum


# Reads parameter inputs.
ap = argparse.ArgumentParser()
ap.add_argument('Source', type=str, nargs=1)
ap.add_argument('Output', type=str, nargs=1)
ap.add_argument('--quota', dest='Quota', type=int, nargs=1)
ap.add_argument('-q', dest='Quota', type=int, nargs=1)
ap.add_argument('-s', dest='StartPoint', default="None", type=str, nargs='?')
ap.add_argument('--start', dest='StartPoint', default="None", type=str, nargs='?')
ap.add_argument('-p', dest='ProjectName', type=str, nargs='?')
ap.add_argument('--project', dest='ProjectName', type=str, nargs='?')

parameter = ap.parse_args()
# parse parameters into values, divide the Quota into months from the yearly quota.
# convert input-parameters into data to interpret
target_file = parameter.Output[0]
startpoint = parameter.StartPoint
if len(startpoint) == 10: #appends hours, minutes and seconds if only date given
      startpoint += "-00-00-00"
startpoint = (str(startpoint)[::])
if parameter.ProjectName is not None:  #if no name is given, sets the filter to ""
    filter = parameter.ProjectName
else:
    filter = ""

if parameter.Quota:
    yearly_quota = parameter.Quota[0]
else:
    yearly_quota = None

if yearly_quota :
    partial_quota = int(yearly_quota / 12)
    #print(partial_quota)# Script runs under the assumption, the inserted quota = 12* the instance-quota
original = parameter.Source[0]

# this type is used to seperate allocatedcpus, starttime, endtime and other currently unused sets of data from the rest
data_type = np.dtype(
    [('JobID', '|S256'),('Account', '|S256'), ('ReqCPUS', 'i4'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
     ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
     ('End', '|S256'),('TotalCPU', '|S256'),('UserCPU', '|S256'),('SystemCPU', '|S256')])


# loads the file specified in original/Source, noteworthy are 'allocCPUS', 'Start' and 'End' (3,26,27)
# the total data available is: "JobIDRaw,Account,User,ReqCPUS,ReqMem,ReqNodes,AllocNodes,AllocCPUS,NNodes,NCPUS,NTasks,
# State,CPUTimeRAW,ElapsedRaw,TotalCPU,SystemCPU,UserCPU,MinCPU,AveCPU,MaxDiskRead,AveDiskRead,MaxDiskWrite,
# AveDiskWrite,MaxRSS,AveRSS,Submit,Start,End,Layout,ReqTRES,AllocTRES,ReqGRES,AllocGRES,Cluster,Partition,
# Submit,Start,End"
Data = np.loadtxt(original, dtype=data_type, delimiter='|', skiprows=0, usecols=(0, 1, 3, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15)
                  )
#efficiencydata = np.loadtxt(original,dtype=eff_type, delimiter='|',skiprows=0,usecols=()
#print("first value in Data is",Data[0]['End'])
Data = Data[(Data[::]['End']).argsort()]
#print(len(Data))
if len(Data) < 1:
    sys.stderr.write("No data in file.")
    sys.exit()

if startpoint == "None":
    x = Data[0][10]
    x = (str(x)[2::])
    x = x[:-1:]
    startpoint = x
    #startpoint = datetime.datetime.strptime(x, "%Y-%m-%d-%H-%M-%S")


highestdata = max(Data[::]['End'])
highestdata = str(highestdata)
highestdata = highestdata[2:-1]
if highestdata < startpoint:
    sys.stderr.write('The startpoint is after the latest date in the file')
    sys.exit()
datetime.datetime.strptime(startpoint, "%Y-%m-%d-%H-%M-%S")
x = (datetime.datetime.strptime(startpoint, "%Y-%m-%d-%H-%M-%S")).timestamp()
x += 3600*24*365

plot_array = (np.zeros((Data.size, 3)))  # three values are needed for each data point, time, cputime and accumulated
# Set a start date way in the future
x_start = datetime.datetime.strptime("3000-01-01-01-01-01", "%Y-%m-%d-%H-%M-%S")  # a date far in the future
x_end = datetime.datetime.strptime("2000-01-01-01-01-01", "%Y-%m-%d-%H-%M-%S")  # a date far in the past
# Set y max to the estimated total amount of core-hours in a year for the Lichtenberg (for max,min computation)
y_start1 = 1000000000000000000000000000000000  # initialized to a huge number so it's always larger.
y_end1 = 0  # initialized to 0 to ensure it's always smaller than the first value (max is used)
x = 0  # iterator variable, counts how many usable points of data exist
# gathers the Cores used and multiplies with the time (divided by 3600) to generate Corehours.
Systemt = []
Usert = []
for row in Data:
    #print(row['JobID'][2::])
    if translate_date_to_sec(row['End']) > 0 and ("." not in str(row['JobID'])) and filter in str(row['Account']):  # this filters jobs that haven't ended, due to them returning "-1".
        #print(row['JobID'])
        end_t = datetime.datetime.strptime(str(row['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # converts the string into a
        # datetime construct to interpret the endtime
        start_t = datetime.datetime.strptime(str(row['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # converts the string
        # into a datetime to interpret the starttime
        x_start = min(end_t, x_start)
        x_end = max(end_t, x_end)
        if row["ElapsedRaw"] < 1:  # for an invalid endtime (still running) or too short a process,
            continue  # skip that set of data
            # To find out the smallest value in a group, set a variable to a value higher than the highest
            #  value in the group and replace the variable's value with every lower value you find within the group
            # the same way the maximum value is determined.
        y_start1 = min(y_start1, row['AllocCPUS'] * row["ElapsedRaw"]/3600)  # calculate the lowest -> hours
        y_end1 = max(y_end1, row['AllocCPUS'] * row["ElapsedRaw"] / 3600)  # calculate the highest -> hours
        plot_array[x, 0] = end_t.timestamp()  # writes the time of end into the array
        #print("start",start_t)
        #print("end",end_t)
        #print("hours:",row["ElapsedRaw"]/ 3600, "cpus:",row['AllocCPUS'])
        plot_array[x, 1] = row['AllocCPUS'] * row["ElapsedRaw"] / 3600  # writes duration as  cores * hours
        formated = row['SystemCPU']
        formated = str(formated)[2:]
        if len(Systemt) == 0:
            Systemt.append(translate_time_to_sec(formated)/3600)
        else:
            Systemt.append(translate_time_to_sec(formated)/3600+Systemt[-1])
        formated = row['UserCPU']
        formated = str(formated)[2:]
        if len(Usert) == 0:
            Usert.append(translate_time_to_sec(formated)/3600)
        else:
            Usert.append(translate_time_to_sec(formated)/3600+Usert[-1])
        x = x + 1  # if data is usable, increments

# Error checks (for lack of valid names in timeframe)
if len(Usert) < 1:
    sys.stderr.write("No project in the given timeframe fits the given Projectname")
    sys.exit()
# creates a cutoff after the array runs out of values (several data points were skipped, results in 0s) and sorts it.
plot_array = plot_array[0:x][:]
plot_array = plot_array[plot_array[:, 0].argsort()]
    #np.sort(plot_array, axis=0)

# The third column is defined by the previous row's third column, as it is the cumulative runtime, the first row has
# no previous row , initialising the first row's with purely the second col.
if len(plot_array) >= 2:
    plot_array[0, 2] = plot_array[0][1]
y_start2 = 0
y_end2 = 0

# calculating cumulative Y-values, finding highest value and assigning it to y_end2, for the second to the last row
for index in range(1, plot_array.shape[0]):
    plot_array[index, 2] = plot_array[index, 1] + plot_array[index - 1, 2]
    y_end2 = max(y_end2, plot_array[index, 2])

# splitting plot_array into x and y values to easier visualize them.
tmp_x = [(datetime.datetime.fromtimestamp(i)) for i in plot_array[:, 0]]
tmp_y = plot_array[:, 2]
tmp_array = plot_array[:, (0, 2)]
# the quota has to be drawn for each instance, instance is duration divided by instance_length + 1
number_of_instances = ((x_end.timestamp() - x_start.timestamp()) / seconds_per_instance) + 1
# splits the graph into intervals and creates three values for each instance, to visualise quotas
# ___b----c___
# ___|________
# ___|________
# ___a________
# The three points a, b and c define each "L"
# the coordinates for each L are saved in  tmp_x2 and tmp_y2
tmp_x2 = np.arange(x_start.timestamp(), x_end.timestamp(), seconds_per_instance)
tmp_x2 = np.repeat(tmp_x2, 3)  # triples tmp_x2 to create thrice the number of values
tmp_x2 = np.sort(tmp_x2)  # Repeat creates "abcabcabc". However "aaabbbccc" is needed, hence sorting.
tmp_y2 = np.zeros(tmp_x2.shape)  # create a new y array to fill with quota coordinates.
temporary = 0  # holding variable for graph-y values (reading the current corehours)
# shifts the second of each triple along the y-axis, and the third along x- and y-axis
if yearly_quota:
    for itera in range(0, int(number_of_instances)):
        for i in range(0, np.size(tmp_x)):
            if tmp_x[i].timestamp() <= tmp_x2[itera * 3]:  # the array was tripled, hence need to go 3 per loop.
                temporary = tmp_y[i]  # Assigning the bottom left corner's y value to a temporary placeholder.
            else:
                break  # Found the highest value that is below the search value. It's in 'temporary'.
        tmp_y2[itera * 3 + 0] = temporary  # bottom left corner of each "L", can stay where the read value is.
        tmp_y2[itera * 3 + 1] = temporary + partial_quota  # moving top left corner of each "L" upwards.
        tmp_y2[itera * 3 + 2] = temporary + partial_quota  # moving top right corner upwards.
        tmp_x2[itera * 3 + 2] = tmp_x2[itera * 3 + 2] + seconds_per_instance  # shifting top right corner  right.

tmp_x3 = []
# transforms x2 into a format visualizable via the plotter alongside the main plot
for x2 in range(0, np.size(tmp_x2)-1):
    #print(len(tmp_x2),len(tmp_x3),x2)
    #print(tmp_x2[x2])
    #tmp_x3[x2] = (datetime.datetime.fromtimestamp(tmp_x2[x2]))
    tmp_x3.append(datetime.datetime.fromtimestamp(tmp_x2[x2]))
tmp_x3 = tmp_x3[0:int(number_of_instances) * 3:1]


#print(len(tmp_y2))

# determines the color via colorisation and then plots three points, stops before the last interval to draw
# sends the span of bottom left corner and top left corner, compares with span between top right and next bottom left
if yearly_quota:
    for iterator in range(0, int(number_of_instances - 1)):  # not possible for the last area, hence skipping it.
        col = colorisation(tmp_y2[iterator * 3 + 3] - tmp_y2[iterator * 3], tmp_y2[iterator * 3 + 2] - tmp_y2[iterator * 3])
        coordsx = ([tmp_x3[iterator * 3 + 1], tmp_x3[iterator * 3 + 2]])
        coordsy= [tmp_y2[iterator * 3+1], tmp_y2[iterator * 3 + 2]]
    #plt.plot([tmp_x3[iterator * 3], tmp_x3[iterator * 3 + 1], tmp_x3[iterator * 3 + 2]],
    #         [tmp_y2[iterator * 3], tmp_y2[iterator * 3 + 1], tmp_y2[iterator * 3 + 2]], col)
        plt.fill_between(coordsx, 0, coordsy, color=col, alpha=0.8)

# determines the last interval's color and draws it (uses the highest
# recorded value as the end value of the ongoing timespan).

#if len(tmp_x3) > 3 and len(tmp_y2) > 3 and yearly_quota:
#    col = colorisation(np.max(tmp_y)-tmp_y2[-3], tmp_y2[-1] - tmp_y2[-3])
#    plt.plot([tmp_x3[-3], tmp_x3[-2], tmp_x3[-1]], [tmp_y2[-3], tmp_y2[-2], np.max(tmp_y2[-1])], col)
axis = plt.gca()  # for plotting/saving the plot as it's own image


if yearly_quota and len(tmp_x) >= 1:
    extrapolationx = []
    extrapolationy = []
    extrapolationx.append(tmp_x[-1])
    extrapolationx.append(tmp_x[-1])
    extrapolationy.append(tmp_y[-1])
    extrapolationy.append(tmp_y[-1])

    extrapolationx[1] = (datetime.datetime.strptime(startpoint, "%Y-%m-%d-%H-%M-%S")).timestamp()
    extrapolationx[1] += (365+30)*24*3600
#print("extrapolx1 = ",extrapolationx[1])
    extrapolationx[1] = datetime.datetime.fromtimestamp(extrapolationx[1])
#print("extrapolx1 = ",extrapolationx[1])
    difference = datetime.datetime.strptime(startpoint, "%Y-%m-%d-%H-%M-%S").timestamp() - tmp_x[0].timestamp()
#print(difference)
#print(difference//(3600*24*30))
    difference = difference//(3600*24*30)
    extrapolationy[1] = extrapolationy[0] + partial_quota * (difference + 2)
#print(extrapolationx,extrapolationy)
    plt .plot(extrapolationx, extrapolationy, "black")

# Issue: adds an additional unwanted line along the x-axis, using max() on each x to remove this?

# Sets the visual borders for the graphs; area of occurring values (main graph) +- 5%.

beginning =  x_start.timestamp()
if startpoint :
    beginning = datetime.datetime.strptime(startpoint, "%Y-%m-%d-%H-%M-%S").timestamp()
    end = datetime.datetime.strptime(startpoint, "%Y-%m-%d-%H-%M-%S").timestamp() + 365 * 24 * 3600
    beginning = beginning - 30*24*3600
    #print("beginning:", beginning)
    end = end + 30*24*3600
    #end = datetime.datetime.fromtimestamp(end)
    #print("end:", end)
#temp_timestamp1 = x_start.timestamp()
#temp_timestamp2 = x_end.timestamp()


# Print statements, to give feedback either onscreen or into a dedicated file to be piped into.
print('the total usertime is ', Usert[-1], "hours")
print('the total Systemtime is ', Systemt[-1], "hours")
print('together they are', Usert[-1]+Systemt[-1], "hours")
print('and the total number of corehours is', tmp_y[-1])
efficiency = ((Usert[-1] + Systemt[-1]))/tmp_y[-1]
# Added rounding to the efficiency percentage feedback.
print('The total efficiency is',int(efficiency*10000)/100+0.005, "%")
if efficiency < 0 or efficiency > 1:
    print("Efficiency is outside of it's boundaries, valid is only between 0 and 1")

totaltime = np.zeros(len(tmp_x))
for i in range(0,len(totaltime)):
    totaltime[i] = Usert[i]+Systemt[i]

axis.set_xlim(datetime.datetime.fromtimestamp(beginning), datetime.datetime.fromtimestamp(end))

#axis.set_xlim([datetime.datetime.fromtimestamp(int(temp_timestamp1 - (temp_timestamp2 - temp_timestamp1) / 20)),
               #datetime.datetime.fromtimestamp(int(temp_timestamp2 + (temp_timestamp2 - temp_timestamp1) / 20))])

if yearly_quota:  # ensuring that the extrapolated quota is still in frame
    axis.set_ylim([y_start2 - (0.05 * y_end2),  max(tmp_y[-1],extrapolationy[1])* 1.05])
else:  # No quota given, image is focused around occupied and utilized resources.
    axis.set_ylim([y_start2 - (0.05 * y_end2), tmp_y[-1] * 1.05])
#print("highest totaltime (last)",totaltime[-1])
#print("tmp_y[-1]",tmp_y[-1])
#print("length of totaltime",len(totaltime))
#print("length of tmp_y",len(tmp_y))
#print("length of tmp_x",len(tmp_x))
#print(min(totaltime),min)
#print(max(totaltime),max)
#print((totaltime[len(totaltime)//2]))
#totaltime.sort()
plt.plot(tmp_x, totaltime, '#d9e72e') #plotting the TotatlCPU Graph
plt.fill_between(tmp_x, 0, totaltime, color='#d9e72e', alpha=0.99) # plotting the area below TotalCPU graph
plt.plot(tmp_x, tmp_y, 'grey', fillstyle='bottom', alpha=0.8)  # plotting the main graph (cores * hours)
plt.fill_between(tmp_x, 0, tmp_y, color="white", alpha=0.7)  # plotting the area below the corehours graph
#plt.plot(tmp_x,totaly)

# Creates a grid in the image to aid the viewer in visually processing the data.
plt.grid(True)
# Labels the two axes.
plt.ylabel('cores * hours')
plt.xlabel('enddate of process (date, time)')
manager = plt.get_current_fig_manager()
# saves the graph as a file under the name given in the "Output" parameter
fig = plt.gcf()
fig.set_size_inches((11, 8.5), forward=False)
fig.savefig(target_file, dpi=500)
