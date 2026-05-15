from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import json
import numpy as np
from PIL import Image
from tensorflow.keras.models import load_model
from cea import convert_to_cea_image

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from flask import send_file
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
import io

# -----------------------------
# APP SETUP
# -----------------------------
app = Flask(__name__)
app.secret_key = "forgexplorer_secret_key"

# -----------------------------
# ADMIN CONFIG
# -----------------------------
ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

# -----------------------------
# CONFIG
# -----------------------------
UPLOAD_FOLDER = "static/uploads"
CEA_FOLDER = "static/cea"
MODEL_PATH = "training_model.h5"
IMAGE_SIZE = (128, 128)
THRESHOLD = 0.5
HISTORY_FILE = "history.json"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CEA_FOLDER, exist_ok=True)

model = load_model(MODEL_PATH)

# -----------------------------
# LOAD HISTORY
# -----------------------------
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        history_data = json.load(f)
else:
    history_data = []

# -----------------------------
# HOME
# -----------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -----------------------------
# ABOUT
# -----------------------------
@app.route("/about")
def about():
    return render_template("about.html")

# -----------------------------
# LOGIN (USER + ADMIN)
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        # 🔐 ADMIN LOGIN
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session.clear()
            session["admin_logged_in"] = True

            session.pop('_flashes', None)
            flash("Login Successful!", "success")

            session["welcome_admin"] = True   # 🔥 show on dashboard

            return redirect(url_for("admin_dashboard"))

        # 👤 USER LOGIN
        users_file = "users.json"

        if os.path.exists(users_file):
            with open(users_file, "r") as f:
                users = json.load(f)
        else:
            users = []

        for user in users:
            if user["email"] == email and user["password"] == password:

                session.clear()
                session["logged_in"] = True
                session["user_email"] = email

                session.pop('_flashes', None)
                flash("Login Successful!", "success")

                return redirect(url_for("home"))

        # ❌ INVALID LOGIN
        session.pop('_flashes', None)
        flash("Invalid Email or Password!", "error")

    return render_template("login.html")

# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET","POST"])
def register():

    if request.method == "POST":

        email = request.form.get("email")
        password = request.form.get("password")

        users_file = "users.json"

        if os.path.exists(users_file):
            with open(users_file,"r") as f:
                users = json.load(f)
        else:
            users = []

        for user in users:
            if user["email"] == email:
                flash("User already exists!", "error")
                return redirect(url_for("register"))

        users.append({
            "email": email,
            "password": password
        })

        with open(users_file,"w") as f:
            json.dump(users,f,indent=4)

        flash("Registration Successful! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
@app.route("/admin-dashboard")
def admin_dashboard():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    # 🔥 SHOW WELCOME ONCE
    if session.get("welcome_admin"):
        flash("Welcome Admin 👋", "success")
        session.pop("welcome_admin", None)

    users_file = "users.json"

    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            users = json.load(f)
    else:
        users = []

    total_users = len(users)
    total_images = len(history_data)

    real_count = sum(1 for h in history_data if h["result"] == "Authentic")
    fake_count = sum(1 for h in history_data if h["result"] == "Forged")

    return render_template(
        "admin.html",
        users=users,
        total_users=total_users,
        total_images=total_images,
        real_count=real_count,
        fake_count=fake_count
    )

# -----------------------------
# DELETE USER
# -----------------------------
@app.route("/delete_user/<email>")
def delete_user(email):

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    users_file = "users.json"

    if os.path.exists(users_file):
        with open(users_file, "r") as f:
            users = json.load(f)
    else:
        users = []

    users = [user for user in users if user["email"] != email]

    with open(users_file, "w") as f:
        json.dump(users, f, indent=4)

    flash("User deleted successfully!", "success")

    return redirect(url_for("admin_dashboard"))

# -----------------------------
# ADMIN LOGOUT
# -----------------------------
@app.route("/admin-logout")
def admin_logout():
    session.pop("admin_logged_in", None)

    session.pop('_flashes', None)
    flash("Logged out successfully!", "success")

    return redirect(url_for("login"))

# -----------------------------
# UPLOAD IMAGE
# -----------------------------
@app.route("/upload", methods=["GET", "POST"])
def upload():

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    image_filename = None

    if request.method == "POST":

        file = request.files.get("image")

        if file:
            base = os.path.splitext(file.filename)[0]
            image_filename = base + ".jpg"

            path = os.path.join(UPLOAD_FOLDER, image_filename)

            img = Image.open(file).convert("RGB")
            img.save(path, "JPEG")

    return render_template("upload.html", image_filename=image_filename)

# -----------------------------
# CEA IMAGE
# -----------------------------
@app.route("/cea/<filename>")
def cea_page(filename):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    image_path = os.path.join(UPLOAD_FOLDER, filename)

    cea_img = convert_to_cea_image(image_path)

    cea_name = os.path.splitext(filename)[0] + "_cea.jpg"
    cea_path = os.path.join(CEA_FOLDER, cea_name)

    cea_img.save(cea_path, "JPEG")

    return render_template(
        "cea.html",
        original_image=f"uploads/{filename}",
        cea_image=f"cea/{cea_name}",
        filename=filename
    )

# -----------------------------
# RESULT
# -----------------------------
@app.route("/result/<filename>")
def result(filename):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    cea_name = os.path.splitext(filename)[0] + "_cea.jpg"
    cea_path = os.path.join(CEA_FOLDER, cea_name)

    # FIX 1: RGB
    img = Image.open(cea_path).convert("RGB").resize(IMAGE_SIZE)

    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 128, 128, 3)

    pred = model.predict(img_array)[0][0]

    if pred >= THRESHOLD:
        label = "Authentic"
        confidence = pred * 100
        forgery_type = "None"
    else:
        label = "Forged"
        confidence = (1 - pred) * 100

        cea_array = np.array(img) / 255.0

        # RGB intensity
        intensity = np.linalg.norm(cea_array, axis=2)

        threshold = np.mean(intensity) + 2 * np.std(intensity)
        mask = intensity > threshold

        artifact_pixels = np.sum(mask)

        ratio = artifact_pixels / intensity.size

        # FIX 2: indentation
        if ratio < 0.01:
            forgery_type = "Possible Copy-Move"
        elif ratio < 0.05:
            forgery_type = "Possible Splicing"
        else:
            forgery_type = "Complex Manipulation"

    history_data.append({
        "email": session.get("user_email"),
        "image": filename,
        "result": label,
        "confidence": f"{confidence:.2f}%"
    })

    with open(HISTORY_FILE, "w") as f:
        json.dump(history_data, f, indent=4)

    return render_template(
        "result.html",
        prediction=label,
        confidence=f"{confidence:.2f}%",
        forgery_type=forgery_type,
        image=f"uploads/{filename}",
        cea_image=f"cea/{cea_name}",
        filename=filename
    )
