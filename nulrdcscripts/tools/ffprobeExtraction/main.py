import os
import subprocess
import ctypes
from concurrent.futures import ProcessPoolExecutor, as_completed
import progressbar
from nulrdcscripts.tools.ffprobeExtraction.params import args
import traceback

def get_unc_path(drive_letter):
    if not drive_letter.endswith(':'):
        drive_letter += ':'
    buffer = ctypes.create_unicode_buffer(1024)
    buffer_size = ctypes.c_ulong(len(buffer))
    try:
        result = ctypes.windll.mpr.WNetGetConnectionW(drive_letter, buffer, ctypes.byref(buffer_size))
        if result == 0:
            print(f"UNC path for {drive_letter}: {buffer.value}")
            return buffer.value
        else:
            print(f"Failed to resolve UNC path for {drive_letter}")
            return None
    except AttributeError:
        print("ctypes.windll.mpr.WNetGetConnectionW not available")
        return None

def resolve_path(path):
    drive, tail = os.path.splitdrive(path)
    unc = get_unc_path(drive)
    if unc:
        resolved = os.path.join(unc, tail.lstrip("\\/"))
        print(f"Resolved path: {resolved}")
        return resolved
    else:
        print(f"Could not resolve UNC path for: {path}")
        return path

def run_ffprobe(command):
    print(f"Running ffprobe command: {' '.join(command)}")
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
    print(f"ffprobe output (truncated): {result.stdout[:500]}")  # Show first 500 chars
    return result.stdout

def process_file(file_path, output_format):
    print(f"Processing file: {file_path}")
    input_path = os.path.abspath(file_path)
    input_path_resolved = resolve_path(input_path)
    input_path_ffmpeg = input_path_resolved.replace("\\", "/")

    base_name = os.path.splitext(input_path)[0]
    video_stats_output_path = f"{base_name}_video_signalstats.csv"

    # QCTools-style filtergraph for direct input
    filter_complex = (
        "signalstats=stat=tout+vrep+brng,"
        "cropdetect=reset=1:round=1,"
        "idet=half_life=1,"
        "deflicker=bypass=1,"
        "split[a][b];"
        "[a]field=top[a1];"
        "[b]field=bottom,split[b1][b2];"
        "[a1][b1]psnr[c1];"
        "[c1][b2]ssim[out0];"
        "[0:a]ebur128=metadata=1,"
        "aformat=sample_fmts=flt|fltp:channel_layouts=stereo,"
        "astats=metadata=1:reset=1:length=0.4[out1]"
    )

    command_video = [
        "ffmpeg",
        "-hide_banner",
        "-nostats",
        "-loglevel", "error",
        "-y",
        "-i", input_path_ffmpeg,
        "-filter_complex", filter_complex,
        "-map", "[out0]",
        "-map", "[out1]",
        "-f", "csv",
        video_stats_output_path
    ]

    print(f"Running ffmpeg command: {' '.join(command_video)}")
    try:
        result = subprocess.run(
            command_video,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )
        if result.returncode != 0:
            print(f"ffmpeg error: {result.stderr}")
            return None
        print(f"Saved ffmpeg output to {video_stats_output_path}")
        return video_stats_output_path
    except Exception as e:
        print(f"Error running ffmpeg for {file_path}: {e}")
        return None

def main():
    print(f"Input path from args: {args.input_path}")
    output_format = args.output_format.lower()
    if output_format not in ["json", "xml"]:
        raise ValueError("Only 'json' or 'xml' formats are supported.")

    files_to_process = []
    if os.path.isdir(args.input_path):
        for root, _, files in os.walk(args.input_path):
            for file in files:
                if file.lower().endswith(".mkv"):
                    full_path = os.path.join(root, file)
                    print(f"Found MKV file: {full_path}")
                    files_to_process.append(full_path)
    elif os.path.isfile(args.input_path) and args.input_path.lower().endswith(".mkv"):
        print(f"Single MKV file to process: {args.input_path}")
        files_to_process.append(args.input_path)
    else:
        print(f"Error: '{args.input_path}' is not a valid .mkv file or directory.")
        return

    print(f"Total files to process: {len(files_to_process)}")
    if not files_to_process:
        print("No MKV files found. Exiting.")
        return

    bar = progressbar.ProgressBar(max_value=len(files_to_process))
    completed = 0

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(process_file, file_path, output_format): file_path for file_path in files_to_process}
        for future in as_completed(futures):
            try:
                video_path = future.result()
                print(f"Video stats: {video_path}")
            except Exception as e:
                print(f"Error processing {futures[future]}: {e}")
                traceback.print_exc()
            completed += 1
            bar.update(completed)

if __name__ == "__main__":
    main()