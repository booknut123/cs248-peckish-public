import streamlit as st
import methods
import pandas as pd
from datetime import date
from datetime import datetime
import sqlite3
import time
import visualization_methods as vm
import db_sync

sidebar, main = st.columns((0.01, 1.5), gap="small", vertical_alignment="top")
try:
    user_id = int(st.session_state.get("user_id"))
except:
    col1, col2 = st.columns((0.3, 1.5))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("From CS248 '25 - Kailyn, Maya, Nina")
    
    st.warning("Not logged in.")
    st.write("Please return to home and log in with your Google account.")
    st.stop()

# with sidebar:
#     col1, col2 = st.columns((0.5, 1.5))
#     col1.image(image='crumb-the-goose.png')
#     col2.header("Peckish")
#     st.write(f"Today: {date.today()}")

with main:

    st.subheader("Journal")
    try:
    
        mealLog = methods.get_meal_log(user_id)
        
        def get_calories(dish_id):
            conn = sqlite3.connect(db_sync.get_db_path())
            try:
                result = conn.execute(
                    "SELECT calories FROM dishes WHERE dish_id = ?",
                    (dish_id,)
                ).fetchone()
                return result[0] if result else 0
            finally:
                conn.close()
        
        processed_data = []
        for entry in mealLog:
            log_id = entry[0]
            dish_ids = entry[1].split(',')  # Split comma-separated dish IDs
            location = entry[2]
            meal = entry[3]
            date = entry[4]
            
            # Create a separate row for each dish ID
            for dish_id in dish_ids:
                processed_data.append({
                    'log_id': log_id,
                    'dish_id': dish_id.strip(),  # Remove any whitespace
                    'location': location,
                    'meal': meal,
                    'date': date
                })

        df = pd.DataFrame(processed_data)
        df['calories'] = df['dish_id'].apply(lambda x: get_calories(x))

        sortedDF = methods.sort_meals_by_date(df)

        for key in sortedDF.keys():
            with st.container(border=True):
                cals = 0
                date = datetime.strptime(key, "%Y-%m-%d").date().weekday()
                weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                weekday = weekdays[date]

                st.subheader(f"{weekday}, {key}")
                col1, col2, col3, col4 = st.columns((1,1,2.5,1))
                col1.write("**Meal**")
                col2.write("**Hall**")
                col3.write("**Dish**")
                col4.write("**Delete**")
                for dish in sortedDF[key]:
                    col1, col2, col3, col4 = st.columns((1,1,2.5,1))
                    col1.write(dish["meal"])
                    col2.write(dish['location'])
                    col3.write(methods.get_dish_name(dish['dish_id']))
                    delete = col4.button("**-**", key=f"delete_ {key}_{dish['dish_id']}") 
                    if delete:
                        methods.delete_meal(dish["log_id"], dish["dish_id"])
                        st.toast("Dish Deleted")
                        time.sleep(1)
                        st.rerun() 
                    cals += methods.get_dish_calories(dish['dish_id'])
                st.write(f"~ Daily calories: {cals} kcal")

    except Exception:
        st.warning("Please log a meal in the Menus tab to view your journal.")
