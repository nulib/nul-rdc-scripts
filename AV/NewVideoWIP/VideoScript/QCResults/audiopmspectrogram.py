from spectrograms import generate_spectrogram as generate_spectrogram
from VideoScript.SetUp.Arguments import args

if audiostreamCounter > 0 and not args.skip_spectrogram:
    print("*generating QC spectrograms*")
    channel_layout_list = input_metadata["techMetaA"]["channels"]
    generate_spectrogram(
        output_AbsPath, channel_layout_list, metaOutputFolder, baseFilename
    )
