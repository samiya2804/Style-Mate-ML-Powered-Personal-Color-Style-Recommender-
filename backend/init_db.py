import mysql.connector

# Connect to your MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="samiya@2804",
    database="myapp"
)

cursor = db.cursor()

# Create the table
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        upload_id INT,
        hair_L FLOAT,
        hair_A FLOAT,
        hair_B FLOAT,
        skin_L FLOAT,
        skin_A FLOAT,
        skin_B FLOAT,
        eye_L FLOAT,
        eye_A FLOAT,
        eye_B FLOAT,
        predicted_season VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (upload_id) REFERENCES uploaded_images(id)
    );
    """)
    print("✅ Table 'predictions' created successfully.")
except mysql.connector.Error as err:
    print("❌ Error:", err)

db.close()
