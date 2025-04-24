import pandas as pd
import datetime
from datetime import date
import requests
import numpy as np
import streamlit as st
import db_sync

from helper_methods import *

def get_dish_info(dishID):
    """
    Returns entire row about a dish
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM dishes WHERE (dish_id = {dishID})")
    return cur.fetchone()

def get_dish_calories(dishID):
    return get_dish_info(dishID)[7]

def get_dish_name(dishID):
        """
        Returns just the name of a dish based on id
        """
        conn = connect_db()
        cur = conn.cursor()

        cur.execute(f"SELECT dish_name FROM dishes WHERE (dish_id = {dishID})")
        dish = cur.fetchone()[0]
        return dish

# @st.cache_data
# def scrape_menu(hall, meal, date): # scrape menu from WellesleyFresh and add to dishes
#     """
#     * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
#     * meal: string, 'Breakfast', 'Lunch' or 'Dinner'
#     * date: datetime object, YYYY-MM-DD
#     Returns the menu for a specific hall and meal on a specific date.
#     Checks that each dish in the menu is already included in the "dish" database.
#     If a dish is not included, adds the dish to the database with a new ID.
#     """
#     locationID, mealID = get_location_meal_ids(hall, meal)
#     base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
#     params = {"date":date,"locationID":locationID,"mealID":mealID}
#     try:
#         response = requests.get(base_url,params=params)
#     except:
#         return pd.DataFrame()
#     data = response.json()
#     df = pd.DataFrame(data)
#     df = clean_WF_menu(df)

#     df['date'] = df['date'].apply(lambda x: x.split("T")[0])
#     df = df[df['date'] == str(date)]
#     update_dish_db(df)

#     return df

# def get_menu(hall, meal, date):
#     conn = connect_db()  
#     df = pd.read_sql_query(
#             """SELECT * FROM CURRENT_DISHES WHERE location = ? AND meal = ? AND date = ?""",
#             conn,
#             params=(hall, meal, date))
#     return df

def print_menu(allergens, preferences, hall, meal, date):
    # st.write(f"print_menu({hall}, {meal}, {date})")
    current_menu = get_menu(hall, meal, date)
    # st.write(current_menu)
    
    conn = connect_db()
    dish_details = pd.read_sql_query(
        f"""SELECT dish_id, dish_name, calories, allergens, preferences FROM dishes
            WHERE dish_id IN ({','.join(['?'] * len(current_menu))})""",
        conn,
        params=current_menu['dish_id'].tolist()
    )
    conn.close()
    
    # Merge and select columns
    full_menu = current_menu.merge(dish_details, on='dish_id')[['dish_id', 'dish_name', 'calories', 'allergens', 'preferences']]
    #st.write(full_menu)
    dfFiltered = filter_menu(full_menu, allergens, preferences)

    #if not dfFiltered.empty:
    return dfFiltered
        
# def get_filtered_menu(allergens, preferences, hall, meal, date):
#     """
#     * allergens: list of strings, [Dairy, Egg, Fish, Peanut, Sesame, Shellfish, Soy, Tree Nut, Wheat]
#     * preferences: list of strings, [Gluten Sensitive, Vegan, Vegetarian] 
#     * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
#     * meal: string, 'Breakfast', 'Lunch' or 'Dinner'
#     * date: datetime object, YYYY-MM-DD   
#     Returns the menu for a specific hall and meal on a specific date with a specific filter applied.
#     Checks that each dish in the menu is already included in the "dish" database.
#     If a dish is not included, adds the dish to the database with a new ID.
#     """
#     df = get_menu(hall, meal, date)
#     dfFiltered = filter_menu(df, allergens, preferences)

#     #if not dfFiltered.empty:
#     return dfFiltered
    

def update_user_allergens_preferences(userID, allergens, preferences):
    """
    * userID: int
    * allergens: list of strings, [Dairy, Egg, Fish, Peanut, Sesame, Shellfish, Soy, Tree Nut, Wheat]
    * preferences: list of strings, [Gluten Sensitive, Vegan, Vegetarian]
    Updates the user's allergens and preferences.
    """
    conn = connect_db()
    cur = conn.cursor()

    allergens = ",".join(allergens)
    preferences = ",".join(preferences)

    cur.execute("UPDATE users SET allergens = ? WHERE user_id = ? ", (allergens, userID))
    cur.execute("UPDATE users SET preferences = ? WHERE user_id = ? ", (preferences, userID))

    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

