import db_sync

import methods.database_menu_methods as dm

def send_friend_request(userID, friendID):
    conn = dm.connect_db()
    cur = conn.cursor()

    #Check if friend is in friends table, updates if not and sends request

    #check is friend
    #if not:
    cur.execute("INSERT INTO requests (user_id, request) VALUES (?, ?)", (userID, friendID,))
    conn.commit()

    conn.close()
    db_sync.push_db_to_github()

def accept_friend_request(userID, friendID):
    conn = dm.connect_db()
    cur = conn.cursor()

    #check is friend
    #if not:
    cur.execute("INSERT INTO friends (user_id, friend) VALUES (?, ?)", (userID, friendID,))
    conn.commit()
    cur.execute("INSERT INTO friends (user_id, friend) VALUES (?, ?)", (friendID, userID,))
    conn.commit()

    remove_friend_request(userID, friendID)

    db_sync.push_db_to_github()


def remove_friend_request(userID, friendID):
    conn = dm.connect_db()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM requests WHERE user_id = ? AND request = ?", (userID, friendID))
    conn.commit()

    cur.execute("DELETE FROM requests WHERE user_id = ? AND request = ?", (friendID, userID))
    conn.commit() 

    conn.close()
    db_sync.push_db_to_github()

def remove_friend(userID, friendID):
    conn = dm.connect_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM friends WHERE user_id = ? AND friend = ?", (userID, friendID))
    conn.commit()

    cur.execute("DELETE FROM friends WHERE user_id = ? AND friend = ?", (friendID, userID))
    conn.commit()  
    
    conn.commit()
    conn.close()
    db_sync.push_db_to_github()

def list_friends(userID):
    conn = dm.connect_db()
    cur = conn.cursor()
    friends = cur.execute("SELECT friend FROM friends WHERE user_id = ?", (userID,)).fetchall()
    
    friends = [friend[0] for friend in friends]
    return friends

def list_friend_requests(userID):
    conn = dm.connect_db()
    cur = conn.cursor()
    requests = cur.execute("SELECT user_id FROM requests WHERE request = ?", (userID,)).fetchall()

    requests = [request[0] for request in requests]

    return requests

def list_outgoing_requests(userID):
    conn = dm.connect_db()
    cur = conn.cursor()

    requests = cur.execute("SELECT request FROM requests WHERE user_id = ?", (userID,)).fetchall()

    requests = [request[0] for request in requests]

    return requests

def get_optin(userID):
    conn = dm.connect_db()
    cur = conn.cursor()
    
    current = cur.execute("SELECT optin FROM users WHERE user_id = ?", (userID,)).fetchone()[0]

    if current == "true":
        return True
    else:
        return False

def toggle_optin(userID):
    
    current = get_optin(userID)

    conn = dm.connect_db()
    cur = conn.cursor()

    if current:    
        cur.execute("DELETE FROM requests WHERE user_id = ?", (userID,))
        cur.execute("DELETE FROM requests WHERE request = ?", (userID,))
        cur.execute("DELETE FROM friends WHERE user_id = ?", (userID,))
        cur.execute("DELETE FROM friends WHERE friend = ?", (userID,))
    else: 
        cur.execute("UPDATE users SET optin = ? WHERE user_id = ?", ("true", userID))
    
    conn.commit()
    conn.close()
    db_sync.push_db_to_github()
