import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # MATLAB-like plotting
#  from matplotlib.collections import PatchCollection
#  from matplotlib.patches import Rectangle
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import sys
import matplotlib.patches as mpatches
#  import re

# todo: consider "_" in jobid, discard data that includes it in the id
# This program creates an image that visualizes a given log file in relation to a given quota.
# determines quota-durations, current default value: 6 hours
# suggested 30*24*60*60 for months, but that creates imprecise months, assumes 30 day per month
# TODO? adapt seconds_per_instance depending on time-range
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
    x_ = str(ymdhms, 'utf-8')
    if x_ == 'Unknown':
        return -1
    else:
        temp_time = datetime.datetime.strptime(str(ymdhms, 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # convert into datetime
        return temp_time.timestamp()  # then convert into unix-seconds (timestamp)


# reads the parameters and interprets -src, -o as well as every parameter not beginning with "-"
def essential_par(parameters):
    if (len(parameters)) < 2:
        sys.stderr.write("This file needs both an input and an output")
        sys.exit()
    sources_key, sources_nok, output, optpara = [], [], [], []
    while parameters:
        if "-src=" == parameters[0][:5]:
            sources_key.append(parameters[0][5:])
            parameters = parameters[1:]
        else:
            if "-o" == parameters[0][:2]:
                output.append(parameters[0][3:])
                parameters = parameters[1:]
            else:
                if "-" in parameters[0][0:2]:
                    optpara.append(parameters[0])
                    parameters = parameters[1:]
                else:
                    sources_nok.append(parameters[0])
                    parameters = parameters[1:]
    if len(output) >= 2:
        sys.stderr.write("Only 1 output file allowed")
        sys.exit()
    if not output:
        output.append(sources_nok[-1])
        sources_nok = sources_nok[:-1]
    sources = sources_key+sources_nok
    return [sources, output, optpara]


def translate_time_to_sec(time):
    flag_days = False
    if '-' in time:
        flag_days = True
    time = time.split('.')[0]
    if len(time) < 2:
        return 0
    sub_splits = time.split('-')
    seconds = 0
    if flag_days:  # days are present
        seconds += 24 * 3600 * int(''.join(c for c in sub_splits[0] if c.isdigit()))
    time_split_seconds = sub_splits[-1].split(':')
    for it in range(len(time_split_seconds)):
        seconds += int(''.join(c for c in (time_split_seconds[-(it + 1)]) if c.isdigit())) * int(math.pow(60, int(it)))
    return seconds


# separates the quotas into four categories, taking the ratios from thresholds and the results from colors
def colorization(value, comp):
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
ap.add_argument("-o", nargs=1)
ap.add_argument("-src", nargs='*')
ap.add_argument('--quota', dest='Quota', type=int, nargs=1)
ap.add_argument('-q', dest='Quota', type=int, nargs=1)
ap.add_argument('-s', dest='StartPoint', default="None", type=str, nargs='?')
ap.add_argument('--start', dest='StartPoint', default="None", type=str, nargs='?')
ap.add_argument('-p', dest='ProjectName', type=str, nargs='?')
ap.add_argument('--project', dest='ProjectName', type=str, nargs='?')
ap.add_argument('rest', type=str, nargs='*')
o_parameters = ap.parse_args()
e_parameters = essential_par((sys.argv[1:]))
# parse parameters into values, divide the Quota into months from the yearly quota.
# convert input-parameters into data to interpret
target_file = e_parameters[1][0]

start_point = o_parameters.StartPoint
if len(start_point) == 10:  # appends hours, minutes and seconds if only date given
    start_point += "-00-00-00"
start_point = (str(start_point)[::])
if o_parameters.ProjectName is not None:  # if no name is given, sets the filter_n to ""
    filter_n = o_parameters.ProjectName
else:
    filter_n = ""

if o_parameters.Quota:
    yearly_quota = o_parameters.Quota[0]
else:
    yearly_quota = None

if yearly_quota:
    partial_quota = int(yearly_quota / 12)
    # Script runs under the assumption, the inserted quota = 12* the instance-quota
originals = e_parameters[0]
# Data type to store the different fields in.
data_type = np.dtype(
    [('JobID', '|S256'), ('Account', '|S256'), ('ReqCPUS', 'i4'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
     ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
     ('End', '|S256'), ('TotalCPU', '|S256'), ('UserCPU', '|S256'), ('SystemCPU', '|S256')])


# loads the file specified in original/Source, noteworthy are 'allocCPUS', 'Start' and 'End' (3,26,27)
# the total data available is: "JobIDRaw,Account,User,ReqCPUS,ReqMem,ReqNodes,AllocNodes,AllocCPUS,NNodes,NCPUS,NTasks,
# State,CPUTimeRAW,ElapsedRaw,TotalCPU,SystemCPU,UserCPU,MinCPU,AveCPU,MaxDiskRead,AveDiskRead,MaxDiskWrite,
# AveDiskWrite,MaxRSS,AveRSS,Submit,Start,End,Layout,ReqTRES,AllocTRES,ReqGRES,AllocGRES,Cluster,Partition,
# Submit,Start,End"

Data = np.loadtxt(originals[0], dtype=data_type, delimiter='|', skiprows=0,
                  usecols=(0, 1, 3, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15)
                  )
Data_temp_2 = []
counter = 0

for j in Data:
    if 'Unknown' not in str(j['End']) and '.' not in str(j['JobID']) and filter_n in str(j['Account']):
        Data_temp_2.append(j)

Data = Data_temp_2


for i in range(1, len(originals)):
    Data_temp = np.loadtxt(originals[i], dtype=data_type, delimiter='|', skiprows=0,
                           usecols=(0, 1, 3, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15))
    Data_temp_2 = []
    for j in Data_temp:
        if 'Unknown' not in str(j['End']) and '.' not in str(j['JobID']) and filter_n in str(j['Account']):
            Data_temp_2.append(j)

    if Data_temp_2:
        if len(Data) > 0:
            Data = np.append(Data, Data_temp_2)
        else:
            Data = Data_temp_2
Data_temp_2 = []
print("total Datapoints:", len(Data))
flattenedData = np.array(Data).flatten().flatten()
Data = flattenedData
Data = Data[(Data[::]['End']).argsort()]
Data = np.array(Data)

if len(Data) < 1:
    sys.stderr.write("No data in file.")
    sys.exit()

if start_point == "None":
    x = Data[0][10]
    x = (str(x)[2::])
    x = x[:-1:]
    start_point = x

highest_data = max(Data[::]['End'])
highest_data = str(highest_data)
highest_data = highest_data[2:-1]
if highest_data < start_point:
    sys.stderr.write('The start_point is after the latest date in the file')
    sys.exit()
datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S")
x = (datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S")).timestamp()
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
System_t = []
User_t = []
for row in Data:
    if translate_date_to_sec(row['End']) > 0 and ("." not in str(row['JobID'])) and filter_n in str(row['Account']):  \
            # this filters jobs that haven't ended, due to them returning "-1".
        end_t = datetime.datetime.strptime(str(row['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # converts the string into a
        # datetime construct to interpret the end time
        start_t = datetime.datetime.strptime(str(row['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # converts the string
        # into a datetime to interpret the start time
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
        plot_array[x, 1] = row['AllocCPUS'] * row["ElapsedRaw"] / 3600  # writes duration as  cores * hours
        formatted = row['SystemCPU']
        formatted = str(formatted)[2:]
        if len(System_t) == 0:
            System_t.append(translate_time_to_sec(formatted) / 3600)
        else:
            System_t.append(translate_time_to_sec(formatted) / 3600 + System_t[-1])
        formatted = row['UserCPU']
        formatted = str(formatted)[2:]
        if len(User_t) == 0:
            User_t.append(translate_time_to_sec(formatted) / 3600)
        else:
            User_t.append(translate_time_to_sec(formatted) / 3600 + User_t[-1])
        x = x + 1  # if data is usable, increments

# Error checks (for lack of valid names in time frame)
if len(User_t) < 1:
    sys.stderr.write("No project in the given timeframe fits the given Projectname")
    sys.exit()
# creates a cutoff after the array runs out of values (several data points were skipped, results in 0s) and sorts it.
plot_array = plot_array[0:x][:]
plot_array = plot_array[plot_array[:, 0].argsort()]

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
#
# the coordinates for each Quota are saved in  tmp_x2 and tmp_y2
tmp_x2 = np.arange(x_start.timestamp(), x_end.timestamp(), seconds_per_instance)
tmp_x2 = np.repeat(tmp_x2, 3)  # triples tmp_x2 to create thrice the number of values
tmp_x2 = np.sort(tmp_x2)  # Repeat creates "abcabcabc". However "aaabbbccc" is needed, hence sorting.
tmp_y2 = np.zeros(tmp_x2.shape)  # create a new y array to fill with quota coordinates.
temporary = 0  # holding variable for graph-y values (reading the current core hours)
# shifts the second of each triple along the y-axis, and the third along x- and y-axis
if yearly_quota:
    for iterator_i in range(0, int(number_of_instances)):
        for i in range(0, np.size(tmp_x)):
            if tmp_x[i].timestamp() <= tmp_x2[iterator_i * 3]:  # the array was tripled, hence need to go 3 per loop.
                temporary = tmp_y[i]  # Assigning the bottom left corner's y value to a temporary placeholder.
            else:
                break  # Found the highest value that is below the search value. It's in 'temporary'.
        tmp_y2[iterator_i * 3 + 0] = temporary  # bottom left corner of each "L", can stay where the read value is.
        tmp_y2[iterator_i * 3 + 1] = temporary + partial_quota  # moving top left corner of each "L" upwards.
        tmp_y2[iterator_i * 3 + 2] = temporary + partial_quota  # moving top right corner upwards.
        tmp_x2[iterator_i * 3 + 2] = tmp_x2[iterator_i * 3 + 2] + seconds_per_instance  # shifting top r. corner  right.

tmp_x3 = []
# transforms x2 into a format that can be visualized via the plotter alongside the main plot
for x2 in range(0, np.size(tmp_x2)-1):
    tmp_x3.append(datetime.datetime.fromtimestamp(tmp_x2[x2]))
tmp_x3 = tmp_x3[0:int(number_of_instances) * 3:1]

# determines the color via colorization and then plots three points, stops before the last interval to draw
# sends the span of bottom left corner and top left corner, compares with span between top right and next bottom left
if yearly_quota:
    for iterator in range(0, int(number_of_instances - 1)):  # not possible for the last area, hence skipping it.
        col = colorization(tmp_y2[iterator * 3 + 3] - tmp_y2[iterator * 3],
                           tmp_y2[iterator * 3 + 2] - tmp_y2[iterator * 3])
        coordinates_x = ([tmp_x3[iterator * 3 + 1], tmp_x3[iterator * 3 + 2]])
        coordinates_y = [tmp_y2[iterator * 3 + 1], tmp_y2[iterator * 3 + 2]]
        plt.fill_between(coordinates_x, 0, coordinates_y, color=col, alpha=0.99)
# determines the last interval's color and draws it (uses the highest

# recorded value as the end value of the ongoing time span).
axis = plt.gca()  # for plotting/saving the plot as it's own image

#  Extrapolation
if yearly_quota and len(tmp_x) >= 1:
    extrapolation_x = []
    extrapolation_y = []
    extrapolation_x.append(tmp_x[-1])
    extrapolation_x.append(datetime.datetime.fromtimestamp(tmp_x3[-1].timestamp() + seconds_per_instance))
    extrapolation_x.append(datetime.datetime.fromtimestamp(tmp_x[0].timestamp() + seconds_per_instance * 12))
    extrapolation_y.append(tmp_y[-1])
    extrapolation_y.append(max(tmp_y[-1], tmp_y2[-3] + partial_quota))
    months_passed = math.ceil((extrapolation_x[1].timestamp() - tmp_x[0].timestamp()) / seconds_per_instance)
    extrapolation_y.append(extrapolation_y[-1] + (12 - months_passed) * partial_quota)
    plt .plot(extrapolation_x, extrapolation_y, "black")

# Sets the visual borders for the graphs; area of occurring values (main graph) +- 5%.
beginning = x_start.timestamp()
if start_point:
    beginning = datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S").timestamp()
    end = datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S").timestamp() + 365 * 24 * 3600
    beginning = beginning - 30*24*3600
    end = end + 30*24*3600

# Print statements, to give feedback either onscreen or into a dedicated file to be piped into.
print('The accumulated TotalCPU time is', int((User_t[-1] + System_t[-1]) * 100) / 100, "hours")
print('and the number of accumulated corehours is', int(tmp_y[-1]*100)/100)
efficiency = (User_t[-1] + System_t[-1]) / tmp_y[-1]
# Added rounding to the efficiency percentage feedback.
print('Which results in an efficiency of', int(efficiency*10000)/100+0.005, "%")
if efficiency < 0 or efficiency > 1:
    print("Efficiency is outside of it's boundaries, valid is only between 0 and 1")

total_time = np.zeros(len(tmp_x))
for i in range(0, len(total_time)):
    total_time[i] = User_t[i] + System_t[i]

axis.set_xlim(datetime.datetime.fromtimestamp(beginning), datetime.datetime.fromtimestamp(end))
if yearly_quota:  # ensuring that the extrapolated quota is still in frame
    axis.set_ylim([y_start2 - (0.05 * y_end2), max(tmp_y[-1], extrapolation_y[-1]) * 1.05])
else:  # No quota given, image is focused around occupied and utilized resources.
    axis.set_ylim([y_start2 - (0.05 * y_end2), tmp_y[-1] * 1.05])

#  Creation of patches for Labels
red_patch = mpatches.Patch(color='#ff0000', alpha=0.7, label='>=150%')
orange_patch = mpatches.Patch(color='#ffa500', alpha=0.7, label='>=110%,<150%')
green_patch = mpatches.Patch(color='#008000', alpha=0.8, label='>=70%,<110%')
light_green_patch = mpatches.Patch(color='#81c478', alpha=0.8, label='<70%')
grey_patch = mpatches.Patch(color='grey', alpha=0.7, label='Allocated Corehours')
yellow_patch = mpatches.Patch(color='#d9e72e', alpha=0.49, label='Utilized Corehours')
black_patch = mpatches.Patch(color='black', alpha=1, label='Extrapolation of guaranteed Corehours')

plt.plot(tmp_x, total_time, '#d9e72e')  # plotting the TotatlCPU Graph
if yearly_quota:  # Legends for if there is a quota, or a shorter Legend in case there isn't.
    plt.legend(handles=[red_patch, orange_patch, green_patch, light_green_patch, grey_patch, yellow_patch, black_patch])
else:
    plt.legend(handles=[grey_patch, yellow_patch])
plt.fill_between(tmp_x, 0, total_time, color='#d9e72e', alpha=0.8)  # plotting the area below TotalCPU graph
plt.plot(tmp_x, tmp_y, 'grey', fillstyle='bottom', alpha=0.8)  # plotting the main graph (cores * hours)
plt.fill_between(tmp_x, 0, tmp_y, color="white", alpha=0.7)  # plotting the area below the corehours graph

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