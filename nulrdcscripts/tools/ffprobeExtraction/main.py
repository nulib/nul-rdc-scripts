import os
import subprocess
import ctypes
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

def process_file(file_path, output_format):
    input_path = os.path.abspath(file_path)
    input_path_resolved = resolve_path(input_path)
    input_path_ffmpeg = input_path_resolved.replace("\\", "/")

    base_name = os.path.splitext(input_path)[0]
    video_stats_output_path = f"{base_name}_video_signalstats.{output_format}"
    audio_stats_output_path = f"{base_name}_audio_astats.{output_format}"

    # Video signalstats
    command_video = [
        "ffprobe",
        "-f", "lavfi",
        "-i", f"movie='{input_path_ffmpeg}',signalstats",
        "-show_frames",
        "-of", output_format
    ]

    # Audio astats
    command_audio = [
        "ffprobe",
        "-f", "lavfi",
        "-i", f"amovie='{input_path_ffmpeg}',astats=metadata=1:reset=1",
        "-show_frames",
        "-of", output_format
    ]

    video_output = run_ffprobe(command_video)
    audio_output = run_ffprobe(command_audio)

    with open(video_stats_output_path, "w", encoding="utf-8") as vfile:
        vfile.write(video_output)

    with open(audio_stats_output_path, "w", encoding="utf-8") as afile:
        afile.write(audio_output)

    return video_stats_output_path, audio_stats_output_path

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
            try:
                video_path, audio_path = future.result()
                print(f"Video stats: {video_path}")
                print(f"Audio stats: {audio_path}")
            except Exception as e:
                print(f"Error processing {futures[future]}: {e}")
            completed += 1
            bar.update(completed)

if __name__ == "__main__":
    main()
