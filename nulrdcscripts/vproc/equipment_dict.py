#!/usr/bin/env python3


def equipment_dict():
    """
    VTRs
    """
    panasonic_ag1980_rack1 = {
        "Coding Algorithm": "A=ANALOG",
        "Output is one of": ["Composite", "S-Video"],
    }
    panasonic_ag1980_rack2 ={
        "Coding Algorithm":"A=ANALOG",
        "Output is one of": ["Composite", "S-Video"],
    }

    """
    TBCs
    """
    dps_295_rack1 = {
        "Coding Algorithm": "A=ANALOG",
        "Hardware Type": "TBC",
        "Output is one of": ["Composite", "S-Video", "Component"],
    }

    dps_575_rack2 = {
        "Coding Algorithm": "A=ANALOG",
        "Hardware Type": "TBC",
        "Output is one of": ["Composite", "S-Video", "Component"],
    }

    """
    ADCs
    """
    hd10ava_rack1 = {"Coding Algorithm": "A=SDI", "Hardware Type": "A/D"}
    hd10ava_rack2 = {"Coding Algorithm": "A=SDI", "Hardware Type": "A/D"}


    """
    Capture Cards
    """
    decklinkstudio4k_rack1 = {"Coding Algorithm": "A=v210", "Hardware Type": "DIO"}
    decklinkstudio4k_rack2 = {"Coding Algorithm": "A=v210", "Hardware Type": "DIO"}

    equipment_dict = {
        "Panasonic AG-1980P Rack 1": panasonic_ag1980_rack1,
        "Panasonic AG-1980P Rack 2": panasonic_ag1980_rack2,
        "DPS-295 Rack 1": dps_295_rack1,
        "DPS-575 Rack 2": dps_575_rack2,
        "HD10AVA Rack1": hd10ava_rack1,
        "HD10AVA Rack2": hd10ava_rack2,
        "Decklink Studio 4k Rack 1": decklinkstudio4k_rack1,
        "Decklink Studio 4K Rack 2": decklinkstudio4k_rack2,
    }

    return equipment_dict
