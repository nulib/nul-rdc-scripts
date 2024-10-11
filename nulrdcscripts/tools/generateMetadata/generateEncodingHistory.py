import pandas as pd
import os

audio = [".wav"]
video = [".mp4", ".mkv"]


def csvtodf(csvitem):
    """Converts csvs to pandas dataframes for easier querying"""
    dataframe = pd.read_csv(csvitem)
    return dataframe


def assignequipdict(file):
    """Assigns file type so that appropriate schema is chosen."""
    fileTA, ext = os.path.splitext(file)
    if ext in audio:
        equip_dict = "equipment_schema_audio.csv"
    elif ext in video:
        equip_dict = "equipment_schema_video.csv"
    else:
        raise Exception(
            "This file is not able to be categorized based on extension. Must be one of .mp4,.mkv,.wav"
        )
    return equip_dict


def generate_coding_history(inventory, coding_history, hardware, append_list, file):
    inventory_df = csvtodf(inventory)
    deck = inventory_df["capture deck"]
    equip_dict = assignequipdict(file)
    if "audio" in equip_dict:
        equip_df = csvtodf(equip_dict)
    else:
        equip_df = csvtodf(equip_dict)


def openInventory(input_folder):
    """Checks that an inventory exists"""
    for i in input_folder:
        if i.endswith(".csv") and "inventory" in i:
            inventory = i
            break
        else:
            raise Exception(
                "There is no CSV file found in the given folder. CSV file must contain the word 'inventory'"
            )
    return inventory