# def get_user_allergens_preferences(userID):
#     """
#     * userID: int
#     Returns a tuple ([allergens], [preferences]) associated with a given user ID
#     """
#     conn = connect_db()
#     cur = conn.cursor()

#     cur.execute(f"SELECT * FROM users WHERE user_id = ?", (userID,))
#     stuff = cur.fetchall()

#     print(stuff)

#     # allergens = ",".join(allergens)
#     # preferences = ",".join(preferences)

#     conn.commit()
#     conn.close()

def log_meal(userID, dishID, hall, mealName, date):
    """
    * userID: int
    * dishID: int
    * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
    * mealName: 'Breakfast', 'Lunch', 'Dinner' or 'Snack' (?)
    * date: datetime object / string, YYYY-MM-DD
    Logs new meal entry.
    Does not check for duplicates.
    """
    
    logID = create_meal(userID, dishID, hall, mealName, date)

    if not logID:
        return False

    connect_bridge(userID, logID)
    return True

# Section for favorites
def add_favorite(userID, dishID):
    """
    * userID: int
    * dishID: int
    Checks if a dish is already favorited by the user.
    If not, adds the dish as a new entry.
    """
    conn = connect_db()
    cur = conn.cursor()

    if not check_is_favorite(userID, dishID):
        cur.execute(f"INSERT INTO favorites (user_id, dish_id, notification, date_added) VALUES (?, ?, ?, ?)", (userID, dishID, "false", date.today()))
    
    cur.execute(F"UPDATE dishes SET rating = rating + 1 WHERE dish_id = {dishID}")
    
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def update_ratings():
    conn = connect_db()
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
    * userID: int
    * dishID: int
    Checks if a dish is already favorited by the user.
    If it is, it removes the dish from the table.
    """
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"DELETE FROM favorites WHERE user_id = ? AND dish_id = ?", (userID, dishID))
    cur.execute(f"UPDATE dishes SET rating = rating - 1 WHERE dish_id = {dishID}")
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def remove_favorite(userID, dishID):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM favorites WHERE user_id = ? and dish_id = ?", (userID, dishID))
    if cur.fetchone()[0] > 0:
        cur.execute(f"DELETE FROM favorites WHERE user_id = ? and dish_id = ?", (userID, dishID))
    
    cur.execute(f"UPDATE dishes SET rating = rating - 1 WHERE dish_id = {dishID}")
    conn.commit()
    conn.close()
        
    db_sync.push_db_to_github()

def check_is_favorite(userID, dishID):
    """
    * userID: int
    * dishID: int
    Returns a boolean indicating whether a dish is the favorite of a user or not.
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM favorites WHERE user_id = ? AND dish_id = ?", (userID, dishID))
    num = cur.fetchone()[0]
    if num == 0:
        return False
    return True

def display_favorites(userID):
    conn = connect_db()
    df = pd.read_sql_query(f"SELECT * FROM favorites WHERE user_id = ?", conn, params=(userID, ))
    # st.write(df)
    conn.close()
    return df

# def favorites_toggle(userID, dishID):
#     """
#     * toggle: Bool
#     * userID: int
#     * dishID: int
#     Callback function for favorites toggle
#     Checks whether dish is already in favorites.
#     If it is not, it calls add_favorite
#     If it is, it calls remove_favorite
#     """
#     conn = connect_db()
#     cur = conn.cursor()
#     toggle = cur.execute(f"SELECT EXISTS (SELECT 1 FROM favorites WHERE favorites.user_id = {userID} AND favorites.dish_id = {dishID})")
#     conn.commit()
#     conn.close()
    
#     if toggle:
#         remove_favorite(userID, dishID)
#     else:
#         add_favorite(userID, dishID)

