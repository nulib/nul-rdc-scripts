import csv
import os
from nulrdcscripts.vproc.params import args


def import_csv(csvInventory):
    csvDict = {}
    try:
        with open(csvInventory, encoding="utf-8") as f:
            # skip through annoying lines at beginning
            while True:
                # save spot
                stream_index = f.tell()
                # skip advancing line by line
                line = f.readline()
                if not (
                    "Name of Person Inventorying" in line
                    or "MEADOW Ingest fields" in line
                ):
                    # go back one line and break out of loop once fieldnames are found
                    f.seek(stream_index, os.SEEK_SET)
                    break
            reader = csv.DictReader(f, delimiter=",")
            # fieldnames to check for
            # some items have multiple options
            # 0 index is our current standard
            video_fieldnames_list = [
                ["filename"],
                ["work_accession_number"],
                ["box/folder alma number", "Box/Folder\nAlma number"],
                ["barcode"],
                ["description"],
                ["record date/time"],
                ["housing/container markings"],
                ["condition notes"],
                ["call number"],
                ["format"],
                ["capture date"],
                ["staff initials", "Digitizer"],
                ["VTR used"],
                ["VTR output used"],
                ["tape brand"],
                ["tape record mode"],
                ["TBC used"],
                ["TBC output used"],
                ["ADC"],
                ["capture card"],
                ["sound"],
                ["video standard", "Region"],
                ["capture notes"],
            ]
            # dictionary of fieldnames found in the inventory file,
            # keyed by our current standard fieldnames
            # ex. for up to date inventory
            # "video standard": "video standard"
            # ex. if old inventory was used
            # "video standard": "Region"
            # this way old inventories work
            fieldnames = {}
            missing_fieldnames = []

            # loops through each field and checks for each option
            for field in video_fieldnames_list:
                for field_option in field:
                    for reader_field in reader.fieldnames:
                        if field_option.lower() in reader_field.lower():
                            # adds the fieldname used in the file
                            # to a dictionary for us to use
                            # the key is our current standard
                            fieldnames.update({field[0]: reader_field})
                            break
                # keep track of any missing
                # uses field[0] so when it tells user which ones are missin
                # they will use our current standard
                if not field[0] in fieldnames:
                    missing_fieldnames.append(field[0])

            if not missing_fieldnames:
                for row in reader:
                    # index field using dictionary of found fieldnames
                    name = row[fieldnames["filename"]]
                    id1 = row[fieldnames["work_accession_number"]]
                    id2 = row[fieldnames["box/folder alma number"]]
                    id3 = row[fieldnames["barcode"]]
                    description = row[fieldnames["description"]]
                    record_date = row[fieldnames["record date/time"]]
                    container_markings = row[fieldnames["housing/container markings"]]
                    if container_markings:
                        container_markings = container_markings.split("\n")
                    condition_notes = row[fieldnames["condition notes"]]
                    format = row[fieldnames["format"]]
                    captureDate = row[fieldnames["capture date"]]
                    # try to format date as yyyy-mm-dd if not formatted correctly
                    try:
                        captureDate = str(guess_date(captureDate))
                    except:
                        captureDate = None
                    staff_initials = row[fieldnames["staff initials"]]
                    vtr = row[fieldnames["VTR used"]]
                    tapeBrand = row[fieldnames["tape brand"]]
                    recordMode = row[fieldnames["tape record mode"]]
                    sound = row[fieldnames["sound"]]
                    sound = sound.split("\n")
                    videoStandard = row[fieldnames["video standard"]]
                    capture_notes = row[fieldnames["capture notes"]]
                    coding_history = []
                    coding_history = generate_coding_history(
                        coding_history,
                        vtr,
                        [tapeBrand, recordMode, videoStandard],
                    )
                    csvData = {
                        "accession number/call number": id1,
                        "box/folder alma number": id2,
                        "barcode": id3,
                        "description": description,
                        "record date": record_date,
                        "housing/container markings": container_markings,
                        "condition notes": condition_notes,
                        "format": format,
                        "staff initials": staff_initials,
                        "capture date": captureDate,
                        "coding history": coding_history,
                        "sound note": sound,
                        "capture notes": capture_notes,
                    }
                    csvDict.update({name: csvData})
            elif not "File name" in missing_fieldnames:
                print("WARNING: Unable to find all column names in csv file")
                print("File name column found. Interpreting csv file as file list")
                print("CONTINUE? (y/n)")
                yes = {"yes", "y", "ye", ""}
                no = {"no", "n"}
                choice = input().lower()
                if choice in yes:
                    for row in reader:
                        name = row["File name"]
                        csvData = {}
                        csvDict.update({name: csvData})
                elif choice in no:
                    quit()
                else:
                    sys.stdout.write("Please respond with 'yes' or 'no'")
                    quit()
            else:
                print("No matching column names found in csv file")
            # print(csvDict)
    except FileNotFoundError:
        print("Issue importing csv file")
    return csvDict


def checkandCreate(inventory_name, indir):
    csvInventory = os.path.join(inventory_name, indir)
    csvDict = import_csv(csvInventory)
    return csvDict


def csvHeaderList():
    csvHeaderList = [
        "shot sheet check",
        "date",
        "file format & metadata verification",
        "date",
        "file inspection",
        "date",
        "QC notes",
        "Access Filename",
        "Preservation Filename",
        "runtime",
    ]
    return csvHeaderList