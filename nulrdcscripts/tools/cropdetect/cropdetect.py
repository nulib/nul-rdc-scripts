import subprocess
import os
import re
from nulrdcscripts.tools.cropdetect.params import args
from collections import Counter


def parse_cropdetect_output(output):
    crop_pattern = re.compile(r"crop=(\d+:\d+:\d+:\d+)")
    crops = crop_pattern.findall(output)
    return crops


def most_frequent_crop(crops):
    return Counter(crops).most_common(1)[0][0]


def largest_crop_box(crops):
    max_w = max_h = max_x = max_y = 0
    for crop in crops:
        w, h, x, y = map(int, crop.split(":"))
        max_w = max(max_w, w + x)
        max_h = max(max_h, h + y)
    min_x = min_y = float("inf")
    for crop in crops:
        w, h, x, y = map(int, crop.split(":"))
        min_x = min(min_x, x)
        min_y = min(min_y, y)
    final_w = max_w - min_x
    final_h = max_h - min_y
    return f"{final_w}:{final_h}:{min_x}:{min_y}"


def run_cropdetect(input_file):
    cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-vf",
        "cropdetect=24:16:0",
        "-frames:v",
        "500",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(
        cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True
    )
    return result.stderr


def crop_video(input_file, crop_value, suffix):
    base, ext = os.path.splitext(input_file)
    output_file = f"{base}_{suffix}{ext}"
    cmd = [
        "ffmpeg",
        "-i",
        input_file,
        "-vf",
        f"crop={crop_value}",
        "-c:a",
        "copy",
        output_file,
    ]
    subprocess.run(cmd)
    return output_file


def main():
    input_file = args.input_path
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    print("Running cropdetect...")
    output = run_cropdetect(input_file)
    crops = parse_cropdetect_output(output)

    if not crops:
        print("No crop values detected.")
        return

    print("Calculating most frequent crop...")
    most_common = most_frequent_crop(crops)
    print(f"Most frequent crop: {most_common}")

    print("Calculating largest crop box...")
    largest_box = largest_crop_box(crops)
    print(f"Largest crop box: {largest_box}")

    print("Cropping video using most frequent crop...")
    crop_video(input_file, most_common, "most_frequent_crop")

    print("Cropping video using largest crop box...")
    crop_video(input_file, largest_box, "largest_crop_box")

    print("Done.")


if __name__ == "__main__":
    main()
