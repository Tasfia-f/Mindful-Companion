# test_encoding.py
import sqlite3

conn = sqlite3.connect('mood_data.db')
conn.text_factory = str  # Force UTF-8
cursor = conn.cursor()

# Test inserting emoji
test_mood = "😊 Happy"
cursor.execute("INSERT INTO moods (date, timestamp, mood, mood_value, category, notes, color) VALUES (?, ?, ?, ?, ?, ?, ?)",
              ('2025-12-22', '2025-12-22T20:41:39.338571', test_mood, 5, 'positive', 'Test', '#4CAF50'))
conn.commit()

# Read it back
cursor.execute("SELECT mood FROM moods ORDER BY id DESC LIMIT 1")
result = cursor.fetchone()
print(f"Stored mood: {result[0]}")
print(f"Type: {type(result[0])}")
print(f"Raw bytes: {result[0].encode('utf-8')}")

conn.close()