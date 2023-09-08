from Arguments.Arguments import args
import FFProbeReport


def ffprobemetadata():
    video_codec_name_list = [
        stream.get("codec_name") for stream in (FFProbeReport.video_output["streams"])
    ]
    audio_codec_name_list = [
        stream.get("codec_long_name")
        for stream in (FFProbeReport.audio_output["streams"])
    ]
    data_streams = [
        stream.get("codec_tag_string") for stream in ("data_output"["streams"])
    ]
    width = [stream.get("width") for stream in (FFProbeReport.video_output["streams"])][
        0
    ]
    height = [
        stream.get("height") for stream in (FFProbeReport.video_output["streams"])
    ][0]
    pixel_format = [
        stream.get("pix_fmt") for stream in (FFProbeReport.video_output["streams"])
    ][0]
    sar = [
        stream.get("sample_aspect_ratio")
        for stream in (FFProbeReport.video_output["streams"])
    ][0]
    dar = [
        stream.get("display_aspect_ratio")
        for stream in (FFProbeReport.video_output["streams"])
    ][0]
    framerate = [
        stream.get("avg_frame_rate")
        for stream in (FFProbeReport.video_output["streams"])
    ][0]
    color_space = [
        stream.get("color_space") for stream in (FFProbeReport.video_output["streams"])
    ][0]
    color_range = [
        stream.get("color_range") for stream in (FFProbeReport.video_output["streams"])
    ][0]
    color_transfer = [
        stream.get("color_transfer")
        for stream in (FFProbeReport.video_output["streams"])
    ][0]
    color_primaries = [
        stream.get("color_primaries")
        for stream in (FFProbeReport.video_output["streams"])
    ][0]
    audio_bitrate = [
        stream.get("bits_per_raw_sample")
        for stream in (FFProbeReport.audio_output["streams"])
    ][0]
    audio_sample_rate = [
        stream.get("sample_rate") for stream in (FFProbeReport.audio_output["streams"])
    ][0]
    audio_channels = [
        stream.get("channels") for stream in (FFProbeReport.audio_output["streams"])
    ][0]
    audio_stream_count = len(audio_codec_name_list)

    tags = [
        streams.get("tags") for streams in (FFProbeReport.attachment_output["streams"])
    ]
    attachment_list = []
    for i in tags:
        attachmentFilename = [i.get("filename")]
        attachment_list.extend(attachmentFilename)

    file_metadata = {
        "filename": filename,
        "filesize": FFProbeReport.format_output.get("format")["size"],
        "duration": FFProbeReport.format_output.get("format")["duration"],
        "streams": FFProbeReport.format_output.get("format")["nb_streams"],
        "video streams": video_codec_name_list,
        "audio streams": audio_codec_name_list,
        "data streams": data_streams,
        "attachments": attachment_list,
    }

    techMetaV = {
        "width": width,
        "height": height,
        "sample aspect ratio": sar,
        "display aspect ratio": dar,
        "pixel format": pixel_format,
        "framerate": framerate,
        "color space": color_space,
        "color range": color_range,
        "color primaries": color_primaries,
        "color transfer": color_transfer,
    }

    techMetaA = {
        "audio stream count": audio_stream_count,
        "audio bitrate": audio_bitrate,
        "audio sample rate": audio_sample_rate,
        "channels": audio_channels,
    }

    ffprobe_metadata = {
        "file metadata": file_metadata,
        "techMetaV": techMetaV,
        "techMetaA": techMetaA,
    }

    return ffprobe_metadata
