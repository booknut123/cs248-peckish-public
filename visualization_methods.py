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
        avgcals[key] = mealcals[key] / mealcounts[key]

    return avgcals




