#  import sys
import numpy as np  # used to handle numbers, data structures and mathematical functions
import datetime  # Used to convert our ascii dates into unix-seconds
import argparse  # used to interpret parameters
import math
import sys
#  import re
import os


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


def essential_par(parameters):
    if (len(parameters)) < 1:
        sys.stderr.write("needs at least one file (input)")
        sys.exit()
    sources_key, sources_nok, opt_para = [], [], []
    while parameters:
        if "-src=" == parameters[0][:5]:
            sources_key.append(parameters[0][5:])
            parameters = parameters[1:]
        else:
            if "-" in parameters[0][0:2]:
                opt_para.append(parameters[0])
                parameters = parameters[1:]
            else:
                sources_nok.append(parameters[0])
                parameters = parameters[1:]
    if not (sources_key or sources_nok):
        sys.stderr.write("needs input file")
        sys.exit()
    sources = sources_key+sources_nok
    return [sources, opt_para]


def translate_time_to_sec(time):
    flag_days = False
    if '-' in time:
        flag_days = True
    time = time.split('.')[0]
    if len(time) < 2:
        return 0
    sub_splits = time.split('-')
    seconds = 0
    if flag_days:
        seconds += 24 * 3600 * int(''.join(c for c in sub_splits[0] if c.isdigit()))
    time_split_seconds = sub_splits[-1].split(':')
    for i_ in range(len(time_split_seconds)):
        seconds += int(''.join(c for c in (time_split_seconds[-(i_ + 1)]) if c.isdigit())) * int(math.pow(60, int(i_)))
    return seconds


parser = argparse.ArgumentParser()
# Creating different parameters to allow the user to specify, what data is to be evaluated.
parser.add_argument("-src", nargs='*')
parser.add_argument('-p', dest='ProjectName', default="", type=str, nargs='?')
parser.add_argument('-l', dest='LowerLimit', default=360, type=int, nargs='?')
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
comma_sep = False

e_parameters = essential_par((sys.argv[1:]))

parameter = parser.parse_args()
LowerLimit = parameter.LowerLimit

if LowerLimit < 60:
    LowerLimit = 60

#  TODO: change csv semicolon separated file to default, make print case the special parameterized case instead.
if ";" in parameter.Separator:
    comma_sep = True
if not parameter.Minimum:
    mini = 0
else:
    mini = parameter.Minimum
maxi = parameter.Maximum
project_name = parameter.ProjectName
start_point = parameter.StartPoint
if len(start_point) == 10:  # appends hours, minutes and seconds if only date given
    start_point += "-00-00-00"
if len(start_point) > 10:
    start_datetime = datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S").timestamp()
else:
    if not comma_sep:
        print("no valid start_point given, using default")
originals = e_parameters[0]
originals = sorted(originals)
data_type = np.dtype(
    [('JobID', '|S256'), ('Account', '|S256'), ('ReqCPUS', 'i4'), ('ReqMem', '|S256'), ('ReqNodes', 'i4'),
     ('AllocNodes', 'i4'), ('AllocCPUS', 'i4'), ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint64'),
     ('ElapsedRaw', 'uint64'), ('Start', '|S256'), ('End', '|S256'), ('TotalCPU', '|S256'), ('UserCPU', '|S256'),
     ('SystemCPU', '|S256')])

Data = np.loadtxt(originals[0], dtype=data_type, delimiter='|', skiprows=0,
                  usecols=(0, 1, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15))
data_temp2 = []
counter = 0
if project_name:
    filter_ = project_name
else:
    filter_ = ""

for j in Data:
    if 'Unknown' not in str(j['End']) and '.' not in str(j['JobID']) and filter_ in str(j['Account']):
        data_temp2.append(j)
        break
init = 0

for i in range(1, len(originals)):
    Data_temp = np.loadtxt(originals[i], dtype=data_type, delimiter='|',
                           skiprows=0, usecols=(0, 1, 3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27, 14, 16, 15))
    data_temp2 = []
    for j in Data_temp:
        if 'Unknown' not in str(j['End']) and '.' not in str(j['JobID']) and filter_ in str(j['Account']) and \
                Data[i]["ElapsedRaw"] > LowerLimit:
            data_temp2.append(j)
    if data_temp2:
        if len(Data) > 0:
            if init:
                Data = np.append(Data, data_temp2)
            else:
                Data = np.append(Data[0], data_temp2)
                Data = Data[1:]
                init = 1
        else:
            Data = data_temp2

Data_temp_2 = []
Data = Data[(Data[::]['End']).argsort()]
if len(Data) < 1:
    sys.stderr.write("No data in file.")
    sys.exit()
