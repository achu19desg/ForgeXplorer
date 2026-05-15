import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from cea import convert_to_cea_image   # CEA import

# -------- CONFIG --------
MODEL_PATH = "training_model.h5"
IMAGE_SIZE = (128, 128)
THRESHOLD = 0.5

# Load trained model
model = load_model(MODEL_PATH)


# -------- IMAGE PREPARATION --------
def prepare_image(image_path):
    """
    Apply CEA + resize + normalization
    """

    cea_image = convert_to_cea_image(image_path)

    # Convert NumPy → PIL (IMPORTANT)
    cea_image = Image.fromarray(cea_image.astype(np.uint8))
    cea_image = cea_image.resize(IMAGE_SIZE)

    # Normalize
    cea_image = np.array(cea_image) / 255.0
    cea_image = cea_image.reshape(1, 128, 128, 3)

    return cea_image


# -------- FORGERY TYPE DETECTION (RGB BASED) --------
def detect_forgery_type(cea_image):
    """
    Detect forgery type using RGB intensity
    """

    cea_image = cea_image / 255.0  # normalize

    # RGB intensity (vector magnitude)
    intensity = np.linalg.norm(cea_image, axis=2)

    threshold = np.mean(intensity) + 2 * np.std(intensity)
    mask = intensity > threshold

    ratio = np.sum(mask) / intensity.size

    if ratio < 0.01:
        return "Possible Copy-Move"
    elif ratio < 0.05:
        return "Possible Splicing"
    else:
        return "Complex Manipulation"


# -------- PREDICTION --------
def predict_image(image_path):
    """
    Predict whether image is Forged or Authentic
    """

    # Generate CEA once (efficient)
    cea_img = convert_to_cea_image(image_path)

    # Prepare image for model
    img = Image.fromarray(cea_img.astype(np.uint8)).resize(IMAGE_SIZE)
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 128, 128, 3)

    # Model prediction
    prediction = model.predict(img_array, verbose=0)[0][0]

    if prediction >= THRESHOLD:
        label = "Authentic"
        confidence = prediction * 100
        forgery_type = "None"

    else:
        label = "Forged"
        confidence = (1 - prediction) * 100

        # Detect forgery type (RGB)
        forgery_type = detect_forgery_type(np.array(img))

    return label, confidence, forgery_type


# -------- TESTING --------
if __name__ == "__main__":

    test_image_path = "dataset/forged/Tp_D_CNN_M_N_art00052_arc00030_11853.jpg"

    label, confidence, forgery_type = predict_image(test_image_path)

    print("Prediction :", label)
    print(f"Confidence : {confidence:.2f}%")

    if label == "Forged":
        print("Forgery Type :", forgery_type)