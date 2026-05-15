import streamlit as st
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from cea import convert_to_cea_image

MODEL_PATH = "train_model.h5"
IMAGE_SIZE = (128, 128)
THRESHOLD = 0.5

@st.cache_resource
def load_cnn_model():
    return load_model(MODEL_PATH)

model = load_cnn_model()

def prepare_image(image_path):
    cea_image = convert_to_cea_image(image_path)
    cea_image = cea_image.resize(IMAGE_SIZE)
    cea_image = np.array(cea_image) / 255.0
    cea_image = cea_image.reshape(1, 128, 128, 3)
    return cea_image

st.set_page_config(page_title="ForgeExplorer", layout="centered")
st.title("🖼️ ForgeExplorer")
st.subheader("Image Forgery Detection using CNN + CEA")

uploaded_file = st.file_uploader(
    "Upload an image for forgery analysis",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    temp_path = "uploaded_image.jpg"
    image.save(temp_path)

    st.markdown("### 📷 Original Image")
    st.image(image, use_container_width=True)

    cea_image = convert_to_cea_image(temp_path)
    st.markdown("### 🔍 Compression Error Analysis (CEA)")
    st.image(cea_image, use_container_width=True)

    input_image = prepare_image(temp_path)
    pred_value = model.predict(input_image)[0][0]

    if pred_value >= THRESHOLD:
        st.success("✅ Prediction: **Authentic**")
        confidence = pred_value * 100
    else:
        st.error("🚨 Prediction: **Forged**")
        confidence = (1 - pred_value) * 100

    st.markdown(f"### 📊 Confidence: **{confidence:.2f}%**")
else:
    st.info("Please upload an image to start analysis.")
