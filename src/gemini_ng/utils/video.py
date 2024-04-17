import math

import av
from PIL import Image


def extract_video_frames(video_path: str, save_dir: str, sample_fps: int = 1) -> list[str]:
    container = av.open(video_path)
    video_stream = container.streams.video[0]

    fps = video_stream.guessed_rate.numerator / video_stream.guessed_rate.denominator

    frame_interval = fps / sample_fps

    step_time = _frame_to_stamp(frame_interval, video_stream)

    frame_paths = _extract_video_frames(
        container, video_stream, save_dir, step_time, seekable=True
    )

    if frame_paths is None:
        frame_paths = _extract_video_frames(
            container, video_stream, save_dir, step_time, seekable=False
        )

    return frame_paths


def _extract_video_frames(
    container: "av.InputContainer",
    video_stream,
    save_dir: str,
    step_time: int,
    seekable: bool,
) -> list[str] | None:
    cur = 0
    seek_target = 0
    frame_paths = []

    for packet in container.demux(video=0):
        if packet.dts is None:
            continue

        for frame in packet.decode():
            if packet.pts and packet.pts >= seek_target:
                frame = frame.to_ndarray(format="rgb24")
                frame = Image.fromarray(frame)
                frame_path = f"{save_dir}/{cur:06d}.jpg"
                frame.save(frame_path)
                frame_paths.append(frame_path)
                cur += 1

                seek_target += step_time
                if seekable:
                    try:
                        container.seek(seek_target, stream=video_stream)
                    except av.error.FFmpegError:
                        return None

    return frame_paths


def _frame_to_stamp(nframe: int, stream) -> int:
    """Convert frame number to timestamp based on fps of video stream."""
    fps = stream.guessed_rate.numerator / stream.guessed_rate.denominator
    seek_target = nframe / fps
    stamp = math.floor(
        seek_target * (stream.time_base.denominator / stream.time_base.numerator)
    )
    return stamp
