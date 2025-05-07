import db_sync
import pandas as pd
from datetime import date

import methods.database_menu_methods as dm

def insert_dish(row):
    """
    Inserts the dish into the dishes database.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    cur.execute(f"""INSERT INTO dishes
                (dish_id, dish_name, description, rating, station, allergens, preferences, calories, fat, cholesterol, sodium, carbohydrates, sugars, protein)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (row['id'], row['name'], row['description'], 0, row['stationName'],",".join(row['allergens']), ",".join(row['preferences']),
                 row['calories'], row['fat'], row['cholesterol'], row['sodium'], row['carbohydrates'], row['sugars'], row['protein']))
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def get_user_logs(userID):
    """
    Returns a list of meal log IDs associated with a given user ID
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT log_id FROM dishes_log_bridge WHERE user_id = ?", (userID,))
    logs = cur.fetchall()
   
    logids = []

    for log in logs:
        if log[0] not in logids:
            logids.append(log[0])

    return logids

def get_log_dishes(logID):
    """
    * logID: int
    Returns the dish IDs associated with a given log ID
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT dish_ids FROM meal_log WHERE log_id = {logID}")

    dishes = cur.fetchone()[0].split(",")

    return dishes

def get_logIds_by_date(userId, date):
    """
    * userID: string
    * date: datetime object, YYYY-MM-DD
    Returns dataframe of all logs from a certain date
    """
    logIds = get_user_logs(userId)
    conn = dm.connect_db()
    cur = conn.cursor()
    id_list = ", ".join("?" for _ in logIds)
    df = pd.read_sql_query(f"SELECT log_id, dish_ids, dining_hall, meal_name FROM meal_log WHERE log_id IN ({id_list}) AND date_logged = {date}")
    conn.close()
    return df
    
def get_dishes_from_meal_log(userID, date, meal):
    """
    * userID: string
    * meal: string, 'Breakfast', 'Lunch' or 'Dinner'
    * date: datetime object, YYYY-MM-DD
    Returns a database dishes (and their calories) associated with a given User ID for a given date
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    logIDs = get_logIds_by_date(userID, date)
    meals = {}
    for id in logIDs:
        cur.exectue(f"SELECT dish_ids, dining_hall, meal_name WHERE (log_id = {id})")
  
    for meal in meals:
        dish = meals[meal]
        for id in dish:
            cur.execute(f"SELECT * FROM dishes WHERE dish_id = {id}")
            d = cur.fetchall()[0]
            meals.append({"meal": meal,"name": d[1], "calories": d[7]})
    df = pd.DataFrame(meals)
    conn.close()
    return df

def create_meal(userID, dishID, hall, mealName, date):
    """
    * userID: string
    * dishID: int
    * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
    * mealName: string, 'Breakfast', 'Lunch' or 'Dinner'
    * date: datetime object, YYYY-MM-DD
    Creates an entry in the meal database.
    Returns the logID for use in connect_bridge().
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    try:
        logs = get_user_logs(userID)
    except:
        logs = []
    found = False
    if logs:
        for log in logs:
            cur.execute(f"SELECT log_id FROM meal_log WHERE log_id = ? AND dining_hall = ? AND meal_name = ? AND date_logged = ?", (log, hall, mealName, date))
            meal = cur.fetchall()
            if meal:
                logID = meal[0][0]
                found = True
                break

    try:
        dishes = get_log_dishes(logID)
        if str(dishID) in dishes:
            return None
    except:
        dishes = []

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
    * userID: string
    * logID: int
    Connects userID and logID in the bridge table.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM dishes_log_bridge WHERE user_id = ? AND log_id = ?", (userID, logID))
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO dishes_log_bridge (user_id, log_id) VALUES (?, ?)", (userID, logID))
    
    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def get_dish_info(dishID):
    """
    * dishID: int
    Returns info about a dish, including dishname, description and nutrients.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM dishes WHERE (dish_id = {dishID})")
    return cur.fetchone()

def get_dish_calories(dishID):
    """
    * dishID: int
    Returns number of calories in a dish.
    """
    return get_dish_info(dishID)[7]

def get_dish_name(dishID):
    """
    * dishID: int
    Returns just the name of a dish based on id
    Credits: Maya, Nina
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    cur.execute(f"SELECT dish_name FROM dishes WHERE (dish_id = {dishID})")
    dish = cur.fetchone()[0]
    return dish

