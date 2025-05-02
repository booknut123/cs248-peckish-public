# Prof Eni's code

import sqlite3
from datetime import datetime
from typing import List

from db_sync import get_db_path
DB_NAME = get_db_path()

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Table for individual users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE
        )
    ''')

    # Table for submission summaries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS missing_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            total_missing INTEGER,
            comment TEXT,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Table for individual missing dishes (linked to summary)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS missing_dishes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dish_id INTEGER,
            date TEXT,
            dining_hall TEXT,
            meal TEXT,
            user_id INTEGER,
            summary_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (summary_id) REFERENCES missing_summary(id)
        )
    ''')

    conn.commit()
    conn.close()


def store_missing_data(
    missing_dish_ids: List[int],
    date: str,
    dining_hall: str,
    meal: str,
    comment: str,
    username: str
):
    timestamp = datetime.now().isoformat(timespec='seconds')
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Ensure user exists and fetch user_id
    cursor.execute('INSERT OR IGNORE INTO users (username) VALUES (?)', (username,))
    cursor.execute('SELECT id FROM users WHERE username = ?', (username,))
    user_id = cursor.fetchone()[0]

    # Insert summary record and get its ID
    cursor.execute('''
        INSERT INTO missing_summary (timestamp, total_missing, comment, user_id)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, len(missing_dish_ids), comment, user_id))
    summary_id = cursor.lastrowid

    # Insert missing dish records linked to summary
    for dish_id in missing_dish_ids:
        cursor.execute('''
            INSERT INTO missing_dishes (dish_id, date, dining_hall, meal, user_id, summary_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (dish_id, date, dining_hall, meal, user_id, summary_id))

    conn.commit()
    conn.close()


# Call this once in your main app to initialize the DB (if not already)
if __name__ == "__main__":
    init_db()
    print("Database initialized.")
