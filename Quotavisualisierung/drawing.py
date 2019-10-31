import matplotlib.patches as mpatches
import numpy as np
import matplotlib.pyplot as plt  # MATLAB-like plotting
import math
import datetime
import io
#import PIL
#from PIL import Image
import matplotlib.ticker as mtick
import matplotlib.dates as mdates
from matplotlib.ticker import ScalarFormatter
import Time_functions as D_

colors = ['#81c478', "#008000", '#ffa500']  # the quota will be colored in the equally indexed color.
thresholds = [0.7, 1.1, 1.5]  # If the usage this month is below thresholds times the quota,
maximum = '#ff0000'  # if the usage is above the (highest threshold) * quota, the Quota will be colored in
#                      the given color 'maximum'.
# separates the quotas into four categories, taking the ratios from thresholds and the results from colors


def colorization(value, comp):
    """
    :param value: The difference between the beginning of the Instance and the end, in Corehours
    :param comp: the given Quota
    :return: A color based on the relationship of the two parameters, red for value >> comp, green
     for value ~~ (roughly equal) comp, blue for comp >> value and orange for value > comp
    """
    if value/comp < thresholds[0]:
        return colors[0]
    if value / comp < thresholds[1]:
        return colors[1]
    if value / comp < thresholds[2]:
        return colors[2]
    else:
        return maximum


# gets the current y labels of the plot
# and should return new labels as well as the new unit
def get_scaled_ylabels (old_y_labels,scaling_value):
    new_ylabels = []
    unit = ""

    old_labels_str = [str(int(l)) for l in old_y_labels]

    # min amount of 0
    min_0_delete=len(old_labels_str[0])

    for label in old_labels_str:
        j = len(label) - 1
        count=0
        while j>0 and label[j]=='0':
            count +=1
            j-=1
        # do not include the 0 label in this consideration
        if min_0_delete > count and label[j]!='0':
            min_0_delete=count

    for label in old_labels_str:
        new_ylabels.append(label[0:-min_0_delete])

    unit = "10^" + str(min_0_delete)

    if unit:
        if unit == "10^7":
            unit = "in ten million"
        if unit == "10^6":
            unit = "in million"
        if unit == "10^5":
            unit = "in hundred thousand"
        if unit == "10^4":
            unit = "in ten thousand"
        if unit == "10^3":
            unit = "in thousand"
        if unit == "10^2":
            unit = "in hundred"

    return new_ylabels, unit


