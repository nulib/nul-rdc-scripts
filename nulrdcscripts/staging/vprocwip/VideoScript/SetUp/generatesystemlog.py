import platform


def generate_system_log(ffvers, tstime, tftime):
    osinfo = platform.platform()
    systemInfo = {
        "operating system": osinfo,
        "ffmpeg version": ffvers,
        "transcode start time": tstime,
        "transcode end time": tftime,
    }
    return systemInfo
