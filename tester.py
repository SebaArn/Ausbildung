#  import numpy as np  # used to handle numbers, data structures and mathematical functions
#  import matplotlib.pyplot as plt  # MATLAB-like plotting
#  from matplotlib.collections import PatchCollection
#  from matplotlib.patches import Rectangle
#  import datetime  # Used to convert our ascii dates into unix-seconds
#  import argparse  # used to interpret parameters
#  import math
#  import sys
#  import matplotlib.patches as mpatches
#  import re
import os
#  import reader

current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'testing_folder')
if not os.path.exists(final_directory):
    os.makedirs(final_directory)

Models = []
Models.append(["0.01+1*p^1.4*log2^1(p)", "metric: time"])
Models.append(["0+1*p^2+1*log2^4(p)", "metric: efficiency"])
Models.append(["0+9.99998e-07*(p^2)", "metric: ner"])
Models.append(["5+-1*log2^2(p)", "metric: tarot"])
Models.append(["0+1*(p^2)", "metric: Speed"])
Models.append(["53.6+-14.4*log2^1(p)", "metric: Evaluation"])
Models.append(["0+1*log2^2(p)", "metric: den"])
Models.append(["10+-1*log2^3(p)", "metric: ter vom Berg"])
Models.append(["53.6+-14.4*log2^1(p)", "metric: enstein"])
Models.append(["0+1*log2^2(p)", "metric: npelstilzchen"])
Models.append(["0+8*log2^5(p)", "metric: np"])
Models.append(["10+1*p", "metric: efficiency"])
Models.append(["10+-1*log2^3(p)", "metric: effizienz"])
Models.append(["15", "metric: zeit"])
Models.append(["10+1*log2^-1(p)", "metric: Verhalten"])
Models.append(["0+8*log2^5(p)", "metric: time"])
Models.append(["0+1*(p^2)+1*log2^1(p)", "metric: time"])
Models.append(["10+-1*log2^3(p)", "metric: time"])
Models.append(["0.5+-1*log2^3(p)+0.25*(p^4)", "metric: nuR"])
Models.append(["1+2+3", "metric: metric"])
Models.append(["-1+-1*(p^-1)+-1*log2^-3(p)", "metric: Vergnügen"])

file_number = len(Models)
for i in range(file_number):
    path_file = os.path.join(final_directory, 'test'+str(i+1)+'.txt')
    with open(path_file, 'w') as a:
        a.write("Model: "+Models[i][0]+"\n")
        a.write(Models[i][1]+"\n")


# creating array of parameters to be executed

c = []
for i in range(file_number):
    l = []
    l.append("test"+str(i+1)+".txt")
    l.append("o"+str(i+1)+".png")
    l.append(str(i+1))
    l.append(str((i+1)*10))
    c.append(l)
print(c)

#  executing each set of parameters.

commands = []
for i in range(file_number):
    command = os.path.join(current_directory, "reader.py")
    command = "python " + command
    command += " -name=" + os.path.join(final_directory, c[i][0])
    command += " -o=" + os.path.join(final_directory, c[i][1])
    command += " -start=" + c[i][2]
    command += " -end=" + c[i][3]
    commands.append(command)

for i in range(file_number):
    os.system(commands[i])

# TODO: Try except blocks for each command, properly throwing errors in reader.py
# TODO: Catch excepts where an error should have been thrown, increment fails and successes.

#  Creation of Files to delete
remove_sources = []
remove_outputs = []
for i in range(file_number):
    command_src = os.path.join(final_directory, "test" + str(i + 1) + ".txt")
    command_out = os.path.join(final_directory, "o" + str(i + 1) + ".png")
    remove_outputs.append(command_out)
    remove_sources.append(command_src)
#  Removal of files
for i in range(file_number - 1, -1, -1):
    try:
        m = 0
        #  os.remove(remove_sources[i])
    except Exception:
        print()
    try:
        m = 0
        #  os.remove(remove_outputs[i])
    except Exception:
        print()



