from methods import *
import db_sync
import sqlite3

def update_db_stuff():
    db_sync.download_db_from_github()
    """
    Creates peckish database, creating tables that don't yet exist.
    """
    conn = sqlite3.connect(db_sync.get_db_path())
    cur = conn.cursor()

    # cur.execute("""DELETE FROM users
    #                 WHERE user_id = ?;""", (___,))
    
    # cur.execute("""
    #             UPDATE notes
    #             SET tags = ?""", 
    #             (None,))

    # cur.execute("DELETE FROM friends")

    # cur.execute("""
    #             ALTER TABLE users
    #             ADD COLUMN optin TEXT
    #             DEFAULT true
    #             """)

    # cur.execute("""
    #             ALTER TABLE friends
    #             RENAME COLUMN incoming_requests TO requests
    #             """)

    # cur.execute("""
    #             ALTER TABLE friends
    #             DROP COLUMN outgoing_requests
    #             """)
    
    # cur.execute("""CREATE TABLE IF NOT EXISTS notes (
    #             user_id TEXT,
    #             date TEXT,
    #             note TEXT
    #             );
    #             """)
            
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()
   
    return conn

# update_db_stuff()