import sqlite3
import pandas as pd
from pandas import DataFrame
import datetime
from datetime import date
import requests
import numpy as np
import methods as m
import helper_methods as hm



def get_user_stats_by_meal(userID):
    conn = hm.connect_db()
    cur = conn.cursor()

    logids = m.get_user_logs(userID)
    dishes = [m.get_log_dishes(logid) for logid in logids]

    stats = []

    for meal in dishes:
        for dish in meal:
            cur.execute(f"SELECT * FROM dishes WHERE dish_id = {dish}")
            d = cur.fetchall()[0]
            stats.append({"calories": d[7], "fat": d[8], "cholesterol": d[9], "sodium": d[10], "carbohydrates": d[11], "sugars": d[12], "protein": d[12]})
    df = pd.DataFrame(stats)
    return df

def get_total_nutrients(userID, stat):
    df = get_user_stats_by_meal(userID)
    total = df[stat].sum()
    average = total/len(df)
    return (total, average)

def visualize_total_stats(userID, stat):
    df = get_user_stats_by_meal(userID)
    return df[stat].tolist()

def dining_hall_tracker(userID):
    conn = hm.connect_db()
    cur = conn.cursor()
    logids = m.get_user_logs(userID)
    dhall_counter = {'Lulu': 0, 'Bates': 0, 'StoneD': 0, 'Tower': 0}
    for id in logids:
        cur.execute(f"SELECT dining_hall FROM meal_log WHERE log_id = {id}")
        dhall = cur.fetchone()[0]
        dhall_counter[dhall] += 1
    conn.close()
    return dhall_counter

def average_cals_by_meal(userID):
    conn = hm.connect_db()
    cur = conn.cursor()

    logids = m.get_user_logs(userID)

    mealcounts = {"Breakfast": 0, "Lunch":0, "Dinner":0}
    mealcals = {"Breakfast": 0, "Lunch":0, "Dinner":0}

    for id in logids:

        cur.execute(f"SELECT meal_name FROM meal_log WHERE log_id = {id}")
        mealName = cur.fetchone()[0]

        mealcounts[mealName] += 1

        dishes = m.get_log_dishes(id)
        cals = 0
        for dish in dishes:
            cals += m.get_dish_calories(dish)
        
        mealcals[mealName] += cals

    avgcals = {}

    for key in mealcals.keys():
        if mealcals[key] == 0 or mealcounts[key] == 0:
            avgcals[key] = 0
        else:
            avgcals[key] = mealcals[key] / mealcounts[key]

    return avgcals

def get_stats_by_date(user_id, date):
    conn = hm.connect_db()
    cur = conn.cursor()

    logs = m.get_user_logs(user_id)
    placeholders = ','.join('?' for _ in logs)
    query = f"SELECT dish_ids FROM meal_log WHERE log_id IN ({placeholders}) AND date_logged = ?"
    dishes = cur.execute(query, (*logs, date)).fetchall()
    dishes = [dish[0] for dish in dishes]

    statdict = {"calories":0, "fat":0, "cholesterol":0, "sodium":0, "carbohydrates":0, "sugars":0, "protein":0}
    nutrients = ["calories", "fat", "cholesterol", "sodium", "carbohydrates", "sugars", "protein"]
    start_index = 7

    for dish in dishes:
        dishs = dish.split(",")
        for d in dishs:
            info = m.get_dish_info(d)
            for i, nutrient in enumerate(nutrients):
                statdict[nutrient] += info[start_index + i]
        
    return statdict
 
def get_stats_by_date_range(user_id, date1, date2, nutrients):

    dates = pd.date_range(date1, date2)
    dates = [str(date).split(" ")[0] for date in dates]
    stats = {n:{} for n in nutrients}


    for date in dates:
        info = get_stats_by_date(user_id, date)
        for n in nutrients:
            stats[n][date] = info[n]

    return stats




