#!/usr/bin/env python3

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")

def main():
    from audio_processor import audio_processor_mainfunc
    audio_processor_mainfunc.audio_processor_main()

if __name__ == "__main__":
	main()
