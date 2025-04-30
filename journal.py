import streamlit as st
import methods
import pandas as pd
from datetime import date
from datetime import datetime
import sqlite3
import time
import visualization_methods as vm
import random
import db_sync

import helper_methods
# helper_methods.create_database()
# st.write("Created database")
# helper_methods.weekly_update_db("4-20-2025")
# st.write("Updated weekly database")

user_id = st.session_state.get("user_id")

if not methods.check_id(user_id):
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

st.header("Journal")
    
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
            st.write("")
            
            st.write("")
            dateDict = sortedDF[key]
            #st.write(dateDict[0])

            col1, col2, col3, col4 = st.columns((1,3, 1,1), vertical_alignment='bottom') 
            col1.write("**Meal**")
            col2.write("**Dish**")
            col3.write("**Hall**")
            col4.write("**Delete**")
            st.write("")

            meals = {'Breakfast': 0, 'Lunch': 0, 'Dinner': 0} 
            for dish in dateDict:
                meals[dish['meal']] = meals.get(dish['meal']) + 1

            if meals['Breakfast'] != 0:  
                i=1
                for dish in dateDict:
                    if dish['meal'] == "Breakfast":
                        col1, col2, col3, col4 = st.columns((1,3, 1, 1))
                        if i==1:
                            col1.write("**Breakfast**")
                        if methods.check_is_favorite(user_id, dish['dish_id']):
                            col2.write(f"{methods.get_dish_name(dish['dish_id'])} :heart:")
                        else: 
                            col2.write(methods.get_dish_name(dish['dish_id']))
                        col3.write(dish['location'])
                        delete = col4.button("**-**", key=f"delete_{key}_{dish['dish_id']}") 
                        if delete:
                            methods.delete_meal(dish["log_id"], dish["dish_id"])
                            st.toast("Dish Deleted")
                            st.rerun() 
                        cals += methods.get_dish_calories(dish['dish_id'])
                        i+=1
                
            if meals['Lunch'] != 0:
                i=1
                for dish in dateDict:
                    if dish['meal'] == 'Lunch':
                        col1, col2, col3, col4 = st.columns((1,3, 1, 1))
                        if i==1:
                            col1.write("**Lunch**")
                        if methods.check_is_favorite(user_id, dish['dish_id']):
                            col2.write(f"{methods.get_dish_name(dish['dish_id'])} :heart:")
                        else: 
                            col2.write(methods.get_dish_name(dish['dish_id']))
                        col3.write(dish['location'])
                        delete = col4.button("**-**", key=f"delete_{key}_{dish['dish_id']}") 
                        if delete:
                            methods.delete_meal(dish["log_id"], dish["dish_id"])
                            st.toast("Dish Deleted")
                            st.rerun() 
                        cals += methods.get_dish_calories(dish['dish_id'])
                        i+=1

            if meals['Dinner'] != 0: 
                i=1
                for dish in dateDict:
                    if dish['meal'] == 'Dinner':
                        col1, col2, col3, col4 = st.columns((1,3, 1, 1))
                        if i==1:
                            col1.write("**Dinner**")
                        if methods.check_is_favorite(user_id, dish['dish_id']):
                            col2.write(f"{methods.get_dish_name(dish['dish_id'])} :heart:")
                        else: 
                            col2.write(methods.get_dish_name(dish['dish_id']))
                        col3.write(dish['location'])
                        delete = col4.button("**-**", key=f"delete_{key}_{dish['dish_id']}") 
                        if delete:
                            methods.delete_meal(dish["log_id"], dish["dish_id"])
                            st.toast("Dish Deleted")
                            st.rerun() 
                        cals += methods.get_dish_calories(dish['dish_id'])
                        i+=1

            st.divider() 
            
            datenote = methods.get_note(user_id, key)
            if datenote:
                st.write(f"**Note**: {datenote}")

            tags = methods.get_tags(user_id, key) 
            if tags:
                if tags[0]:
                    tags = tags[0].split(",")
                if tags[0]:
                    st.write(f"**Tags**: {', '.join([methods.get_username(tag) for tag in tags])}")

            col1, col2 = st.columns((2)) 
            
            with col1.expander("See Daily Nutrionals"):
                info = vm.get_stats_by_date(user_id,key)
                for n in info:
                    if n == "calories":
                        uom = "kcal"
                    elif n == "cholesterol" or n == "sodium":
                        uom = "mg"
                    else:
                        uom = "g"
                    st.write(f"{n}: {info[n]} {uom}") 

            with col2.expander("Add Note & Tag Friends"): 

                with st.form(f"Add Note {key}"):
                    note = st.text_input("Note (submit blank to delete):") 
                    submittedN = st.form_submit_button("Submit Note")
                    if submittedN:
                        methods.add_note(user_id, key, note)
                        st.toast("Note added!")
                        st.rerun()
                
                friends = methods.list_friends(user_id)
                if not friends:
                    st.write("You must add a friend on your Social page to tag them.")
                else:
                    with st.form(f"Tag Friend {key}"):
                        tagged = st.multiselect('Tags (submit blank to delete):', friends, format_func=lambda x: methods.get_username(x), placeholder="Search for friends by name!")
                        submittedT = st.form_submit_button("Submit Tags")
                        if submittedT:
                            methods.add_tags(user_id, key, tagged)
                            st.toast("Tags added!")
                            st.rerun()
        st.write("")

except Exception as e:
    #st.write(e)
    st.warning("Please log a meal in the Menus tab to view your journal.")

