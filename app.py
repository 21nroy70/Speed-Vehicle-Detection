# app.py  – unchanged UI plus metrics panel
import streamlit as st, tempfile, os
from SpeedRadar2 import process_video

st.set_page_config(page_title="Vehicle Speed Monitor", layout="wide")
st.title("🚗 Vehicle Detection & Speed Monitoring")

lim = st.sidebar.slider("Speed limit (mph)", 20, 120, 80)
buf = st.sidebar.slider("Buffer over limit (mph)", 0, 20, 5)

vid = st.file_uploader("Upload highway video", ["mp4","avi"])
if vid:
    base, ext = os.path.splitext(vid.name)
    inp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    inp.write(vid.read()); inp.flush()
    out = tempfile.NamedTemporaryFile(delete=False, suffix=ext); out.close()

    st.info("Processing…")
    try:
        metrics = process_video(inp.name, out.name, lim, buf)
        st.success("✅ Done")
        st.video(out.name)
        with open(out.name,"rb") as f:
            st.download_button("📥 Download", f, f"output_{base}{ext}", mime="video/mp4")

        st.subheader("Run-time Metrics")
        cols = st.columns(2)
        cols[0].metric("Vehicles Detected", metrics["Total Vehicles"])
        cols[1].metric("Over-limit",        metrics["Over-limit"])
        cols[0].metric("Mean Speed (mph)",  metrics["Mean Speed (mph)"])
        cols[1].metric("Processing FPS",    metrics["Processing FPS"])

    except Exception as e:
        st.error(f"Failed: {e}")
else:
    st.warning("Upload a highway video to begin.")
