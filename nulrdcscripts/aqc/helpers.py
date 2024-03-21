#!/usr/bin/env python3

"""
General helper functions for aqc.
"""

from progressbar import *
import pandas as pd
import os
import datetime

def print_lstats(lstats: dict):

    """
    Prints loudness statistics to terminal.

    :param dict lstats: loudness stats
    """

    print(f"\n\tMax TP:\t{lstats["Max TP"]:9.2f} dBTP")
    print(f"\tLUFS-I:\t{lstats["LUFS-I"]:9.2f} LUFS")
    print(f"\tLRA:\t{lstats["LRA"]:9.2f} LU")

def print_warnings(warnings: dict):
    
    """
    Prints warnings to terminal.

    :param dict warnings: dict of warnings where key timestamp and value is a warning type
    """

    print()
    for key in warnings:
        print("\t" + key + ": " + warnings[key])

def df_print(df: pd.DataFrame):

    """
    Prints a dataframe in a specific way I wanted it to print at a certain time.
    Not sure if this is necessary anymore.

    :param pandas.DataFrame df: DataFrame to print
    """

    # print with my own settings
    with pd.option_context('display.max_rows', 8,
                    'display.max_columns', 4,
                    'display.precision', 2,
                    ):

        print(df)

def default_widgets(label: str = ""):

    """
    Setups up the default widgets used in the progress bar.
    This way they can all be custom and look the same.

    :param str label: progress bar label
    :return: widgets for progress bar
    :rtype: list
    """

    widgets = [
        FormatLabel(label + " |"), ' ', 
        Percentage(format='%(percentage)3d%%'), ' ', 
        Bar("#"), ' ',
        Timer(format='Time: %(elapsed)s', timedelta = '0:00:01.00')
        #AdaptiveETA(exponential_smoothing=True, exponential_smoothing_factor=0.1), ' ',
    ]
    return widgets

def hms2seconds(hms: str):
   
    """
    Converts HH:MM:SS time to seconds

    :param str hms: time in HH:MM:SS
    :return: total seconds
    :rtype: float
    """

    if hms == "N/A":
       return -1
   
    timedeltaObj = datetime.datetime.strptime(hms, "%H:%M:%S.%f") - datetime.datetime(1900,1,1)
    return timedeltaObj.total_seconds()

def sec2time(seconds: float):

    """
    Converts seconds to HH:MM:SS time, truncating milliseconds.

    :param float seconds: total seconds
    :return: HH:MM:SS time
    :rtype: str
    """

    seconds = int(seconds)
    h = seconds // 3600
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60

    return f"{h:02d}:{m:02d}:{s:02d}"

def sec2mstime(seconds: float):

    """
    Converts seconds to HH:MM:SS.ss time, including milliseconds.

    :param float seconds: total seconds
    :return: HH:MM:SS.ss time
    :rtype: str
    """

    h = int(seconds // 3600)
    m = int(seconds % 3600 // 60)
    s = seconds % 3600 % 60

    return f"{h:02d}:{m:02d}:{s:05.2f}"

def get_immediate_subdirectories(folder: str):
    """
    Gets list of immediate subdirectories of input folder.

    :param str folder: fullpath to input folder
    :return: immediate subdirectory names (not fullpath)
    :rtype: list[str]

    """
    return [
        name for name in os.listdir(folder) if os.path.isdir(os.path.join(folder, name))
    ]