import numpy as np
import matplotlib.pyplot as plt  # MATLAB-like plotting
import datetime
import argparse
import os.path


# Read parameter inputs three are expected; two filenames and one Number >0.
# if the number is 0, an error is thrown, numbers below 0 will not throw an error, but
# not result in meaningful visualisations
ap = argparse.ArgumentParser()
ap.add_argument('Source', type=str, nargs=1)
ap.add_argument('Output', type=str, nargs=1)
ap.add_argument('Quota', type=int, nargs='?')
parameter = ap.parse_args()

# parse parameters into values, divide the Quota into months from the yearly quota.
# convert input-parameters into data to interpret
plt.rcParams['figure.figsize'] = [6, 4]  # set global parameters
targetFile = ap.parse_args()
yearlyQuota = ap.parse_args().Quota
partialQuota = int(yearlyQuota / 12)
dataType = np.dtype(
    [('JobID', '|S256'), ('ReqCPUS', 'i4'), ('ReqMem', '|S256'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
     ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
     ('End', '|S256')])
job_record = np.dtype([('ReqCPUS', 'i4'), ('ReqMem', 'i4')])
original = parameter.Source[0]
currentPath = os.path.abspath(".")

# copy and test may cause issues, as they use the currently active path and assume that both files actually exist
copy = os.path.join(currentPath, "copy.log-example")
test = os.path.join(currentPath, "testinput.log-example")
# load the data from file with the given name, discarding most irrelevant sets of data.
Data = np.loadtxt(original, dtype=dataType, delimiter='|', skiprows=0, usecols=(1, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27))
fin_dtype = np.dtype(
    [('Corehours', 'uint64'), ('Endtime', 'S256')]
)

# translateDateToSec receives a date and returns the date in unix-time, if it's a valid date,
# (i.e not "Unknown" otherwise returns -1)
# If there is more invalid inputs possible in the log-system, this has to be expanded.
def translateDateToSec(YMDHMS):
    """
    :param YMDHMS: the year-month-day-hour-minute-second data to be translated into unix-time
    :return: the amount of seconds passed since the first of january 1970 00:00 UTC
    """
    x_ = str(YMDHMS, 'utf-8')
    if x_ == 'Unknown':
        return -1
    else:
        temptime = datetime.datetime.strptime(str(YMDHMS, 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        return temptime.timestamp()


# To find out the smallest value in a group, set a variable to a value higher than the highest
#  value in the group and replace the variable's value with every lower value you find within the group
# the same way the maximum value is determined.
PlotArray = (np.zeros((Data.size, 3)))
x = 0
time_accumulator = 0
# Set a start date way in the future
x_start = datetime.datetime.strptime("3000-01-01-01-01-01", "%Y-%m-%d-%H-%M-%S")
x_end = datetime.datetime.strptime("2000-01-01-01-01-01", "%Y-%m-%d-%H-%M-%S")
# Set y max to the estimated total amount of core-hours in a year for the Lichtenberg (for max,min computation)
y_start1 = 1000000000000000000000000000000000
y_end1 = 0
# gathers the Cores used and multiplies with the time to generate Corehours.
for row in Data:
    if translateDateToSec(row[11]) > 0:
        end_t = datetime.datetime.strptime(str(row['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        start_t = datetime.datetime.strptime(str(row['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        x_start = min(end_t, x_start)
        x_end = max(end_t, x_end)
        if (end_t - start_t).seconds < 1:
            continue
        y_start1 = min(y_start1, (row['AllocCPUS'] * (end_t - start_t).seconds))
        y_end1 = max(y_end1, (row['AllocCPUS'] * (end_t - start_t).seconds) / 3600)
        PlotArray[x, 0] = end_t.timestamp()
        PlotArray[x, 1] = (row['AllocCPUS'] * (end_t - start_t).seconds / 3600)
        x = x + 1

# creates a cutoff after the array runs out of values and sorts it.
PlotArray = PlotArray[0:x][:]
PlotArray = np.sort(PlotArray, axis=0)
PlotArray[0, 2] = PlotArray[0][1]
y_start2 = 0
y_end2 = 0

# calculating cumulative Y-values, finding highest value and assigning it to y_end2
for x in range(1, PlotArray.shape[0]):
    PlotArray[x, 2] = PlotArray[x, 1] + PlotArray[x - 1, 2]
    y_end2 = max(y_end2, PlotArray[x, 2])

# reading in testdata
SecondData = np.loadtxt(test, dtype='S256', delimiter='|', skiprows=0, usecols=(1, 14, 26, 27))

# test outputs, clears writingfile, then adds the three datapoints from test data for each row
file = open("writingfile.txt", "w")
file.close()
file = open("writingfile.txt", "a")
z = 0
for row in SecondData:
    file.write(SecondData[z][0].decode('UTF-8') + " " + SecondData[z][2].decode('UTF-8') + " " +
               SecondData[z][1].decode('UTF-8') + "\n")
    z = z + 1
file.close()

# splitting PlotArray into x and y values to easier visualize them.
tmp_x = [(datetime.datetime.fromtimestamp(i)) for i in PlotArray[:, 0]]
tmp_y = PlotArray[:, 2]
tmp_array = PlotArray[:, (0, 2)]

# creates quota-durations, current default value: 6 hours
# suggested 30*24*60*60 for months, imprecise months, assumes 30 day per month
#TODO: adapt instances depending on timerange
instances = 6*60*60

# splits the graph into intervals and creates three values for each instance, to visualise quotas
n_instances = ((x_end.timestamp() - x_start.timestamp()) / instances) + 1
tmp_x2 = np.arange(x_start.timestamp(), x_end.timestamp(), instances)
tmp_x2 = np.repeat(tmp_x2, 3)
tmp_x2 = np.sort(tmp_x2)
tmp_y2 = np.zeros(tmp_x2.shape)
temporary = 0
iter2 = 0

# shifts the second of each triple along the y-axis, and the third along x- and y-axis
for iter in range(0, int(n_instances)):
    for i in range(0, np.size(tmp_x)):
        if tmp_x[i].timestamp() <= tmp_x2[iter*3]:
            temporary = tmp_y[i]
        else:
            break
    tmp_y2[iter * 3] = temporary
    tmp_y2[iter*3+1] = temporary + partialQuota
    tmp_y2[iter*3+2] = temporary + partialQuota
    tmp_x2[iter*3+2] = tmp_x2[iter*3+2] + instances
tmp_x3 = tmp_x

# transforms x2 into a format visualizable via the plotter alongside the main plot
for x2 in range(0,np.size(tmp_x2)):
    tmp_x3[x2] = (datetime.datetime.fromtimestamp(tmp_x2[x2]))
tmp_x3 = tmp_x3[0:int(n_instances)*3:1]

# separates the quotas into four categories


def colorisation (value, comp):
    """
    :param value: The difference between the beginning of the Instance and the end, in Coreseconds
    :param comp: the given Quota,
    :return: A color based on the relationship of the two parameters, red for value >> comp, green
    for value ~~ (roughly equal) comp, blue for comp >> value and orange for value > comp
    """
    if value/comp < 0.7:
        return 'lightblue'
    if value / comp < 1.1:
        return "#008000"
    if value / comp < 1.3:
        return '#ffa500'
    else:
        return '#ff0000'


# plotting the main graph
plt.plot(tmp_x, tmp_y, 'black')
# adds an additional unwanted line along the x-axis

# determines the color via colorisation and then plots three points, stops before the last interval to draw
for e in range(0,int(n_instances-1)):
    col = colorisation(tmp_y2[e*3+3]-tmp_y2[e*3], tmp_y2[e*3+2]-tmp_y2[e*3])
    plt.plot([tmp_x3[e*3], tmp_x3[e*3+1],tmp_x3[e*3+2]], [tmp_y2[e*3], tmp_y2[e*3+1], tmp_y2[e*3+2]], col)

# determines the last interval's color and draws it (uses the highest
# recorded value as the end value of the ongoing timespan)
col = colorisation(np.max(tmp_y)-tmp_y2[-3], tmp_y2[-1] - tmp_y2[-3])
plt.plot([tmp_x3[-3], tmp_x3[-2], tmp_x3[-1]], [tmp_y2[-3], tmp_y2[-2], np.max(tmp_y2[-1])], col)

axis = plt.gca()

# sets the visual borders for the graphs, area of occurring values (main graph) +- 5%
temptimest = x_start.timestamp()
temptimest2 = x_end.timestamp()
axis.set_xlim([datetime.datetime.fromtimestamp(int(temptimest - (temptimest2 - temptimest) / 20)),
               datetime.datetime.fromtimestamp(int(temptimest2 + (temptimest2 - temptimest) / 20))])
axis.set_ylim([y_start2 - (0.05 * y_end2), y_end2 * 1.05])

# creates a grid in the image to aid the viewer in processing the data.
plt.grid(True)

# labels the two axis
plt.ylabel('Corehours')
plt.xlabel('Enddate of Process')
manager = plt.get_current_fig_manager()

# saves the graph as a file under the given name
fig = plt.gcf()
fig.set_size_inches((11, 8.5), forward=False)
fig.savefig(targetFile.Output[0], dpi=500)
