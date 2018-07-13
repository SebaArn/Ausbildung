import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib.pyplot as plt  # MATLAB-like plotting
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import re
# This code has unfixed issues, they are marked by the indicator "Issue:"

# This program creates an image that visualizes a given log file in relation to a given quota.

# determines quota-durations, current default value: 6 hours
# suggested 30*24*60*60 for months, but that creates imprecise months, assumes 30 day per month
# TODO: adapt seconds_per_instance depending on timerange
seconds_per_instance = 30.25 * 24 * 60 * 60
# Issue: hasn't implemented a proper month solution.

thresholds = [0.7, 1.1, 1.5]  # If the usage this month is below thresholds times the quota,
colors = ['#add8e6', "#008000", '#ffa500']  # the "L" will be colored in the equally indexed color.
maximum = '#ff0000'  # if the usage is above the (highest threshold) * quota, the "L" will be colored in
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
    x_ = str(ymdhms, 'utf-8')
    if x_ == 'Unknown':
        return -1
    else:
        temp_time = datetime.datetime.strptime(str(ymdhms, 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # convert into datetime
        return temp_time.timestamp()  # then convert into unix-seconds (timestamp)

def translate_time_to_sec(time):
    #print(time)
    seconds = 0
    flagdays = False
    if '-' in time:
        flagdays = True
    time = time.split('.')[0]
    #print(time)
    if len(time) < 2:
        return 0
    #time = time[1:-1:]
    subsplits = time.split('-')
    #print(subsplits)
    #print("länge",len(subsplits))
    seconds = 0
    if flagdays:  # days are present
        #print('days are present')
        #print(subsplits[0],'Days')
        #print('test')
        #print(''.join(c for c in subsplits[0] if c.isdigit()))
        seconds += 24 * 3600 * int(''.join(c for c in subsplits[0] if c.isdigit()))
        print(time, "contains")
        print(int(''.join(c for c in subsplits[0] if c.isdigit())),"days")
        print("->",seconds,"seconds")
        #print('that is ',seconds,"seconds")
    timesplitseconds = subsplits[-1].split(':')
    #print(timesplitseconds)
    #print(seconds,'seconds')
    for i in range(len(timesplitseconds)):
        #print(timesplitseconds[-(i+1)],"timesplitseconds[-(i+1)]")
        #print(''.join(c for c in (timesplitseconds[-(i + 1)]) if c.isdigit()),i)
        seconds += int(''.join(c for c in (timesplitseconds[-(i + 1)]) if c.isdigit())) * int(math.pow(60, int(i)))
        #print(seconds,'seconds')
    #print('done')
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


# Reads parameter inputs. Three are expected: two filenames and one Number >0.
# if the number is 0, an error is thrown, numbers below 0 will not throw an error, but
# not result in meaningful quota-visualisations
ap = argparse.ArgumentParser()
ap.add_argument('Source', type=str, nargs=1)
ap.add_argument('Output', type=str, nargs=1)
ap.add_argument('Quota', type=int, nargs='?')
parameter = ap.parse_args()
# parse parameters into values, divide the Quota into months from the yearly quota.
# convert input-parameters into data to interpret
target_file = parameter.Output[0]
yearly_quota = parameter.Quota
if yearly_quota:
    partial_quota = int(yearly_quota / 12)  # Script runs under the assumption, the inserted quota = 12* the instance-quota
original = parameter.Source[0]

# this type is used to seperate allocatedcpus, starttime, endtime and other currently unused sets of data from the rest
data_type = np.dtype(
    [('JobID', '|S256'), ('ReqCPUS', 'i4'), ('ReqMem', '|S256'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
     ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
     ('End', '|S256'),('TotalCPU', '|S256'),('UserCPU', '|S256'),('SystemCPU', '|S256')])


# loads the file specified in original/Source, noteworth are 'allocCPUS', 'Start' and 'End' (3,26,27)
# the total data available is: "JobIDRaw,Account,User,ReqCPUS,ReqMem,ReqNodes,AllocNodes,AllocCPUS,NNodes,NCPUS,NTasks,
# State,CPUTimeRAW,ElapsedRaw,TotalCPU,SystemCPU,UserCPU,MinCPU,AveCPU,MaxDiskRead,AveDiskRead,MaxDiskWrite,
# AveDiskWrite,MaxRSS,AveRSS,Submit,Start,End,Layout,ReqTRES,AllocTRES,ReqGRES,AllocGRES,Cluster,Partition,
# Submit,Start,End"
Data = np.loadtxt(original, dtype=data_type, delimiter='|', skiprows=0, usecols=(0, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27,15,17,16)
                  )# currently only 3, 26,27 are used.
#efficiencydata = np.loadtxt(original,dtype=eff_type, delimiter='|',skiprows=0,usecols=()
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
Totalt = []
for row in Data:
    print(row['JobID'][2::])
    if translate_date_to_sec(row['End']) > 0 and '.' not in str(row['JobID']):  # this filters jobs that haven't ended, due to them returning "-1".
        end_t = datetime.datetime.strptime(str(row['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # converts the string into a
        # datetime construct to interpret the endtime
        start_t = datetime.datetime.strptime(str(row['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # converts the string
        # into a datetime to interpret the starttime
        x_start = min(end_t, x_start)
        x_end = max(end_t, x_end)
        if (end_t - start_t).seconds < 1:  # for an invalid endtime (still running) or too short a process,
            continue  # skip that set of data
            # To find out the smallest value in a group, set a variable to a value higher than the highest
            #  value in the group and replace the variable's value with every lower value you find within the group
            # the same way the maximum value is determined.
        y_start1 = min(y_start1, (row['AllocCPUS'] * (end_t - start_t).seconds)/3600.0)  # calculate the lowest -> hours
        y_end1 = max(y_end1, (row['AllocCPUS'] * (end_t - start_t).seconds) / 3600.0)  # calculate the highest -> hours
        plot_array[x, 0] = end_t.timestamp()  # writes the time of end into the array
        plot_array[x, 1] = (row['AllocCPUS'] * (end_t - start_t).seconds / 3600.0)  # writes duration as hours * cores
        print("cpus:",row['AllocCPUS'])
        print("hours:",(end_t - start_t).seconds / 3600.0)
        print("product =", (row['AllocCPUS'] * (end_t - start_t).seconds / 3600.0))
        #print(row['UserCPU'],"/" ,row['SystemCPU'])
        #print(row['SystemCPU'])
        formated = row['SystemCPU']
        #print(formated,'systemcpu')
        formated = str(formated)[2:]
        #print(formated)
        if len(Systemt) == 0:
            Systemt.append(translate_time_to_sec(formated))
        else:
            Systemt.append(translate_time_to_sec(formated)+Systemt[-1])
        #Systemt += translate_time_to_sec(formated)
        formated = row['UserCPU']
        #print(formated,'usercpu')
        formated = str(formated)[2:]
        #Usert += translate_time_to_sec(formated)
        if len(Usert) == 0:
            Usert.append(translate_time_to_sec(formated))
        else:
            Usert.append(translate_time_to_sec(formated)+Usert[-1])
        formated = row['TotalCPU']
        #print(formated,'usercpu')
        formated = str(formated)[2:]
        #Usert += translate_time_to_sec(formated)
        if len(Totalt) == 0:
            Totalt.append(translate_time_to_sec(formated))
        else:
            Totalt.append(translate_time_to_sec(formated)+Totalt[-1])
        #Systemt += int(''.join(list(row['SystemCPU'])[2::]).split(':'))
        #Usert += int(''.join(list(row['UserCPU'])[2::]))
        # into array (cpuruntime)
        x = x + 1  # if data is usable, increments

# creates a cutoff after the array runs out of values (several data points were skipped, results in 0s) and sorts it.
plot_array = plot_array[0:x][:]
plot_array = plot_array[plot_array[:, 0].argsort()]
    #np.sort(plot_array, axis=0)

# The third column is defined by the previous row's third column, as it is the cumulative runtime, the first row has
# no previous row , initialising the first row's with purely the second col.
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


pc = PatchCollection
# determines the color via colorisation and then plots three points, stops before the last interval to draw
# sends the span of bottom left corner and top left corner, compares with span between top right and next bottom left
for iterator in range(0, int(number_of_instances - 1)):  # not possible for the last area, hence skipping it.
    col = colorisation(tmp_y2[iterator * 3 + 3] - tmp_y2[iterator * 3], tmp_y2[iterator * 3 + 2] - tmp_y2[iterator * 3])
    coordsx = ([tmp_x3[iterator * 3 + 1], tmp_x3[iterator * 3 + 2]])
    coordsy= [tmp_y2[iterator * 3+1], tmp_y2[iterator * 3 + 2]]
    # plt.plot([tmp_x3[iterator * 3], tmp_x3[iterator * 3 + 1], tmp_x3[iterator * 3 + 2]],
    #         [tmp_y2[iterator * 3], tmp_y2[iterator * 3 + 1], tmp_y2[iterator * 3 + 2]], col)
    plt.fill_between(coordsx, 0, coordsy, color=col, alpha=0.8)
    #rect = Rectangle((tmp_x3[iterator * 3 + 1],tmp_y2[iterator * 3 + 1]),tmp_x3[iterator * 3 + 2]-tmp_x3[iterator * 3 + 1],tmp_y2[iterator * 3 + 2])
    #plt.add_patch(rect)

# determines the last interval's color and draws it (uses the highest
# recorded value as the end value of the ongoing timespan).

if len(tmp_x3) > 3 and len(tmp_y2) > 3 and yearly_quota:
    col = colorisation(np.max(tmp_y)-tmp_y2[-3], tmp_y2[-1] - tmp_y2[-3])
    plt.plot([tmp_x3[-3], tmp_x3[-2], tmp_x3[-1]], [tmp_y2[-3], tmp_y2[-2], np.max(tmp_y2[-1])], col)
axis = plt.gca()  # for plotting/saving the plot as it's own image

# Issue: adds an additional unwanted line along the x-axis, using max() on each x to remove this?

# Sets the visual borders for the graphs; area of occurring values (main graph) +- 5%.
temp_timestamp1 = x_start.timestamp()
temp_timestamp2 = x_end.timestamp()


print('the total usertime is ', Usert[-1], "seconds")
print('the total Systemtime is ', Systemt[-1], "seconds")
print('together they are', Usert[-1]+Systemt[-1], "seconds")
print('highest totalt measured for reference:', Totalt[-1], "seconds")
print('divided by 3600 for hours is',(Usert[-1]+Systemt[-1])/3600, "hours")
print('highest totalt measured for reference:', Totalt[-1]//3600, "seconds")
print('and the total number of corehours is', tmp_y[-1])
efficiency = ((Usert[-1] + Systemt[-1])/3600)/tmp_y[-1]
#efficiency = totaltime/tmp_y[-1]
print('The total efficiency is',int(efficiency*10000)/100, "%")
if efficiency < 0 or efficiency > 1:
    print("Efficiency is outside of it's boundaries, valid is only between 0 and 1")

totaltime = np.zeros(len(tmp_x))
for i in range(0,len(totaltime)):
    totaltime[i] = (Usert[i]+Systemt[i])//3600
    #print(totaltime[i])



axis.set_xlim([datetime.datetime.fromtimestamp(int(temp_timestamp1 - (temp_timestamp2 - temp_timestamp1) / 20)),
               datetime.datetime.fromtimestamp(int(temp_timestamp2 + (temp_timestamp2 - temp_timestamp1) / 20))])
axis.set_ylim([y_start2 - (0.05 * y_end2),  max(totaltime[-1],tmp_y2[-1])* 1.05])
print("highest totaltime (last)",totaltime[-1])
print("tmp_y[-1]",tmp_y[-1])
#totaltime.sort()
print("length of totaltime",len(totaltime))
print("length of tmp_y",len(tmp_y))
print("length of tmp_x",len(tmp_x))
#print(min(totaltime),min)
#print(max(totaltime),max)
#print((totaltime[len(totaltime)//2]))
#totaltime.sort()
plt.plot(tmp_x, totaltime, '#eeff7f')
plt.fill_between(tmp_x, 0, totaltime, color='#eeff7f', alpha=0.8)
plt.plot(tmp_x, tmp_y, 'grey', fillstyle='bottom', alpha=0.7)  # plotting the main graph (cores * hours)
plt.fill_between(tmp_x, 0, tmp_y, color="white", alpha=0.65)
#totaly = np.zeros(len(Totalt))
#for i in range(len(Totalt)):
#    totaly[i] = Totalt[i]/3600


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
