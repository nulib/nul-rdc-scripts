def qc_results(inventoryCheck, losslessCheck, mediaconchResults):
    QC_results = {}
    QC_results["QC"] = {
        "Inventory Check": inventoryCheck,
        "Lossless Check": losslessCheck,
        "Mediaconch Results": mediaconchResults,
    }
    return QC_results
