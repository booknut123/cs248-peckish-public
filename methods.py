import sqlite3
import pandas as pd
from pandas import DataFrame
from pandas import DataFrame
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

@st.cache_data
def get_menu(hall, meal, date):
    """
    * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
    * meal: string, 'Breakfast', 'Lunch' or 'Dinner'
    * date: datetime object, YYYY-MM-DD
    Returns the menu for a specific hall and meal on a specific date.
    Checks that each dish in the menu is already included in the "dish" database.
    If a dish is not included, adds the dish to the database with a new ID.
    """
    locationID, mealID = get_location_meal_ids(hall, meal)
    base_url = "https://dish.avifoodsystems.com/api/menu-items/week"
    params = {"date":date,"locationID":locationID,"mealID":mealID}
    try:
        response = requests.get(base_url,params=params)
    except:
        return pd.DataFrame()
    data = response.json()
    df = pd.DataFrame(data)
    df = clean_menu(df)

    df['date'] = df['date'].apply(lambda x: x.split("T")[0])
    df = df[df['date'] == str(date)]
    update_dish_db(df)

    return df

def get_filtered_menu(allergens, preferences, hall, meal, date):
    """
    * allergens: list of strings, [Dairy, Egg, Fish, Peanut, Sesame, Shellfish, Soy, Tree Nut, Wheat]
    * preferences: list of strings, [Gluten Sensitive, Vegan, Vegetarian] 
    * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
    * meal: string, 'Breakfast', 'Lunch' or 'Dinner'
    * date: datetime object, YYYY-MM-DD   
    Returns the menu for a specific hall and meal on a specific date with a specific filter applied.
    Checks that each dish in the menu is already included in the "dish" database.
    If a dish is not included, adds the dish to the database with a new ID.
    """
    df = get_menu(hall, meal, date)
    dfFiltered = filter_menu(df, allergens, preferences)

    #if not dfFiltered.empty:
    return dfFiltered
    

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

#     cur.execute(f"SELECT * FROM users WHERE user_id = {userID}")
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

    connect_bridge(userID, logID)

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
        cur.execute(f"INSERT INTO favorites (user_id, dish_id, date_added) VALUES (?, ?, ?)", (userID, dishID, date.today()))
    
    conn.commit()
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

    cur.execute(f"DELETE FROM favorites WHERE user_id = {userID} AND dish_id = {dishID}")

    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def remove_favorite(userID, dishID):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT COUNT(*) FROM favorites WHERE user_id = ? and dish_id = ?", (userID, dishID))
    if cur.fetchone()[0] > 0:
        cur.execute(f"DELETE FROM favorites WHERE user_id = ? and dish_id = ?", (userID, dishID))
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
    df = pd.read_sql_query(f"SELECT * FROM favorites WHERE (user_id = {userID})", conn)
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

create_database()

def sort_meals_by_date(df):
    print("")
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


    
