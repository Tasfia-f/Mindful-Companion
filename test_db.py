import sqlite3
import os

# Test database connection
print(f"Current directory: {os.getcwd()}")
print(f"Database exists: {os.path.exists('mood_data.db')}")

try:
    conn = sqlite3.connect('mood_data.db')
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables in database: {tables}")
    
    # Check moods table
    cursor.execute("SELECT COUNT(*) FROM moods")
    count = cursor.fetchone()[0]
    print(f"Rows in moods table: {count}")
    
    # Show first few rows
    cursor.execute("SELECT * FROM moods ORDER BY timestamp DESC LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  - {row}")
    
    conn.close()
    
except Exception as e:
    print(f"Error: {e}")