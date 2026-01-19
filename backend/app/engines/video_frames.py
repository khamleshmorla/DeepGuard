import cv2
import os
import tempfile


def extract_video_frames(
    video_path: str,
    max_frames: int = 15,
    interval_sec: float = 1.0
):
    """
    Extract stable frames from video at fixed time intervals.
    Skips overly blurry frames.
    """
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    frame_interval = int(fps * interval_sec)
    frames = []

    count = 0
    saved = 0
    tmp_dir = tempfile.mkdtemp()

    while cap.isOpened() and saved < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if count % frame_interval == 0:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Skip extremely blurry frames
            if blur < 50:
                count += 1
                continue

            path = os.path.join(tmp_dir, f"frame_{saved}.jpg")
            cv2.imwrite(path, frame)
            frames.append(path)
            saved += 1

        count += 1

    cap.release()
    return frames
