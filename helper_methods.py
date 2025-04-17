import sqlite3
import pandas as pd
from pandas import DataFrame
import datetime
from datetime import date
import requests
import numpy as np
import db_sync

def create_database():
    db_sync.download_db_from_github()
    """
    Creates peckish database, creating tables that don't yet exist.
    """
    conn = sqlite3.connect("/tmp/peckish.db")
    cur = conn.cursor()

    #cur.execute("""DROP TABLE IF EXISTS users""")
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_id TEXT, 
                email TEXT UNIQUE,
                name TEXT,
                given_name TEXT,
                allergens TEXT,
                preferences TEXT,
                picture_url TEXT,
                first_seen TIMESTAMP,
                last_login TIMESTAMP
                );
                """)
    #cur.execute("""DROP TABLE IF EXISTS favorites""")
    cur.execute("""CREATE TABLE IF NOT EXISTS favorites (
                favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(user_id),
                dish_id INTEGER,
                date_added TEXT
            );
        """)
    
    #cur.execute("""DROP TABLE IF EXISTS dishes""")
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

    #cur.execute("""DROP TABLE IF EXISTS meal_log""")
    cur.execute("""CREATE TABLE IF NOT EXISTS meal_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                dish_ids TEXT,
                dining_hall TEXT,
                meal_name TEXT,
                date_logged TEXT,
                note TEXT
            );
        """)
    #cur.execute("""DROP TABLE IF EXISTS dishes_log_bridge""")
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
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("DROP TABLE IF EXISTS users")
    cur.execute("DROP TABLE IF EXISTS favorites")
    cur.execute("DROP TABLE IF EXISTS dishes")
    cur.execute("DROP TABLE IF EXISTS meal_log")
    cur.execute("DROP TABLE IF EXISTS dishes_log_bridge")

    create_database()

def connect_db():
    """
    Connects to peckish database.
    """
    return sqlite3.connect("/tmp/peckish.db")

def get_location_meal_ids(hall, meal):
    """
    Returns location and meal IDs associated with a specific request.
    """
    mealDict = {"Bates":{"Breakfast":145,"Lunch":146,"Dinner":311,"LocationID":95},"Lulu":{"Breakfast":148,"Lunch":149,"Dinner":312,"LocationID":96},"Tower":{"Breakfast":153,"Lunch":154,"Dinner":310,"LocationID":97},"StoneD":{"Breakfast":261,"Lunch":262,"Dinner":263,"LocationID":131}}
    return (mealDict[hall]["LocationID"],mealDict[hall][meal])

def clean_dicts(dct,name):
    """
    Helper function for clean_menu().
    Converts names from a dictionary into a comma seperated strings.
    """
    lst = []
    for i in dct:
        lst.append(i["name"])
    return lst

def clean_menu(df):
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
   
    cats = ['calories','fat','cholesterol','sodium','carbohydrates','sugars','protein']
    for cat in cats:
        df[cat] = df['nutritionals'].apply(lambda dct: int(dct[cat]) if dct[cat] else np.nan)
    df = df.drop("nutritionals", axis=1)

    df["allergens"] = df["allergens"].apply(lambda dct: clean_dicts(dct, "allergens"))
    df["preferences"] = df["preferences"].apply(lambda dct:clean_dicts(dct, "preferences"))

    df = df.drop_duplicates(subset=["id", "date"])

    return df

def insert_dish(row):
    """
    Inserts the dish into the dishes database.
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO dishes (dish_id, dish_name, description, rating, station, allergens, preferences, calories, fat, cholesterol, sodium, carbohydrates, sugars, protein) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(row['id'], row['name'], row['description'], 0, row['stationName'], ",".join(row['allergens']), ",".join(row['preferences']), row['calories'], row['fat'], row['cholesterol'], row['sodium'], row['carbohydrates'], row['sugars'], row['protein']))
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def update_dish_db(df):
    """
    Updates the dishes database after viewing a menu.
    For each dish, checks if that dish's ID is already in the database.
    If not, interts the dish into the database as a new entry.
    """
    conn = connect_db()
    cur = conn.cursor()
   
    cur.execute("SELECT COUNT(*) FROM dishes")
    if cur.fetchall() == 0:
        for _,row in df.iterrows():
            insert_dish(row)
    else:
        for _,row in df.iterrows():
            cur.execute(f"SELECT COUNT(*) FROM dishes WHERE dish_id = {row['id']}")
            num = cur.fetchall()[0][0]
            if num == 0:
                insert_dish(row)

