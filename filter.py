import sys
import numpy as np  # used to handle numbers, data structures and mathematical functions
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import sys
import re


# TODO: Resolve issue with "Unknown" being the highest, resulting in the programm not propperly evaluating if \ startpoint is too late.
#

border = 0.08

def translate_date_to_sec(ymdhms):
    """
    :param ymdhms: the year-month-day-hour-minute-second data (datetime.datetime) to be translated into unix-seconds.
    :return: the amount of seconds passed since the first of january 1970 00:00 UTC, if invalid: "-1".
    """
    x_ = str(ymdhms, 'utf-8')
    if x_ == 'Unknown':
        return -1
    else:
        temp_time = datetime.datetime.strptime(str(ymdhms, 'utf-8'), "%Y-%m-%d-%H-%M-%S")  # convert into datetime
        return temp_time.timestamp()  # then convert into unix-seconds (timestamp)


def essentialpar(parameters):
    print(parameters)
    print(len(parameters))
    if (len(parameters)) < 1:
        sys.stderr.write("needs at least one file (input)")
        sys.exit()
    sourceskey, sourcesnok, optpara = [], [], []
    while parameters:
        if "-src=" == parameters[0][:5]:
            sourceskey.append(parameters[0][5:])
            parameters = parameters[1:]
            #print("src found")
        else:
            if "-" in parameters[0][0:2]:
                optpara.append(parameters[0])
                parameters = parameters[1:]
                #print("other param")
            else:
                sourcesnok.append(parameters[0])
                parameters = parameters[1:]
                #print("probably source found")
    print(sourceskey, sourcesnok, optpara)
    if not (sourceskey or sourcesnok):
        print(sourceskey,sourcesnok)
        sys.stderr.write("needs input file")
        sys.exit()
    sources = sourceskey+sourcesnok
    return [sources, optpara]


def translate_time_to_sec(time):
    seconds = 0
    flagdays = False
    if '-' in time:
        flagdays = True
    time = time.split('.')[0]
    if len(time) < 2:
        return 0
    subsplits = time.split('-')
    seconds = 0
    if flagdays:
        seconds += 24 * 3600 * int(''.join(c for c in subsplits[0] if c.isdigit()))
    timesplitseconds = subsplits[-1].split(':')
    for i in range(len(timesplitseconds)):
        seconds += int(''.join(c for c in (timesplitseconds[-(i + 1)]) if c.isdigit())) * int(math.pow(60, int(i)))
    return seconds


parser = argparse.ArgumentParser()
# Creating different parameters to allow the user to specify, what data is to be evaluated.
parser.add_argument("-src", nargs='*')
#parser.add_argument('--start', dest='StartPoint', default="None", type=str, nargs='?')
parser.add_argument('-p', dest='ProjectName', default="", type=str, nargs='?')
parser.add_argument('-l', dest='LowerLimit', default=0, type=int, nargs='?')
parser.add_argument('-s', dest='StartPoint', default="None", type=str, nargs='?')
parser.add_argument('--start', dest='StartPoint', default="None", type=str, nargs='?')
parser.add_argument('--project', dest='ProjectName', default="", type=str, nargs='?')
parser.add_argument('-max', dest='Maximum', default=0.3, type=float, nargs='?')
parser.add_argument('--Maximum', default=0.3, type=float, nargs='?')
parser.add_argument('-min', dest='Minimum', default=0.0, type=float, nargs='?')
parser.add_argument('--Minimum',  default=0.0, type=float, nargs='?')
parser.add_argument('--separator', dest="Separator",  default="\n", type=str, nargs='?')
parser.add_argument('-sep', dest="Separator",  default="\n", type=str, nargs='?')
parser.add_argument('rest', type=str, nargs='*')
commasep = False

eparameters = essentialpar((sys.argv[1:]))

# Intern variable, saving, whether the results are separated by comma or by newline

parameter = parser.parse_args()
LowerLimit = parameter.LowerLimit

if LowerLimit < 360:
    LowerLimit = 360

if parameter.Separator == ",":
    commasep = True
if not parameter.Minimum:
    mini = 0
else:
    mini = parameter.Minimum
maxi = parameter.Maximum
projectname = parameter.ProjectName
startpoint = parameter.StartPoint
if len(startpoint) == 10:  # appends hours, minutes and seconds if only date given
    startpoint += "-00-00-00"
if len(startpoint)>10:
    startdatetime = datetime.datetime.strptime(startpoint, "%Y-%m-%d-%H-%M-%S").timestamp()
else:
    print("no valid startpoint given, using default")