# -----------------------------
# HISTORY
# -----------------------------
# -----------------------------
# HISTORY (ADMIN + USER)
# -----------------------------
@app.route("/history")
def history():

    # 🔐 ADMIN → see all history
    if session.get("admin_logged_in"):
        return render_template("history.html", history=history_data)

    # 👤 USER → see only their history
    elif session.get("logged_in"):
        user_email = session.get("user_email")

        user_history = [h for h in history_data if h["email"] == user_email]

        return render_template("history.html", history=user_history)

    # ❌ Not logged in
    return redirect(url_for("login"))

# -----------------------------
# DELETE HISTORY ITEM
# -----------------------------
@app.route("/delete_history/<int:index>")
def delete_history(index):

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    if 0 <= index < len(history_data):
        history_data.pop(index)

        with open(HISTORY_FILE, "w") as f:
            json.dump(history_data, f, indent=4)

        flash("History item deleted!", "success")

    return redirect(url_for("history"))


# -----------------------------
# DELETE MULTIPLE HISTORY
# -----------------------------
@app.route("/delete_multiple_history")
def delete_multiple_history():

    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))

    indexes = request.args.get("indexes")

    if indexes:
        indexes = list(map(int, indexes.split(",")))

        # delete in reverse order (important!)
        for i in sorted(indexes, reverse=True):
            if 0 <= i < len(history_data):
                history_data.pop(i)

        with open(HISTORY_FILE, "w") as f:
            json.dump(history_data, f, indent=4)

        flash("Selected records deleted!", "success")

    return redirect(url_for("history"))

# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for("home"))


# -----------------------------
# report download
# -----------------------------
@app.route("/download_report/<filename>")
def download_report(filename):

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    # -------- PATHS --------
    cea_name = os.path.splitext(filename)[0] + "_cea.jpg"
    cea_path = os.path.join(CEA_FOLDER, cea_name)
    original_path = os.path.join(UPLOAD_FOLDER, filename)

    # -------- PREDICTION --------
    img = Image.open(cea_path).convert("RGB").resize(IMAGE_SIZE)

    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 128, 128, 3)

    pred = model.predict(img_array, verbose=0)[0][0]

    if pred >= THRESHOLD:
        label = "Authentic"
        confidence = pred * 100
        forgery_type = "None"
    else:
        label = "Forged"
        confidence = (1 - pred) * 100

        # SAME LOGIC AS RESULT PAGE
        cea_array = np.array(img) / 255.0

        intensity = np.linalg.norm(cea_array, axis=2)

        threshold = np.mean(intensity) + 2 * np.std(intensity)
        mask = intensity > threshold

        artifact_pixels = np.sum(mask)
        ratio = artifact_pixels / intensity.size

        if ratio < 0.01:
            forgery_type = "Possible Copy-Move"
        elif ratio < 0.05:
            forgery_type = "Possible Splicing"
        else:
            forgery_type = "Complex Manipulation"

    # -------- USER + DATE --------
    user_email = session.get("user_email", "Unknown User")
    current_time = datetime.now().strftime("%d-%m-%Y %H:%M")

    # -------- PDF START --------
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # -------- HEADER --------
    logo_path = os.path.join("static/images", "logo.png")

    logo = RLImage(logo_path, width=70, height=70) if os.path.exists(logo_path) else ""

    title = Paragraph(
        "<font size=26 color='#00BCD4'><b>ForgeXplorer</b></font><br/>"
        "<font size=14>Forgery Detection Report</font>",
        styles['Title']
    )

    header_table = Table([[logo, title]], colWidths=[80, 400])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 10))

    from reportlab.platypus import HRFlowable
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph(f"<b>User:</b> {user_email}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {current_time}", styles['Normal']))
    elements.append(Spacer(1, 15))

    # -------- IMAGES --------
    img1 = RLImage(original_path, width=200, height=200)
    img2 = RLImage(cea_path, width=200, height=200)

    image_table = Table([
        [img1, img2],
        ["Original Image", "CEA Image"]
    ])

    image_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    elements.append(image_table)
    elements.append(Spacer(1, 20))

    # -------- RESULT --------
    bg_color = colors.lightgreen if label == "Authentic" else colors.red

    result_table = Table([
        [f"Prediction: {label}"],
        [f"Confidence: {confidence:.2f}%"],
        [f"Forgery Type: {forgery_type}"]
    ])

    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
    ]))

    elements.append(result_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(
        "Generated by ForgeXplorer AI System",
        styles['Italic']
    ))

    doc.build(elements)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="Forgery_Report.pdf",
        mimetype="application/pdf"
    )
# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)