# def log_meal(userID, dishID, hall, mealName, date):
#     """
#     FOR USE IN STREAMLIT
#     * userID: int
#     * dishID: int
#     * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
#     * mealName: 'Breakfast', 'Lunch', 'Dinner' or 'Snack' (?)
#     * date: datetime object / string, YYYY-MM-DD
#     Logs new meal entry.
#     Does not check for duplicates.
#     """
#     logID = create_meal(dishID, hall, mealName, date)
#     connect_bridge(userID, logID)

def delete_meal(logID, dishID):
    """
    * logID: int
    * dishID: int
    Removes meal associated with a given log ID and dish ID from the meal log and bridge databases.
    """
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"SELECT dish_ids FROM meal_log WHERE log_id = {logID}")
    dishes = cur.fetchone()

    dishes = [dish for dish in dishes][0].split(",")
    dishes = [dish for dish in dishes if dish != str(dishID)]

    if not dishes:
        cur.execute(f"DELETE FROM meal_log WHERE log_id = {logID}")
        cur.execute(f"DELETE FROM dishes_log_bridge WHERE log_id = {logID}")

    else:
        dishes = ",".join(dishes)
        cur.execute("UPDATE meal_log SET dish_ids = ? WHERE log_id = ?", (dishes, logID))

    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def display_meal_log(userID):
    """
    * userID: int
    * logID: int
    Removes meal associated with a given user ID and log ID from the dishes database.
    """
    conn = connect_db()
    cur = conn.cursor()

    logIDs = get_user_logs(userID)
    
    meals = []
    for log in logIDs:
        meals.append(get_log_dishes(log))

    for meal in meals:
        for id in meal:
            cur.execute("SELECT * FROM dishes WHERE dish_id = ?")

    #for item in meals:

    #df = pd.DataFrame(columns=['something','something'])
    #for meal in meals:
        
    #return 

def check_is_favorite(userID, dishID):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM favorites WHERE user_id = ? AND dish_id = ?", (userID, dishID))
    num = cur.fetchone()[0]

    if num == 0:
        return False
    else:
        return True

def get_meal_log(userID):
    
    logIDs = get_user_logs(userID)
    logIDs = ",".join([str(logID) for logID in logIDs])
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM meal_log WHERE log_id IN ({logIDs})")
    dishes = cur.fetchall()
    conn.close()
    return dishes

def get_dish_rating(dishID):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) FROM favorites WHERE dish_id = {dishID}")
    num = cur.fetchone()[0]
    return num

def top5favs():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT dish_name, rating FROM dishes ORDER BY rating DESC")
    top5 = cur.fetchmany(5)
    conn.close()
    return top5


def sort_meals_by_date(df):
    dates = sorted(df["date"].unique(), reverse=True)

    my_dict = df.to_dict(orient='index')
    keys = my_dict.keys()

    date_sorted = {}
    for date in dates:
        dishes = []
        for key in keys:
            if my_dict[key]['date'] == date:
                dishes += [my_dict[key]]
        date_sorted[date] = dishes
    
    return date_sorted

def get_user_allergens_preferences(userID):
     """
     * userID: int
     Returns the user's allergens and preferences as a tuple (allergens, preferences)
     """
     conn = connect_db()
     cur = conn.cursor()
 
     cur.execute(f"SELECT allergens, preferences FROM users where user_id = ?", (userID,))
     stuff = cur.fetchone()
 
 
     conn.close()
     return stuff

def get_username(user_id):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute(f"SELECT user_name FROM users WHERE user_id = ?", (user_id,))
    username = cur.fetchone()
    return username[0]
 
def set_username(userID, username):
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (username, userID))
    conn.commit()
    conn.close()

def get_border_log_dates(userID):
    """
    Returns all dates that meals were logged by a user,
    including the first and last dates
    """
    conn = connect_db()
    cur = conn.cursor()

    logs = get_user_logs(userID)
    placeholders = ','.join('?' for _ in logs)
    query = f"SELECT DISTINCT date_logged FROM meal_log WHERE log_id IN ({placeholders})"
    dates = cur.execute(query, (logs)).fetchall()
    dates = [date[0] for date in dates]

    dates2 = {"min":min(dates),"max":max(dates),"all":dates}

    return dates2


