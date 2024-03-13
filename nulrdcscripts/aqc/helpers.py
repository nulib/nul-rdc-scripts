#!/usr/bin/env python3

from progressbar import *
import pandas as pd
import os
import datetime

def print_lstats(lstats):

    print(f"\n\tMax TP:\t{lstats["Max TP"]:9.2f} dBTP")
    print(f"\tLUFS-I:\t{lstats["LUFS-I"]:9.2f} LUFS")
    print(f"\tLRA:\t{lstats["LRA"]:9.2f} LU")

def print_warnings(warnings):
    print()
    for key in warnings:
        print("\t" + key + ": " + warnings[key])

def df_print(df):
    # print with my own settings
    with pd.option_context('display.max_rows', 8,
                    'display.max_columns', 4,
                    'display.precision', 2,
                    ):

        print(df)

def default_widgets(label=""):
    widgets = [
        FormatLabel(label + " |"), ' ', 
        Percentage(format='%(percentage)3d%%'), ' ', 
        Bar("#"), ' ',
        Timer(format='Time: %(elapsed)s', timedelta = '0:00:01.00')
        #AdaptiveETA(exponential_smoothing=True, exponential_smoothing_factor=0.1), ' ',
    ]
    return widgets

def get_total_seconds(stringHMS):
   if stringHMS == "N/A":
       return -1
   
   timedeltaObj = datetime.datetime.strptime(stringHMS, "%H:%M:%S.%f") - datetime.datetime(1900,1,1)
   return timedeltaObj.total_seconds()

def sec2time(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60

    return f"{h:02d}:{m:02d}:{s:02d}"

def sec2mstime(seconds):
    h = int(seconds // 3600)
    m = int(seconds % 3600 // 60)
    s = seconds % 3600 % 60

    return f"{h:02d}:{m:02d}:{s:05.2f}"

def get_immediate_subdirectories(folder):
    """
    get list of immediate subdirectories of input
    """
    return [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]