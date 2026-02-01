import cv2
import sys
import numpy as np

# Optional YOLO dependency (Ultralytics)
# pip install ultralytics
try:
    from ultralytics import YOLO
except Exception:
    YOLO = None


def _safe_half_fps(fps: float) -> int:
    # Use a safe integer FPS for output; avoid 0 FPS.
    if fps is None or fps <= 0:
        return 15
    return max(1, int(round(fps / 2)))


def _quantize_colors(img: np.ndarray, levels: int) -> np.ndarray:
    """
    Reduce color diversity (lower entropy) to make patches more similar.
    levels: 2..256. Lower = stronger compression.
    """
    levels = int(levels)
    if levels <= 1:
        return img
    step = max(1, 256 // levels)
    return (img // step) * step


def _compress_background(
    frame_bgr: np.ndarray,
    bg_scale: float = 0.125,
    blur_ksize: int = 9,
    quantize_levels: int = 32
) -> np.ndarray:
    """
    Background entropy collapse:
    - downscale aggressively then upscale (destroys fine detail)
    - blur (removes high-frequency edges)
    - optional color quantization (reduces patch diversity)
    """
    h, w = frame_bgr.shape[:2]

    # Aggressive downscale -> upscale
    s = float(bg_scale)
    s = min(max(s, 0.05), 1.0)  # clamp
    small_w = max(1, int(w * s))
    small_h = max(1, int(h * s))

    small = cv2.resize(frame_bgr, (small_w, small_h), interpolation=cv2.INTER_AREA)
    bg = cv2.resize(small, (w, h), interpolation=cv2.INTER_LINEAR)

    # Blur (odd kernel size required)
    k = int(blur_ksize)
    if k < 0:
        k = 0
    if k % 2 == 0:
        k += 1
    if k >= 3:
        bg = cv2.GaussianBlur(bg, (k, k), 0)

    # Color quantization
    if quantize_levels and quantize_levels < 256:
        bg = _quantize_colors(bg, quantize_levels)

    return bg


def _make_importance_mask(
    frame_shape,
    boxes_xyxy,
    dilate_px: int = 12
) -> np.ndarray:
    """
    Build a soft-ish binary mask from YOLO boxes: foreground=1, background=0.
    Dilate to keep some context around objects.
    """
    h, w = frame_shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)

    for (x1, y1, x2, y2) in boxes_xyxy:
        x1 = max(0, min(w - 1, int(x1)))
        y1 = max(0, min(h - 1, int(y1)))
        x2 = max(0, min(w - 1, int(x2)))
        y2 = max(0, min(h - 1, int(y2)))
        if x2 > x1 and y2 > y1:
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, thickness=-1)

    if dilate_px and dilate_px > 0:
        k = int(dilate_px) * 2 + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        mask = cv2.dilate(mask, kernel, iterations=1)

    # Convert to float alpha [0,1]
    alpha = mask.astype(np.float32) / 255.0
    alpha = np.expand_dims(alpha, axis=2)
    return alpha


def _signature_from_boxes(boxes_xyxy, round_to: int = 10) -> str:
    """
    Create a stable "scene signature" from detections to compare frames.
    """
    if boxes_xyxy is None or len(boxes_xyxy) == 0:
        return "none"
    arr = []
    for (x1, y1, x2, y2) in boxes_xyxy:
        arr.append((
            int(round(x1 / round_to) * round_to),
            int(round(y1 / round_to) * round_to),
            int(round(x2 / round_to) * round_to),
            int(round(y2 / round_to) * round_to),
        ))
    arr.sort()
    return str(arr)


def _motion_score(prev_small_gray: np.ndarray, curr_small_gray: np.ndarray) -> float:
    """
    Simple motion metric: mean absolute difference on small grayscale frames.
    """
    diff = cv2.absdiff(prev_small_gray, curr_small_gray)
    return float(np.mean(diff))


