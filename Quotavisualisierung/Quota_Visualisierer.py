import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib
matplotlib.use('Agg')
import Parsing
import matplotlib.pyplot as plt  # MATLAB-like plotting
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import matplotlib.dates as mdates
import sys
import os
import math
#import PIL
import getpass
import pymysql
import Time_functions as D_
import drawing

fig = plt.gcf()
gs1 = plt.subplot2grid((2, 1), (0, 0))
nutzergraph = False
f, (a0, a1) = plt.subplots(2, 1, gridspec_kw={'height_ratios': [3, 1]})
# ISSUE: "_" is currently not excluded like "." is, no known occurrences, outdated?
# This program creates an image that visualizes a given log file in relation to a given quota.

plt.rcParams['figure.figsize'] = [6, 4]  # set global parameters, plotter initialisation
# translate_date_to_sec receives a date and returns the date in unix-seconds, if it's a valid date,
fmt = "%Y-%m-%d-%H-%M"  # standard format for Dates, year month, day, hour, minute
quotaexists = 0
number_id=0
# Formats the Date into Month and Year.
myFmt = mdates.DateFormatter('%b %y')
nothing = mdates.DateFormatter(' ')
ap = argparse.ArgumentParser() # Reads parameter inputs.
Parsing.argparsinit(ap, sys.argv)
originals = Parsing.get_original()
partial_quota = Parsing.get_partial_quota()
yearly_quota = Parsing.get_yearly_quota()
start_point = Parsing.get_start_point()
filter_n = Parsing.get_filter()
originals = Parsing.get_original()
nutzergraph = Parsing.get_nutzer_graph()
datum = Parsing.get_datum()
number_of_months_DB = Parsing.get_number_of_months()
target = Parsing.get_target()
Parameternummer = Parsing.get_parameter_nr()
#print("PARANR",Parameternummer)
###### SQL connection to projectrequest database #####
if Parameternummer:  # tries obtaining quota and startdate from projectdatabase
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
    number_of_months_DB = DBDaten[1]
    start_point = datetime.datetime.fromtimestamp(DBDaten[0])
    yearly_quota = DBDaten[2] / DBDaten[1] * 12

    if yearly_quota > 0:
        partial_quota = int(yearly_quota / 12)
    else:
        partial_quota = 0  # Script runs under the assumption, the inserted quota = 12* the instance-quota

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
else:
    sys.stderr.write("can not find sourcefile:'" + str(originals[0]) + "'\n")
    sys.exit("File not found")
Data = np.loadtxt(originals[0], dtype=data_type, delimiter='|', skiprows=0,
                  usecols=(0, 1, 3, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15))
Data_temp_2 = []
counter = 0
for j in Data:
    if 'Unknown' not in str(j['End']) and '.' not in str(j['JobID']) and filter_n in str(j['Account']):
        Data_temp_2.append(j)
Data = Data_temp_2
for i in range(1, len(originals)):
    Data_temp = np.loadtxt(originals[i], dtype=data_type, delimiter='|', skiprows=0,ndmin=1,
                           usecols=(0, 1, 3, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15))
    Data_temp_2 = []
    if len(Data_temp) > 0:
        for j in Data_temp:
            if 'Unknown' not in str(j['End']) and '.' not in str(j['JobID']) and filter_n in str(j['Account']):
                Data_temp_2.append(j)
        if Data_temp_2:
            if len(Data) > 0:
                Data = np.append(Data, Data_temp_2)
            else:
                Data = Data_temp_2
Data_temp_2 = []
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
    start_point = datetime.datetime.strptime(x, "%Y-%m-%d-%H-%M-%S")
#else:
#    start_point = datetime.datetime.
highest_data = max(Data[::]['End'])
highest_data = str(highest_data)
highest_data = highest_data[2:-4]
## hotfix:
##highest_data = datetime.datetime.strptime(highest_data, fmt)
##highest_data = datetime.datetime.strftime(highest_data, fmt)
if datetime.datetime.strptime(highest_data,fmt).timestamp() < start_point.timestamp():
    sys.stderr.write('The start_point is after the latest date in the file')
    sys.exit()
#datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S")
#x = (datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S")).timestamp()+3600*24*365
#x = start_point.timestamp()+3600*24*365
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
if datum:
    latest = datum
    x_end = datetime.datetime.strptime(latest)
    #latest = datetime.datetime.strptime("2019-10-29-00-00-00", "%Y-%m-%d-%H-%M-%S")  # parameter
    #x_end = latest
