

# SpeedRadar2.py
import cv2
import numpy as np
from tracker2 import EuclideanDistTracker

# measurement line positions (pct of frame height)
START_PCT = 0.8
END_PCT   = 0.2

def process_video(input_path, output_path,
                  speed_limit_mph=80, buffer_mph=5.0):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    H   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (W, H))

    # background subtractor + kernels
    back_sub = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    kOp = np.ones((3,3), np.uint8)
    kCl = np.ones((11,11), np.uint8)
    kEr = np.ones((5,5), np.uint8)

    tracker = EuclideanDistTracker(pixel_to_meter=0.05)
    speed_threshold = speed_limit_mph + buffer_mph

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        fg = back_sub.apply(frame)
        _, mask = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)
        m1 = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kOp)
        m2 = cv2.morphologyEx(m1,    cv2.MORPH_CLOSE, kCl)
        e  = cv2.erode(m2, kEr)

        cnts, _ = cv2.findContours(e, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        detections = []
        for cnt in cnts:
            if cv2.contourArea(cnt) < 1000:
                continue
            x, y, w, h = cv2.boundingRect(cnt)
            detections.append([x, y, w, h])

        boxes = tracker.update(detections, frame_idx, fps)
        for x, y, w, h, oid in boxes:
            sp = tracker.getsp(oid)
            color = (0,255,0) if sp <= speed_threshold else (0,0,255)
            cv2.rectangle(frame, (x,y), (x+w,y+h), color, 2)
            cv2.putText(frame, f"{oid}: {sp} mph", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
            tracker.capture(frame, x, y, w, h, sp, oid)

        # draw lines
        start_y = int(H * START_PCT)
        end_y   = int(H * END_PCT)
        cv2.line(frame, (0, start_y), (W, start_y), (255,0,0), 2)
        cv2.line(frame, (0, end_y),   (W, end_y),   (255,0,0), 2)

        writer.write(frame)

    cap.release()
    writer.release()