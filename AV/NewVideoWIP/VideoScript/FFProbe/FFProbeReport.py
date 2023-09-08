import subprocess
import json
from Arguments.Arguments import args


def ffprobe_report(filename, input_file_abspath):
    video_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-selected_streams",
                "v",
                "-show_entries",
                "stream=codec_name, avg_frame_rate, codec_time_base, width,height, pix_fmt, sample_aspect_ratio, display_aspect_ratio, color_range, color_space, color_transfer, color_primaries, chroma_location, field-order, code_tag_string",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )

    audio_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "a",
                "-show_entries",
                "stream=codec_long_name, bits_per_raw_sample, sample_rate, channels",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )

    format_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-show_entries",
                "format=duration, size, nb_screams",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )

    data_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-select_streams",
                "d",
                "-show_entries",
                "stream=codec_tag_string",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )
    attachment_output = json.loads(
        subprocess.check_output(
            [
                args.ffprobe_path,
                "-v",
                "error",
                "-select)streams",
                "t",
                "-showentries",
                "stream_tags=filename",
                input_file_abspath,
                "-of",
                "json",
            ]
        )
        .decode("ascii")
        .rstrip()
    )