first_data = min(Data[::]['End'])
first_data = str(first_data)
first_data = first_data[2:-1]
if len(start_point) < 11:
    start_point = first_data
    start_datetime = datetime.datetime.strptime(start_point, "%Y-%m-%d-%H-%M-%S").timestamp()
    if not comma_sep:
        print("invalid start_datetime, using first occurrence.")

highest_data = max(Data[::]['End'])
highest_data = str(highest_data)
highest_data = highest_data[2:-1]
if highest_data < start_point:
    sys.stderr.write('The start_point is after the latest date in the file')
    sys.exit()
sp = 0
job_list = []
text_list = []
table_list = [";".join(["Job nr.", "Account (project name)", "efficiency (%)", "totalCPU (hours)",
                        'ElapsedRaw (Seconds)', "number of CPUs:", 'number of nodes:', "Memory", " Mn/Mc:",
                        "Corehours", "Parameter: efficiency >= " + str(mini*100) + "% and efficiency <= " +
                        str(maxi*100) + "%.", "Runtime >= " + str((LowerLimit//6)/10) + " minutes"])]
text_list.append("Parameter: efficiency >= " + str(mini * 100) + "% and efficiency >= " + str(maxi * 100) + "%.")
text_list.append("Runtime >= " + str((LowerLimit / 6) // 10) + " minutes")
for i in range(len(Data)):
    if translate_date_to_sec(Data[i]['End']) > 0 and '.' not in str(Data[i]['JobID']) and filter_ in \
            str(Data[i]['Account'])and str(Data[i]['End'])[2:-1] >= start_point and Data[i]["ElapsedRaw"] > LowerLimit:
        if Data[i]["ElapsedRaw"] < 1:
            continue
        formated = Data[i]['TotalCPU']
        formated = str(formated)[2:]
        efficiency = translate_time_to_sec(formated) / (Data[i]['AllocCPUS']*Data[i]["ElapsedRaw"])
        if mini <= efficiency <= maxi:
            id_ = str(Data[i]['JobID'])
            id_ = id_[2:-1:]
            job_list.append(id_)
            acc = str(Data[i]['Account'])
            acc = acc[2:-1:]
            seq_of_data = [str(id_), str(acc), str(int(abs(efficiency * 100000)) / 1000),
                           str((translate_time_to_sec(formated) // 36) / 100), str((Data[i]['ElapsedRaw'] // 36) / 100),
                           str(Data[i]['NCPUS']), str(Data[i]['NNodes']), (str(Data[i]['ReqMem'])[2:-3]),
                           (str(Data[i]['ReqMem'])[-3:-1]), str((int(Data[i]['CPUTimeRAW'] // 36) / 100))]
            excl = ";".join(seq_of_data)
            s = "Job nr. " + str(id_).ljust(8) + " (account = " + acc + ") has the efficiency " + \
                str(int(abs(efficiency*1000))/10).ljust(5) + "% with a totalCPU of " \
                + str((translate_time_to_sec(formated)//360)/10).ljust(8) + " hours. Runtime in hours:" + \
                str((Data[i]['ElapsedRaw']//360)/10).ljust(6) + " number of CPUs:" + str(Data[i]['NCPUS']).ljust(4) + \
                ' number of nodes:' + str(Data[i]['NNodes']).ljust(4)
            if "Mc" in str(Data[i]['ReqMem'])[2:-1]:
                s += ". Memory (Mc):"+(str(Data[i]['ReqMem'])[2:-1]).ljust(9)
            else:
                s += ". Memory (Mn):"+(str(Data[i]['ReqMem'])[2:-1]).ljust(9)
            s += ". Corehours:"+str(int(Data[i]['CPUTimeRAW']//360)/10)
            text_list.append(s)
            table_list.append(excl)

if len(text_list) == 0:
    sys.stderr.write("No data fitting the project_name within the specified borders within the specified time")
    sys.exit()


if comma_sep:
    pathname = os.path.dirname(originals[0])

    if len(originals) < 2:
        path_file = os.path.join(pathname, os.path.basename(originals[0].split('.')[0]) +
                                 "_mi" + str(mini).replace(".", "_") + "_ma" + str(maxi).replace('.', '_') + ".csv")
    else:
        path_file = os.path.join(pathname, os.path.basename(originals[0].split('.')[0]) + '_bis_' +
                                 os.path.basename(originals[-1].split('_')[1].split('.')[0] + "_mi" +
                                                  str(mini).replace(".", "_") + "_ma"+str(maxi).replace('.', '_') + ".csv"))
    with open(path_file, 'w')as a:
        a.write("\n".join(table_list))
        print('wrote in: '+path_file)
else:
    print("\n".join(text_list))