#data_type = np.dtype(
#    [('JobID', '|S256'), ('Account', '|S256'), ('ReqCPUS', 'i4'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
#     ('AllocCPUS', 'i4'),
#     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
#     ('End', '|S256'), ('TotalCPU', '|S256'), ('UserCPU', '|S256'), ('SystemCPU', '|S256')])

Data.append(Data[0])
Data[-1][8] = 1
Data[-1][9] = x_end
Data[-1][10] = x_end
Data[-1][11] = "00:00:01"
Data[-1][12] = "00:00:01"
Data[-1][12] = "00:00:01"
 #### Setzte einen Punkt an den aktuellen Tag ####
for row in Data:
    end_t = datetime.datetime.strptime(str(row['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # converts the string into a
    # datetime construct to interpret the end time
    start_t = datetime.datetime.strptime(str(row['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # converts the string
    # into a datetime to interpret the start time
    x_start = min(end_t, x_start)
    x_end = max(end_t, x_end)
    if D_.translate_date_to_sec(row['End']) > 0 and ("." not in str(row['JobID'])) and filter_n in str(row['Account']):  \
            # this filters jobs that haven't ended, due to them returning "-1".
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
            System_t.append(D_.translate_time_to_sec(formatted) / 3600)
        else:
            System_t.append(D_.translate_time_to_sec(formatted) / 3600 + System_t[-1])
        formatted = row['UserCPU']
        formatted = str(formatted)[2:]
        if len(User_t) == 0:
            User_t.append(D_.translate_time_to_sec(formatted) / 3600)
        else:
            User_t.append(D_.translate_time_to_sec(formatted) / 3600 + User_t[-1])
        x = x + 1  # if data is usable, increments
# Error checks (for lack of valid names in time frame)
if len(User_t) < 1:
    sys.stderr.write("No project in the given timeframe fits the given Projectname")
    sys.exit()
beginning = D_.first_of_month(x_start)
beginning_dt = beginning
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
stringstart = datetime.datetime.strftime(x_start, fmt).split("-")
stringend = datetime.datetime.strftime(x_end, fmt).split("-")
number_of_instances = (int(stringend[0])-int(stringstart[0]))*12 + int(stringend[1])-int(stringstart[1])
# splits the graph into intervals and creates three values for each instance, to visualise quotas
# the coordinates for each Quota are saved in  tmp_x2 and tmp_y2
months = int(tmp_x[-1].strftime(fmt).split("-")[1]) - int(x_start.strftime(fmt).split("-")[1]) + 2
if number_of_months_DB:
    months = number_of_months_DB
Xtics = []
Xtics.append(D_.first_of_month(datetime.datetime.fromtimestamp(beginning_dt.timestamp()-1)))
for i in range(max(14, months)):
    Xtics.append(D_.first_of_month(datetime.datetime.fromtimestamp(Xtics[-1].timestamp()+2700000)))
Xticstimestamps = []
for i in Xtics:
    Xticstimestamps.append(i.timestamp())
tmp_y2 = []
# shifts the second of each triple along the y-axis, and the third along x- and y-axis
blocks_x = [D_.first_of_month(x_start).timestamp()]
if yearly_quota:
    for iterator_i in range(0, int(number_of_instances)):
        temporary = D_.find_y_from_given_time(datetime.datetime.fromtimestamp(blocks_x[-1]), tmp_x, tmp_y)
        tmp_y2.append(temporary)  # bottom left corner of each "L", can stay where the read value is.
        tmp_y2.append(temporary + partial_quota)  # End of the L
        startcurrentmonth = D_.first_of_month(datetime.datetime.fromtimestamp(blocks_x[-1]))
        somewherenextmonth = datetime.datetime.fromtimestamp(startcurrentmonth.timestamp()+2764800)
        startnextmonth = D_.first_of_month(somewherenextmonth)
        blocks_x.append(startcurrentmonth.timestamp())
        blocks_x.append(startnextmonth.timestamp())
    if len(blocks_x) > 1:
        blocks_x = blocks_x[1:]

    blocks_x.append(D_.first_of_month(datetime.datetime.fromtimestamp(blocks_x[-1]+3456000)).timestamp())
# transforms x2 into a format that can be visualized via the plotter alongside the main plot
tmp_y2.append(tmp_y[-1])
f = drawing.generate_plot(partial_quota, number_of_instances, f, a0, a1, tmp_y2, tmp_x, tmp_y, blocks_x, start_point,
                          Xtics, yearly_quota, x_start, datum, User_t, System_t, y_start2, y_end2, beginning_dt,
                          nutzergraph, fig, x_end, Data, filter_n)
#f.save (target, format="PNG")   # for png compression
f.savefig(target, dpi=130, quality=80)
