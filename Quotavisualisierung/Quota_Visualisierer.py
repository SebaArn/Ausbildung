import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib
import glob
import getpass
import os
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # MATLAB-like plotting
#  from matplotlib.collections import PatchCollection
#  from matplotlib.patches import Rectangle
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import matplotlib.gridspec
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
import sys
import matplotlib.patches as mpatches
import pymysql
#  import re

fig = plt.gcf()
gs1 = plt.subplot2grid((2,1),(0,0))

f, (a0, a1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
# ISSUE: "_" is currently not excluded like "." is, no known occurrences, outdated?
# This program creates an image that visualizes a given log file in relation to a given quota.
# Instances are currently approximations of months
#seconds_per_instance = 365.25/12 * 24 * 60 * 60  # outdated, no longer used
thresholds = [0.7, 1.1, 1.5]  # If the usage this month is below thresholds times the quota,
colors = ['#81c478', "#008000", '#ffa500']  # the quota will be colored in the equally indexed color.
maximum = '#ff0000'  # if the usage is above the (highest threshold) * quota, the Quota will be colored in
#  the given color 'maximum'.
#plt.plot([1,2,3])
plt.rcParams['figure.figsize'] = [6, 4]  # set global parameters, plotter initialisation
# translate_date_to_sec receives a date and returns the date in unix-seconds, if it's a valid date,
# (i.e not "Unknown" otherwise returns -1)
# If there is more invalid inputs possible in the log-system, this has to be expanded.
fmt = "%Y-%m-%d-%H-%M"

# returns a date of the first second of the same month as the given date.
def first_of_month(date):
    a_date = date.strftime(fmt)
    sp = a_date.split("-")
    recombining = sp[0]+"-"+sp[1]+"-"+"01-00-00"
    retdate = datetime.datetime.strptime(recombining, fmt)
    return retdate

def find_y_from_x(x, xarray, yarray):
    holdx = xarray[0]
    holdy = yarray[0]
    for i in range(len(xarray)):
        #print(xarray[i].timestamp(),holdx.timestamp(),x.timestamp())
        if  (xarray[i].timestamp() >= holdx.timestamp() and xarray[i].timestamp() <= x.timestamp()):
            #print(holdx,holdy)
            holdx = xarray[i]
            holdy = yarray[i]
    return holdy
# returns the timestamp of a given string representing a date.
def translate_date_to_sec(ymdhms):
    """
    :param ymdhms: the year-month-day-hour-minute-second data (datetime.datetime) to be translated into unix-seconds.
    :return: the amount of seconds passed since the first of january 1970 00:00 UTC, if invalid: "-1".
    """
    x_ = str(ymdhms, 'utf-8')
    if x_ == 'Unknown':
        return -1
    else:
        temp_time = datetime.datetime.strptime(str(ymdhms, 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # cxonvert into datetime
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
quotaexists = 0
number_id=0

# Reads parameter inputs.
ap = argparse.ArgumentParser()
ap.add_argument("-o", nargs=1)
ap.add_argument("-n", nargs='*', dest="Number_id")
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
yearly_quota = 0
target_file = e_parameters[1][0]
Parameternummer = 0
#multidisplaying two different Graphs, one for Efficiency, one for the overall consumption
if o_parameters.Number_id:
    Parameternummer = o_parameters.Number_id[0]
if Parameternummer:   #tries obtaining quota and startdate from projectdatabase
    user = getpass.getuser()
    password = getpass.getpass()
    db2 = pymysql.connect(host='hlr-hpc1.hrz.tu-darmstadt.de',
                          port=3306,
                          user=user,
                          password=password,
                          db='projektantrag')
    cur = db2.cursor()
    string = "SELECT projektstart,number_of_months,coreh FROM data WHERE id=" + str(
        Parameternummer) + ";"
    cur.execute(string)
    DBDaten = cur.fetchall()[0]
    start_point = datetime.datetime.fromtimestamp(DBDaten[0])
    yearly_quota = DBDaten[2]/DBDaten[1]*12

    #TODO: check if the yearly quota is calculated correctly. twelve times the corehours divided by number of months,
    #TODO: to create a monthly quota, it is divised by twelve again.

if o_parameters.StartPoint:
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
    if not yearly_quota:
        yearly_quota = 0

if yearly_quota>0:
    partial_quota = int(yearly_quota / 12)
else:
    partial_quota = 0
    # Script runs under the assumption, the inserted quota = 12* the instance-quota
originals = e_parameters[0]
if e_parameters[0]:
    pass
else:
    sys.stderr.write("Error: no source identified, expecting source in format: 'src=path/*' or 'src path/filename'.\n")
    sys.exit("Did not find a source file")
if "*" in e_parameters[0][0] or "?" in e_parameters[0][0]:
    originals = glob.glob(e_parameters[0][0])
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


if os.path.isfile(originals[0]):
    print("visualizing files:")
    for i in originals:
        print(i)
    pass
else:
    sys.stderr.write("can not find sourcefile:'" + str(originals[0]) + "'\n")
    sys.exit("File not found")


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
if len(Data) < 1:
    sys.stderr.write("No data found")
    sys.exit()
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
x = 0  # i variable, counts how many usable points of data exist
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


beginning = first_of_month(x_start)
beginning_dt = beginning
Xtics = []
Xtics.append(first_of_month(datetime.datetime.fromtimestamp(beginning_dt.timestamp()-1)))
for i in range (14):
    Xtics.append(first_of_month(datetime.datetime.fromtimestamp(Xtics[-1].timestamp()+2700000)))

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
stringstart = datetime.datetime.strftime(x_start,fmt).split("-")
stringend = datetime.datetime.strftime(x_end,fmt).split("-")
number_of_instances = (int(stringend[0])-int(stringstart[0]))*12 + int(stringend[1])-int(stringstart[1])
print("instances:" ,number_of_instances)
#print(x_end)
#print(x_start)
# splits the graph into intervals and creates three values for each instance, to visualise quotas
#l
# the coordinates for each Quota are saved in  tmp_x2 and tmp_y2
Xticstimestamps = []
for i in Xtics:
    Xticstimestamps.append(i.timestamp())
tmp_x2 = Xticstimestamps[1:]
tmp_x2 = np.repeat(tmp_x2, 3)  # triples tmp_x2 to create thrice the number of values
tmp_x2 = np.sort(tmp_x2)  # Repeat creates "abcabcabc". However "aaabbbccc" is needed, hence sortin
tmp_y2= []
temporary = 0  # holding variable for graph-y values (reading the current core hours)
# shifts the second of each triple along the y-axis, and the third along x- and y-axis
print(yearly_quota)
blocks_x = [first_of_month(x_start).timestamp()]
if yearly_quota:
    for iterator_i in range(0, int(number_of_instances)):
        temporary = find_y_from_x(datetime.datetime.fromtimestamp(blocks_x[-1]),tmp_x,tmp_y)
        tmp_y2.append(temporary)  # bottom left corner of each "L", can stay where the read value is.
        tmp_y2.append(temporary + partial_quota)  # moving top left corner of each "L" upwards.
          # moving top right corner upwards.
        #print(blocks_x)
        startcurrentmonth = first_of_month(datetime.datetime.fromtimestamp(blocks_x[-1]))
        somewherenextmonth = datetime.datetime.fromtimestamp(startcurrentmonth.timestamp()+2764800)
        startnextmonth = first_of_month(somewherenextmonth)
        tmp_x2[iterator_i * 3] = startcurrentmonth.timestamp()
        tmp_x2[iterator_i * 3+1] = startcurrentmonth.timestamp()
        tmp_x2[iterator_i * 3+2] = startnextmonth.timestamp()
        blocks_x.append(startcurrentmonth.timestamp())
        blocks_x.append(startnextmonth.timestamp())
blocks_x = blocks_x[1:]
#print("LENGTH:",len(blocks_x))
#print("blocks_x",blocks_x)
#print("tmp_y2",tmp_y2)
    # shi   fting top r. corner  right.
#if yearly_quota:
#    if (tmp_y2):
#        tmp_y2.append(tmp_y2[-1]+partial_quota)
#    else:
#        tmp_y2 = [0,0,0]
tmp_x3 = []
#for i in range(len(tmp_x2)):
    #print(datetime.datetime.fromtimestamp(tmp_x2[i]).strftime(fmt))
# transforms x2 into a format that can be visualized via the plotter alongside the main plot
for x2 in range(0, np.size(tmp_x2)-1):
    tmp_x3.append(datetime.datetime.fromtimestamp(tmp_x2[x2]))
tmp_x3 = tmp_x3[0:int(number_of_instances) * 3:1]

#Tmp_y2[] ist die erreichte toptime


monthly_cputime = []
monthly_used = []
effarray = []

tmp_y2.append(tmp_y[-1])

# determines the color via colorization and then plots three points, stops before the last interval to draw
# sends the span of bottom left corner and top left corner, compares with span between top right and next bottom left
if partial_quota:
    for i in range(0,number_of_instances):  # not possible for the last area, hence skipping it.
        #print("quoting")
        col = colorization(find_y_from_x(datetime.datetime.fromtimestamp(blocks_x[i*2+1]),tmp_x,tmp_y) - find_y_from_x(datetime.datetime.fromtimestamp(blocks_x[i*2]),tmp_x,tmp_y),partial_quota)
        coordinates_x = (datetime.datetime.fromtimestamp(blocks_x[i*2]),datetime.datetime.fromtimestamp(blocks_x[i*2]), datetime.datetime.fromtimestamp(blocks_x[i * 2+ 1]))
        coordinates_y = [tmp_y2[i * 2 ],tmp_y2[i * 2+1 ], tmp_y2[i * 2+1]]
        #print(coordinates_x,coordinates_y)
        a0.fill_between(coordinates_x, 0, coordinates_y, color=col, alpha=0.99)

        monthly_cputime.append(tmp_y2[i * 2 + 1] - tmp_y2[i * 2])
# determines the last interval's color and draws it (uses the highest

# recorded value as the end value of the ongoing time span).
axis = plt.gca()  # for plotting/saving the plot as it's own image



# Sets the visual borders for the graphs; area of occurring values (main graph) +- 5%.
if start_point:
    beginning = datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S").timestamp()
    end = datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S").timestamp() + 365 * 24 * 3600
    beginning = beginning - 30*24*3600
    end = end + 30*24*3600

extrapolation_x = []
extrapolation_y = []
#  Extrapolation
#extrapolation_y.app
if (len(tmp_y2)<3):
    tmp_y2.append(0)
    tmp_y2.append(0)
monthsleft = int(12 + ((x_start.timestamp() - tmp_x[-1].timestamp()) / 2629800 + 0.9) // 1)
if yearly_quota and len(tmp_x) >= 1:
    #month = 2629800
    extrapolation_point_x = first_of_month(tmp_x[-1])
    extrapolation_point_y = find_y_from_x(tmp_x[-1],tmp_x,tmp_y)
    extrapolation_point_y = max(extrapolation_point_y, tmp_y2[-3]+partial_quota)
    extrapolation_point_y = extrapolation_point_y-partial_quota
    extrapolation_x.append(first_of_month(extrapolation_point_x))
    extrapolation_y.append(extrapolation_point_y)
    xtr_pt_x = extrapolation_point_x
    xtr_pt_y = extrapolation_point_y
    print("left:",monthsleft)
    for i in range(monthsleft):
        #extrapolation_x.append(datetime.datetime.fromtimestamp(tmp_x[-1].timestamp()+i*2629800))
        extrapolation_x.append(first_of_month(datetime.datetime.fromtimestamp(xtr_pt_x.timestamp()+i*2851200)))
        extrapolation_x.append(first_of_month(datetime.datetime.fromtimestamp(xtr_pt_x.timestamp() + i * 2851200)))
        extrapolation_x.append(first_of_month(datetime.datetime.fromtimestamp(xtr_pt_x.timestamp() + (i + 1) * 2851200)))
        #extrapolation_y.append(tmp_y[-1]+i*partial_quota)
        extrapolation_y.append(tmp_y[-1]+(i)*partial_quota)
        extrapolation_y.append(tmp_y[-1]+(i+1)*partial_quota)
        extrapolation_y.append(tmp_y[-1]+(i+1)*partial_quota)
    #print(extrapolation_y)
    #print(len(extrapolation_y))
    #print(len(extrapolation_x))
    if (monthsleft):
        a0.plot(extrapolation_x, extrapolation_y, "black")

if (monthsleft):
    extrapolation_y.append(0)
else:
    extrapolation_y = [0]
beg_14_months = beginning+36817200
fourteen_dt = datetime.datetime.fromtimestamp(beg_14_months)
# Print statements, to give feedback either onscreen or into a dedicated file to be piped into.
print('The accumulated TotalCPU time is', int((User_t[-1] + System_t[-1]) * 100) / 100, "hours")
print('and the number of accumulated corehours is', int(tmp_y[-1]*100)/100)
efficiency = (User_t[-1] + System_t[-1]) / tmp_y[-1]
# Added rounding to the efficiency percentage feedback.
print('Which results in an efficiency of', int(efficiency*10000)/100+0.005, "%")
if efficiency < 0 or efficiency > 1:
    print("Efficiency is outside of it's boundaries, valid is only between 0 and 1")

accum_total_time = np.zeros(len(tmp_x))
for i in range(0, len(accum_total_time)):
    accum_total_time[i] = User_t[i] + System_t[i]
#print(accum_total_time)
delta = [0]
total_time = []
total_time.append(accum_total_time[0])

difference = [0]
for i in range(1,len(accum_total_time)):
    #print(i)
    total_time.append(accum_total_time[i]- accum_total_time[i-1])
    #delta.append(max(-100,(min(100, 100*(total_time[i]-(tmp_y[i]))))))

    #difference.append()
    delta.append(100*((accum_total_time[i]-accum_total_time[i-1])/(tmp_y[i]-tmp_y[i-1])))
    if (delta[i]>100):
        print((accum_total_time[i]-accum_total_time[i-1]),(tmp_y[i]-tmp_y[i-1]))
    #difference.append(delta[i]-delta[i-1])
#print(delta)



if yearly_quota:  # ensuring that the extrapolated quota is still in frame
    a0.set_ylim([y_start2 - (0.05 * y_end2), max(tmp_y[-1], max(extrapolation_y)) * 1.2])
    print("limit",a0.get_ylim()[1])
else:  # No quota given, image is focused around occupied and utilized resources.
    print("NO YEARLY DETECTED")
    a0.set_ylim([y_start2 - (0.05 * y_end2), tmp_y[-1] * 1.05])



#  Creation of patches for Labels
red_patch = mpatches.Patch(color='#ff0000', alpha=0.7, label='>=150%')
orange_patch = mpatches.Patch(color='#ffa500', alpha=0.7, label='>=110%,<150%')
green_patch = mpatches.Patch(color='#008000', alpha=0.8, label='>=70%,<110%')
light_green_patch = mpatches.Patch(color='#81c478', alpha=0.8, label='<70%')
grey_patch = mpatches.Patch(color='grey', alpha=0.7, label='Allocated Corehours')
yellow_patch = mpatches.Patch(color='#d9e72e', alpha=0.49, label='Utilized Corehours')
black_patch = mpatches.Patch(color='black', alpha=1, label='Extrapolation of guaranteed Corehours')

a0.plot(tmp_x, accum_total_time, '#d9e72e')  # plotting the TotatlCPU Graph
if yearly_quota:  # Legends for if there is a quota, or a shorter Legend in case there isn't.
    a0.legend(handles=[red_patch, orange_patch, green_patch, light_green_patch, grey_patch, yellow_patch, black_patch])
else:
    a0.legend(handles=[grey_patch, yellow_patch])
a0.fill_between(tmp_x, 0, accum_total_time, color='#d9e72e', alpha=0.45)  # plotting the area below TotalCPU graph
a0.plot(tmp_x, tmp_y, 'grey', fillstyle='bottom', alpha=0.35)  # plotting the main graph (cores * hours)
a0.fill_between(tmp_x, 0, tmp_y, color="white", alpha=0.25)  # plotting the area below the corehours graph

if yearly_quota:
    for i in range(0, int(number_of_instances)):  # not possible for the last area, hence skipping it.
        monthly_used.append(accum_total_time[i * 3 + 3] - accum_total_time[i * 3])


percentages = [0]
for i in range(len(monthly_cputime)):
    percentages.append (10*(monthly_cputime[i]/monthly_used[i]))

for i in range(len(percentages)):
    effarray.append(percentages[i])
tmp_x3 = []

for i in range(len(tmp_x2)//3):
    tmp_x3.append(tmp_x2[i*3])
tmp_x4 = []
for i in range(len(tmp_x3)):
    tmp_x4.append(datetime.datetime.fromtimestamp(tmp_x3[i]))
perc = []
a0.grid(True)
axis2 = fig.add_subplot(212)
a1.plot(tmp_x, delta, '.', color="purple", alpha=0.9) # percentages amplified by the lower bound to be more visible.
plt.ylabel('Efficiency')


# Formats the Date into Month and Year.
myFmt = mdates.DateFormatter('%b %y')
nothing = mdates.DateFormatter(' ')

eff_distance = 0 - axis.get_ylim()[0]
# Creates a grid in the image to aid the viewer in visually processing the data.
a1.grid(True)
a1.set_ylim([-5, 105])
a1.set_yticks(np.arange(0, 101, 10),minor=True) # minor tick-lines are much thinner than regular ones
a1.set_yticks(np.arange(0, 101, 25))
a1.yaxis.set_major_formatter(mtick.PercentFormatter())
plt.xlabel('Efficiency')
plt.xlabel('enddate of process (date, time)')
a0.xaxis.tick_top()
a0.set_xlim((beginning_dt, fourteen_dt))
a1.xlim = (beginning_dt, fourteen_dt)
plt.sca(a0)
plt.ticklabel_format(axis='y', style='sci', scilimits=(0, 4))
plt.xticks(Xtics)
plt.ylabel('CPUhours')
emptylabels = []
for i in a0.get_xticklabels():
    emptylabels.append(["",""])
a0.set_xticklabels = emptylabels
plt.sca(a1)
#dictates gap in height, left border, right border, gap in width, bottom border, top border
plt.subplots_adjust(hspace=0.03,left=0.075, right=0.925, wspace=0.07, bottom=0.07,top=0.975)
plt.xlim(beginning_dt,fourteen_dt)
plt.xticks(Xtics)
a0.xaxis.set_major_formatter(nothing) # removes the Xtic notations
a1.xaxis.set_major_formatter(myFmt) # puts the
# autospacing
# f.tight_layout()
a1.grid(which='minor', alpha=0.2)
a1.grid(which='major', alpha=0.5)
f.set_size_inches((11, 8.5), forward=False)
# saves the graph as a file under the name given in the "Output" parameter
f.savefig(target_file, dpi=500)
#print(tmp_y2)