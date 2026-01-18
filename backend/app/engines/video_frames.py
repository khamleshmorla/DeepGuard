import cv2
import os
import tempfile


def extract_video_frames(
    video_path: str,
    max_frames: int = 15,
    interval_sec: float = 1.0
):
    """
    Extract frames from video at fixed time intervals.
    Returns list of image file paths.
    """

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        fps = 25  # fallback

    frame_interval = int(fps * interval_sec)
    frames = []

    count = 0
    saved = 0

    while cap.isOpened() and saved < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if count % frame_interval == 0:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            cv2.imwrite(tmp.name, frame)
            frames.append(tmp.name)
            saved += 1

        count += 1

    cap.release()
    return frames
