import datetime
import math

fmt = "%Y-%m-%d-%H-%M"  # standard format for Dates, year month, day, hour, minute


def first_of_month(date):  # returns a date of the first second of the same month as the given date.
    a_date = date.strftime(fmt)
    sp = a_date.split("-")
    recombining = sp[0]+"-"+sp[1]+"-"+"01-00-00"
    retdate = datetime.datetime.strptime(recombining, fmt)
    return retdate


def translate_date_to_sec(ymdhms):  # returns the timestamp of a given string representing a date.
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


def translate_time_to_sec(t):  # expects a string with (DD-)HH:mm:SS(.milliseconds)
    flag_days = False
    if '-' in t:
        flag_days = True
    t = t.split('.')[0]
    if len(t) < 2:
        return 0
    sub_splits = t.split('-')
    seconds = 0
    if flag_days:  # days are present
        seconds += 24 * 3600 * int(''.join(c for c in sub_splits[0] if c.isdigit()))  # converting days to seconds
    time_split_seconds = sub_splits[-1].split(':') # seperating the date into hours, minutes, seconds
    for it in range(len(time_split_seconds)):
        seconds += int(''.join(c for c in (time_split_seconds[-(it + 1)]) if c.isdigit())) * int(math.pow(60, int(it)))
        # adding hours*3600 and minutes*60 and second * 1 to seconds
    return seconds


def find_y_from_given_time(time, xarray, yarray): # retrieves the closest value before a given Stelle
    holdx = xarray[0]
    holdy = yarray[0]
    for i in range(len(xarray)):
        if xarray[i].timestamp() >= holdx.timestamp() and xarray[i].timestamp() <= time.timestamp():
            holdx = xarray[i]
            holdy = yarray[i]
    return holdy


def analyze_day(date, yD):  # gathers the occupied and utilized times for every job on a specific day. also time of the
    reserv = 0  # latest job to finish on said day
    used = 0
    time = 0
    for i in range(len(yD)):
        if str(date[:11]) in str(yD[i][11][:10]):
            reserv += int(str(yD[i][5]))*int(yD[i][9])  # ['AllocCPUs'])*int(yD[i]['ElapsedRAW'])/3600
            if len(yD[i][13]) > 3:
                used += translate_time_to_sec(str(yD[i][13]))  # ['UserCPU'])[2:])
                used += translate_time_to_sec(str(yD[i][14]))  # ['SystemCPU']
            time = (yD[i][11])
            used = float(used)
    return [reserv, used, time]


def analyze_month(date_of_month, dataset): # gathers info on all individual days of a month.
    daily_eff_days = []
    daily_eff_eff = []
    daysofmonth = []
    reserved = []
    used = []
    time = []
    for i in dataset:
        if str(i[11])[2:10] in date_of_month.strftime(fmt):
            daysofmonth.append(str(i[11])[2:12])
    daysofmonth = sorted(set(daysofmonth))
    days = []
    effs = []
    for i in daysofmonth:
        reserv_used_time = analyze_day(i, dataset)
        if reserv_used_time[0] >= 1:
            reserved.append(reserv_used_time[0])
            used.append(reserv_used_time[1])
            time.append(reserv_used_time[2])
            days.append(reserv_used_time[2])
            effs.append(100*reserv_used_time[1]/reserv_used_time[0])
    daily_eff_days = daily_eff_days + days
    daily_eff_eff = daily_eff_eff + effs
    return [reserved, used, time, daily_eff_days, daily_eff_eff]