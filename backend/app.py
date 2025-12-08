from flask import Flask, render_template,  request, redirect, flash , session , url_for
from datetime import timedelta 
import os  
import json
from extract_colors import rgb_to_lab, draw_color_swatch
import pandas as pd
import joblib
import numpy as np
from extract_colors import extract_colors_from_photo
import cv2
from flask import send_from_directory
import time
from datetime import datetime ,  timezone
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
import sqlite3
from dotenv import load_dotenv
load_dotenv()
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import g
import random
import sqlite3
import smtplib
import bcrypt
from extract_colors import rgb_to_lab
from predict_season import predict_season
from functools import wraps
app = Flask(
    __name__,
    # template_folder="../frontend/templates",
    # static_folder="../frontend/static"
     template_folder=os.path.join("..", "frontend", "templates"),
            static_folder=os.path.join("..", "frontend", "static")
)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)
app.config["SESSION_PERMANENT"] = True
# SQLite Configuration
DB_PATH = os.path.join(os.getcwd(), "myapp.db")

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DB_PATH,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Register the close_db function to run after each request
app.teardown_appcontext(close_db)

def get_cursor():
    db = get_db()
    # Return a new cursor for each operation to maintain thread safety, 
    # but the connection itself is thread-safe within the request context (due to flask.g)
    return db.cursor()
BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER_REL = 'uploads'
UPLOAD_FOLDER_ABS = os.path.join(BASE_DIR, UPLOAD_FOLDER_REL) # Make it absolute

os.makedirs(UPLOAD_FOLDER_ABS, exist_ok=True) # Now creates the folder relative to app.py location

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_ABS # Use the absolute path in config
# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



PALETTE_PATH = os.path.join(BASE_DIR, 'data', 'season_palettes.json')

# Load the palette data
with open(PALETTE_PATH, 'r') as f:
    SEASON_PALETTES = json.load(f)

# Remove default values so failure is obvious if .env isn't loaded
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME') 
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

cloudinary.config( 
    cloud_name = CLOUDINARY_CLOUD_NAME, 
    api_key = CLOUDINARY_API_KEY, 
    api_secret = CLOUDINARY_API_SECRET,
    secure = True
)
# Load  seasons JSON with looks (each season has 6 images)
seasons_data = SEASON_PALETTES


@app.route('/')
def index():
    return render_template("index.html")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "warning")
            # Redirect to login, preserving the attempted destination URL ('next')
            return redirect(url_for('login', next=request.endpoint))
        return f(*args, **kwargs)
    return decorated_function


def rgb_to_lab(color):
    rgb_color = np.uint8([[color]])
    lab_color = cv2.cvtColor(rgb_color, cv2.COLOR_RGB2LAB)[0][0]
    return lab_color
def lab_to_rgb(lab_color):
    # Convert standard LAB to OpenCV scale
    L = lab_color[0] * 255 / 100
    a = lab_color[1] + 128
    b = lab_color[2] + 128

    lab_scaled = np.uint8([[[L, a, b]]])
    rgb = cv2.cvtColor(lab_scaled, cv2.COLOR_LAB2RGB)[0][0]
    return [int(x) for x in rgb]

def parse_point(coord_str):
 try:
    x, y = map(int, coord_str.split(','))
    return x, y
 except:
        return 0, 0  # fallback

def classify_skin_tone(skin_lab):
    L = skin_lab[0]
    if L > 80:
        return "Fair"
    elif L > 65:
        return "Medium"
    elif L > 50:
        return "Olive"
    elif L > 35:
        return "Brown"
    else:
        return "Deep Brown"