def log_meal(userID, dishID, hall, mealName, date):
    """
    * userID: int
    * dishID: int
    * hall: string, 'Bates', 'Lulu', 'Tower' or 'StoneD'
    * mealName: 'Breakfast', 'Lunch', 'Dinner' or 'Snack' (?)
    * date: datetime object / string, YYYY-MM-DD
    Logs new meal entry.
    Does not check for duplicates.
    Credits: Nina
    """
    
    logID = create_meal(userID, dishID, hall, mealName, date)

    if not logID:
        return False

    connect_bridge(userID, logID)
    return True

def delete_meal(logID, dishID):
    """
    * logID: int
    * dishID: int
    Removes meal associated with a given log ID and dish ID from the meal log and bridge databases.
    """
    conn = dm.connect_db()
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

def get_meal_log(userID):
    """
    userID: int
    Returns a list of all meals logged by a user
    Credits: Maya
    """
    logIDs = get_user_logs(userID)
    logIDs = ",".join([str(logID) for logID in logIDs])
    conn = dm.connect_db()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM meal_log WHERE log_id IN ({logIDs})")
    dishes = cur.fetchall()
    conn.close()
    return dishes

def get_dish_rating(dishID):
    """
    dishID: int
    returns rating of dish from dishes table
    Credit: Maya
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    cur.execute(f"SELECT rating FROM dishes WHERE dish_id = {dishID}")
    num = cur.fetchone()[0]
    conn.close()
    return num

def sort_meals_by_date(df):
    """
    df: DataFrame
    Returns a dictionary of meals sorted by date logged.
    """
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

def get_border_log_dates(userID):
    """
    * userID: string
    Returns all dates that meals were logged by a user,
    including the first and last dates
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    logs = get_user_logs(userID)
    placeholders = ','.join('?' for _ in logs)
    query = f"SELECT DISTINCT date_logged FROM meal_log WHERE log_id IN ({placeholders})"
    dates = cur.execute(query, (logs)).fetchall()
    dates = [date[0] for date in dates]

    dates2 = {"min":min(dates),"max":max(dates),"all":dates}

    return dates2

def get_total_dishes_logged(userID):
    """
    * userID: string
    Returns an integer number of dishes logged by a user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    
    logs = get_user_logs(userID)
    dishes = [get_log_dishes(log) for log in logs]
    numdishes = 0
    for dish in dishes:
        numdishes += len(dish)

    return numdishes

def get_log_date(logID):
    """
    * logID: int
    Returns the date in which a meal was logged by a user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    date = cur.execute("SELECT date_logged FROM meal_log WHERE log_id = ?", (logID,)).fetchone()[0]

    if date:
        date = '/'.join((date)[5:].split('-'))
        return date

def get_last_logged_date(userID, dishname):
    """
    * userID: string
    * dishname: string
    Returns the date in which a dish was last logged by a user.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    logs = get_user_logs(userID)

    dates = []
    for log in logs:
        dishes = [get_dish_name(dish) for dish in get_log_dishes(log)]
        if dishname in dishes:
            dates.append(get_log_date(log))
    
    if dates:
        return max(dates)
    else:
        return "Never"

def get_logIDs_by_date_range(dates):
    """
    * dates: list of datetime objects / strings, YYYY-MM-DD
    Returns a list of logIDs logged within a given date range.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    logs = []
    for date in dates:
        logs += cur.execute("SELECT log_id FROM meal_log WHERE date_logged = ?", (date,)).fetchall()

    return [log[0] for log in logs]

def get_log_hall(logID):
    """
    * logID: int
    Returns the hall in which a meal was logged.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    hall = cur.execute("SELECT dining_hall FROM meal_log WHERE log_id = ?", (logID,)).fetchone()[0]

    return hall

def get_dupe_dishIDs(dishname):
    """
    * dishname: string
    Returns the dishIDs for any dishes which share a common dishname.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    dishids = cur.execute("SELECT dish_id FROM dishes WHERE dish_name = ?", (dishname,)).fetchall()

    return dishids