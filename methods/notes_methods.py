import db_sync
import datetime
from datetime import datetime

import methods.database_menu_methods as dm
import methods.dishes_log_methods as dl

def add_note(userID, date, note):
    """
    * userID: string
    * date: datetime object / string, YYYY-MM-DD
    * note: string
    Adds / updates the note for a day for a given user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    num = cur.execute("SELECT COUNT(*) FROM notes WHERE user_id = ? AND date = ?", (userID, date)).fetchone()[0]
    
    if num == 0:
        cur.execute("INSERT INTO notes (user_id, date, note) VALUES (?, ?, ?)", (userID, date, note))
        conn.commit()

    else:
        cur.execute("UPDATE notes SET note = ? WHERE user_id = ? AND date = ? ", (note, userID, date))
        conn.commit()
    
    db_sync.push_db_to_github()

    conn.close()

def get_note(userID, date):
    """
    * userID: string
    * date: datetime object / string, YYYY-MM-DD
    Returns the note for a day for a given user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    note = cur.execute("SELECT note FROM notes WHERE user_id = ? AND date = ?", (userID, date)).fetchone()

    if not note:
        return ""

    else:
        return note[0]
    
def add_tags(userID, date, tagslist):
    """
    * userID: string
    * date: datetime object / string, YYYY-MM-DD
    * taglist: list of strings (userIDs)
    Adds / updates the tags for a day for a given user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    tags = ",".join(tagslist)

    num = cur.execute("SELECT COUNT(*) FROM notes WHERE user_id = ? AND date = ?", (userID, date)).fetchone()[0]
    
    if num == 0:
        cur.execute("INSERT INTO notes (user_id, date, tags) VALUES (?, ?, ?)", (userID, date, tags))
        conn.commit()

    else:
        cur.execute("UPDATE notes SET tags = ? WHERE user_id = ? AND date = ? ", (tags, userID, date))
        conn.commit()

    conn.close()
    db_sync.push_db_to_github()

def get_tags(userID, date):
    """
    * userID: string
    * date: datetime object / string, YYYY-MM-DD
    Returns the tags for a day for a given user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    tags = cur.execute("SELECT tags FROM notes WHERE user_id = ? AND date = ?", (userID, date)).fetchone()
    
    if not tags:
        return None

    else:
        return tags
    
def get_tag_history(userID, friendID):
    """
    * userID: string
    * friendID: string
    Returns the tags and notes associated with days where two users tagged eachother.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    logs = dl.get_user_logs(friendID)
    dates = set([dl.get_log_date(log) for log in logs])
    dates = [str(datetime.strptime(f"2025/{date}", "%Y/%m/%d").date()) for date in dates]

    taghistory = {}
    for date in dates:
        tags = get_tags(friendID, date)
        if tags and tags[0]:
            tags = (tags[0]).split(",")
            if tags and (userID in tags):
                taghistory[date] = (get_note(friendID, date), tags)

    return taghistory