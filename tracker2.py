

# tracker2.py
import os
import cv2
import math

# -------------------------------
# Configuration
# -------------------------------
speed_limit = 80       # mph

# Prepare folders & log
tf_folder = "TrafficRecord"
ex_folder = os.path.join(tf_folder, "exceeded")
os.makedirs(ex_folder, exist_ok=True)
log_file = os.path.join(tf_folder, "SpeedRecord.txt")
with open(log_file, "w") as f:
    f.write("ID\tSPEED (mph)\n---\t-----------\n")

class EuclideanDistTracker:
    def __init__(self, pixel_to_meter=0.05):
        # id -> (cx, cy)
        self.center_points = {}
        # id -> last frame index
        self.prev_frame    = {}
        # id -> speed in mph
        self.speeds        = {}
        # conversion: meters per pixel
        self.pixel_to_meter = pixel_to_meter
        # capture flags
        self.captured      = {}
        # stored fps
        self.fps           = None

    def update(self, detections, frame_idx, fps):
        self.fps = fps
        boxes_ids = []
        for x, y, w, h in detections:
            cx, cy = x + w//2, y + h//2
            matched = False
            # match existing object
            for oid, (px, py) in self.center_points.items():
                dist = math.hypot(cx - px, cy - py)
                if dist < 50:
                    # compute instantaneous speed (m/s)
                    prev_idx = self.prev_frame.get(oid)
                    if prev_idx is not None and fps > 0:
                        dt = (frame_idx - prev_idx) / fps
                        if dt > 0:
                            dx = math.hypot(cx - px, cy - py)
                            v_m_s = (dx * self.pixel_to_meter) / dt
                            # convert to mph (1 m/s ≈ 2.23694 mph)
                            self.speeds[oid] = v_m_s * 2.23694
                    else:
                        self.speeds[oid] = 0
                    # update center & frame
                    self.center_points[oid] = (cx, cy)
                    self.prev_frame[oid]    = frame_idx
                    boxes_ids.append([x, y, w, h, oid])
                    matched = True
                    break
            # new object
            if not matched:
                oid = len(self.center_points)
                self.center_points[oid] = (cx, cy)
                self.prev_frame[oid]     = frame_idx
                self.speeds[oid]         = 0
                self.captured[oid]       = False
                boxes_ids.append([x, y, w, h, oid])
        return boxes_ids

    def getsp(self, oid):
        return int(self.speeds.get(oid, 0))

    def capture(self, frame, x, y, w, h, speed, oid):
        if self.captured.get(oid):
            return
        if speed <= speed_limit:
            return
        self.captured[oid] = True
        crop = frame[y:y+h, x:x+w]
        fname = f"{oid}_speed_{int(speed)}.jpg"
        path = os.path.join(tf_folder, fname)
        cv2.imwrite(path, crop)
        with open(log_file, "a") as f:
            f.write(f"{oid}\t{int(speed)} <---exceeded\n")

    def limit(self):
        return speed_limit
