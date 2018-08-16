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


def fun_log(a, b, p, c):
    # function = a+b*log2(p)
    return a + b * log2(p, c)


def fun_poly(a, b, p):
    return a+b*p


def fun_pot(a, b, p, c):
    return a + b* p**c


def log2(x, y):
    return math.log(x, int(2**y))


parser = argparse.ArgumentParser()
# Creating different parameters to allow the user to specify, what data is to be evaluated.
parser.add_argument('-name', dest='Name', default="", type=str, nargs=1)
parser.add_argument("-start", dest="Start", type=int, default=4, nargs=1)
parser.add_argument("-end", dest="End", default=64, type=int, nargs=1)
parameter = parser.parse_args()
print(parameter)
if not(parameter.Start and parameter.End and parameter.Name):
    sys.stderr.write("needs three parameters")
    sys.exit()
try:
    left = parameter.Start[0]
    right = parameter.End[0]
    filename = parameter.Name[0]
except:
    sys.stderr.write("error reading file, aquiring left and right border")
    sys.exit()
if left < 4:
    print("a left border < 4 make no sense, replacing it with 4.")
    left = 4
file_object = open(filename, 'r')
lines = file_object.readlines()
testinput = "0"
for i in lines:
    if "model: " in i:
        testinput = str(i)
testinput = testinput.strip()
# newpath = r'C:\thisshouldntexist'
# os.makedirs("thisshouldnotexist")
# testinput = "model: 0+5*p"
# testinput = "3.94994+0.00166031*(p^0.5)"
# testinput  = "model: 0+9.99998e-07*(p^2)"
print(testinput)
print(testinput)
results = []
a = 0
b = 1
c = 1
mode = 0
reading = testinput.replace("model: ", "")
# polynomial, logarithm, literal
if "log" in reading and not mode:
    a = float(reading.split("+")[0])
    print("a", a)
    b = float(reading.split("+")[1].split("*")[0])
    print("b", b)
    print(reading.split("^")[1])
    c = float(reading.split("^")[1].split("(")[0] )
    print("c", c)
    mode = 1
if "p^" in reading and not mode:
    a = float(reading.split("+")[0])
    print("a", a)
    b = float(reading.split("+")[1].split("*")[0])
    print("b", b)
    c = float(reading.split("^")[1].split(")")[0] )
    print("c", c)
    mode = 2
if "+" in reading and not mode:
    a = float(reading.split("+")[0])
    print("a", a)
    b = float(reading.split("+")[1].split("*")[0])
    print("b", b)
    # c = 2**math.log(b,2)
    mode = 3
if "p" not in reading and not mode:
    a = float(reading)
    b = 0
    mode = 4
start = 2**int(math.log(left, 2))
end = 2**int(math.log(right, 2))
if end < start + 2:
    print("end point needs to be higher than starting point, replacing it with +2")
    end = start + 2
# modes:
# 0 means log and poly
# 1 means only poly
# 2 means constant/literal
if mode == 1:
    for p in range(start, end):
        results.append(fun_log(a, b, p, c))
if mode == 2:
    for p in range(start, end):
        results.append(fun_pot(a, b, p, c))
if mode == 3:
    for p in range(start, end):
        results.append(fun_poly(a, b, p))
if mode == 4:
    for p in range(start, end):
        results.append(a)
plt.plot(results)
plt.grid(True)
# print(conv[9:-1])
# print(a)
print("given range:",left, right)
print("used range:",start, end)
plt.draw()
plt.show()
