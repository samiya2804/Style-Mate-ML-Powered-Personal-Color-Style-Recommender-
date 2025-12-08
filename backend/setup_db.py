import sqlite3

conn = sqlite3.connect("myapp.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT UNIQUE,
    password TEXT,
    country TEXT,
    state TEXT,
    zipcode TEXT,
    gender TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS uploaded_images (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    filename TEXT,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    upload_id INTEGER,
    hair_L REAL, hair_A REAL, hair_B REAL,
    skin_L REAL, skin_A REAL, skin_B REAL,
    eye_L REAL, eye_A REAL, eye_B REAL,
    predicted_season TEXT
)
""")

conn.commit()
conn.close()

print("Database setup complete!")
