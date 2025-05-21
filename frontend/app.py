from flask import Flask, render_template,  request, redirect, flash , session , url_for
from datetime import timedelta 
import os  
from flask import send_from_directory
import time
from datetime import datetime
from werkzeug.utils import secure_filename
from email.mime.text import MIMEText
import mysql.connector
import random
import sqlite3
import smtplib
import bcrypt

app = Flask(__name__)
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
@app.route('/')
def index():
    return render_template("index.html")

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

            #  timestamp unique
            ts_str = timestamp.strftime("%Y%m%d%H%M%S")
            unique_filename = f"{filename.rsplit('.', 1)[0]}_{ts_str}.{filename.rsplit('.', 1)[1]}"
            save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            file.save(save_path)

            # ✅ Save to MySQL database
            user_id = session.get('user_id')
            sql = "INSERT INTO uploaded_images (user_id, filename, timestamp) VALUES (%s, %s, %s)"
            val = (user_id, unique_filename, timestamp)
            cursor.execute(sql, val)
            db.commit()

            return redirect(url_for('upload'))  # reload page
    return render_template('upload.html')

@app.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # secure the page

    user_id = session['user_id']
    cursor.execute("SELECT filename, timestamp FROM uploaded_images WHERE user_id = %s", (user_id,))
    raw_uploads = cursor.fetchall()

    uploads=[]

    for filename, timestamp in raw_uploads: 
           if isinstance(timestamp, str):
            timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
           uploads.append({
            'filename': filename,
            'date': timestamp.strftime('%Y-%m-%d'),
            'time': timestamp.strftime('%I:%M:%S %p')
        })


    return render_template('recommendations.html', uploads=uploads)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")

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
