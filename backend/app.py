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
import mysql.connector
import random
import sqlite3
import smtplib
import bcrypt
from extract_colors import rgb_to_lab
from predict_season import predict_season

app = Flask(
    __name__,
    # template_folder="../frontend/templates",
    # static_folder="../frontend/static"
     template_folder=os.path.join("..", "frontend", "templates"),
            static_folder=os.path.join("..", "frontend", "static")
)
app.secret_key = "skinanalysis"

# MySQL Configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="samiya@2804",
    database="myapp"
)
cursor = db.cursor()
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Auto-create uploads
# save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
# file.save(save_path)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


BASE_DIR = os.path.dirname(__file__)
PALETTE_PATH = os.path.join(BASE_DIR, 'data', 'season_palettes.json')

# Load the palette data
with open(PALETTE_PATH, 'r') as f:
    SEASON_PALETTES = json.load(f)

@app.route('/')
def index():
    return render_template("index.html")

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
  
# @app.route('/analyze', methods=['POST'])
# def analyze():
#     coords = request.form['coords_json']
#     coords = __import__('json').loads(coords)
#     fn = request.form['filename']
#     img = cv2.imread(os.path.join(app.config['UPLOAD_FOLDER'], fn))
#     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     results = {}
#     labels = ['hair', 'eye', 'skin']

#     for i, pt in enumerate(coords):
#         x, y = map(int, (pt['x'], pt['y']))
#         region = img_rgb[max(y-3,0):y+3, max(x-3,0):x+3]
#         avg = np.mean(region.reshape(-1,3), axis=0)
#         lab = rgb_to_lab(avg)
#         rgb = lab_to_rgb(lab)
#         results[f'{labels[i]}_lab'] = [round(float(v)) for v in lab]
#         results[f'{labels[i]}_rgb'] = [int(v) for v in rgb]

#     return render_template('results.html', **results)

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

@app.route('/upload', methods=['GET', 'POST']  ,endpoint='upload')
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part"
        file = request.files['file']
        if file.filename == '':
            return "No selected file"
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now()  # actual datetime

            unique_filename = f"{filename.rsplit('.', 1)[0]}_{timestamp.strftime('%Y%m%d%H%M%S')}.{filename.rsplit('.', 1)[1]}"
            save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(save_path)

              #Save to MySQL database
            user_id = session.get('user_id')
            sql = "INSERT INTO uploaded_images (user_id, filename, timestamp) VALUES (%s, %s, %s)"
            val = (user_id, unique_filename, timestamp)
            cursor.execute(sql, val)
            db.commit()
            upload_id = cursor.lastrowid
             # Loading image and extract user-selected points
            
            # image = cv2.imread(save_path)
            # image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB

            # Read image and get color
            image = cv2.imread(save_path)
            if image is None:
                return "Image processing failed", 500
            
              # Get swatch coordinates from form
            hair_coord = request.form.get('hair')
            eye_coord = request.form.get('eye')
            skin_coord = request.form.get('skin')

            if not (hair_coord and eye_coord and skin_coord):
                return "Missing one or more swatch points", 400

            def get_rgb(coord):
                x, y = map(int, coord.split(','))
                return image[y, x][::-1]  # BGR to RGB
               # Extract RGB
            hair_rgb = get_rgb(hair_coord)
            eye_rgb = get_rgb(eye_coord)
            skin_rgb = get_rgb(skin_coord)
           
         # Convert to LAB
            hair_lab = [float(x) for x in rgb_to_lab(hair_rgb)]
            eye_lab = [float(x) for x in rgb_to_lab(eye_rgb)]
            skin_lab = [float(x) for x in rgb_to_lab(skin_rgb)]

            # Predict season
            season = predict_season(save_path)

            # Save prediction
            sql = """
                INSERT INTO predictions (
                    user_id, upload_id,
                    hair_L, hair_A, hair_B,
                    skin_L, skin_A, skin_B,
                    eye_L, eye_A, eye_B,
                    predicted_season
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
            def parse_coord(coord):
                x, y = map(int, coord.split(','))
                return (x, y)

            overlay_image = image.copy()
            draw_color_swatch(overlay_image, parse_coord(hair_coord), hair_rgb, "Hair")
            draw_color_swatch(overlay_image, parse_coord(skin_coord), skin_rgb, "Skin")
            draw_color_swatch(overlay_image, parse_coord(eye_coord), eye_rgb, "Eye")

            swatch_output_path = os.path.join(UPLOAD_FOLDER, f"{filename.rsplit('.', 1)[0]}_swatches.jpg")
            cv2.imwrite(swatch_output_path, overlay_image)

            overlay_filename = os.path.basename(swatch_output_path)
            season_data = SEASON_PALETTES.get(season, {})
            skin_tone_name = classify_skin_tone(skin_lab)

            season_description = season_data.get("description", "")
            season_colors = season_data.get("colors", [])
            avoid_colors = season_data.get("avoid_colors", [])
            makeup = season_data.get("makeup", {})
            fabrics = season_data.get("fabrics", [])
            tone_contrast = season_data.get("tone_contrast", "")

            return render_template('results.html',
                                   hair_color=hair_rgb,
                                   skin_color=skin_rgb,
                                   eye_color=eye_rgb,
                                   season=season,
                                   filename=unique_filename,
                                   overlay_image= overlay_filename,
                                   season_description=season_description,
                                   avoid_colors=avoid_colors,
                                   makeup=makeup,
                                   fabrics=fabrics,
                                   tone_contrast=tone_contrast,
                                   season_colors=season_colors,
                                   skin_tone_name=skin_tone_name,
                                   )

      
        # return redirect(url_for('upload'))  # reload page
    return render_template('upload.html')


UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # backend/uploads

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/results')
def results():
    return render_template("results.html")

@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Ensure only logged-in users access this

    user_id = session['user_id']
    cursor.execute("SELECT id ,filename, timestamp FROM uploaded_images WHERE user_id = %s", (user_id,))
    raw_uploads = cursor.fetchall()

    uploads = []

    for upload_id ,filename, timestamp in raw_uploads:
        cursor.execute("""
            SELECT skin_L, skin_A, skin_B, predicted_season
            FROM predictions
            WHERE upload_id = %s
        """, (upload_id,))
        prediction = cursor.fetchone()

        if prediction:
          skin_lab = prediction[:3]
          season = prediction[3]
          skin_tone = classify_skin_tone(skin_lab)

          season_data = SEASON_PALETTES.get(season, {})
          season_colors = season_data.get("colors", [])
          avoid_colors = season_data.get("avoid_colors", [])
        else:
          skin_tone = None
          season_colors = []
          avoid_colors = []


        # if timestamp is None:
        #   continue 
        uploads.append({
            'filename': filename,
            'date': timestamp.strftime('%Y-%m-%d')  if timestamp else 'Unknown',
            'time': timestamp.strftime('%I:%M:%S %p')  if timestamp else 'Unknown' ,
            'skin_tone': skin_tone,
            'season_colors': season_colors,
            'avoid_colors': avoid_colors
        })

    return render_template('recommendations.html', uploads=uploads)


# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Fetch the most recent prediction data for the logged-in user
    cursor.execute("""
        SELECT 
            hair_L, hair_A, hair_B,
            skin_L, skin_A, skin_B,
            eye_L, eye_A, eye_B,
            predicted_season
        FROM predictions
        WHERE user_id = %s
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

    return render_template("profile.html",
                           hair_color=hair_color,
                           skin_color=skin_color,
                           eye_color=eye_color,
                           season_colors=season_colors,
                           avoid_colors=avoid_colors,
                           season=season
                           )


