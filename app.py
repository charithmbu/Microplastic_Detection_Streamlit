import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image

# ---------------- CONFIG ----------------
EXAMPLE_DIR = "Example_images"
PIXEL_TO_NM = 100
RISK_THRESHOLD = 15

# ---------------- UI ----------------
st.set_page_config(page_title="Microplastic Detection System", layout="wide")
st.title("🧪 Microplastic Detection System")

st.markdown("### 📥 Choose Input Method")

input_mode = st.radio(
    "Select Input Type:",
    ["Upload Image", "Use Example Image", "Capture from Camera"]
)

img = None

# ---------------- CAMERA INPUT ----------------
if input_mode == "Capture from Camera":
    camera_image = st.camera_input("Capture image from microscope / camera")
    if camera_image:
        img = Image.open(camera_image).convert("RGB")
        img = np.array(img)
        st.image(img, caption="Captured Image")

# ---------------- EXAMPLE IMAGE ----------------
elif input_mode == "Use Example Image":
    if not os.path.exists(EXAMPLE_DIR):
        st.error("Example images folder not found.")
    else:
        example_images = sorted(os.listdir(EXAMPLE_DIR))
        selected_image = st.selectbox("Select an example image:", example_images)

        img_path = os.path.join(EXAMPLE_DIR, selected_image)
        img = Image.open(img_path).convert("RGB")
        img = np.array(img)
        st.image(img, caption=f"Example Image: {selected_image}")

# ---------------- UPLOAD IMAGE ----------------
else:
    uploaded_file = st.file_uploader(
        "Upload Microscopic Image",
        type=["jpg", "jpeg", "png"]
    )
    if uploaded_file:
        img = Image.open(uploaded_file).convert("RGB")
        img = np.array(img)
        st.image(img, caption="Uploaded Image")

# ---------------- PROCESSING (NO YOLO) ----------------
if img is not None:
    st.subheader("📊 Detection Summary")
    st.warning("⚠️ Detection model is disabled in this deployment.")

    total_count = 0
    sizes_nm = []

    st.write("Total Microplastics Detected: **0**")
    st.info("No microplastics detected.")

    # ---------------- GRAPH PLACEHOLDER ----------------
    labels = ["Min Size", "Average Size", "Max Size"]
    counts = [0, 0, 0]

    fig, ax = plt.subplots()
    ax.bar(labels, counts)
    ax.set_ylabel("Count")
    ax.set_title("Microplastic Size Distribution (Count-Based)")

    st.pyplot(fig)
