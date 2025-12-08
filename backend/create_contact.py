import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "myapp.db")

def migrate_uploaded_images_table():
    db = sqlite3.connect(DB_PATH)
    cursor = db.cursor()
    print("Starting database migration...")

    # Step 1: Check if the 'uploaded_images' table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='uploaded_images';")
    if cursor.fetchone() is None:
        print("Table 'uploaded_images' does not exist. Creating new table.")
        # If the table genuinely doesn't exist, create the complete new version.
        cursor.execute("""
            CREATE TABLE uploaded_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                image_url TEXT NOT NULL,      
                public_cloud_id TEXT NOT NULL,  
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        db.commit()
        return

    # Step 2: Check for and add the 'image_url' column (assuming the old table used 'filename')
    try:
        # Check if the required new columns are missing
        cursor.execute("PRAGMA table_info(uploaded_images);")
        columns = [info[1] for info in cursor.fetchall()]

        if 'image_url' not in columns:
            print("Migrating: Adding 'image_url' and 'public_cloud_id' columns.")
            
            # Add image_url column
            cursor.execute("ALTER TABLE uploaded_images ADD COLUMN image_url TEXT;")
            
            # Add public_cloud_id column
            cursor.execute("ALTER TABLE uploaded_images ADD COLUMN public_cloud_id TEXT;")
            
            db.commit()
            print("Migration successful: Columns added for Cloudinary integration.")
        else:
            print("Migration skipped: Cloudinary columns already exist.")

    except sqlite3.Error as e:
        print(f"Migration error: {e}")
        # Rollback in case of error
        db.rollback() 
    finally:
        db.close()


if __name__ == '__main__':
    migrate_uploaded_images_table()