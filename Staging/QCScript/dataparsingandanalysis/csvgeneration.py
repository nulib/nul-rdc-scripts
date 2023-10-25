import pandas as pd
import csv

def videostatscsv(videostats):
    csv_columns= list(videostats.keys())
    
    try:
        with open ('videodata.csv', 'w') as videocsvfile:
            writer = csv.DictWriter(videocsvfile, fieldnames=csv_columns)
            writer.writeheader()
            for data in videostats:
                writer.writerow(data)
    except IOError:
        print ('I/O Error')


