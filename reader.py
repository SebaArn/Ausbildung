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


def fun_log(a, b, p, c):  # Implementation of a logarithmic function.
    # function = a+b*log2(p)
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
parser.add_argument("-f", dest="Focus", type=int, nargs='*')
parameter = parser.parse_args()
# print(parameter)

deviationbar = False   # Determines if the deviation-bar is displayed.

if not(parameter.Start and parameter.End and parameter.Name and parameter.Output):  # Invalid inputs
    sys.stderr.write("needs a source, an output file, a start and an endpoint.")
    sys.exit()
fexists = False
#eval = "Runtime"
try:
    left = parameter.Start[0]
    right = parameter.End[0]
    filename = parameter.Name[0]
    out = parameter.Output[0]
    if parameter.Focus:
        #print(len(parameter.Focus))
        print("focus=",parameter.Focus[0])
        if len(parameter.Focus) > 0:
            focus = parameter.Focus[0]
            fexists = True
    else:
        print("no focus")
        fexists = False

except:
    sys.stderr.write("error reading file, aquiring left and right border")
    sys.exit()
if left < 1:
    print("a left border < 1 make no sense, replacing it with 1.")
    start = 1
else:
    start = left
file_object = open(filename, 'r')
lines = file_object.readlines()
testinput = "0"
measures = []
for i in lines:
    if "metric:" in i:
        eval = i[9:-1]
    if "Mean" in i:
        measures.append(i)
    if "model: " in i:
        testinput = str(i)
testinput = testinput.strip()
# testinput = "model: 0+5*p"
# testinput = "3.94994+0.00166031*(p^0.5)"
# testinput  = "model: 0+1*(p^2)"
# print(testinput)
results = []
a = 0
b = 1
c = 1
mode = 0
reading = testinput.replace("model: ", "")
# polynomial, logarithm, literal
if "log" in reading and not mode:
    a = float(reading.split("+")[0])
    #   print("a", a)
    b = float(reading.split("+")[1].split("*")[0])
    #   print("b", b)
    c = float(reading.split("^")[1].split("(")[0] )
    #   print("c", c)
    mode = 1
if "p^" in reading and not mode:
    a = float(reading.split("+")[0])
    #   print("a", a)
    b = float(reading.split("+")[1].split("*")[0])
    #   print("b", b)
    c = float(reading.split("^")[1].split(")")[0] )
    #   print("c", c)
    mode = 2
if "+" in reading and not mode:
    a = float(reading.split("+")[0])
    #   print("a", a)
    b = float(reading.split("+")[1].split("*")[0])
    #   print("b", b)
    mode = 3
if "p" not in reading and not mode:
    a = float(reading)
    b = 0
    mode = 4
start = 2**int(math.log(start, 2))
end = 2**int(math.ceil(math.log(right, 2)))
if end < start + 1:
    print("end point needs to be higher than starting point, replacing it with the next 2^x")
    end = 2**int(math.log(right, 2)+1)
# modes:
# 0 means none (yet)
# 1 means log
# 2 means potential
# 3 means  poly
# 4 means constant/literal
x = []
if mode == 1:
    for p in np.arange(start, (end+1),0.1):
        results.append(fun_log(a, b, p, c))
        x.append(p)
        #funtodraw = fun_log()
if mode == 2:
    for p in np.arange(start, (end+1),0.1):
        results.append(fun_pot(a, b, p, c))
        x.append(p)
        #funtodraw = fun_pot()
if mode == 3:
    for p in np.arange(start, (end+1),0.1):
        results.append(fun_poly(a, b, p))
        x.append(p)
        #funtodraw = fun_poly()
if mode == 4:
    for p in np.arange(start, (end+1),0.1):
        results.append(a)
        x.append(p)
        #funtodraw = a
plt.plot(x, results, color='grey', alpha=0.7)
xval = []
means = []
for i in range(len(measures)):
    xval.append(float(measures[i].split()[0]))
    means.append(float(measures[i].split()[2]))
axis = plt.gca()
axis.set_xlim(start - 0.05*end, end + 0.05*end )
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
if fexists:
    #print("fexists")
    for i in np.arange(max(int(focus-0.05*(end-start)),int(start)),min(int(focus+0.05*(end-start)), end),0.1):
        # print(i)
        f.append(results[int((i-start)*10)])
        x2.append(i+1)
        #t+=str(i)

# Drawing marker in specified range
plt.plot(x2, f, linewidth=3, color='red', alpha=0.8)
for i in range(len(xval)):
    plt.plot([xval[i]], [means[i]], marker='o', markersize=3, color='#00e5e5', alpha=0.85)
    if deviationbar:
        plt.errorbar(xval[i], means[i], 0.05*(max(results)-results[0]), color='orange', alpha=0.9, capsize=3)


plt.draw()
fig = plt.gcf()
fig.set_size_inches((11, 8.5), forward=False)
fig.savefig(out, dpi=500)
print(means)
print(xval)
print(testinput)