### REPLACE the existing @app.route('/upload', ...) function with the block below ###
@app.route('/upload', methods=['GET', 'POST'], endpoint='upload')
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Local temp save (we still save a local copy for processing)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            extension = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{filename.rsplit('.', 1)[0]}_{timestamp}.{extension}"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(save_path)
            print(
              "---------------------------------------Cloudinary ENV:-----------------------------------",
 
)
            # Upload to Cloudinary
            try:
                upload_result = cloudinary.uploader.upload(
                    save_path,
                    folder="stylemate_uploads",
                    use_filename=True,
                    unique_filename=False,
                    overwrite=False
                )


                image_url = upload_result.get('secure_url')
                public_id = upload_result.get('public_id')
            except Exception as e:
                # If cloud upload fails, fall back to local usage but warn
                print("Cloudinary upload failed:", e)
                image_url = None
                public_id = None
            db = get_db()
            cursor = get_cursor()
            # Save to DB (using image_url & public_cloud_id). If Cloudinary failed, we still store local filename in image_url.
            user_id = session.get('user_id')
            timestamp_db = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # If cloud upload succeeded use image_url, otherwise use local path reference
            stored_image_url = image_url if image_url else f"/uploads/{unique_filename}"
            stored_public_id = public_id if public_id else ""

            sql = """
                INSERT INTO uploaded_images (user_id, image_url, public_cloud_id, timestamp)
                VALUES (?, ?, ?, ?)
            """
            val = (user_id, stored_image_url, stored_public_id, timestamp_db)
            cursor.execute(sql, val)
            db.commit()
            upload_id = cursor.lastrowid

            # Load image from local saved path for pixel operations
            image = cv2.imread(save_path)
            if image is None:
                return "Image processing failed", 500

            # Swatch points from form
            hair_coord = request.form.get('hair')
            eye_coord = request.form.get('eye')
            skin_coord = request.form.get('skin')

            if not (hair_coord and eye_coord and skin_coord):
                return "Missing one or more swatch points", 400

            def get_rgb(coord):
                x, y = map(int, coord.split(','))
                # make sure coords are inside image
                h, w = image.shape[:2]
                x = max(0, min(x, w-1))
                y = max(0, min(y, h-1))
                return image[y, x][::-1]  # BGR -> RGB

            hair_rgb = get_rgb(hair_coord)
            eye_rgb = get_rgb(eye_coord)
            skin_rgb = get_rgb(skin_coord)

            # Convert to LAB
            hair_lab = [float(x) for x in rgb_to_lab(hair_rgb)]
            eye_lab = [float(x) for x in rgb_to_lab(eye_rgb)]
            skin_lab = [float(x) for x in rgb_to_lab(skin_rgb)]

            # Predict season using your model
            season = predict_season(save_path)

            # Save season + (keep gender previously set or default)
            session.permanent = True
            session["season"] = season
            session["gender"] = session.get("gender", "female")
            session.modified = True

            # Save prediction row (same as before)
            sql = """
                INSERT INTO predictions (
                    user_id, upload_id,
                    hair_L, hair_A, hair_B,
                    skin_L, skin_A, skin_B,
                    eye_L, eye_A, eye_B,
                    predicted_season
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            val = (
                user_id, upload_id,
                *hair_lab,
                *skin_lab,
                *eye_lab,
                season
            )
            cursor.execute(sql, val)
            db.commit()
            print(
              "---------------------------------------Cloudinary ENV:-----------------------------------"
)

            # Draw swatches on overlay and save overlay locally (optional)
            def parse_coord(coord):
                x, y = map(int, coord.split(','))
                return (x, y)

            overlay_image = image.copy()
            draw_color_swatch(overlay_image, parse_coord(hair_coord), hair_rgb, "Hair")
            draw_color_swatch(overlay_image, parse_coord(skin_coord), skin_rgb, "Skin")
            draw_color_swatch(overlay_image, parse_coord(eye_coord), eye_rgb, "Eye")

            swatch_output_local = os.path.join(app.config['UPLOAD_FOLDER'], f"{filename.rsplit('.', 1)[0]}_{timestamp}_swatches.jpg")
            cv2.imwrite(swatch_output_local, overlay_image)

            # Optionally upload overlay to Cloudinary as well (not required)
            overlay_cloud_url = None
            overlay_public_id = None
            try:
                overlay_res = cloudinary.uploader.upload(
                    swatch_output_local,
                    folder="stylemate_uploads/overlays",
                    use_filename=True
                )
                overlay_cloud_url = overlay_res.get('secure_url')
                overlay_public_id = overlay_res.get('public_id')
            except Exception as exc:
                print("Overlay upload failed:", exc)

            season_data = SEASON_PALETTES.get(season, {})
            skin_tone_name = classify_skin_tone(skin_lab)
            
            return render_template(
                'results.html',
                hair_color=hair_rgb,
                skin_color=skin_rgb,
                eye_color=eye_rgb,
                season=season,
                image_url=stored_image_url,
                overlay_url=overlay_cloud_url or f"/uploads/{os.path.basename(swatch_output_local)}",
                season_description=season_data.get("description", ""),
                avoid_colors=season_data.get("avoid_colors", []),
                makeup=season_data.get("makeup", {}),
                fabrics=season_data.get("fabrics", []),
                tone_contrast=season_data.get("tone_contrast", ""),
                season_colors=season_data.get("colors", []),
                skin_tone_name=skin_tone_name,
                
            )

    return render_template('upload.html')


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # backend/uploads

### REPLACE the existing @app.route('/uploads/<path:filename>') handler with this ###
@app.route('/uploads/<path:filename>')
@login_required
def uploaded_file(filename):
    # If the filename looks like a Cloudinary URL, serve as-is. Otherwise try to serve local.
    if filename.startswith("http://") or filename.startswith("https://"):
        return redirect(filename)
    # Attempt to serve local file
    local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(local_path):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    db = get_db()
    cursor = get_cursor()
    # Not found locally — attempt to lookup in DB and redirect to image_url
    cursor.execute("SELECT image_url FROM uploaded_images WHERE image_url LIKE ? OR image_url LIKE ?", (f"%{filename}%", f"%/{filename}%"))
    row = cursor.fetchone()
    if row:
        return redirect(row[0])
    return "File not found", 404

@app.route('/results')
@login_required
def results():

    if 'user_id' not in session:
        flash("Please login to see results", "danger")
        return redirect(url_for('login'))
    
    # 1. Get request-local DB connection and cursor
    db = get_db()
    cursor = get_cursor()

    user_id = session['user_id']

    # Get the latest uploaded image + prediction (use image_url)
    cursor.execute("""
        SELECT u.image_url, p.hair_L, p.hair_A, p.hair_B,
               p.skin_L, p.skin_A, p.skin_B,
               p.eye_L, p.eye_A, p.eye_B,
               p.predicted_season
        FROM uploaded_images u
        JOIN predictions p ON u.id = p.upload_id
        WHERE u.user_id = ?
        ORDER BY u.id DESC
        LIMIT 1
    """, (user_id,))

    row = cursor.fetchone()

    if not row:
        flash("No analysis data found. Please upload an image first.", "warning")
        return redirect(url_for('upload'))

    image_url = row[0]
    hair_lab = row[1:4]
    skin_lab = row[4:7]
    eye_lab = row[7:10]
    season = row[10]

    # Convert LAB to RGB
    def lab_to_rgb(lab_color):
        L = lab_color[0] * 255 / 100
        a = lab_color[1] + 128
        b = lab_color[2] + 128
        lab_scaled = np.uint8([[[L, a, b]]])
        rgb = cv2.cvtColor(lab_scaled, cv2.COLOR_LAB2RGB)[0][0]
        return [int(x) for x in rgb]

    hair_color = lab_to_rgb(hair_lab)
    skin_color = lab_to_rgb(skin_lab)
    eye_color = lab_to_rgb(eye_lab)

    # Get season data
    # SEASON_PALETTES should be accessible as a global variable
    season_data = SEASON_PALETTES.get(season, {})
    season_colors = season_data.get("colors", [])
    avoid_colors = season_data.get("avoid_colors", [])
    makeup = season_data.get("makeup", {"lip": [], "eyes": [], "blush": []})
    fabrics = season_data.get("fabrics", [])
    tone_contrast = season_data.get("tone_contrast", "")
    season_description = season_data.get("description", "")
    characteristics = season_data.get("characteristics", []) 
    return render_template(
        "results.html",
        hair_color=hair_color,
        skin_color=skin_color,
        eye_color=eye_color,
        season=season,
        season_colors=season_colors,
        avoid_colors=avoid_colors,
        makeup=makeup,
        fabrics=fabrics,
        tone_contrast=tone_contrast,
        season_description=season_description,
        image_url=image_url,
        characteristics = characteristics
    )
@app.route('/recommendations')
@login_required
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # 1. Get request-local DB connection and cursor
    db = get_db()
    cursor = get_cursor()

    user_id = session['user_id']

    # Fetch all uploaded images for the user
    cursor.execute("""
        SELECT id, image_url, timestamp
        FROM uploaded_images
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))
    raw_uploads = cursor.fetchall()

    uploads = []
    for upload_id, image_url, timestamp in raw_uploads:
        if timestamp:
            date_str = timestamp[:10]
            time_str = timestamp[11:16]
        else:
            date_str = 'Unknown'
            time_str = 'Unknown'

        # Fetch the prediction for the current upload_id
        cursor.execute("""
            SELECT skin_L, skin_A, skin_B, predicted_season
            FROM predictions
            WHERE upload_id = ?
        """, (upload_id,))
        prediction = cursor.fetchone()

        if prediction:
            skin_lab = prediction[:3]
            season = prediction[3]
            # Assumes classify_skin_tone is globally defined and accessible
            skin_tone = classify_skin_tone(skin_lab) 
            # Assumes SEASON_PALETTES is globally defined and accessible
            season_data = SEASON_PALETTES.get(season, {}) 
            season_colors = season_data.get("colors", [])
            avoid_colors = season_data.get("avoid_colors", [])
        else:
            skin_tone = None
            season_colors = []
            avoid_colors = []

        uploads.append({
            'id': upload_id,
            'image_url': image_url,
            'date': date_str,
            'time': time_str,
            'skin_tone': skin_tone,
            'season_colors': season_colors,
            'avoid_colors': avoid_colors
        })

    return render_template('recommendations.html', uploads=uploads)
