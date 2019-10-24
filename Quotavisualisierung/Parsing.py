import argparse
import sys
import datetime
import glob

nutzergraph = False
yearly_quota = 0
start_point = 0
filter_n = 0
originals = ""
number_of_months_DB = 0
partial_quota = 0
finished = False
target_file = ""
Parameternummer = 0


def essential_par(parameters):  # reads the parameters and interprets -src, -o as well as every parameter not beginning with "-"
    if len(parameters) < 2:
        print(parameters)
        sys.stderr.write("This file needs both an input and an output")
        sys.exit()
    sources_key, sources_nok, output, optpara = [], [], [], []
    while parameters:
        if "-src=" == parameters[0][:5]:
            sources_key.append(parameters[0][5:])
            parameters = parameters[1:]
        else:
            if "-o" == parameters[0][:2]:
                output.append(parameters[0][3:])
                parameters = parameters[1:]
            else:
                if "-" in parameters[0][0:2]:
                    optpara.append(parameters[0])
                    parameters = parameters[1:]
                else:
                    sources_nok.append(parameters[0])
                    parameters = parameters[1:]
    if len(output) >= 2:
        sys.stderr.write("Only 1 output file allowed")
        sys.exit()
    if not output:
        output.append(sources_nok[-1])
        sources_nok = sources_nok[:-1]
    sources = sources_key+sources_nok
    return [sources, output, optpara]


def argparsinit(param, sysargv): ### Reads the Console Inputs, interprets them for the main module to request
    global finished
    global yearly_quota
    global start_point
    global filter_n
    global originals
    global number_of_months_DB
    global partial_quota
    global finished
    global Parameternummer
    global target_file
    ap = param
    ap.add_argument("-o", nargs=1)
    ap.add_argument("-n", nargs='*', dest="Number_id")
    ap.add_argument("-src", nargs='*')
    ap.add_argument('--quota', dest='Quota', type=int, nargs=1)
    ap.add_argument('-q', dest='Quota', type=int, nargs=1)
    ap.add_argument('-s', dest='StartPoint', default="None", type=str, nargs='?')
    ap.add_argument('--start', dest='StartPoint', default="None", type=str, nargs='?')
    ap.add_argument('-p', dest='ProjectName', type=str, nargs='?')
    ap.add_argument('--project', dest='ProjectName', type=str, nargs='?')
    ap.add_argument('rest', type=str, nargs='*')
    ap.add_argument('-usergraph', type=bool)
    ap.add_argument('-finished', type=bool)
    o_parameters = ap.parse_args()
    print("O UND E PARA",sysargv[1:], o_parameters)
    e_parameters = essential_par((sysargv[1:]))
    if "usergraph" in str(sysargv):
        global nutzergraph
        nutzergraph = True
    finished = False
    if "-finished" in str(sysargv):

        finished = True
    # parse parameters into values, divide the Quota into months from the yearly quota.
    # convert input-parameters into data to interpret
    yearly_quota = 0
    number_of_months_DB = 0
    target_file = e_parameters[1][0]
    # multidisplaying two different Graphs, one for Efficiency, one for the overall consumption
    if o_parameters.Number_id:
        Parameternummer = o_parameters.Number_id[0]
    if o_parameters.StartPoint:
        start_point = o_parameters.StartPoint
        if len(start_point) == 10:  # appends hours, minutes and seconds if only date given
            start_point += "-00-00-00"
        start_point = (str(start_point)[::])
    if o_parameters.ProjectName is not None:  # if no name is given, sets the filter_n to ""
        filter_n = o_parameters.ProjectName
    else:
        filter_n = ""
    if o_parameters.Quota:
        yearly_quota = o_parameters.Quota[0]
    else:
        if not yearly_quota:
            yearly_quota = 0
    if yearly_quota > 0:
        partial_quota = int(yearly_quota / 12)
    else:
        partial_quota = 0  # Script runs under the assumption, the inserted quota = 12* the instance-quota
    originals = e_parameters[0]
    if e_parameters[0]:
        pass
    else:
        sys.stderr.write(
            "Error: no source identified, expecting source in format: 'src=path/*' or 'src path/filename'.\n")
        sys.exit("Did not find a source file")
    if "*" in e_parameters[0][0] or "?" in e_parameters[0][0]:
        originals = glob.glob(e_parameters[0][0])
    return


def get_filter():
    return filter_n


def get_yearly_quota():
    return yearly_quota


def get_nutzer_graph():
    return nutzergraph


def get_start_point():
    return start_point


def get_original():
    return originals


def get_number_of_months():
    return number_of_months_DB


def get_partial_quota():
    return partial_quota


def get_finished():
    return finished


def get_target():
    return target_file


def get_parameter_nr():
    return Parameternummer
