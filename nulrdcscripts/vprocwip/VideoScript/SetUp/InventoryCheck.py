def inventory_check(item_csvDict):
    if item_csvDict is None:
        print ("Unable to locate file in CSV data")
        inventoryCheck="FAIL"
    else:
        print ("Item found in inventory")
        inventoryCheck="PASS"
    return inventoryCheck