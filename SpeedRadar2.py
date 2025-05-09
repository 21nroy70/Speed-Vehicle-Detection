# SpeedRadar2.py
import time, cv2, numpy as np
from tracker2 import EuclideanDistTracker

START_PCT, END_PCT = 0.8, 0.2   # measurement lines

def process_video(input_path, speed_limit_mph=80, buffer_mph=5.0):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(3)), int(cap.get(4))

    # Always overwrite processed.mp4
    out_file = "processed.mp4"
    writer = cv2.VideoWriter(
        out_file,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps, (W, H))

    back_sub = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    kOp, kCl, kEr = (np.ones(k, np.uint8) for k in [(3,3),(11,11),(5,5)])

    tracker   = EuclideanDistTracker(pixel_to_meter=0.05)
    threshold = speed_limit_mph + buffer_mph

    speeds, frame_idx = [], 0
    t0 = time.time()

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1

        fg = back_sub.apply(frame)
        _, m = cv2.threshold(fg, 200, 255, 0)
        m1 = cv2.morphologyEx(m, cv2.MORPH_OPEN,  kOp)
        m2 = cv2.morphologyEx(m1, cv2.MORPH_CLOSE, kCl)
        e  = cv2.erode(m2, kEr)

        cnts,_ = cv2.findContours(e,
                    cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dets = []
        for c in cnts:
            if cv2.contourArea(c) < 1000:
                continue
            x,y,w,h = cv2.boundingRect(c)
            dets.append([x,y,w,h])

        for x,y,w,h,oid in tracker.update(dets, frame_idx, fps):
            sp = tracker.getsp(oid)
            if sp:
                speeds.append(sp)
            col = (0,255,0) if sp <= threshold else (0,0,255)
            cv2.rectangle(frame,(x,y),(x+w,y+h),col,2)
            cv2.putText(frame, f"{oid}:{sp} mph",
                        (x,y-8),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,col,2)
            tracker.capture(frame, x, y, w, h, sp, oid)

        sy, ey = int(H * START_PCT), int(H * END_PCT)
        cv2.line(frame, (0,sy), (W,sy), (255,0,0), 2)
        cv2.line(frame, (0,ey), (W,ey), (255,0,0), 2)

        writer.write(frame)

    runtime = time.time() - t0
    cap.release()
    writer.release()

    arr = np.array(speeds)
    metrics = {
        "Vehicles":        len(speeds),
        "Over-limit":      int((arr > threshold).sum()),
        "Avg Speed (mph)": round(arr.mean(),1) if arr.size else 0,
        "Proc. FPS":       round(frame_idx / runtime, 1)
    }
    return metrics
