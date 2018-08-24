import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib.pyplot as plt  # MATLAB-like plotting
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import sys
import matplotlib.patches as mpatches
import re

## TODO: Create a function that allows log and pot


def fun_log_pot(a,b, c, d, p):
    return a + b * p**c * log2(p, d)


def fun_log(a, b, p, c):  # Implementation of a logarithmic function.
    return a + b * log2(p, c)


def fun_poly(a, b, p):  # Implementation of a polynomial function.
    return a+b*p


def fun_pot(a, b, p, c):  # Implementation of a potential function.
    return a + b* p**c


def log2(x, y):  # logarithm to the base of 2^x
    return math.log(x, int(2**y))


parser = argparse.ArgumentParser()
# Creating different parameters to allow the user to specify, what data is to be evaluated.
parser.add_argument('-name', dest='Name', default="", type=str, nargs=1)
parser.add_argument('-o', dest='Output', default="", type=str, nargs=1)
parser.add_argument("-start", dest="Start", type=int, default=4, nargs=1)
parser.add_argument("-end", dest="End", default=64, type=int, nargs=1)
parser.add_argument("-f", dest="Focus", type=float, nargs='*')
parser.add_argument("-help", dest="Help", type=bool, nargs='*')
parameter = parser.parse_args()
deviationbar = False   # Determines if the deviation-bar is displayed.

if not(parameter.Start and parameter.End and parameter.Name and parameter.Output):  # Invalid inputs
    sys.stderr.write("needs a source, an output file, a start and an endpoint.")
    sys.exit()
f_exists = False
if parameter.Help is not None:
    s = "This Program receives a source file's name, an output path and na,e, as well as a start and an end value, "
    s += "these parameters can be given by running the program with -name=_Name_ -o=_pathname_ start=_start_ -end=_end_"
    print(s)
    sys.exit()
try:
    left = parameter.Start[0]
    right = parameter.End[0]
    filename = parameter.Name[0]
    out = parameter.Output[0]
    if parameter.Focus:
        print("focus=", parameter.Focus[0])
        if len(parameter.Focus) > 0:
            focus = parameter.Focus[0]
            f_exists = True
    else:
        print("no focus")
        f_exists = False
except:
    sys.stderr.write("error reading filename, acquiring left and right border")
    sys.exit()
if left < 1:
    print("a start point < 1 make no sense, replacing it with 1.")
    start = 1
else:
    start = left
start = 2**int(math.log(start, 2))
end = 2**int(math.ceil(math.log(right, 2)))
print("________",end, start,)
if end < start + 1:
    print("end point needs to be greater than starting point, replacing it with the next 2^N")
    end = 2**int(math.ceil(math.log(left+1, 2)))
print("________",end, start)

interval = (end - start)/8000
#interval = 0.1

try:
    file_object = open(filename, 'r')
except:
    sys.exit("Error regarding "+filename+" No right to read or file doesn't exist.")
lines = file_object.readlines()
measures = []
for i in lines:
    if "metric:" in i:
        eval = i[9:-1]
    if "Mean" in i:
        measures.append(i)
    if "model: " in i.lower():
        readline = str(i).lower()
workline = readline.strip()
results = []
a = 0
b = 1
c = 1
mode = 0
reading = workline.replace("model: ", "")
# polynomial, logarithm, literal

print(reading)
if "log" in reading and "p^" in reading:
    if len(reading.split("log")) > 2:
        multiple = "logs"
        sys.exit("Program not currently providing results for multiple logarithms")
    if len(reading.split("p^")) > 2:
        multiple = "potencies"
        sys.exit("Program not currently providing results for multiple potencies")
    # return a + b * p**c * log2(p,d)
    print(reading)
    a = float(reading.split("+")[0])
    b = float(reading.split("+")[1].split("*")[0])
    c = float(reading.split("p^")[1].split("*")[0])
    d = float(reading.split("^")[-1].split("(")[0])
    mode = 1
if "log" in reading and not mode:
    if len(reading.split("log")) > 2:
        multiple = "logs"
        sys.exit("Program not currently providing results for multiple logarithms")
        #sys.exit()
    a = float(reading.split("+")[0])
    b = float(reading.split("+")[1].split("*")[0])
    c = float(reading.split("^")[1].split("(")[0])
    mode = 2
    print("mode found 2")
