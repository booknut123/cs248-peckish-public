import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import requests
import methods as m
import helper_methods as hm

def write_streamlit():
    st.set_page_config(
        page_title="Peckish",
        page_icon="crumb-the-goose.png",
        initial_sidebar_state="collapsed",
        layout="wide")
    hm.create_database()

    sidebar, main = st.columns((0.5, 1.5), gap="small", vertical_alignment="center")
    
    with sidebar:
        # st.write("Placeholder")
        st.header("Peckish")
        st.subheader(f"Today: {date.today()}")
        userId = 0 #for testing purposes
        st.write(f"User ID: {userId}")
    
    with main:
        
        
        home, menus, journal, visualize, favorites, settings = st.tabs(["Home", "Menus", "Journal", "Visualize", "Favourites", "Settings"])
        with home:
            st.header("Home")
            st.write(f"Hello today is: {date.today()}**(change format)**! Here is what *selected dining hall* is offering today! "
                     + "Or maybe some info about the weather?? Something nice and friendly?")
            st.sidebar.write("**Maybe we could have info about top rated foods for today here? and other daily info?**")
        
        with menus:
            st.header("Menus")
            
            testID = st.text_input("TestID (try 1!)", key="visualization test")

            location = st.pills("Pick a location!", ("Bates", "Lulu", "Tower", "StoneD"), selection_mode="multi")
            meal = st.selectbox("Pick a meal!", ("Breakfast", "Lunch", "Dinner"))

            today = date.today().weekday()
            if(today == 6):
                today = -1

            values = [-1, 0, 1, 2, 3, 4, 5] #our week starts on Sunday which is index -1 in lables
            labels = ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']   
            selection = st.select_slider('Choose a range',values, value=today, format_func=(lambda x:labels[x]))

            d = date.today() + timedelta(days=selection - today)
            st.write("Selected Date: ", d)
            
            col1, col2, col3, col4 = st.columns((2,1,1,1))
            col1.write("**Dish name**")
            col2.write("**Calories**")
            col3.write("**Favorite**")
            col4.write("**Log dish**")
            #right now this just writes the data frame, but in the future we probably want it to be a table 
            
            if testID:
                for l in location:
                    df = m.get_menu(l, meal, d)
                    st.write(f"**{l}**")
                    lid = m.get_location_meal_ids(l, meal)
                    for index, row in df.iterrows():
                        col1, col2, col3, col4 = st.columns((2,1,1,1))
                        col1.write(row["name"])
                        col2.write(f"{row['calories']} kcal")
                        favorite = col3.toggle(label="Fav", key=f"{lid}{row['id']}", args=(testID, row['id'],), on_change=m.favorites_toggle)
                        log = col4.button("**+**", key=f"-{lid}{row['id']}",args=(testID, row['id'], l, meal, d,), on_click=m.log_meal)
        
        with journal:
            st.header(f"Journal: {date.today()}")
            if testID:
                col1, col2, col3, col4 = st.columns((1,3,1,1))
                col1.write("**meal**")
                col2.write("**name**")
                col3.write("**calories**")
                col4.write("**delete**")
                mealLog = m.get_meal_log(testID)
                st.write(mealLog)
                # for index, row in mealLog.iterrows():
                #     col1, col2, col3, col4 = st.columns((1,3,1,1))
                #     col1.write(row["meal"])
                #     col2.write(row["name"])
                #     col3.write(f"{row['calories']} kcal")
                #     delete = col4.button("delete", key=f"J{index}")        
            #for testing
            # for index, row in mealLog.iterrows():
            #         col1, col2, col3, col4 = st.columns((2,1,1,1))
            #         col1.write(row["dish_id"]) #replace with actual dish name from db
            #         col2.write(row['dining_hall'])
            #         col3.write(row['meal_name'])
            #         col4.write(row['date_logged'])

        with visualize:
            st.header("Visualizations")
            #if testID:
                #st.line_chart(m.visualize_total_stats(testID), x_label="Meal #", y_label="Nutrient count")

        with favorites:
            st.header("Favorites")
            favs = m.display_favorites(userId)
            for fav in favs:
                st.write(fav)
        with settings:
            st.header("Settings")
        
def main():
    write_streamlit()
    
if __name__ == '__main__':
    main()