


# app.py
import streamlit as st
import tempfile
import os
from SpeedRadar2 import process_video

st.set_page_config(page_title="Vehicle Speed Monitor", layout="wide")
st.title("🚗 Vehicle Detection & Speed Monitoring")

st.sidebar.header("Settings")
speed_limit = st.sidebar.slider("Speed limit (mph)", 20, 120, 80)
buffer_mph  = st.sidebar.slider("Buffer over limit (mph)", 0, 20, 5)

video_file = st.file_uploader("Upload highway video", type=["mp4","avi"])
if video_file:
    base, ext = os.path.splitext(video_file.name)
    in_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    in_tmp.write(video_file.read()); in_tmp.flush()
    in_path = in_tmp.name

    out_name = f"output_{base}{ext}"
    out_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    out_path = out_tmp.name; out_tmp.close()

    st.info("Processing…")
    try:
        process_video(
            input_path=in_path,
            output_path=out_path,
            speed_limit_mph=speed_limit,
            buffer_mph=buffer_mph
        )

        st.success("✅ Done! Here’s the result:")
        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        st.write(f"**Output file:** `{out_name}` — {size_mb:.2f} MB")

        with open(out_path, "rb") as f:
            st.download_button(
                label="📥 Download processed video",
                data=f,
                file_name=out_name,
                mime="video/mp4" if ext.lower()==".mp4" else "video/x-msvideo",
            )
        st.video(out_path)

    except Exception as e:
        st.error(f"Failed: {e}")
else:
    st.warning("Please upload a video to begin.")
