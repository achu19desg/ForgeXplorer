# 🔍 ForgeXplorer - Image Forgery Detection System

## 📌 Overview
ForgeXplorer is a deep learning-based Image Forgery Detection System developed to identify whether a digital image is authentic or manipulated. The project combines **Compression Error Analysis (CEA)** with a **Convolutional Neural Network (CNN)** to detect hidden inconsistencies in images and classify them as **Real** or **Forged**.

The system provides an interactive web interface where users can upload images and instantly receive prediction results along with confidence scores and visual analysis.

---

## 🚀 Features

✅ Image Forgery Detection using Deep Learning  
✅ Compression Error Analysis (CEA) preprocessing  
✅ CNN-based binary classification  
✅ Confidence score prediction  
✅ Original vs Processed image visualization  
✅ User-friendly web interface  
✅ Detection history support  
✅ Real-time image analysis  

---

## 🧠 Technologies Used

### 🔹 Frontend
- HTML
- Tailwind CSS
- JavaScript

### 🔹 Backend
- Flask
- Python

### 🔹 Deep Learning & Image Processing
- TensorFlow / Keras
- OpenCV
- NumPy
- Pillow (PIL)
- Matplotlib
- Scikit-learn

---

## 📂 Dataset Used

📁 **CASIA V2 Dataset**  

The project uses the CASIA V2 dataset containing:
- Authentic Images
- Forged Images


 Dataset is taken from Kaggle.

---

## ⚙️ Working Process

1️⃣ User uploads an image through the web interface  
2️⃣ Compression Error Analysis (CEA) is applied  
3️⃣ Processed image is passed into the CNN model  
4️⃣ The model predicts whether the image is:

- ✅ Authentic
- ❌ Forged

5️⃣ The system displays:
- Prediction result
- Confidence score
- Original image
- Processed image

---

## 🖥️ Project Structure

```bash
ForgeXplorer/
│
├── screenshots/
├── static/
├── templates/
├── dataset/
├── models/
├── uploads/
├── app.py
├── traincnn.ipynb
├── requirements.txt
└── README.md
```

---

## 📸 Screenshots

### 🏠 Home Page
![Home Page](screenshots/frontpage.png)

---

## ▶️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/forgexplorer.git
cd forgexplorer
```

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run Flask Application

```bash
python app.py
```

### 4️⃣ Open Browser

```bash
http://127.0.0.1:5000/
```

---

## 📊 Model Details

- Model Type: Convolutional Neural Network (CNN)
- Input Size: 128 × 128
- Preprocessing: Compression Error Analysis (CEA)

### Classification Output
- Real Image
- Forged Image

---

## 📈 Evaluation Metrics

📌 Accuracy  
📌 Precision  
📌 Recall  
📌 F1-Score  
📌 Confusion Matrix  
📌 ROC-AUC Score  

---

## ⚠️ Limitations

- Performance depends on dataset quality
- Complex manipulations may be difficult to detect
- High computational resources required for training

---

## 🔮 Future Scope

🚀 Tampered region localization  
🚀 Deepfake detection  
🚀 Real-time forgery detection  
🚀 Mobile application development  
🚀 Explainable AI visualization (Grad-CAM)  

---

## 👩‍💻 Author

**Archana P**  
MCA Student  
Deep Learning & Digital Image Forensics Project

---

## ⭐ Conclusion

ForgeXplorer provides an efficient and automated solution for detecting manipulated digital images using deep learning and image forensic techniques. The system improves digital content authenticity verification and supports applications in digital forensics, cybersecurity, journalism, and social media verification.
