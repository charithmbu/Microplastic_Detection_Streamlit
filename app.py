import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os
import requests
import base64
from PIL import Image
import io

# ---------------- CONFIG ----------------
API_URL = "https://microplastic-detection-backend.onrender.com/detect"
EXAMPLE_DIR = "Example_images"
PIXEL_TO_NM = 100
RISK_THRESHOLD = 15

# ---------------- UI ----------------
st.set_page_config(page_title="Microplastic Detection System", layout="wide")
st.title("🧪 Microplastic Detection System (YOLOv8)")

st.markdown("### 📥 Choose Input Method")

input_mode = st.radio(
    "Select Input Type:",
    ["Upload Image", "Use Example Image", "Capture from Camera"]
)

img_bytes = None

# ---------------- CAMERA INPUT ----------------
if input_mode == "Capture from Camera":
    cam = st.camera_input("Capture image from microscope / camera")
    if cam:
        img_bytes = cam.getvalue()
        st.image(Image.open(cam), caption="Captured Image")

# ---------------- EXAMPLE IMAGE ----------------
elif input_mode == "Use Example Image":
    if os.path.exists(EXAMPLE_DIR):
        img_name = st.selectbox("Select example image", os.listdir(EXAMPLE_DIR))
        path = os.path.join(EXAMPLE_DIR, img_name)
        with open(path, "rb") as f:
            img_bytes = f.read()
        st.image(Image.open(path), caption="Example Image")

# ---------------- UPLOAD IMAGE ----------------
else:
    file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
    if file:
        img_bytes = file.read()
        st.image(Image.open(file), caption="Uploaded Image")

# ---------------- API CALL ----------------
if img_bytes:
    st.subheader("🚀 Running Detection...")

    response = requests.post(
        API_URL,
        files={"file": ("image.jpg", img_bytes, "image/jpeg")},
        timeout=180
    )

    if response.status_code != 200:
        st.error("❌ Detection API Error")
        st.stop()

    data = response.json()

    # -------- SHOW ANNOTATED IMAGE --------
    if "annotated_image" in data:
        decoded = base64.b64decode(data["annotated_image"])
        annotated_img = Image.open(io.BytesIO(decoded))
        st.image(annotated_img, caption="Detected Microplastics", width = 600)

    # -------- SUMMARY --------
    total_count = data["total_count"]
    boxes = data["boxes"]

    st.subheader("📊 Detection Summary")
    st.write(f"Total Microplastics Detected: **{total_count}**")
    st.write(f"Risk Score: **{data['risk_score']}**")
    st.write(f"Final Status: **{data['status']}**")

    # -------- SIZE LOGIC (UNCHANGED) --------
    sizes_nm = []
    for box in boxes:
        w_nm = box["width"] * PIXEL_TO_NM
        h_nm = box["height"] * PIXEL_TO_NM
        sizes_nm.append(np.sqrt(w_nm * h_nm))

    if sizes_nm:
        min_size = min(sizes_nm)
        max_size = max(sizes_nm)
        avg_size = sum(sizes_nm) / len(sizes_nm)

        min_thresh = min_size * 1.10
        max_thresh = max_size * 0.90

        min_count = sum(s <= min_thresh for s in sizes_nm)
        max_count = sum(s >= max_thresh for s in sizes_nm)
        avg_count = total_count - min_count - max_count

        st.subheader("📦 Size Category Counts")
        st.write(f"Min Size: {min_count}")
        st.write(f"Average Size: {avg_count}")
        st.write(f"Max Size: {max_count}")

        fig, ax = plt.subplots()
        ax.bar(["Min", "Avg", "Max"], [min_count, avg_count, max_count])
        ax.set_ylabel("Count")
        st.pyplot(fig)
#This is updated
