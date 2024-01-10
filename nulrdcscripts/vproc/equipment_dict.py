#!/usr/bin/env python3


def equipment_dict():
    """
    VTRs
    """
    panasonic_ag1980R1 = {
        "Coding Algorithm": "A=ANALOG",
        "Output is one of": ["Composite", "S-Video"],
        "Additional Information": "T= Serial Number: JSTC00083 ; NUTag: 10518",
    }
    panasonic_ag1980R2 = {
        "Coding Algorithm": "A=ANALOG",
        "Output is one of": ["Composite", "S-Video"],
        "Additional Information": "T= Serial Number:  ; NUTag: ",
    }
    sony_svo5800R2 = {
        "Coding Algorithm": "A=ANALOG",
        "Output is one of": ["Composite", "S-Video"],
        "Additional Information": "T= Serial Number: 13570 or E0707415 ; NUTag: 95094",
    }
    """
    TBCs
    """
    dps_295 = {
        "Coding Algorithm": "A=ANALOG",
        "Hardware Type": "TBC",
        "Output is one of": ["Composite", "S-Video", "Component"],
        "Additional Information": "T= Serial Number: 9211295054 ; NUTag: 10517",
    }

    dps_575 = {
        "Coding Algorithm": "A=ANALOG",
        "Hardware Type": "TBC",
        "Output is one of": ["Composite", "S-Video", "Component"],
        "Additional Information": "T= Serial Number: LHTI0192186004 ; NUTag: 10697",
    }

    """
    ADCs
    """
    hd10avaR1 = {
        "Coding Algorithm": "A=SDI",
        "Hardware Type": "A/D",
        "Additional Information": "T= Serial Number: K0190697 ; NUTag: 10519",
    }
    hd10avaR2 = {
        "Coding Algorithm": "A=SDI",
        "Hardware Type": "A/D",
        "Additional Information": "T= Serial Number:  ; NUTag: ",
    }

    """
    Capture Cards
    """
    DecklinkStudio4KR1 = {
        "Coding Algorithm": "A=v210",
        "Hardware Type": "DIO",
        "Additional Information": "T= Serial Number:  ; NUTag: 11270",
    }
    DecklinkStudio4KR2 = {
        "Coding Algorithm": "A=v210",
        "Hardware Type": "DIO",
        "Additional Information": "T= Serial Number:  ; NUTag: 11269",
    }

    equipment_dict = {
        "Sony SVO 5800 Rack2": sony_svo5800R2,
        "Panasonic AG-1980P Rack1": panasonic_ag1980R1,
        "Panasonic AG-1980P Rack2": panasonic_ag1980R2,
        "DPS-295": dps_295,
        "DPS-575": dps_575,
        "HD10AVA Rack1": hd10avaR1,
        "HD10AVA Rack2": hd10avaR2,
        "Decklink Studio 4K Rack1": DecklinkStudio4KR1,
        "Decklink Studio 4K Rack2": DecklinkStudio4KR2,
    }

    return equipment_dict
