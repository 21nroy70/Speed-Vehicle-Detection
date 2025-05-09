# app.py
import streamlit as st, tempfile, os, qrcode, io
from SpeedRadar2 import process_video

# Your public Drive folder link containing processed.mp4:
DRIVE_FOLDER = (
    "https://drive.google.com/file/d/1i6iwIWCFV2U4GtCYkFfiJfKSZSRTNvB1/view?usp=sharing"
)

st.set_page_config(page_title="Vehicle Speed Monitor", layout="wide")
st.title("🚗 Vehicle Detection & Speed Monitoring")

# Sidebar: sliders
lim = st.sidebar.slider("Speed limit (mph)",      20, 120, 80)
buf = st.sidebar.slider("Buffer over limit (mph)", 0,  20,  5)

# Main: uploader + process
vid = st.file_uploader("Upload highway video", ["mp4","avi"])
if vid:
    base, ext = os.path.splitext(vid.name)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    tmp.write(vid.read()); tmp.flush()

    st.info("Processing…")
    try:
        metrics = process_video(tmp.name, lim, buf)

        st.success("✅ Processed Video:")
        st.video("processed.mp4")
        with open("processed.mp4", "rb") as f:
            st.download_button(
                "📥 Download processed.mp4", f, "processed.mp4", "video/mp4"
            )

        # Run-time metrics
        st.subheader("Run-time Metrics")
        c1, c2 = st.columns(2)
        c1.metric("Vehicles",        metrics["Vehicles"])
        c2.metric("Over-limit",      metrics["Over-limit"])
        c1.metric("Avg Speed (mph)", metrics["Avg Speed (mph)"])
        c2.metric("Proc. FPS",       metrics["Proc. FPS"])

        # Static QR linking to your Drive folder
        st.markdown("#### 🎥 Scan to view your processed video")
        qr = qrcode.make(DRIVE_FOLDER)
        buf = io.BytesIO()
        qr.save(buf, format="PNG")
        st.image(buf, use_container_width=True)
        st.markdown(f"[Open Drive folder]({DRIVE_FOLDER})")

    except Exception as e:
        st.error(f"❌ Processing failed: {e}")
else:
    st.warning("Please upload a highway video to begin.")