if "p^" in reading and not mode:
    if len(reading.split("p^")) > 2:
        multiple = "potencies"
        sys.exit("Program not currently providing results for multiple potencies")
    a = float(reading.split("+")[0])
    b = float(reading.split("+")[1].split("*")[0])
    c = float(reading.split("^")[1].split(")")[0])
    mode = 3
    print("mode found 3")
if "+" in reading and not mode:
    if len(reading.split("+")) > 2:
        multiple = "additions"
        sys.exit("Program not currently providing results for multiple additions")
    a = float(reading.split("+")[0])
    b = float(reading.split("+")[1].split("*")[0])
    mode = 4
    print("mode found 4")
if "p" not in reading and not mode:
    a = float(reading)
    b = 0
    mode = 5
    print("mode found 5")
if mode == 0:
    sys.exit("no valid term found.")
#except:
#    sys.stderr("Program does not currently work for multiple "+multiple)
#    sys.exit
# mode: determines, which type of function is to be called
# 0 means none (yet)
# 1 means log
# 2 means potential
# 3 means  poly
# 4 means constant/literal

# creating y-values with a function depending on which mode was selected.
# TODO: Rather than creating 10 values for every number between start and end, creating a set number of values based on
# TODO: the width of the to be created image.

x = []
print("mode", mode)
if mode == 1:
    for p in np.arange(start, (end+1), interval):
        results.append(fun_log_pot(a, b, c, d, p))
        x.append(p)
if mode == 2:
    for p in np.arange(start, (end+1), interval):
        results.append(fun_log(a, b, p, c))
        x.append(p)
if mode == 3:
    for p in np.arange(start, (end+1), interval):
        results.append(fun_pot(a, b, p, c))
        x.append(p)
if mode == 4:
    for p in np.arange(start, (end+1), interval):
        results.append(fun_poly(a, b, p))
        x.append(p)
if mode == 5:
    for p in np.arange(start, (end+1), interval):
        results.append(a)
        x.append(p)
plt.plot(x, results, color='grey', alpha=0.7)
xval = []
means = []
for i in range(len(measures)):
    xval.append(float(measures[i].split()[0]))
    means.append(float(measures[i].split()[2]))

print(len(results))
axis = plt.gca()
axis.set_xlim(start - 0.05*end, end + 0.05*end)
axis.set_ylim(0, max(results)*1.05)
plt.grid(True)
print("given range:", left, "<->", right)
print("used range:", start, "<->", end)

# Labeling the Axis and creating Legend
plt.ylabel("run"+eval.lower()+" of computation")
plt.xlabel('# of cores the program runs on')
grey_patch = mpatches.Patch(color='grey', alpha=0.7, label='Run'+eval.lower()+' of computation with given cores')
teal_patch = mpatches.Patch(color='#00e5e5', alpha=0.97, label='Measurements (mean)')
plt.legend(handles=[grey_patch, teal_patch])
manager = plt.get_current_fig_manager()

# f: y-axis values
f = []

# x2: X-axis values within the specified range
x2 = []

# Copying values for specified range
if f_exists:
    for i in np.arange(max(focus-0.05*(end-start), start), min(focus+0.050*(end-start), end)+interval, interval):
        #print(i)
        f.append(results[int((i-start)*(1/interval))])
        x2.append(x[int((i-start)*(1/interval))])

#if f_exists:
#    i = max(focus-0.05*(end-start),)
#    while

# Drawing marker in specified range
plt.plot(x2, f, linewidth=3, color='red', alpha=0.75)
for i in range(len(xval)):
    plt.plot([xval[i]], [means[i]], marker='o', markersize=2, color='#00e5e5', alpha=0.85)
    if deviationbar:
        plt.errorbar(xval[i], means[i], 0.05*(max(results)-results[0]), color='orange', alpha=0.9, capsize=3)

plt.draw()
fig = plt.gcf()
# Saving the image to a file in given name.
fig.set_size_inches((11, 8.5), forward=False)
fig.savefig(out, dpi=500)
