# Create a file: add_test_mood.py
import sqlite3
from datetime import datetime, date

conn = sqlite3.connect('mood_data.db')
cursor = conn.cursor()

# Add a test mood
cursor.execute('''
    INSERT INTO moods (date, timestamp, mood, mood_value, category, notes, color)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (
    date.today().isoformat(),
    datetime.now().isoformat(),
    "😊 Happy",
    5,
    "positive",
    "Test mood entry",
    "#4CAF50"
))

conn.commit()
print("✅ Added test mood to database")
conn.close()