### ADD this new route somewhere in your app.py ###

@app.route('/delete_upload/<int:upload_id>', methods=['POST'])
@login_required
def delete_upload(upload_id):
    if 'user_id' not in session:
        flash("Unauthorized", "danger")
        return redirect(url_for('login'))
    db = get_db()
    cursor = get_cursor()
    # Verify ownership
    cursor.execute("SELECT id FROM uploaded_images WHERE id = ? AND user_id = ?", (upload_id, session['user_id']))
    row = cursor.fetchone()
    if not row:
        flash("Upload not found or you are not authorized to delete it.", "danger")
        return redirect(url_for('recommendations'))

    # Soft delete: remove DB row(s). Keep Cloudinary asset intact.
    try:
        cursor.execute("DELETE FROM predictions WHERE upload_id = ?", (upload_id,))
        cursor.execute("DELETE FROM uploaded_images WHERE id = ?", (upload_id,))
        db.commit()
        flash("Upload removed from your history.", "success")
    except sqlite3.Error as e:
        db.rollback()
        flash("Failed to delete upload. Try again.", "danger")
        print("Delete error:", e)

    return redirect(url_for('recommendations'))

# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/looks")
@login_required
def looks():
    return render_template("looks.html", seasons=seasons_data)

@app.route('/profile')
@login_required
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    cursor = get_cursor()
    user_id = session['user_id']

    # Fetch the most recent prediction data for the logged-in user
    cursor.execute("""
        SELECT 
            hair_L, hair_A, hair_B,
            skin_L, skin_A, skin_B,
            eye_L, eye_A, eye_B,
            predicted_season
        FROM predictions
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))

    result = cursor.fetchone()

    if not result:
        flash("No color analysis data found. Please upload a photo first.", "warning")
        return redirect(url_for('upload'))

    hair_lab = result[0:3]
    skin_lab = result[3:6]
    eye_lab = result[6:9]
    season = result[9]

    def lab_to_rgb(lab_color):
        L = lab_color[0] * 255 / 100
        a = lab_color[1] + 128
        b = lab_color[2] + 128
        lab_scaled = np.uint8([[[L, a, b]]])
        rgb = cv2.cvtColor(lab_scaled, cv2.COLOR_LAB2RGB)[0][0]
        return [int(x) for x in rgb]

    hair_color = lab_to_rgb(hair_lab)
    skin_color = lab_to_rgb(skin_lab)
    eye_color = lab_to_rgb(eye_lab)

    season_data = SEASON_PALETTES.get(season, {})
    season_colors = season_data.get("colors", [])
    avoid_colors = season_data.get("avoid_colors", [])
    characteristics = season_data.get("characteristics", [])
    return render_template("profile.html",
                           hair_color=hair_color,
                           skin_color=skin_color,
                           eye_color=eye_color,
                           season_colors=season_colors,
                           avoid_colors=avoid_colors,
                           season=season,
                           characteristics = characteristics
                           )


@app.route("/chatbot")
def chatbot():
    return render_template(
        "chatbot.html",
      
    )

@app.route("/export_style_summary")
@login_required
def export_style_summary():
    return render_template(
        "export_style_summary.html",
      
    )

@app.route('/consulting')
@login_required
def consulting():
    return render_template("consulting.html")

@app.route('/details')
def details():
    return render_template("details.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")



#delete the account or data from a table of a user

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    # print("DB path:", os.path.abspath('myapp.db'))  # Add this line
    if request.form.get('confirm_delete') == 'yes':
        db = get_db()
        cursor = get_cursor()
        user_id = session.get('user_id')  # session holds their ID
        if user_id:
            # conn = sqlite3.connect('myapp.db')  #  DB
            cursor.execute("DELETE FROM users WHERE id =  ?", (user_id,))
            db.commit()
            session.clear()
            flash("Your account has been deleted successfully.", "success")
            return redirect('/account-deleted')
        return redirect('/')

@app.route('/account-deleted')
def account_deleted():
     return redirect("/")  # This will instantly redirect to /
    #  return "Your account has been deleted successfully."



# Change password

@app.route('/forgetpassword' , methods=["GET" , "POST"])
def forgetpassword():
    if request.method == "POST":
        email = request.form["email"]
        db = get_db()
        cursor = get_cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        if user:
           otp = str(random.randint(100000, 999999))
           session["reset_email"] = email
           session["reset_otp"] = otp
           send_otp_email(email, otp)
           flash("OTP has been sent to your email.", "info")
           return redirect("/verifyotp")
        else:
            flash("Email not found.", "danger")

    return render_template("forgetpassword.html")

def send_otp_email(to_email, otp):
    sender = "stylemate2025@gmail.com"
    password = os.environ.get('EMAIL_SENDER_PASSWORD')  #  app password, NOT your regular password
    
    subject = "Password Reset OTP"
    body = f"Hello,\n\nYour OTP for password reset is: {otp}\n\nIf you didn't request this, please ignore."
    
    msg = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to_email, msg)
        print("OTP email sent successfully.")
    # except smtplib.SMTPAuthenticationError:
    #     print("Authentication error: check your email and app password.")
    except Exception as e:
        print(f"Failed to send email: {e}")
@app.route('/verifyotp' , methods=["GET","POST"])
def verify_otp():
     if request.method == "POST":
        entered_otp = request.form["otp"]
        if entered_otp == session.get("reset_otp"):
            flash("OTP verified. Please reset your password.", "success")
            return redirect("/resetpassword")
        else:
            flash("Invalid OTP", "danger")

     return render_template("verify_otp.html")

@app.route("/resetpassword", methods=["GET", "POST"])
def resetpassword():
    if "reset_email" not in session:
        flash("Unauthorized access", "danger")
        return redirect("/login")
    db = get_db()
    cursor = get_cursor()
    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect("/resetpassword")
        
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_pw.decode('utf-8'), session["reset_email"]))
        db.commit()
        session.pop("reset_email", None)
        session.pop("reset_otp", None)
        flash("Password reset successfully!", "success")
        return redirect("/login")
    
    return render_template("reset_password.html")

# change password end 

# //new routes
@app.route('/services')
def services():
 return render_template("services.html")

@app.route('/about')
def about():
 return render_template("about.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        if not name or not email or not message:
            flash("All fields are required.", "danger")
            return render_template("contact.html")
        db = get_db()
        cursor = get_cursor()    
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("""
                INSERT INTO contact_submissions (name, email, subject, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, subject, message, timestamp))
            db.commit()
            
            # Optionally send an email notification here, but skipping for brevity.
            
            flash("Thank you for contacting us! We will respond shortly.", "success")
            return redirect(url_for('contact'))
            
        except sqlite3.Error as e:
            flash(f"A database error occurred: {e}", "danger")
            return render_template("contact.html")

    return render_template("contact.html")

