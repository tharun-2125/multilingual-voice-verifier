import sqlite3
import os

db_path = "traceclaim.db"

if not os.path.exists(db_path):
    print("Database file does not exist yet. It will be created automatically on the next request.")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check existing columns
    cursor.execute("PRAGMA table_info(transcriptions);")
    columns = [row[1] for row in cursor.fetchall()]
    
    migrated = False
    
    if "content_category" not in columns:
        print("Adding column 'content_category' to transcriptions table...")
        cursor.execute("ALTER TABLE transcriptions ADD COLUMN content_category VARCHAR;")
        migrated = True
        
    if "recommendations" not in columns:
        print("Adding column 'recommendations' to transcriptions table...")
        cursor.execute("ALTER TABLE transcriptions ADD COLUMN recommendations TEXT;")
        migrated = True
        
    if "extracted_claim" not in columns:
        print("Adding column 'extracted_claim' to transcriptions table...")
        cursor.execute("ALTER TABLE transcriptions ADD COLUMN extracted_claim TEXT;")
        migrated = True
        
    if migrated:
        conn.commit()
        print("Database migration completed successfully.")
    else:
        print("Database already has the required columns. No migration needed.")
        
    conn.close()
