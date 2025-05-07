from flask import Flask, render_template,  request, redirect, flash
import mysql.connector
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
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload')
def upload():
    return render_template("upload.html")


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

@app.route('/login')
def login():
    return render_template("login.html")

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
