import csv
import sys
from generatecodinghistory import generate_coding_history
from VideoScript.SystemFileDirectory.guessdate import guess_date

def import_csv(csvInventory):
    csvDict={}
    try:
        with open(csvInventory, encoding='utf-8')as f:
            reader = csv.DictReader(f, delimiter=',')
            video_fieldnames_list = ['filename', 'work_accession_number', 
                                     'ALMA number/Finding Aid', 'Barcode', 'description', 'Record Date/Time', 'Housing/Container Markings', 'Condition Notes', 'Format', 'Capture Date', 'Digitizer', 'VTR', 'VTR Output Used', 'Tape Brand', 'Tape Record Mode', 'TBC', 'TBC Output Used', 'ADC', 'Capture Card', 'Sound','Region', 'Capture Notes']
            missing_fieldnames = [i for i in video_fieldnames_list if not i in 
                                  reader.fieldnames]
            if not missing_fieldnames:
                for row in reader:
                    name = row['filename']
                    id1 = row['work_accession_number']
                    id2 = row['ALMA number/Finding Aid']
                    id3 = row['Barcode']
                    description = row['description']
                    record_date = row['Record Date/Time']
                    container_markings = row['Housing/Container Markings']
                    container_markings = container_markings.split('\n')
                    condition_notes = row['Condition Notes']
                    format = row['Format']
                    captureDate = row['Capture Date']

            if captureDate:
                    captureDate = str(guess_date(captureDate))
                    digitizationOperator = row['Digitizer']
                    vtr = row['VTR']
                    vtrOut = row['VTR Output Used']
                    tapeBrand = row['Tape Brand']
                    recordMode = row['Tape Record Mode']
                    tbc = row['TBC']
                    tbcOut = row['TBC Output Used']
                    adc = row['ADC']
                    dio = row['Capture Card']
                    sound = row['Sound']
                    sound = sound.split('\n')
                    region = row['Region']
                    capture_notes = row['Capture notes']
                    coding_history = []
                    coding_history = generate_coding_history(coding_history, 
                                                             vtr, [tapeBrand, recordMode, region, vtrOut])
                    coding_history = generate_coding_history(coding_history, 
                                                             tbc, [tbcOut])
                    coding_history = generate_coding_history(coding_history, 
                                                             adc, [None])
                    coding_history = generate_coding_history(coding_history, 
                                                             dio, [None])
                    csvData = {'Accession number/Call number' : id1,
                               'ALMA number/Finding Aid' : id2,
                               'Barcode' : id3,
                               'Description' : description,
                               'Record Date' : record_date,
                               'Container Markings' : container_markings,
                               'Condition Notes' : condition_notes,
                               'Format' : format,
                               'Digitization Operator' : digitizationOperator,
                               'Capture Date' : captureDate,
                               'Coding History' : coding_history,
                               'Sound Note' : sound,
                               'Capture Notes' : capture_notes
                              }
                    csvDict.update({name : csvData})
            elif not 'File name' in missing_fieldnames:
                print("WARNING: Unable to find all column names in csv file")
                print('''"File name column found. Interpreting csv file as 
                      file list"''')
                print("CONTINUE? (y/n)")
                yes = {'yes','y', 'ye', ''}
                no = {'no','n'}
                choice = input().lower()
                if choice in yes:
                   for row in reader:
                        name = row['File name']
                        csvData = {}
                        csvDict.update({name : csvData})
                elif choice in no:
                   quit()
                else:
                   sys.stdout.write("Please respond with 'yes' or 'no'")
                   quit()
            else:
                print("No matching column names found in csv file")
            #print(csvDict)
    except FileNotFoundError:
        print("Issue importing csv file")
    return csvDict