@app.route('/editprofile')
@login_required
def editprofile():
     if 'user_id' not in session:
        return redirect(url_for('login')) # Added login check for safety

     cursor = get_cursor() # Retrieve cursor here
     cursor.execute("SELECT username, email, country, state, zipcode, gender FROM users WHERE id = ?", (session['user_id'],))
     row = cursor.fetchone()

     user= {
        "username": row[0],
        "email": row[1],
        "country": row[2],
        "state": row[3],
        "zipcode": row[4],
        "gender": row[5]
    }

     return render_template("editprofile.html" , user=user)

@app.route('/newdetails' , methods=["POST"])
@login_required
def newdetails():
    if 'user_id' not in session:
        flash("Unauthorized access", "danger")
        return redirect("/login")
    db = get_db()
    cursor = get_cursor()
    # Fetch the new form values
    new_username = request.form["username"]
    new_email = request.form["email"]
    new_country = request.form["country"]
    new_state = request.form["state"]
    new_zipcode = request.form["zipcode"]
    new_gender = request.form["gender"]

    # Optionally, compare with old values before updating

    # Update the database
    try:
        cursor.execute("""
            UPDATE users 
            SET username=?, email=?, country=?, state=?, zipcode=?, gender=?
            WHERE id=?
        """, (new_username, new_email, new_country, new_state, new_zipcode, new_gender, session['user_id']))
        db.commit()

        # Update session if necessary
        session["username"] = new_username
        session["email"] = new_email

        flash("Profile updated successfully!", "success")
        return redirect("/profile")
    except sqlite3.Error as err:
        flash(f"Error updating profile: {err}", "danger")
        return redirect("/editprofile")

