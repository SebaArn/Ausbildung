import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib.pyplot as plt  # MATLAB-like plotting
#  from matplotlib.collections import PatchCollection
#  from matplotlib.patches import Rectangle
#  import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import sys
import matplotlib.patches as mpatches
#  import re

#  allow negative potencies? Will there be negative logarithms?
def log2(x_, y_):  # logarithm to the base of 2^x
    return math.log(x_, 2**y_)


def general_function(c_, i_, j_, p_):
    if j_ == 0:
        return c_ * p_**i_
    return c_ * p_**i_ * log2(p_, j_)


parser = argparse.ArgumentParser()
# Creating different parameters to allow the user to specify, what data is to be evaluated, what to do with the result.
parser.add_argument('-name', dest='Name', default="", type=str, nargs=1)
parser.add_argument('-o', dest='Output', default="", type=str, nargs=1)
parser.add_argument("-start", dest="Start", type=int, default=4, nargs=1)
parser.add_argument("-end", dest="End", default=64, type=int, nargs=1)
parser.add_argument("-f", dest="Focus", type=float, nargs='*')
parser.add_argument("-help", dest="Help", type=bool, nargs='*')
parameter = parser.parse_args()
deviation_bar = False   # Determines if the deviation-bar is displayed.

if not(parameter.Start and parameter.End and parameter.Name and parameter.Output):  # Invalid inputs
    sys.stderr.write("needs a source, an output file, a start and an endpoint.")
    sys.exit()
focus_exists = False
if parameter.Help is not None:
    s = "This Program receives a source file's name, an output path and na,e, as well as a start and an end value, \
    these parameters can be given by running the program with -name=_Name_ -o=_pathname_ start=_start_ -end=_end_"
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
            focus_exists = True
except Exception:
    sys.stderr.write("error reading filename, acquiring start- and end point")
    sys.exit()
if left < 1:
    print("a start point < 1 make no sense, replacing it with 1.")
    start = 1
else:
    start = left
start = 2**int(math.log(start, 2))
end = 2**int(math.ceil(math.log(right, 2)))
if end < start + 1:
    print("end point needs to be greater than starting point, replacing it with the next 2^N")
    end = 2**int(math.ceil(math.log(left+1, 2)))
interval = (end - start)/800
try:
    file_object = open(filename, 'r')
except Exception:
    sys.exit("Error regarding "+filename+" No right to read or file doesn't exist.")
lines = file_object.readlines()
measures = []
read_line = ""
units = ""
for i in lines:
    if "metric:" in i:
        units = i[8:-1]
    else:
        units = 0
    if "Mean" in i:
        measures.append(i)
    if "model: " in i.lower():
        read_line = str(i).lower()
work_line = read_line.strip()
reading = work_line.replace("model: ", "")
addend = reading.split('+')
print(addend)
x = []
results = []
c_list = []
i_list = []
j_list = []
for d in range(len(addend)):  # reads each addend-term
    i = 0
    j = 0
    if len(addend[d].split('*')) == 1:
        c = float(addend[d])
    else:
        for z in range(len(addend[d].split('*'))):  # reads each factor-term
            factor_term_part = addend[d].split('*')[z]
            if factor_term_part == factor_term_part.replace('p', ""):
                c = float(factor_term_part)
            elif 'log2^' in factor_term_part:
                j = float(factor_term_part.split('log2^')[1].split('(p)')[0])
            elif "p^" in factor_term_part:
                i = float(factor_term_part.split('p^')[1].split(')')[0])
    c_list.append(c)
    i_list.append(i)
    j_list.append(j)

for p in np.arange(start, (end+1), interval):
    y = 0
    for d in range(len(addend)):
        y += general_function(c_list[d], i_list[d], j_list[d], p)
    results.append(y)
    x.append(p)
plt.plot(x, results, color='grey', alpha=0.7)
x_values = []
means = []

for i in range(len(measures)):
    x_values.append(float(measures[i].split()[0]))
    means.append(float(measures[i].split()[2]))
axis = plt.gca()
axis.set_xlim(start - 0.05*end, end + 0.05*end)
axis.set_ylim(0, max(results)*1.05)
plt.grid(True)
print("given range:", left, "<->", right)
print("used range:", start, "<->", end)
# Labeling the Axis
if len(units) > 0:
    plt.ylabel("run" + units.lower() + " of computation")
else:
    plt.ylabel("run of computation")
plt.xlabel('# of cores the program runs on')
# establishing legends
if len(units) > 0:
    grey_patch = mpatches.Patch(color='grey', alpha=0.7, label='Run' + units[0].lower() + units[1::] +
                                                               ' of computation with given cores (' + reading + ")")
else:
    grey_patch = mpatches.Patch(color='grey', alpha=0.7, label='Run of computation with given cores (' + reading + ')')
teal_patch = mpatches.Patch(color='#00e5e5', alpha=0.97, label='Measurements (mean)')
plt.legend(handles=[grey_patch, teal_patch])
manager = plt.get_current_fig_manager()
# f: y-axis values
f = []
# x2: X-axis values within the specified range
x2 = []
# Copying values for specified range
if focus_exists:
    for i in np.arange(max(focus-0.05*(end-start), start), min(focus+0.050*(end-start), end)+interval, interval):
        f.append(results[int((i-start)*(1/interval))])
        x2.append(x[int((i-start)*(1/interval))])

# Drawing marker in specified range
plt.plot(x2, f, linewidth=3, color='red', alpha=0.75)
for i in range(len(x_values)):
    plt.plot([x_values[i]], [means[i]], marker='o', markersize=2, color='#00e5e5', alpha=0.85)
    if deviation_bar:
        plt.errorbar(x_values[i], means[i], 0.05 * (max(results) - results[0]), color='orange', alpha=0.9, capsize=3)

plt.draw()
fig = plt.gcf()
# Saving the image to a file in given name.
fig.set_size_inches((11, 8.5), forward=False)
fig.savefig(out, dpi=500)
