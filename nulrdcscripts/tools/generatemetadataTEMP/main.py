import subprocess
import json
import sys
import os
from nulrdcscripts.tools.generatemetadataTEMP.params import args


def generate_ffprobe_report(file_path):
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=filename,size,duration",
        "-show_streams",
        "-show_format",
        "-print_format",
        "json",
        file_path,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return json.loads(result.stdout)


def extract_technical_metadata(streams):
    video_metadata = {}
    audio_metadata = {
        "audio stream count": 0,
        "audio bitrate (kbps)": [],
        "audio sample rate (Hz)": [],
        "channels": [],
        "audio streams": [],
    }
    data_streams = []
    attachments = []

    audio_codec_full_names = {
        "pcm_s16le": "PCM signed 16-bit little-endian",
        "pcm_s24le": "PCM signed 24-bit little-endian",
        "aac": "Advanced Audio Coding (AAC)",
        # Add more codec full names as needed
    }

    for stream in streams:
        if stream["codec_type"] == "video":
            video_metadata = {
                "width": stream.get("width", ""),
                "height": stream.get("height", ""),
                "sample aspect ratio": stream.get("sample_aspect_ratio", ""),
                "display aspect ratio": stream.get("display_aspect_ratio", ""),
                "pixel format": stream.get("pix_fmt", ""),
                "framerate": stream.get("r_frame_rate", ""),
                "color space": stream.get("color_space", ""),
                "color range": stream.get("color_range", None),
                "color primaries": stream.get("color_primaries", ""),
                "color transfer": stream.get("color_transfer", ""),
            }
        elif stream["codec_type"] == "audio":
            audio_metadata["audio stream count"] += 1
            audio_metadata["audio bitrate (kbps)"].append(
                f"{int(stream.get('bit_rate', 0)) / 1000:.2f} kbps"
            )
            audio_metadata["audio sample rate (Hz)"].append(
                f"{stream.get('sample_rate', '')} Hz"
            )
            audio_metadata["channels"].append(stream.get("channels", ""))

            codec_name = stream.get("codec_name", "")
            full_name = audio_codec_full_names.get(codec_name, codec_name)
            audio_metadata["audio streams"].append(full_name)

        elif stream["codec_type"] == "data":
            data_streams.append(stream.get("codec_name", ""))
        elif stream["codec_type"] == "attachment":
            attachments.append(stream.get("filename", ""))

    return video_metadata, audio_metadata, data_streams, attachments


def create_json_report(preservation_data, access_data):
    (
        preservation_video_metadata,
        preservation_audio_metadata,
        preservation_data_streams,
        preservation_attachments,
    ) = extract_technical_metadata(preservation_data.get("streams", []))
    (
        access_video_metadata,
        access_audio_metadata,
        access_data_streams,
        access_attachments,
    ) = extract_technical_metadata(access_data.get("streams", []))

    report = {
        "": [
            {
                "inventory metadata": {
                    "accession number/call number": "",
                    "box/folder alma number": "",
                    "barcode": "",
                    "description": "",
                    "record date": "",
                    "housing/container markings": "",
                    "condition notes": "",
                    "format": "",
                    "staff initials": "",
                    "capture date": "",
                    "coding history": [
                        "Sony SVO-5800; 10516; JVC; SP; NTSC; Component",
                        "Sony SVO-5800; 10516; Component",
                        "AJA HD10AVA; K0159767",
                        "DeckLink Studio 4K",
                    ],
                    "sound note": [""],
                    "capture notes": "",
                }
            },
            {
                "system information": {
                    "operating system": os.name,
                    "ffmpeg version": preservation_data.get("format", {}).get(
                        "format_long_name", ""
                    ),
                    "transcode start time": "",
                    "transcode end time": "",
                }
            },
            {
                "preservation-file metadata": {
                    "filename": preservation_data.get("format", {}).get("filename", ""),
                    "file size (bytes)": f"{preservation_data.get('format', {}).get('size', '')} bytes",
                    "duration (seconds)": f"{preservation_data.get('format', {}).get('duration', '')} seconds",
                    "streams": len(preservation_data.get("streams", [])),
                    "video streams": [
                        stream["codec_name"]
                        for stream in preservation_data.get("streams", [])
                        if stream["codec_type"] == "video"
                    ],
                    "audio streams": preservation_audio_metadata["audio streams"],
                    "data streams": preservation_data_streams,
                    "attachments": preservation_attachments,
                    "md5 checksum": "",
                    "a/v streamMD5s": [],
                }
            },
            {
                "access-file metadata": {
                    "filename": access_data.get("format", {}).get("filename", ""),
                    "file size (bytes)": f"{access_data.get('format', {}).get('size', '')} bytes",
                    "duration (seconds)": f"{access_data.get('format', {}).get('duration', '')} seconds",
                    "streams": len(access_data.get("streams", [])),
                    "video streams": [
                        stream["codec_name"]
                        for stream in access_data.get("streams", [])
                        if stream["codec_type"] == "video"
                    ],
                    "audio streams": access_audio_metadata["audio streams"],
                    "data streams": access_data_streams,
                    "attachments": access_attachments,
                    "md5 checksum": "",
                    "a/v streamMD5s": [],
                }
            },
            {
                "technical metadata": [
                    {"video": preservation_video_metadata},
                    {"audio": preservation_audio_metadata},
                ]
            },
            {"QC": {"inventory check": "PASS"}},
        ]
    }
    return report


def find_files(directory, extensions):
    files_list = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                files_list.append(os.path.join(root, file))
    return files_list


def main():
    input_path = os.path.abspath(args.input_path)

    if os.path.isdir(input_path):
        mkv_files = find_files(input_path, (".mkv",))
        mp4_files = find_files(input_path, (".mp4",))

        if not mkv_files or not mp4_files:
            print("No .mkv or .mp4 files found in the directory.")
            return

        preservation_file = mkv_files[0]
        access_file = mp4_files[0]

    else:
        preservation_file = input_path
        access_file = os.path.abspath(sys.argv[2])

    # Get the input directory
    input_directory = (
        os.path.dirname(input_path) if os.path.isfile(input_path) else input_path
    )

    preservation_data = generate_ffprobe_report(preservation_file)
    access_data = generate_ffprobe_report(access_file)
    report = create_json_report(preservation_data, access_data)

    # Write the JSON report to the input directory
    output_path = os.path.join(input_directory, "report.json")
    with open(output_path, "w") as f:
        json.dump(report, f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_path> [<access_file>]")
    else:
        main()
