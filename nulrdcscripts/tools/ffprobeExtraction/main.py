import os
import subprocess
import ctypes
import json
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed
import progressbar
from nulrdcscripts.tools.ffprobeExtraction.params import args

def get_unc_path(drive_letter):
    if not drive_letter.endswith(':'):
        drive_letter += ':'
    buffer = ctypes.create_unicode_buffer(1024)
    buffer_size = ctypes.c_ulong(len(buffer))
    try:
        result = ctypes.windll.mpr.WNetGetConnectionW(drive_letter, buffer, ctypes.byref(buffer_size))
        if result == 0:
            return buffer.value
        else:
            return None
    except AttributeError:
        return None

def resolve_path(path):
    drive, tail = os.path.splitdrive(path)
    unc = get_unc_path(drive)
    if unc:
        return os.path.join(unc, tail.lstrip("\\/"))
    else:
        return path

def run_ffprobe(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    return result.stdout

def merge_json_outputs(signalstats_data, metadata_data):
    signalstats_json = json.loads(signalstats_data)
    metadata_json = json.loads(metadata_data)
    merged = {
        "signalstats": signalstats_json,
        "metadata": metadata_json
    }
    return json.dumps(merged, indent=2)

def merge_xml_outputs(signalstats_data, metadata_data):
    signalstats_xml = ET.fromstring(signalstats_data)
    metadata_xml = ET.fromstring(metadata_data)
    root = ET.Element("ffprobe")
    root.append(signalstats_xml)
    root.append(metadata_xml)
    return ET.tostring(root, encoding="unicode")

def process_file(file_path, output_format):
    input_path = os.path.abspath(file_path)
    input_path_resolved = resolve_path(input_path)
    input_path_ffmpeg = input_path_resolved.replace("\\", "/")
    output_path = os.path.splitext(input_path)[0] + "_merged." + output_format

    command_signalstats = [
        "ffprobe",
        "-f", "lavfi",
        "-i", f"movie='{input_path_ffmpeg}',signalstats",
        "-show_frames",
        "-of", output_format
    ]

    command_metadata = [
        "ffprobe",
        "-i", input_path_ffmpeg,
        "-show_streams",
        "-show_format",
        "-of", output_format
    ]

    signalstats_output = run_ffprobe(command_signalstats)
    metadata_output = run_ffprobe(command_metadata)

    if output_format == "json":
        merged_output = merge_json_outputs(signalstats_output, metadata_output)
    else:
        merged_output = merge_xml_outputs(signalstats_output, metadata_output)

    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(merged_output)

    return output_path

def main():
    input_path = args.input_path
    output_format = args.output_format.lower()
    if output_format not in ["json", "xml"]:
        raise ValueError("Only 'json' or 'xml' formats are supported.")

    files_to_process = []
    if os.path.isdir(input_path):
        for root, _, files in os.walk(input_path):
            for file in files:
                if file.lower().endswith(".mkv"):
                    files_to_process.append(os.path.join(root, file))
    elif os.path.isfile(input_path) and input_path.lower().endswith(".mkv"):
        files_to_process.append(input_path)
    else:
        print(f"Error: '{input_path}' is not a valid .mkv file or directory.")
        return

    bar = progressbar.ProgressBar(max_value=len(files_to_process))
    completed = 0

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_file, file_path, output_format): file_path for file_path in files_to_process}
        for future in as_completed(futures):
            result_path = future.result()
            completed += 1
            bar.update(completed)
            print(f"Processed: {result_path}")

if __name__ == "__main__":
    main()
