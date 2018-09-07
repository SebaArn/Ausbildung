# import numpy as np  # used to handle numbers, data structures and mathematical functions
import matplotlib.pyplot as plt  # MATLAB-like plotting
# from matplotlib.collections import PatchCollection
# from matplotlib.patches import Rectangle
# import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import sys
#import os
# import matplotlib.patches as mpatches
# import re


def log2(x, y):
    return math.log(x, int(2**y))


parser = argparse.ArgumentParser()
# Creating different parameters to allow the user to specify, what data is to be evaluated.
parser.add_argument('-name', dest='Name', default="", type=str, nargs=1)
parser.add_argument('-o', dest='Output', default="", type=str, nargs=1)
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
    out = parameter.Output[0]
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
newpath = r'C:\thisshouldntexist'
#os.makedirs("thisshouldnotexist")
testinput = "os.makedirs(newpath)"
print(testinput)


a = []
conv = testinput.replace("model: ", "")
conv = "a.append("+conv+")"
conv = conv.replace("log2^", "log2(p,")
conv = conv.replace("(p))", "))")
conv = conv.replace("^", "**")  # important to do this after log2^ has been replaced
start = 2**int(math.log(left, 2))
end = 2**int(math.log(right, 2))


if end < start + 2:
    print("end point needs to be higher than starting point, replacing it with +2")
    end = start + 2


for p in range(start, end):
    exec(conv)

plt.plot(a)
plt.grid(True)
print(conv[9:-1])
# print(a)
print(left, right)
print(start, end)
plt.draw()
plt.show()