# print("Parameter:",parameter)
# print("Original:",parameter.original)
originals = eparameters[0]
data_type = np.dtype(
    [('JobID', '|S256'),('Account', '|S256'), ('ReqCPUS', 'i4'), ('ReqMem', '|S256'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'),
     ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'), ('ElapsedRaw', 'uint64'), ('Start', '|S256'),
     ('End', '|S256'),('TotalCPU', '|S256'),('UserCPU', '|S256'),('SystemCPU', '|S256')])

Data = np.loadtxt(originals[0], dtype=data_type, delimiter='|', skiprows=0, usecols=(0, 1, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15)
                  )
datatemp2 = []
counter = 0

if projectname:
    filter_ = projectname
else:
    filter_ =""


for j in Data:
    #print(str(j['End']),str(j['JobID']),str(j['Account']))
    #print('Unknown','.',filter_ )
    if 'Unknown' not in str(j['End']) and '.' not in str(j['JobID']) and filter_ in str(j['Account']):
        datatemp2.append(j)
        break
init = 0

Data = datatemp2

for i in range(0,len(originals)):
    Datatemp = np.loadtxt(originals[i], dtype=data_type, delimiter='|', skiprows=0, usecols=(0, 1, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15))
    datatemp2 =[]
    for j in Datatemp:
        if 'Unknown' not in str(j['End']) and '.' not in str(j['JobID']) and filter_ in str(j['Account']) and Data[i]["ElapsedRaw"] > LowerLimit:
            datatemp2.append(j)
    if datatemp2:
        if len(Data) > 0:
            if init:
                Data = np.append(Data,datatemp2)
            else:
                Data = np.append(Data[0], datatemp2)
                Data = Data[1:]
                init = 1
        else:
            Data = datatemp2

print(np.shape(Data))

Datatemp2 = []
Data = Data[(Data[::]['End']).argsort()]

if len(Data) < 1:
    sys.stderr.write("No data in file.")
    sys.exit()
firstdata = min(Data[::]['End'])
firstdata = str(firstdata)
firstdata = firstdata[2:-1]


if len(startpoint) < 11:
    startpoint = firstdata
    startdatetime = datetime.datetime.strptime(startpoint, "%Y-%m-%d-%H-%M-%S").timestamp()
    print("invalid startdatetime, using first occurrence.")

highestdata = max(Data[::]['End'])
highestdata = str(highestdata)
highestdata = highestdata[2:-1]
if highestdata < startpoint:
    sys.stderr.write('The startpoint is after the latest date in the file')
    sys.exit()

sp = 0

#print(startpoint)
#for i in range(len(Data)):
#    x = str(Data[i]["End"])[2:-1:]
#    #print(x)
#    if x != "Unknown":
#        if datetime.datetime.strptime(x, "%Y-%m-%d-%H-%M-%S").timestamp() >= startdatetime:
#            sp = i
#            continue
#            #


joblist = []
textlist = []

for i in range(len(Data)):
    if translate_date_to_sec(Data[i]['End']) > 0 and '.' not in str(Data[i]['JobID']) and filter_ in str(Data[i]['Account'])and str(Data[i]['End'])[2:-1] >= startpoint and Data[i]["ElapsedRaw"] > LowerLimit:
        #start_t = datetime.datetime.strptime(str(Data[i]['Start'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        #end_t = datetime.datetime.strptime(str(Data[i]['End'], 'utf-8'), "%Y-%m-%d-%H-%M-%S")
        if Data[i]["ElapsedRaw"] < 1:
            continue
        formated = Data[i]['TotalCPU']
        #print("totalCPU:",formated)
        formated = str(formated)[2:]
        #print("seconds:",translate_time_to_sec(formated))
        efficiency = translate_time_to_sec(formated) / (Data[i]['AllocCPUS']*Data[i]["ElapsedRaw"])
        if efficiency <= maxi and efficiency >= mini:
            id = str(Data[i]['JobID'])
            id = id[2:-1:]
            joblist.append(id)
            acc = str(Data[i]['Account'])
            acc = acc[2:-1:]
            if efficiency <= 0.01:
                print(Data[i])
            s = "Job nr. " + str(id).ljust(8) + " (account = " + acc + ") has the efficiency " + str(int(abs(efficiency*1000))/10).ljust(5)+"%."\
                + " Runtime in hours:"+str((Data[i]['ElapsedRaw']//360)/10).ljust(6)+" number of CPUs:"+str(Data[i]['NCPUS']).ljust(4)+' number of nodes:'\
                +str(Data[i]['NNodes']).ljust(4)+". Memory:"+(str(Data[i]['ReqMem'])[2:-1]).ljust(9)+". Corehours:"+str(int(Data[i]['CPUTimeRAW']//360)/10)
            textlist.append(s)

if len(textlist) == 0:
    sys.stderr.write("No data fitting the projectname within the specified borders within the specified time")
    sys.exit()


if commasep:
    print(textlist)
else:
    print("\n".join(textlist))

