import numpy as np
import datetime
import matplotlib as mpl  # general matplotlib import
import matplotlib.pyplot as plt  # MATLAB-like plotting
import struct
import csv
import sys
import string
import pandas

# %matplotlib inline

plt.rcParams['figure.figsize'] = [6, 4]  # set global parameters

dtype1 = np.dtype(
    [('ReqCPUS', 'i4'), ('ReqMem', '|S256'), ('ReqNodes', 'i4'), ('AllocNodes', 'i4'), ('AllocCPUS', 'i4'),
     ('NNodes', 'i4'), ('NCPUS', 'i4'), ('CPUTimeRAW', 'uint32'), ('ElapsedRaw', 'uint32'), ('Start', '|S256'),
     ('End', '|S256')])

job_record = np.dtype([('ReqCPUS', 'i4'), ('ReqMem', 'i4')])
original = "HKHLR_SLURM_Darmstadt_2018-W14.log-example"
copy = "copy.log-example"


# np.loadtxt(original, dtype={'names': ('ReqCPUS','ReqMem','ReqNodes','AllocNodes','AllocCPUS','NNodes','NCPUS','CPUTimeRAW','ElapsedRaw','Start','End'),
#                            'formats': ('i64',  'i64',    'i64',    'i64',       'i64',       'i64'   , 'i64'  'i64'     ,'i64'       ,'S256' ,'S256')}, delimiter = '|',
#           usecols = (                    3,    4,         5,         6,           7,          8,        9,      12,          13,        26,    27))

Data = np.loadtxt(original, dtype=dtype1, delimiter='|', skiprows=0, usecols=(3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27))
CopyData = np.loadtxt(copy, dtype=dtype1, delimiter='|', skiprows=1, usecols=(3, 4, 5, 6, 7, 8, 9, 12, 13, 26, 27))
#print(Data)
#print(CopyData)
fin_dtype = np.dtype(
    [('Corehours', 'uint64'), ('Endtime', 'S256')]
)


def translateDateToSec(YMDHMS):
    x = str(YMDHMS, 'utf-8')
    temp = 3600 * 24 * 30 * 365 * 2017
    if x == 'Unknown':
        return -1
    else:
        Year, Month, Day, Hour, Minute, Second = x.split("-")
        # print(int(float(Second))+ int(float(Minute))*60 +int(float(Hour))*3600 + (int(float(Day))-1)*3600*24 +(int(float(Month))-1)*3600*24*DaysByTheFirstOfMonth(Month) + (int(float(Year))-1)*3600*24*30*364)
        return (int(float(Second)) + int(float(Minute)) * 60 + int(float(Hour)) * 3600 + (
                    int(float(Day)) - 1) * 3600 * 24 + 3600 * 24 * DaysByTheFirstOfMonth(Month) + (
                            int(float(Year)) - 1) * 3600 * 24 * 30 * 365)# - temp


# TODO adapt then 364 above to consider every 4th year, every 100 years, every 400 years, these are only aprox
def DaysByTheFirstOfMonth(month):
    my_dictionary = {
        '01': 0,
        '02': 31,
        '03': 59,
        '04': 90,
        '05': 120,
        '06': 151,
        '07': 181,
        '08': 212,
        '09': 243,
        '10': 273,
        '11': 304,
        '12': 334,
    }
    return my_dictionary[month]


#
# TODO fix DaysByTheFirstofMonth and the line that calls it (a set term for each of the 12 months?)
#

f = (np.zeros((Data.size, 2)))
x = 0
for column in Data:
    f[x][0] = (column[7] * column[4])
    if translateDateToSec(column[10]) > 0:
        f[x][1] = translateDateToSec(column[10])
    if x >= 1:
        f[x][0] = f[x][0] + f[x - 1][0]
    if translateDateToSec(column[10]) < 0:
        np.delete(f, f[x,0])
        np.delete(f, f[x,1])
        x = x - 1
    x = x + 1

#TODO: Round to days via  860400 Seconds? That way every
print(f)
# n = np.linspace(0,100000,1000000)
# plt.plot(n, (f[n][1]/f[n][2]))
#f = np.sort(f - 1)
coreseconds = f[:, 0]
times = f[:, 1]
plt.plot(times, coreseconds)
plt.show()
#print(f[:, 1])
#print()
