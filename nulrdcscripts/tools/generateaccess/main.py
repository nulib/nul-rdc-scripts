import os
from nulrdcscripts.tools.generateaccess.params import args


def main():
    input_path = os.path.abspath(args.input_path)
    if os.path.isdir(input_path):
        for folder in os.scandir(input_path):
            if folder.is_dir():
                for subfolder in os.scandir(folder.path):
                    if subfolder.is_dir():
                        for file in os.scandir(subfolder.path):
                            if file.name.endswith(".mkv"):
                                transcode(file.path)
                            else:
                                raise Exception(
                                    "This type of file is not supported for transcoding by this script"
                                )
            else:
                if folder.name.endswith(".mkv"):
                    transcode(folder.path)
                else:
                    raise Exception(
                        "This type of file is not supported for transcoding by this script"
                    )


def transcode(file_path):
    transcode_pass = [1, 2]
    outfile = file_path.replace("_p.mkv", "_a.mp4")
    for item in transcode_pass:
        standard_input = f"-c:v libx264 -preset medium -b:v 8000k -pass {item} -filter_complex '[0:a:0]aformat=channel_layouts=stereo[a0];[0:a:1]aformat=channel_layouts=stereo[a1]; amerge=inputs=2[a]' -map 0:v -map '[a]' -map -0:t -f mp4"
        if item == 1:
            command = f"ffmpeg -y -i {file_path} {standard_input} nul"
        else:
            command = f"ffmpeg -y -i {file_path} {standard_input} {outfile}"
        os.system(command)


if __name__ == "__main__":
    main()
