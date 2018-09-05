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
import os
#import reader



#  TODO: Create temporary files
#  Execute the reader on these files
#  check which errors occur, if these errors are the expected errors
#  delete both the temporary source files, as well as the generated files

# TODO: Fully creating entire textfiles rather than only reading them?
current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'testing_folder')
if not os.path.exists(final_directory):
    os.makedirs(final_directory)


Models = []
Models.append("0.01+1*p^1.4*log2^1(p)")
Models.append("log(log(10))+p^10+p^11")
Models.append("0+9.99998e-07*(p^2)")
Models.append("5+-1*log2^2(p)")
Models.append("0+1*(p^2)")
Models.append("53.6+-14.4*log2^1(p)")
Models.append("0+1*log2^2(p)")
Models.append("10+-1*log2^3(p)")
Models.append("53.6+-14.4*log2^1(p)")
Models.append("0+1*log2^2(p)")
Models.append("0+8*log2^5(p)")
Models.append("10+1*p")
Models.append("10+-1*log2^3(p)")
Models.append("15")
Models.append("0+5*p")
Models.append("0+8*log2^5(p)")
Models.append("10+1*p")
Models.append("10+-1*log2^3(p)")
Models.append("15")
Models.append("0+5*p")


#TODO: create testing files

filenum = len(Models)
for i in range(filenum):
    path_file = os.path.join(final_directory, 'test'+str(i+1)+'.txt')
    with open(path_file, 'w') as a:
        a.write("Model: "+Models[i])




#  creating array of parameters to be executed

c = []
for i in range(filenum):
    l = []
    l.append("test"+str(i+1)+".txt")
    l.append("o"+str(i+1)+".png")
    l.append(str(i+1))
    l.append(str((i+1)*10))
    c.append(l)
print(c)


#  executing each set of parameters.

commands = []
for i in range(filenum):
    command = os.path.join(current_directory, "reader.py")
    command = "python " + command
    command += " -name=" + os.path.join(final_directory, c[i][0])
    command += " -o=" + os.path.join(final_directory, c[i][1])
    command += " -start=" + c[i][2]
    command += " -end=" + c[i][3]
    commands.append(command)

#print(command)
#eingabe = input("Ihre Eingabe")
for i in range(filenum):
    os.system(commands[i])

#try:
#    os.system(commands[1])
#except:
#    print()
#os.system(commands[2])
#os.system(commands[3])
#os.system(commands[3])
#os.system(commands[3])

# TODO: Try except blocks for each command, propperly throwing errors in reader.py
#  TODO: Catch excepts where an error should have been thrown, increment fails and successes.


#  Creation of Files to delete
removesources = []
removeoutputs = []
for i in range(filenum):
    commandsrc = os.path.join(final_directory, "test"+str(i+1)+".txt")
    commandout = os.path.join(final_directory, "o"+str(i+1)+".png")
    removeoutputs.append(commandout)
    removesources.append(commandsrc)

#  Removal of files
for i in range(filenum-1, -1, -1):
    try:
        m = 0
        os.remove(removesources[i])
    except:
        print()
    try:
        m = 0
        #os.remove(removeoutputs[i])
    except:
        print()