def connect_bridge(userID, logID):
    """
    Connects userID and logID in the bridge table.
    """
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM dishes_log_bridge")
    if cur.fetchone()[0] == 0:
        bridgeID = 1
    else:
        cur.execute("SELECT bridge_id FROM dishes_log_bridge ORDER BY bridge_id DESC LIMIT 1;")
        bridgeID = cur.fetchone()[0] + 1

    cur.execute("INSERT INTO dishes_log_bridge (bridge_id, user_id, log_id) VALUES (?, ?, ?)", (bridgeID, userID, logID))
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def get_user_logs(userID):
    """
    Returns a list of meal log IDs associated with a given user ID
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT log_id FROM dishes_log_bridge WHERE user_id = {userID}")
    logs = cur.fetchall()
   
    logids = []

    for log in logs:
        if log[0] not in logids:
            logids.append(log[0])

    return logids

def get_log_dishes(logID):
    """
    Returns the dish IDs associated with a given log ID
    """
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT dish_ids FROM meal_log WHERE log_id = {logID}")

    dishes = cur.fetchone()[0].split(",")

    return dishes

def get_logIds_by_date(userId, date):
    """
    Returns dataframe of all logs from a certain date
    """
    logIds = get_user_logs(userId)
    conn = connect_db()
    cur = conn.cursor()
    id_list = ", ".join("?" for _ in logIds)
    df = pd.read_sql_query(f"SELECT log_id, dish_ids, dining_hall, meal_name FROM meal_log WHERE log_id IN ({id_list}) AND date_logged = date")
    conn.close()
    return df
    

# def get_dishes_from_meal_log(userID, date, meal):
#     """
#     Returns a database dishes (and their calories) associated with a given User ID for a given date
#     """
#     conn = connect_db()
#     cur = conn.cursor()

#     logIDs = get_logIds_by_date(userID, date)
#     meals = {}
#     for id in logIDs:
#         cur.exectue(f"SELECT dish_ids, dining_hall, meal_name WHERE (log_id = {id})")
  
#     for meal in meals:
#         dish = meals[meal]
#         for id in dish:
#             cur.execute(f"SELECT * FROM dishes WHERE dish_id = {id}")
#             d = cur.fetchall()[0]
#             m.append({"meal": meal,"name": d[1], "calories": d[7]})
#     df = pd.DataFrame(m)
#     conn.close()
#     return df

def create_meal(userID, dishID, hall, mealName, date):
    """
    Creates an entry in the meal database.
    Returns the logID for use in connect_bridge().
    """
    conn = connect_db()
    cur = conn.cursor()

    logs = get_user_logs(userID)
    found = False
    for log in logs:
        cur.execute(f"SELECT log_id FROM meal_log WHERE log_id = ? AND dining_hall = ? AND meal_name = ? AND date_logged = ?", (log, hall, mealName, date))
        meal = cur.fetchall()
        if meal:
            logID = meal[0][0]
            found = True
            break

    if found:
        cur.execute(f"SELECT dish_ids FROM meal_log WHERE log_id = {logID}")
        dishes = cur.fetchone()[0]

        newDishes = f"{dishes},{dishID}"

        cur.execute(f"UPDATE meal_log SET dish_ids = ? WHERE log_id = ?", (newDishes, logID))
        conn.commit()
        conn.close()
        
    else:
        date = str(date)
        cur.execute("INSERT INTO meal_log (dish_ids, dining_hall, meal_name, date_logged) VALUES (?,?,?,?)", (dishID, hall, mealName, date))

        cur.execute("SELECT MAX(log_id) FROM meal_log")
        
        logID = cur.fetchone()[0]

        conn.commit()
        conn.close()
        
    db_sync.push_db_to_github()
    return logID

def connect_bridge(userID, logID):
    """
    Connects userID and logID in the bridge table.
    """
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM dishes_log_bridge WHERE user_id = ? AND log_id = ?", (userID, logID))
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO dishes_log_bridge (user_id, log_id) VALUES (?, ?)", (userID, logID))
    
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()
    
def filter_menu(df, allergens, preferences):
    for allergen in allergens:
        df = df[df["allergens"].apply(lambda x: allergen not in x)]
    for preference in preferences:
        df = df[df["preferences"].apply(lambda x: preference in x)]
    return df