def check_is_notif(userID, dishID):
    conn = connect_db()
    cur = conn.cursor()

    stuff = cur.execute(f"SELECT notification FROM favorites WHERE user_id = ? AND dish_id = ?", (userID, dishID)).fetchone()[0]

    if stuff == "false":
        return False
    return True

def toggle_notif(userID, dishID):
    conn = connect_db()
    cur = conn.cursor()

    if not check_is_notif(userID, dishID):
        cur.execute("UPDATE favorites SET notification = ? WHERE user_id = ? AND dish_id = ?", ("true", userID, dishID))
    else:
        cur.execute("UPDATE favorites SET notification = ? WHERE user_id = ? AND dish_id = ?", ("false", userID, dishID))

    conn.commit()
    conn.close()

def get_user_favorites(userID):
    """
    Returns dish ids and notif bool for each dish a user has favorited
    """
    conn = connect_db()
    cur = conn.cursor()

    faves = cur.execute("SELECT dish_id, notification FROM favorites WHERE user_id = ?", (userID,)).fetchall()
    return faves

def get_faves_for_week(userID, date):
    conn = connect_db()
    cur = conn.cursor()

    faves = get_user_favorites(userID)
    faves = [fave[0] for fave in faves if fave[1] == "true"]

    if not faves:
        return None
    
    placeholders = ','.join('?' for _ in faves)

    query = f"SELECT dish_id, meal, location, date FROM current_dishes WHERE dish_id IN ({placeholders}) AND date >= {str(date)}"

    dishes = cur.execute(query, (faves)).fetchall()
    dishnames = [get_dish_name(dish[0]) for dish in dishes]

    organizeddishes = {}
    for dish, name in zip(dishes, dishnames):
        if name not in organizeddishes:
            organizeddishes[name] = [{"meal": dish[1], "location": dish[2], "date": dish[3]}]
        else:
            organizeddishes[name] += [({"meal": dish[1], "location": dish[2], "date": dish[3]})]

    return organizeddishes

def get_user_join_date(userID):
    conn = connect_db()
    cur = conn.cursor()

    date = cur.execute("SELECT first_seen FROM users WHERE user_id = ?", (userID,)).fetchone()[0]
    return date.split(" ")[0]

def get_total_dishes_logged(userID):
    conn = connect_db()
    cur = conn.cursor()
    
    logs = get_user_logs(userID)
    dishes = [get_log_dishes(log) for log in logs]
    numdishes = 0
    for dish in dishes:
        numdishes += len(dish)

    return numdishes

def add_note(userID, date, note):
    conn = connect_db()
    cur = conn.cursor()

    num = cur.execute("SELECT COUNT(*) FROM notes WHERE user_id = ? AND date = ?", (userID, date)).fetchone()[0]
    
    if num == 0:
        cur.execute("INSERT INTO notes (user_id, date, note) VALUES (?, ?, ?)", (userID, date, note))
        conn.commit()

    else:
        cur.execute("UPDATE notes SET note = ? WHERE user_id = ? AND date = ? ", (note, userID, date))
        conn.commit()

    conn.close()

def get_note(userID, date):
    conn = connect_db()
    cur = conn.cursor()

    note = cur.execute("SELECT note FROM notes WHERE user_id = ? AND date = ?", (userID, date)).fetchone()

    if not note:
        return ""

    else:
        return note[0]

def get_name(userID):
    conn = connect_db()
    cur = conn.cursor()

    name = cur.execute("SELECT name FROM users WHERE user_id = ?", (userID,)).fetchone()

    return name[0]
  

def get_all_names():
    conn = connect_db()
    cur = conn.cursor()

    names = cur.execute("SELECT DISTINCT name FROM users").fetchall()

    return names

def add_tags(userID, date, tagslist):
    conn = connect_db()
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

def get_tags(userID, date):
    conn = connect_db()
    cur = conn.cursor()

    tags = cur.execute("SELECT tags FROM notes WHERE user_id = ? AND date = ?", (userID, date)).fetchone()
    
    if not tags:
        return None

    else:
        return tags

def check_id(userID):
    conn = connect_db()
    cur = conn.cursor()
    match = cur.execute("SELECT user_id FROM users WHERE user_id = ?", (userID, )).fetchone()
    return (match != None)