@app.route('/chatbot')
def chatbot():
    return render_template("chatbot.html")

@app.route('/history')
def history():
    return render_template("history.html")

@app.route('/details')
def details():
    return render_template("details.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")



#delete the account or data from a table of a user

@app.route('/delete_account', methods=['POST'])
def delete_account():
    # print("DB path:", os.path.abspath('myapp.db'))  # Add this line
    if request.form.get('confirm_delete') == 'yes':
        user_id = session.get('user_id')  # session holds their ID
        if user_id:
            # conn = sqlite3.connect('myapp.db')  #  DB
            cursor.execute("DELETE FROM users WHERE id =  %s", (user_id,))
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
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
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
    sender = "samiyaa2804@gmail.com"
    password = "ewhp ivly ldpx kkyu"  #  app password, NOT your regular password
    
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

    if request.method == "POST":
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        
        if password != confirm_password:
            flash("Passwords do not match", "danger")
            return redirect("/resetpassword")
        
        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("UPDATE users SET password = %s WHERE email = %s", (hashed_pw.decode('utf-8'), session["reset_email"]))
        db.commit()
        session.pop("reset_email", None)
        session.pop("reset_otp", None)
        flash("Password reset successfully!", "success")
        return redirect("/login")
    
    return render_template("reset_password.html")

# change password end 



@app.route('/editprofile')
def editprofile():
     cursor.execute("SELECT username, email, country, state, zipcode, gender FROM users WHERE id = %s", (session['user_id'],))
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
def newdetails():
    if 'user_id' not in session:
        flash("Unauthorized access", "danger")
        return redirect("/login")

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
            SET username=%s, email=%s, country=%s, state=%s, zipcode=%s, gender=%s
            WHERE id=%s
        """, (new_username, new_email, new_country, new_state, new_zipcode, new_gender, session['user_id']))
        db.commit()

        # Update session if necessary
        session["username"] = new_username
        session["email"] = new_email

        flash("Profile updated successfully!", "success")
        return redirect("/profile")
    except mysql.connector.Error as err:
        flash(f"Error updating profile: {err}", "danger")
        return redirect("/editprofile")

@app.route('/login' , methods=["GET" , "POST"])
def login():
    next_page = request.args.get('next')  # Get the page to go next
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        remember = request.form.get("remember")
        cursor.execute("SELECT id,password,email,username FROM users WHERE email= %s" , (email,))
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
        VALUES (%s, %s, %s, %s, %s, %s, %s)              
                       
        """ , (username, email, hashed_pw.decode('utf-8'), country, state, zipcode, gender))
        db.commit()
        flash("Registration successful!" , "success")

    except mysql.connector.Error as err:
        flash(f"Error: {err}", "danger")

    return redirect("/login")


if __name__ == '__main__':
    app.run(debug=True)
