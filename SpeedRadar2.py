# SpeedRadar2.py  – identical detection logic + quick metrics
import time, cv2, numpy as np
from tracker2 import EuclideanDistTracker

START_PCT, END_PCT = 0.8, 0.2           # reference lines

def process_video(input_path, output_path,
                  speed_limit_mph=80, buffer_mph=5.0):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    W, H = int(cap.get(3)), int(cap.get(4))

    # writer
    writer = cv2.VideoWriter(
        output_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps, (W, H))

    # background subtractor
    back_sub = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
    kOp, kCl, kEr = (np.ones(k, np.uint8) for k in [(3,3),(11,11),(5,5)])

    tracker = EuclideanDistTracker(pixel_to_meter=0.05)
    speed_threshold = speed_limit_mph + buffer_mph

    frame_idx, total_frames = 0, 0
    speed_list = []
    t0 = time.time()

    while True:
        ret, frame = cap.read()
        if not ret: break
        frame_idx += 1; total_frames += 1

        fg = back_sub.apply(frame)
        _, m = cv2.threshold(fg, 200, 255, 0)
        m1 = cv2.morphologyEx(m, cv2.MORPH_OPEN,  kOp)
        m2 = cv2.morphologyEx(m1,cv2.MORPH_CLOSE, kCl)
        e  = cv2.erode(m2, kEr)

        cnts,_ = cv2.findContours(e, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        dets = [list(cv2.boundingRect(c)) for c in cnts if cv2.contourArea(c) > 1000]

        for x,y,w,h,oid in tracker.update(dets, frame_idx, fps):
            sp = tracker.getsp(oid)
            if sp: speed_list.append(sp)
            col = (0,255,0) if sp <= speed_threshold else (0,0,255)
            cv2.rectangle(frame,(x,y),(x+w,y+h),col,2)
            cv2.putText(frame,f"{oid}:{sp} mph",(x,y-8),
                        cv2.FONT_HERSHEY_SIMPLEX,0.6,col,2)
            tracker.capture(frame,x,y,w,h,sp,oid)

        # draw lines
        sy, ey = int(H*START_PCT), int(H*END_PCT)
        cv2.line(frame,(0,sy),(W,sy),(255,0,0),2)
        cv2.line(frame,(0,ey),(W,ey),(255,0,0),2)

        writer.write(frame)

    runtime = time.time() - t0
    cap.release(); writer.release()

    # ---- simple metrics ----
    speeds_np = np.array(speed_list)
    metrics = {
        "Total Vehicles":    len(speed_list),
        "Over-limit":        int((speeds_np > speed_threshold).sum()),
        "Mean Speed (mph)":  round(speeds_np.mean(),1) if speeds_np.size else 0,
        "Processing FPS":    round(total_frames / runtime, 1)
    }
    return metrics
