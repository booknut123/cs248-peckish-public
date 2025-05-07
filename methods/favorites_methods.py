import db_sync
import pandas as pd
from datetime import date

import methods.database_menu_methods as dm
import methods.dishes_log_methods as dl

def add_favorite(userID, dishID):
    """
    * userID: int
    * dishID: int
    Checks if a dish is already favorited by the user.
    If not, adds the dish as a new entry.
    Credits: Nina, Maya
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    if not check_is_favorite(userID, dishID):
        cur.execute(f"INSERT INTO favorites (user_id, dish_id, notification, date_added) VALUES (?, ?, ?, ?)", (userID, dishID, "false", date.today()))
    
    cur.execute(F"UPDATE dishes SET rating = rating + 1 WHERE dish_id = {dishID}")
    
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def update_ratings():
    """
    Helper function when favorites table did not align with ratings in dish table
    Updates ratings according to the favorites table
    Credits: Maya
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT dish_id FROM favorites")
    favs = cur.fetchall()

    ratings = []
    for id in favs:
        cur.execute(f"SELECT COUNT(*) from favorites WHERE dish_id = {id[0]}")
        r = cur.fetchone()
        ratings += [(id[0], r[0])]
    for r in ratings:
        cur.execute("UPDATE dishes SET rating = ? WHERE dish_id = ?", (r[1], r[0]))
    conn.close()
    db_sync.push_db_to_github()


def remove_favorite(userID, dishID):
    """
    * userID: string
    * dishID: int
    Checks if a dish is already favorited by the user.
    If it is, it removes the dish from the table.
    Credit: Nina, Maya
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    cur.execute(f"DELETE FROM favorites WHERE user_id = ? AND dish_id = ?", (userID, dishID))
    cur.execute(f"UPDATE dishes SET rating = rating - 1 WHERE dish_id = {dishID}")
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def check_is_favorite(userID, dishID):
    """
    * userID: string
    * dishID: int
    Returns a boolean indicating whether a dish is the favorite of a user or not.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM favorites WHERE user_id = ? AND dish_id = ?", (userID, dishID))
    num = cur.fetchone()[0]
    if num == 0:
        return False
    return True

def display_favorites(userID):
    """
    * userID: string
    Returns a dataframe of dishes favorited by a user.
    """
    conn = dm.connect_db()
    df = pd.read_sql_query(f"SELECT * FROM favorites WHERE user_id = ?", conn, params=(userID, ))
    conn.close()
    return df

def top5favs():
    """
    Returns a list of the dishes with the top 5 highest ratings in dishes table.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    cur.execute("SELECT dish_name, rating FROM dishes ORDER BY rating DESC")
    top5 = cur.fetchmany(5)
    conn.close()
    return top5

def weeklyTop5favs():
    """
    Returns a list of the top 5 dishes being served this week with the highest rating.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    cur.execute("SELECT dish_id FROM current_dishes")
    dishes = cur.fetchall()
    dishes = [id[0] for id in dishes]
    ids = ", ".join(str(id) for id in dishes)
    cur.execute(f"SELECT dish_name, rating FROM dishes WHERE dish_id in ({ids}) ORDER BY rating DESC")
    top5 = cur.fetchmany(5)
    conn.close()
    return top5

def check_is_notif(userID, dishID):
    """
    * userID: string
    * dishID: int
    Returns a boolean indicating whether a user has turned on notifications for a favorited dish.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    stuff = cur.execute(f"SELECT notification FROM favorites WHERE user_id = ? AND dish_id = ?", (userID, dishID)).fetchone()[0]

    if stuff == "false":
        return False
    return True

def toggle_notif(userID, dishID):
    """
    * userID: string
    * dishID: int
    Toggles notifications for a dish for a given user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    if not check_is_notif(userID, dishID):
        cur.execute("UPDATE favorites SET notification = ? WHERE user_id = ? AND dish_id = ?", ("true", userID, dishID))
    else:
        cur.execute("UPDATE favorites SET notification = ? WHERE user_id = ? AND dish_id = ?", ("false", userID, dishID))

    conn.commit()
    conn.close()

def get_user_favorites(userID):
    """
    * userID: string
    Returns dish ids and notif bool for each dish a user has favorited
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    faves = cur.execute("SELECT dish_id, notification FROM favorites WHERE user_id = ?", (userID,)).fetchall()
    return faves

def get_faves_for_week(userID, date):
    """
    * userID: string
    * date: datetime object / string, YYYY-MM-DD
    Returns a list of dishes and their appearances in the upcoming week for a given user's favorites.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    faves = get_user_favorites(userID)
    faves = [fave[0] for fave in faves if fave[1] == "true"]

    if not faves:
        return None
    
    placeholders = ','.join('?' for _ in faves)

    query = f"SELECT dish_id, meal, location, date FROM current_dishes WHERE dish_id IN ({placeholders}) AND date >= {str(date)}"

    dishes = cur.execute(query, (faves)).fetchall()
    dishnames = [dl.get_dish_name(dish[0]) for dish in dishes]

    organizeddishes = {}
    for dish, name in zip(dishes, dishnames):
        if name not in organizeddishes:
            organizeddishes[name] = [{"meal": dish[1], "location": dish[2], "date": dish[3]}]
        else:
            organizeddishes[name] += [({"meal": dish[1], "location": dish[2], "date": dish[3]})]

    return organizeddishes

def compare_favorites(userID, friendID):
    """
    * userID: string
    * friendID: string
    Returns a list of dishIDs shared between two users.
    """
    userfaves = [fave[0] for fave in get_user_favorites(userID)]
    friendfaves = [fave[0] for fave in get_user_favorites(friendID)]

    sharedfaves = [fave for fave in userfaves if fave in friendfaves]

    return sharedfaves

def get_fave_date(userID, dishID):
    """
    * userID: string
    * dishID: int
    Returns the date in which a dish was (most recently) favorited by a user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    date = cur.execute("SELECT date_added FROM favorites WHERE user_id = ? and dish_id = ?", (userID, dishID,)).fetchone()[0]

    if date:
        date = '/'.join((date)[5:].split('-'))
        return date
