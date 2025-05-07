import db_sync
import sqlite3
import datetime
from datetime import timedelta
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import requests

import methods.dishes_log_methods as dl

def connect_db():
    """
    Connects to peckish database.
    """
    return sqlite3.connect(db_sync.get_db_path())

def create_database():
    db_sync.download_db_from_github()
    """
    Creates peckish database, creating tables that don't yet exist.
    """
    conn = sqlite3.connect(db_sync.get_db_path())
    cur = conn.cursor()

    # cur.execute("""DROP TABLE IF EXISTS users""")
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id TEXT,
                email TEXT UNIQUE,
                name TEXT,
                user_name TEXT,
                given_name TEXT,
                allergens TEXT,
                preferences TEXT,
                picture_url TEXT,
                first_seen TIMESTAMP,
                last_login TIMESTAMP
                );
                """)
    
    # cur.execute("""DROP TABLE IF EXISTS favorites""")
    cur.execute("""CREATE TABLE IF NOT EXISTS favorites (
                favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(user_id),
                dish_id INTEGER,
                notification TEXT,
                date_added TEXT
            );
        """)
    
    # cur.execute("""DROP TABLE IF EXISTS dishes""")
    cur.execute("""CREATE TABLE IF NOT EXISTS dishes (
                dish_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dish_name TEXT,
                description TEXT,
                rating INTEGER,
                station TEXT,
                allergens TEXT,
                preferences TEXT,
                calories INTEGER,
                fat INTEGER,
                cholesterol INTEGER,
                sodium INTEGER,
                carbohydrates INTEGER,
                sugars INTEGER,
                protein INTEGER
            );
        """)
    
    # cur.execute("""DROP TABLE IF EXISTS current_dishes""")
    cur.execute("""CREATE TABLE IF NOT EXISTS current_dishes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    dish_id INTEGER references dishes(dish_id),
                    meal TEXT, 
                    location TEXT, 
                    date TEXT
                    );
                """)

    # cur.execute("""DROP TABLE IF EXISTS meal_log""")
    cur.execute("""CREATE TABLE IF NOT EXISTS meal_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dish_ids TEXT,
                dining_hall TEXT,
                meal_name TEXT,
                date_logged TEXT,
                note TEXT
            );
        """)
    # cur.execute("""DROP TABLE IF EXISTS dishes_log_bridge""")
    cur.execute("""CREATE TABLE IF NOT EXISTS dishes_log_bridge (
                bridge_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(user_id),
                log_id INTEGER REFERENCES meal_log(log_id)
            );
        """)
   
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()
   
    return conn

def clear_db():
    """
    Resets peckish database and removes all entries.
    """
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS favorites")
    cur.execute("DROP TABLE IF EXISTS dishes")
    cur.execute("DROP TABLE IF EXISTS current_dishes")
    cur.execute("DROP TABLE IF EXISTS meal_log")
    cur.execute("DROP TABLE IF EXISTS dishes_log_bridge")

    create_database()

def clean_dicts(dct, name):
    """
    Helper function for clean_WF_menu().
    Converts names from a dictionary into a comma separated strings.
    """
    lst = []
    for i in dct:
        lst.append(i["name"])
    return lst

def clean_WF_menu(df):
    """
    Cleans a WF API dataframe.
    Removes unused categories.
    Reformats nutritionals into new columns.
    Converts allergens and preferences into comma seperated strings.
    """
    cols = ["image","categoryName","stationOrder","price","servingSize","servingSizeUOM","caloriesFromFat","saturatedFat","transFat","dietaryFiber","addedSugar"]
    for col in cols:
        if col in df.columns:
            df = df.drop(col, axis=1)
   
    if not df.empty:
        cats = ['calories','fat','cholesterol','sodium','carbohydrates','sugars','protein']
        for cat in cats:
            if 'nutritionals' in df.columns:
                df[cat] = df['nutritionals'].apply(lambda dct: int(dct[cat]) if dct[cat] else np.nan)
        
        df = df.drop("nutritionals", axis=1)

        df["allergens"] = df["allergens"].apply(lambda dct: clean_dicts(dct, "allergens"))
        df["preferences"] = df["preferences"].apply(lambda dct:clean_dicts(dct, "preferences"))

        df = df.drop_duplicates(subset=["id", "date"])

    return df

def get_location_meal_ids(hall, meal):
    """
    * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
    * meal: string, 'Breakfast', 'Lunch' or 'Dinner'
    Returns location and meal IDs associated with a specific request.
    """
    mealDict = {
            "Bates": {
                "Breakfast": 145,
                "Lunch": 146,
                "Dinner": 311,
                "LocationID": 95},
            "Lulu": {
                "Breakfast": 148,
                "Lunch": 149,
                "Dinner": 312,
                "LocationID": 96},
            "Tower": {
                "Breakfast": 153,
                "Lunch": 154,
                "Dinner": 310,
                "LocationID": 97},
            "StoneD": {
                "Breakfast": 261,
                "Lunch": 262,
                "Dinner": 263,
                "LocationID": 131}}
    return (mealDict[hall]["LocationID"], mealDict[hall][meal])

def update_dish_db(df):
    """
    Updates the dishes database after viewing a menu.
    For each dish, checks if a dish's ID is already in the database.
    If not, interts the dish into the database as a new entry.
    """
    conn = connect_db()
    cur = conn.cursor()
   
    cur.execute("SELECT COUNT(*) FROM dishes")
    if cur.fetchall() == 0:
        for _,row in df.iterrows():
            dl.insert_dish(row)
    else:
        for _,row in df.iterrows():
            cur.execute(f"SELECT COUNT(*) FROM dishes WHERE dish_id = {row['id']}")
            num = cur.fetchall()[0][0]
            if num == 0:
                dl.insert_dish(row)
    db_sync.push_db_to_github()

@st.cache_data
def scrape_menu(hall, meal, date): # scrape menu from WellesleyFresh and add to dishes
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

    if not df.empty:
        df = clean_WF_menu(df)

        df['date'] = df['date'].apply(lambda x: x.split("T")[0])
        df = df[df['date'] == str(date)]
        update_dish_db(df)
        db_sync.push_db_to_github()
    
    return df

def weekly_update_db(sunday_date): # For use with current_dishes table
    """
    Updates current_dishes table for the next week.
    """
    conn = connect_db()
    cur = conn.cursor()

    #if table already populated, exit method
    num = cur.execute("SELECT COUNT(*) FROM current_dishes").fetchone()
    if num[0] != 0:
        date = cur.execute("SELECT date FROM current_dishes LIMIT 1").fetchone()
        if date[0] == sunday_date:
            return

    mealDict = {
        "Bates": {
            "Breakfast": 145,
            "Lunch": 146,
            "Dinner": 311,
            "LocationID": 95},
        "Lulu": {
            "Breakfast": 148,
            "Lunch": 149,
            "Dinner": 312,
            "LocationID": 96},
        "Tower": {
            "Breakfast": 153,
            "Lunch": 154,
            "Dinner": 310,
            "LocationID": 97},
        "StoneD": {
            "Breakfast": 261,
            "Lunch": 262,
            "Dinner": 263,
            "LocationID": 131}}
    
    st.write("weekly_update_db()")
    date_obj = datetime.strptime((sunday_date), "%Y-%m-%d")  # Parse the string
   
    cur.execute("""DROP TABLE IF EXISTS current_dishes""")
    cur.execute("""CREATE TABLE IF NOT EXISTS current_dishes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    dish_id INTEGER references dishes(dish_id),
                    meal TEXT, 
                    location TEXT, 
                    date TEXT
                    );
                """)
    
    for day in range(7):
        new_date = date_obj.date() + timedelta(days=day)
        for location, meals in mealDict.items():
            for meal, __ in meals.items():
                if meal != "LocationID":
                    df = scrape_menu(location, meal, new_date)
                    #st.write(f"{location} {meal} {new_date}")
                    #st.write(df)
                    update_dish_db(df)
                    
                    ## add to current_dishes
                    for _,row in df.iterrows():
                        #st.write(f"{row['id']} {meal} {location} {new_date}")
                        cur.execute(f"""INSERT INTO current_dishes (dish_id, meal, location, date) VALUES (?,?,?,?)""", (row['id'], meal, location, new_date))
                        conn.commit()
                                
    cur.close()
    conn.close()
    db_sync.push_db_to_github()  

def pescatarian(df):
    """
    Helper method for creating a preference that filters for dishes that include fish and shellfish, but no meat
    Credits: Maya
    """
    if not df.empty:
        df1 = df[df["allergens"].apply(lambda x: 'Fish' in x or 'Shellfish' in x)]
        df2 = df[df["preferences"].apply(lambda x: 'Vegetarian' in x)]
        df = pd.concat([df1, df2])
    return df

def filter_menu(df, allergens, preferences):
    """
    * allergens: list of strings, [Dairy, Egg, Fish, Peanut, Sesame, Shellfish, Soy, Tree Nut, Wheat]
    * preferences: list of strings, [Gluten Sensitive, Vegan, Vegetarian]
    Uses inputted allergens and preferences and returns a dataframe with meals that match the filter criteria.
    Credits: Nina, Maya
    """
    for pref in preferences:
        if pref == "Pescatarian":
            df = pescatarian(df)
    if not df.empty:
        for allergen in allergens:
            df = df[df["allergens"].apply(lambda x: allergen not in x)]
        for preference in preferences:
            if preference != "Pescatarian":
                df = df[df["preferences"].apply(lambda x: preference in x)]
    return df

def get_menu(hall, meal, date):
    """
    * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
    * meal: string, 'Breakfast', 'Lunch' or 'Dinner'
    * date: datetime object, YYYY-MM-DD
    Returns dataframe for a certain dining hall, meal, and date.
    """
    conn = connect_db()  
    df = pd.read_sql_query(
            """SELECT * FROM CURRENT_DISHES WHERE location = ? AND meal = ? AND date = ?""",
            conn,
            params=(hall, meal, date))
    return df

def print_menu(allergens, preferences, hall, meal, date):
    """
    * allergens: list of strings, [Dairy, Egg, Fish, Peanut, Sesame, Shellfish, Soy, Tree Nut, Wheat]
    * preferences: list of strings, [Gluten Sensitive, Vegan, Vegetarian]
    * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
    * meal: string, 'Breakfast', 'Lunch' or 'Dinner'
    * date: datetime object, YYYY-MM-DD
    Updates the user's allergens and preferences.
    Credits: 
    """
    current_menu = get_menu(hall, meal, date)
    
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
    dfFiltered = filter_menu(full_menu, allergens, preferences)

    return dfFiltered