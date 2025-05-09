# tracker2.py
import os, cv2, math

# ------------------------------- Configuration -------------------------------
speed_limit      = 80       # mph
pixel_to_meter   = 0.05     # meters per pixel
tf_folder        = "TrafficRecord"
os.makedirs(f"{tf_folder}/exceeded", exist_ok=True)
log_file         = os.path.join(tf_folder, "SpeedRecord.txt")
with open(log_file, "w") as f:
    f.write("ID\tSPEED (mph)\n---\t-----------\n")
# -----------------------------------------------------------------------------


class EuclideanDistTracker:
    def __init__(self, pixel_to_meter=pixel_to_meter):
        self.center_points  = {}    # id -> (cx, cy)
        self.prev_frame     = {}    # id -> frame_idx
        self.speeds         = {}    # id -> mph
        self.captured       = {}    # id -> bool
        self.pixel_to_meter = pixel_to_meter

    def update(self, detections, frame_idx, fps):
        boxes_ids = []
        for x, y, w, h in detections:
            cx, cy = x + w//2, y + h//2
            matched = False
            for oid, (px, py) in self.center_points.items():
                if (cx - px)**2 + (cy - py)**2 < 50**2:
                    prev_idx = self.prev_frame.get(oid)
                    if prev_idx is not None and fps > 0:
                        dt = (frame_idx - prev_idx) / fps
                        if dt > 0:
                            dx = math.hypot(cx - px, cy - py)
                            v_m_s = (dx * self.pixel_to_meter) / dt
                            self.speeds[oid] = v_m_s * 2.23694
                    else:
                        self.speeds[oid] = 0
                    self.center_points[oid] = (cx, cy)
                    self.prev_frame[oid]    = frame_idx
                    boxes_ids.append([x, y, w, h, oid])
                    matched = True
                    break
            if not matched:
                oid = len(self.center_points)
                self.center_points[oid] = (cx, cy)
                self.prev_frame[oid]    = frame_idx
                self.speeds[oid]         = 0
                self.captured[oid]       = False
                boxes_ids.append([x, y, w, h, oid])
        return boxes_ids

    def getsp(self, oid):
        return int(self.speeds.get(oid, 0))

    def capture(self, frame, x, y, w, h, speed, oid):
        if self.captured.get(oid) or speed <= speed_limit:
            return
        self.captured[oid] = True
        crop = frame[y:y+h, x:x+w]
        fname = f"{oid}_speed_{int(speed)}.jpg"
        path  = os.path.join(tf_folder, fname)
        cv2.imwrite(path, crop)
        if speed > speed_limit:
            cv2.imwrite(f"{tf_folder}/exceeded/{fname}", crop)
        with open(log_file, "a") as f:
            tag = " <---exceeded" if speed > speed_limit else ""
            f.write(f"{oid}\t{int(speed)}{tag}\n")

    def limit(self):
        return speed_limit
