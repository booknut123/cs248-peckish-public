import pandas as pd
from datetime import date
from datetime import timedelta

import methods.database_menu_methods as dm
import methods.dishes_log_methods as dl


def get_user_stats_by_meal(userID):
    """
    * userID: string
    Returns a dataframe including nutritional information about each meal logged by a user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    logids = dl.get_user_logs(userID)
    dishes = [dl.get_log_dishes(logid) for logid in logids]

    stats = []

    for meal in dishes:
        for dish in meal:
            cur.execute(f"SELECT * FROM dishes WHERE dish_id = {dish}")
            d = cur.fetchall()[0]
            stats.append({"calories": d[7], "fat": d[8], "cholesterol": d[9], "sodium": d[10], "carbohydrates": d[11], "sugars": d[12], "protein": d[13]})
    df = pd.DataFrame(stats)
    return df

def get_total_nutrients(userID, stat):
    """
    * userID: string
    * stat: string
    Returns the total and average (per meal) number of a stat for a given user.
    """
    df = get_user_stats_by_meal(userID)
    total = df[stat].sum()
    average = total/len(df)
    return (total, average)

def visualize_total_stats(userID, stat):
    """
    * userID: string
    * stat: string
    Returns a list of nutritional information about each meal logged by a user.
    """
    df = get_user_stats_by_meal(userID)
    return df[stat].tolist()

def dining_hall_tracker(userID):
    """
    * userID: int
    Returns how often a user visits each dining hall
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    logids = dl.get_user_logs(userID)
    dhall_counter = {'Lulu': 0, 'Bates': 0, 'StoneD': 0, 'Tower': 0}
    for id in logids:
        cur.execute(f"SELECT dining_hall FROM meal_log WHERE log_id = {id}")
        dhall = cur.fetchone()[0]
        dhall_counter[dhall] += 1
    conn.close()
    return dhall_counter

def average_cals_by_meal(userID):
    """
    * userID: string
    Returns average calories by meal type (breakfast, lunch, dinner) for a given user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    logids = dl.get_user_logs(userID)

    mealcounts = {"Breakfast": 0, "Lunch":0, "Dinner":0}
    mealcals = {"Breakfast": 0, "Lunch":0, "Dinner":0}

    for id in logids:

        cur.execute(f"SELECT meal_name FROM meal_log WHERE log_id = {id}")
        mealName = cur.fetchone()[0]

        mealcounts[mealName] += 1

        dishes = dl.get_log_dishes(id)
        cals = 0
        for dish in dishes:
            cals += dl.get_dish_calories(dish)
        
        mealcals[mealName] += cals

    avgcals = {}

    for key in mealcals.keys():
        if mealcals[key] == 0 or mealcounts[key] == 0:
            avgcals[key] = 0
        else:
            avgcals[key] = mealcals[key] / mealcounts[key]

    return avgcals

def get_stats_by_date(user_id, date):
    """
    * userID: string
    * date: datetime object / string, YYYY-MM-DD
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    logs = dl.get_user_logs(user_id)
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
            info = dl.get_dish_info(d)
            for i, nutrient in enumerate(nutrients):
                statdict[nutrient] += info[start_index + i]
        
    return statdict
 
def get_stats_by_date_range(user_id, date1, date2, nutrients):
    """
    * userID: string
    * date1: datetime object / string, YYYY-MM-DD
    * date2: datetime object / string, YYYY-MM-DD
    * nutrients: list of strings
    Returns a dictionary of nutritional stats for a user in a given date range (date1 to date2).
    """
    dates = pd.date_range(date1, date2)
    dates = [str(date).split(" ")[0] for date in dates]
    stats = {n:{} for n in nutrients}


    for date in dates:
        info = get_stats_by_date(user_id, date)
        for n in nutrients:
            stats[n][date] = info[n]

    return stats

def hall_popularity_last_7_days():
    """
    Returns a dictionary containing the number of meals logged at each dining hall in the past 7 days.
    """
    today = date.today()
    dates = [str(today - timedelta(days=i)) for i in range(0,7)]

    logs = dl.get_logIDs_by_date_range(dates)

    halls = [dl.get_log_hall(log) for log in logs]
    
    hallcounts = {"Bates": halls.count("Bates"), "Lulu": halls.count("Lulu"), "Tower": halls.count("Tower"), "StoneD": halls.count("StoneD")}

    return hallcounts