def reduce_video(
    input_path: str,
    yolo_model_path: str = "yolo11n.pt",   # change to your YOLOv11 weight file
    use_yolo: bool = True,
    out_scale: float = 0.5,               # final output resolution scale
    base_skip: int = 2,                   # keep every Nth frame (2 = keep every other)
    motion_thresh: float = 2.0,           # lower = more aggressive skipping
    bg_scale: float = 0.125,
    blur_ksize: int = 9,
    quantize_levels: int = 32
):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print("Cannot open video")
        return

    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(3))
    height = int(cap.get(4))

    out_w = max(1, int(width * out_scale))
    out_h = max(1, int(height * out_scale))
    out_fps = _safe_half_fps(fps)

    output_path = input_path.replace(".mp4", "_reduced.mp4")

    # Load YOLO model if available/desired
    model = None
    if use_yolo:
        if YOLO is None:
            print("Ultralytics not installed. Run: pip install ultralytics")
            print("Continuing without YOLO (only basic frame skip + resize).")
            use_yolo = False
        else:
            try:
                model = YOLO(yolo_model_path)
            except Exception as e:
                print(f"Failed to load YOLO model '{yolo_model_path}': {e}")
                print("Continuing without YOLO (only basic frame skip + resize).")
                use_yolo = False

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, out_fps, (out_w, out_h))

    frame_id = 0
    prev_sig = None
    prev_small_gray = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Base temporal reduction (keeps every Nth frame)
        if frame_id % base_skip != 0:
            frame_id += 1
            continue

        # Prepare small grayscale for motion scoring (cheap)
        small_for_motion = cv2.resize(frame, (160, 90), interpolation=cv2.INTER_AREA)
        curr_small_gray = cv2.cvtColor(small_for_motion, cv2.COLOR_BGR2GRAY)

        # Semantic detection (YOLO) to build importance mask
        boxes_xyxy = []
        if use_yolo and model is not None:
            # Ultralytics returns results list
            results = model.predict(frame, verbose=False)
            r = results[0]
            if r.boxes is not None and len(r.boxes) > 0:
                xyxy = r.boxes.xyxy.cpu().numpy()
                for b in xyxy:
                    boxes_xyxy.append((b[0], b[1], b[2], b[3]))

        # Semantic frame skipping: skip if (low motion) AND (same detection signature)
        curr_sig = _signature_from_boxes(boxes_xyxy)
        if prev_small_gray is not None and prev_sig is not None:
            m = _motion_score(prev_small_gray, curr_small_gray)
            if (m < motion_thresh) and (curr_sig == prev_sig):
                # Skip writing this frame (extra token reduction)
                frame_id += 1
                continue

        # Build a semantic-aware frame:
        # - foreground: keep original (object regions)
        # - background: collapse entropy heavily (downscale+blur+quantize)
        if use_yolo and len(boxes_xyxy) > 0:
            bg = _compress_background(
                frame,
                bg_scale=bg_scale,
                blur_ksize=blur_ksize,
                quantize_levels=quantize_levels
            )
            alpha = _make_importance_mask(frame.shape, boxes_xyxy, dilate_px=12)
            sem = (frame.astype(np.float32) * alpha + bg.astype(np.float32) * (1.0 - alpha)).astype(np.uint8)
        else:
            # If no detections, compress whole frame more strongly (still reduces token diversity)
            sem = _compress_background(
                frame,
                bg_scale=bg_scale,
                blur_ksize=blur_ksize,
                quantize_levels=quantize_levels
            )

        # Final spatial reduction (classic token reduction)
        out_frame = cv2.resize(sem, (out_w, out_h), interpolation=cv2.INTER_AREA)
        out.write(out_frame)

        prev_sig = curr_sig
        prev_small_gray = curr_small_gray
        frame_id += 1

    cap.release()
    out.release()
    print("Saved:", output_path)


if __name__ == "__main__":
    # Usage:
    #   python reducer.py input.mp4
    # Optional: edit defaults inside reduce_video(), especially yolo_model_path.
    video = sys.argv[1]
    reduce_video(video)