def generate_plot(partial_quota, number_of_instances, f, a0, a1, tmp_y2, tmp_x, tmp_y, blocks_x, start_point, Xtics,
                  yearly_quota, x_start, finished, User_t, System_t, y_start2, y_end2, beginning_dt, nutzergraph,
                  fig, x_end, Data, filter_n):
    if filter_n:
        f.suptitle(str(filter_n),fontweight="bold")
    else:
        f.suptitle(str(Data[0]['Account'])[2:-1],fontweight="bold")
    global daily_eff_days
    global daily_eff_eff
    fmt = "%Y-%m-%d-%H-%M"  # standard format for Dates, year month, day, hour, minute
    myFmt = mdates.DateFormatter('%b %y')
    nothing = mdates.DateFormatter(' ')
    monthly_cputime = []
    monthly_used = []
    effarray = []
    tmp_y2.append(tmp_y[-1])
    if partial_quota:  #### drawing of the quota####
        for i in range(0, number_of_instances):  # not possible for the last area, hence skipping it.
            col = colorization(D_.find_y_from_given_time(datetime.datetime.fromtimestamp(blocks_x[i*2+1]), tmp_x, tmp_y) -
                               D_.find_y_from_given_time(datetime.datetime.fromtimestamp(blocks_x[i*2]), tmp_x, tmp_y), partial_quota)
            coordinates_x = (datetime.datetime.fromtimestamp(blocks_x[i*2]), datetime.datetime.fromtimestamp(blocks_x[i*2]),
                             datetime.datetime.fromtimestamp(blocks_x[i * 2 + 1]))
            coordinates_y = [tmp_y2[i * 2], tmp_y2[i * 2+1], tmp_y2[i * 2+1]]
            a0.fill_between(coordinates_x, 0, coordinates_y, color=col, alpha=0.99)
            monthly_cputime.append(tmp_y2[i * 2 + 1] - tmp_y2[i * 2])
        value1 = D_.find_y_from_given_time(datetime.datetime.fromtimestamp(blocks_x[-1]), tmp_x, tmp_y)
        value2 = D_.find_y_from_given_time(datetime.datetime.fromtimestamp(blocks_x[-2]), tmp_x, tmp_y)
        col = colorization(value1 - value2, partial_quota)
        coordinates_x = (datetime.datetime.fromtimestamp(blocks_x[-2]), datetime.datetime.fromtimestamp(blocks_x[-2]),
                         datetime.datetime.fromtimestamp(blocks_x[-1]))
        coordinates_y = (value2,value2+partial_quota,value2+partial_quota)
        a0.fill_between(coordinates_x, 0, coordinates_y, color=col, alpha=0.99)
    # determines the last interval's color and draws it (uses the highest
    # recorded value as the end value of the ongoing time span).
    axis = plt.gca()  # for plotting/saving the plot as it's own image
    # Sets the visual borders for the graphs; area of occurring values (main graph) +- 5%.
    if start_point:  # setting the beginning and end of the graph
        beginning = start_point.timestamp()
        end = start_point.timestamp() + 365 * 24 * 3600
        beginning = beginning - 30*24*3600
        end = end + 30*24*3600
    extrapolation_x = []
    extrapolation_y = []
    if len(tmp_y2) < 3:
        tmp_y2.append(0)
        tmp_y2.append(0)
    # TODO: check if monthsleft aus DBZugriff funktioniert
    monthsleft = int(12 + ((x_start.timestamp() - x_end.timestamp()) / 2629800 + 0.9) // 1)
    if yearly_quota and len(tmp_x) >= 1:
        extrapolation_point_x = D_.first_of_month(x_end)
        extrapolation_point_y = D_.find_y_from_given_time(tmp_x[-1],tmp_x,tmp_y)
        extrapolation_point_y = max(extrapolation_point_y, D_.find_y_from_given_time(D_.first_of_month(extrapolation_point_x),tmp_x,tmp_y)+partial_quota)
        extrapolation_x.append(D_.first_of_month(extrapolation_point_x))
        extrapolation_x.append(D_.first_of_month(extrapolation_point_x))
        extrapolation_x.append(D_.first_of_month(datetime.datetime.fromtimestamp(extrapolation_point_x.timestamp()+2851200)))
        extrapolation_y.append(D_.find_y_from_given_time(extrapolation_point_x, tmp_x, tmp_y))
        extrapolation_y.append(max(extrapolation_y[0]+partial_quota, tmp_y[-1]))
        extrapolation_y.append(extrapolation_y[-1])
        expoint_y = extrapolation_y[-1]

        extrapolation_y[-2] = tmp_y[-1]
        extrapolation_y[-1] = tmp_y[-1]
        expoint_y = extrapolation_y[-1]

        xtr_pt_x = extrapolation_point_x
        xtr_pt_y = extrapolation_point_y
        for i in range(1, monthsleft):  # The three points required for each block
            extrapolation_x.append(D_.first_of_month(datetime.datetime.fromtimestamp(xtr_pt_x.timestamp()+ i * 2851200)))
            extrapolation_x.append(D_.first_of_month(datetime.datetime.fromtimestamp(xtr_pt_x.timestamp() + i * 2851200)))
            extrapolation_x.append(D_.first_of_month(datetime.datetime.fromtimestamp(xtr_pt_x.timestamp() + (i + 1) * 2851200)))
            extrapolation_y.append(expoint_y + (i-1) * partial_quota)
            extrapolation_y.append(expoint_y + i * partial_quota)
            extrapolation_y.append(expoint_y + i * partial_quota)
        if monthsleft:
            a0.plot(extrapolation_x[3:], extrapolation_y[3:], "black")
    if monthsleft:
        extrapolation_y.append(0)
    else:
        extrapolation_y = [0]
    beg_14_months = beginning+36817200
    fourteen_dt = datetime.datetime.fromtimestamp(beg_14_months)
    # Print statements, to give feedback either onscreen or into a dedicated file to be piped into.
    print('The accumulated TotalCPU time is', int((User_t[-1] + System_t[-1]) * 100) / 100, "hours")
    print('and the number of accumulated corehours is', int(tmp_y[-1]*100)/100)
    efficiency = (User_t[-1] + System_t[-1]) / tmp_y[-1]
    # Added rounding to the efficiency percentage feedback.
    print('Which results in an efficiency of', int(efficiency*10000)/100+0.005, "%")
    if efficiency < 0 or efficiency > 1:
        print("Efficiency is outside of it's boundaries, valid is only between 0 and 1")
    accum_total_time = np.zeros(len(tmp_x))
    for i in range(0, len(accum_total_time)):
        accum_total_time[i] = User_t[i] + System_t[i]
    delta = [0]
    total_time = []
    total_time.append(accum_total_time[0])
    total_time.append(accum_total_time[0])
    difference = [0]
    for i in range(1,len(accum_total_time)):
        total_time.append(accum_total_time[i]- accum_total_time[i-1])
        delta.append(100*((accum_total_time[i]-accum_total_time[i-1])/(tmp_y[i]-tmp_y[i-1])))
        if delta[i] > 100:
            a = 0
    if yearly_quota:  # ensuring that the extrapolated quota is still in frame
        a0.set_ylim([y_start2 - (0.05 * y_end2), max(tmp_y[-1], max(extrapolation_y),max(coordinates_y)) * 1.2])
    #    print("limit",a0.get_ylim()[1])
    else:  # No quota given, image is focused around occupied and utilized resources.
        print("NO YEARLY DETECTED")
        a0.set_ylim([y_start2 - (0.05 * y_end2), tmp_y[-1] * 1.05])
    #####  Creation of patches for Legend #####
    red_patch = mpatches.Patch(color='#ff0000', alpha=0.7, label='>=150%')
    orange_patch = mpatches.Patch(color='#ffa500', alpha=0.7, label='>=110%,<150%')
    green_patch = mpatches.Patch(color='#008000', alpha=0.8, label='>=70%,<110%')
    light_green_patch = mpatches.Patch(color='#81c478', alpha=0.8, label='<70%')
    grey_patch = mpatches.Patch(color='dimgrey', alpha=0.75, label='Allocated corehours')
    yellow_patch = mpatches.Patch(color='#d9e72e', alpha=0.49, label='Utilized corehours')
    black_patch = mpatches.Patch(color='black', alpha=1, label='Remaining corehours')
    a0.plot(tmp_x, accum_total_time, '#d9e72e')  # plotting the TotatlCPU Graph
    if yearly_quota:  # Legends for if there is a quota, or a shorter Legend in case there isn't.
        a0.legend(handles=[red_patch, orange_patch, green_patch, light_green_patch, grey_patch, yellow_patch, black_patch])
    else:
        a0.legend(handles=[grey_patch, yellow_patch])
    a0.fill_between(tmp_x, 0, accum_total_time, color='#d9e72e', alpha=0.70)  # plotting the area below TotalCPU graph
    a0.plot(tmp_x, tmp_y, 'dimgrey', fillstyle='bottom', alpha=0.75)  # plotting the main graph (cores * hours)
    a0.fill_between(tmp_x, 0, tmp_y, color="grey", alpha=0.45)  # plotting the area below the corehours graph
    for i in range(len(accum_total_time),number_of_instances*3+4):  # ensuring that empty months will be accounted for
        accum_total_time = np.append(accum_total_time, accum_total_time[-1])  # filling accumulated time with most recent
    if yearly_quota:
        for i in range(0, int(number_of_instances)):  # not possible for the last area, hence skipping it.
            monthly_used.append(accum_total_time[i * 3 + 3] - accum_total_time[i * 3])
    percentages = [0]
    for i in range(len(monthly_cputime)):
        if monthly_used[i] >= 1:
            percentages.append(10*(monthly_cputime[i]/monthly_used[i]))
    for i in range(len(percentages)):
        effarray.append(percentages[i])
    a0.grid(True)
    axis2 = fig.add_subplot(212)
    a1legend1 = mpatches.Patch(color='Red', alpha=0.8, label="per day")
    a1legend2 = mpatches.Patch(color='purple', alpha=0.8, label='per job')
    a1.plot(tmp_x, delta, '.', color="purple", markersize=5, alpha=0.35)  # percentages amplified by the lower bound to
    a1.legend(handles=[a1legend1,a1legend2])
    plt.ylabel('Efficiency')  # be more visible.
    daily = []
    dates = []
    for i in range(int(x_start.timestamp()), int(x_end.timestamp()), 2764800):
        r = D_.gather_efficiencies_for_month(datetime.datetime.fromtimestamp(i), Data)
        daily_eff_days = r[-2]
        daily_eff_eff = r[-1]
        r = r[:-2]
        for j in range(len(r[0])):
            if r[1][j] > 0:
                daily.append(100*r[1][j]/r[0][j])
                dates.append(r[2][j])
    formatteddates = []
    for i in dates:
        if len(str(i)) > 5 and "." not in str(i):
            transp = str(i)[2:18]
            formatteddates.append(datetime.datetime.strptime(transp, fmt))
    eff_days = []
    #for i in dates:
    #    eff_days.append(datetime.datetime.strptime(str(i)[2:18], fmt))
    a1.plot(formatteddates, daily, '.', color="Red", markersize=3, alpha=0.85)
    eff_distance = 0 - axis.get_ylim()[0]
    a1.grid(True)    # Creates a grid in the image to aid the viewer in visually processing the data.
    a1.set_ylim([-5, 105])
    if nutzergraph:
        a1.set_ylim([0, 100])  # Usergraphs don't display anything above 100% or below 0%.
    a1.set_yticks(np.arange(0, 101, 10), minor=True)  # minor tick-lines are much thinner than regular ones
    a1.set_yticks(np.arange(0, 101, 25))
    a1.yaxis.set_major_formatter(mtick.PercentFormatter())
    plt.xlabel('Efficiency')
    plt.xlabel(' ')
    a0.xaxis.tick_top()
    a0.set_xlim((beginning_dt, fourteen_dt))
    a1.xlim = (beginning_dt, fourteen_dt)
    plt.sca(a0)
    a0.yaxis.set_major_formatter(ScalarFormatter(useOffset=True))
    plt.xticks(Xtics)
    plt.ylabel('CPUhours')
    emptylabels = []
    for i in a0.get_xticklabels():
        emptylabels.append(["", ""])

    new_ylabels,unit = get_scaled_ylabels(a0.get_yticks(),tmp_y[-1])

    plt.ylabel("CPUhours ("+unit+")")

    a0.set_xticklabels = emptylabels
    a0.set_yticklabels(new_ylabels)
    plt.sca(a1)
    # dictates gap in height, left border, right border, gap in width, bottom border, top border
    plt.subplots_adjust(hspace=0.03, left=0.1, right=0.925, wspace=0.07, bottom=0.035, top=0.95)
    plt.xlim(beginning_dt, fourteen_dt)
    plt.xticks(Xtics)
    a0.xaxis.set_major_formatter(nothing)  # removes the x-tic notations
    a1.xaxis.set_major_formatter(myFmt)
    a1.grid(which='minor', alpha=0.2)
    a1.grid(which='major', alpha=0.5)
    f.set_size_inches((11, 8.5), forward=False)
    ## for png compression
    #ram = io.BytesIO()
    #plt.savefig(ram, format='png')
    #ram.seek(0)
    #im = Image.open(ram)
    #im2 = im.convert('RGB').convert('P', palette=Image.ADAPTIVE)
    #return im2
    #print(tmp_x)
    #print(tmp_y)
    return f
