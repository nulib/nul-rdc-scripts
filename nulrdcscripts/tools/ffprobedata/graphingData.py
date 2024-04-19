import nulrdcscripts.tools.ffprobedata
import json


def cleanJSON(file):
    data = json.load(file)
    to_pop = [
        "media_type",
        "stream_index",
        "key_frame",
        "pts",
        "pkt_dts",
        "pkt_dts_time",
        "best_effort_timestamp",
        "best_effort_timestamp_time",
        "pkt_duration",
        "pkt_duration_time",
        "pkt_pos",
        "pkt_size",
        "width",
        "height",
        "crop_top",
        "crop_bottom",
        "crop_left",
        "crop_right",
        "pix_fmt",
        "sample_aspect_ratio",
        "pict_type",
        "coded_picture_number",
        "interlaced_frame",
        "top_field_first",
        "repeat_pict",
        "color_range",
        "color_space",
        "color_primaries",
        "color_transfer",
        "chroma_location",
    ]
    i = 0
    while i < len(to_pop):
        remove = to_pop[i]
        data = data.pop(remove)
        i += 1
