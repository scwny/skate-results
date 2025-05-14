import cv2
import numpy as np
from django.core.files.base import ContentFile
from huggingface_hub import hf_hub_download
from doclayout_yolo import YOLOv10

# Load pretrained YOLO document layout model
model_path = hf_hub_download(
    repo_id="juliozhao/DocLayout-YOLO-DocStructBench",
    filename="doclayout_yolo_docstructbench_imgsz1024.pt"
)
model = YOLOv10(model_path)

def scan_trim_boundary(gray, axis="top", max_trim=0.08, dark_thresh=160, bright_thresh=200, sustain_count=10):
    """
    Scans from one edge and trims dark rows/cols if followed by bright content.
    Returns start and end indices to slice the image cleanly.
    """
    h, w = gray.shape
    limit_y = int(h * max_trim)
    limit_x = int(w * max_trim)

    if axis == "top":
        for y in range(limit_y):
            if np.mean(gray[y, :]) < dark_thresh:
                # Check if followed by bright block
                if all(np.mean(gray[y+i, :]) > bright_thresh for i in range(1, sustain_count) if y+i < h):
                    return y, h
        return 0, h

    elif axis == "bottom":
        for y in range(h - 1, h - limit_y - 1, -1):
            if np.mean(gray[y, :]) < dark_thresh:
                if all(np.mean(gray[y-i, :]) > bright_thresh for i in range(1, sustain_count) if y-i >= 0):
                    return 0, y
        return 0, h

    elif axis == "left":
        for x in range(limit_x):
            if np.mean(gray[:, x]) < dark_thresh:
                if all(np.mean(gray[:, x+i]) > bright_thresh for i in range(1, sustain_count) if x+i < w):
                    return x, w
        return 0, w

    elif axis == "right":
        for x in range(w - 1, w - limit_x - 1, -1):
            if np.mean(gray[:, x]) < dark_thresh:
                if all(np.mean(gray[:, x-i]) > bright_thresh for i in range(1, sustain_count) if x-i >= 0):
                    return 0, x
        return 0, w

    return 0, h if axis in ["top", "bottom"] else w


def detect_and_crop_document(django_file):
    # Decode image from Django file
    image_data = np.frombuffer(django_file.read(), np.uint8)
    img = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

    # Detect document with YOLO
    results = model.predict(img, imgsz=1024, conf=0.2, device="cpu")
    if not results or not results[0].boxes:
        raise ValueError("No document detected.")

    boxes = results[0].boxes.xyxy.cpu().numpy()
    if boxes.shape[0] == 0:
        raise ValueError("No bounding boxes found.")

    # Use largest detected bounding box
    areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
    x1, y1, x2, y2 = boxes[np.argmax(areas)].astype(int)

    # Shrink slightly to avoid bounding box slop
    margin = 10
    x1 = max(x1 + margin, 0)
    y1 = max(y1 + margin, 0)
    x2 = min(x2 - margin, img.shape[1])
    y2 = min(y2 - margin, img.shape[0])
    cropped = img[y1:y2, x1:x2]

    # Convert to grayscale
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)

    # Trim all 4 sides using sustained brightness detection
    top, _ = scan_trim_boundary(gray, axis="top")
    _, bottom = scan_trim_boundary(gray, axis="bottom")
    left, _ = scan_trim_boundary(gray, axis="left")
    _, right = scan_trim_boundary(gray, axis="right")

    # Clamp ranges to prevent over-trim
    bottom = max(bottom, top + 10)
    right = max(right, left + 10)

    cleaned = gray[top:bottom, left:right]

    # Smooth edges, then threshold
    blurred = cv2.GaussianBlur(cleaned, (3, 3), 0)

    bw = cv2.adaptiveThreshold(
        blurred,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=15,
        C=10
    )

    _, buffer = cv2.imencode(".jpg", bw)
    return ContentFile(buffer.tobytes(), name="scanned.jpg")