@app.route('/login' , methods=["GET" , "POST"])
def login():
    next_page = request.args.get('next')  # Get the page to go next
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")
        db = get_db()
        cursor = get_cursor()
        cursor.execute("SELECT id,password,email,username FROM users WHERE email= ?" , (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            session['user_id'] = user[0]
            session["username"] = user[3]
            session["email"]= user[2]
             # Remember me logic: make session permanent
            if remember == "on":
                session.permanent = True
                app.permanent_session_lifetime = timedelta(days=3)

            flash("Login successful!", "success")
            return redirect(f"/{next_page}") if next_page else redirect("/")
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()  #it clears the session of a user 
    flash("logged out sucessfully", "info")
    return redirect("/login")

@app.route('/signup')
def signup():
    return render_template("register.html")

@app.route("/register" , methods=["POST"])
def register():
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    confirm_password = request.form["confirm_password"]
    country = request.form["country"]
    state = request.form["state"]
    zipcode = request.form["zipcode"]
    gender = request.form["gender"]
    terms = request.form["terms"]
    db = get_db()
    cursor = get_cursor()
    if password != confirm_password:
        flash("Passwords do not match" , "danger")
        return redirect("/signup")
    if terms != "agree":
        flash("You must agree to the terms and conditions", "danger")
        return redirect("/signup")
    # Hash the password
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try: 
        cursor.execute("""
        INSERT INTO users (username, email, password, country, state, zipcode, gender)
        VALUES (?, ?, ?, ?, ?, ?, ?)              
                       
        """ , (username, email, hashed_pw.decode('utf-8'), country, state, zipcode, gender))
        db.commit()
        flash("Registration successful!" , "success")

    except sqlite3.Error as err:
        flash(f"Error: {err}", "danger")

    return redirect("/login")


if __name__ == '__main__':
    app.run(debug=True)
