Version Date: 05/04/2024

Document Owner: Sophia Francis

Software Used: ffmpeg

# Description
This is a video trimmer script that can be used as a module for another script or solo.


# Installation Instructions
This script runs through poetry and can be installed and updated from it. 

## Usage

### Trim the beginning of the video: 

- HH:MM:SS should be where you want the video to start
    ```
    poetry run videotrimmer -i \path\to\input -s HH:MM:SS
    ```
### Trim the end of the video or between to points:
- HH:MM:SS(a) should be where you want the video to start
    - If not given <u>00:00:00</u> is utilized
- HH:MM:SS(b) should be where you want the video to end

    ```
    poetry run videotrimmer -i \path\to\input -s HH:MM:SS(a) -e HH:MM:SS(b)
    ```

### If you need to use a unique ffmpeg path (default uses ffmpeg from path)
- Follow the examples above depending on what you are trying to do
- At the end add:
    ```
    -ffmpeg </path/to/ffmpeg>
    ```