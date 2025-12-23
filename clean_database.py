# clean_database.py
import sqlite3

conn = sqlite3.connect('mood_data.db')
cursor = conn.cursor()

# Delete all rows
cursor.execute("DELETE FROM moods")
conn.commit()

# Reset auto-increment
cursor.execute("DELETE FROM sqlite_sequence WHERE name='moods'")
conn.commit()

print("✅ Database cleaned. Ready for new data.")
conn.close()