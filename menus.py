import streamlit as st
import methods
from datetime import date, datetime, timedelta
import pandas as pd
import emoji

sidebar, main = st.columns((0.5, 1.5), gap="small", vertical_alignment="top")
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

with sidebar:
    st.image(image='crumb-the-goose.png')
        
    st.subheader("Selection")
    locations = ["Bates", "Lulu", "Tower", "StoneD"]
    selected_locations = st.pills("Pick dining halls!", options=locations, selection_mode="multi", default=locations)
    
    meal = st.selectbox(
        "Pick a meal!",
        ("Breakfast", "Lunch", "Dinner"),
    )
    
    d = date.today()
    today = d.weekday() # Monday, Tuesday, Wednesday, etc.
    if(today == 6):
        today = -1
    values = [-1, 0, 1, 2, 3, 4, 5] #our week starts on Sunday which is index -1 in lables
    labels = ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']   
    selection = st.select_slider(
        'Day', values, value=today,
        format_func=(lambda x:labels[x]),
        )

    d += timedelta(days=selection - today)
    # st.write("Selected Date: ", d)
    
    st.subheader("Filter")

    st.write("**Preferences**")
    preferences = ["Vegan", "Vegetarian", "Gluten Sensitive"]
    selected_preferences = []
    for i, pref in enumerate(preferences):
        if st.checkbox(pref):
                selected_preferences.append(pref)
        
    st.write("**Allergens (exclude)**")
    allergens = ["Dairy", "Egg", "Fish", "Peanut", "Sesame", "Shellfish", "Soy", "Tree Nut", "Wheat"]
    selected_allergens = []
    for i, aller in enumerate(allergens):
        if st.checkbox(aller):
                selected_allergens.append(aller)
    
with main:
    if selected_locations:
        st.subheader(f"{meal}")
        st.write(f"{labels[selection]}, {d} {'(Today)' if str(d) == str(date.today()) else ''}")
        for loc in selected_locations:
            with st.container(border=True):
                st.subheader(loc)
                df = methods.get_filtered_menu(selected_allergens, selected_preferences, loc, meal, d)
                if not df.empty:
                    # Header row
                    col1, col2, col3, col4 = st.columns((0.5, 2.5, 1, 1), vertical_alignment="top")
                    col1.write("**Log**")
                    col2.write("**Dish**")
                    col3.write("**Calories**")
                    col4.write("**Favorite**")
                
                    for index, row in df.iterrows():
                        col1, col2, col3, col4 = st.columns((0.5, 2.5, 1, 1), vertical_alignment="top")                    
                        col2.write(row["name"])
                        col3.write(f"{row['calories']}")
                
                        # Favorite toggle (empty/filled heart)
                        heart_key = f"favorite_{loc}_{index}"
                        if heart_key not in st.session_state:
                            st.session_state[heart_key] = False

                        numfaves = str(methods.get_dish_rating(row['id']))
                        heart_clicked = col4.button(
                            f"❤️ {numfaves}" if methods.check_is_favorite(user_id, row['id']) else f"🤍 {numfaves}",
                            key=f"btn_{heart_key}"
                        )

                        if heart_clicked:
                            st.session_state[heart_key] = not st.session_state[heart_key]
                            if st.session_state[heart_key]:
                                methods.add_favorite(user_id, row['id'])
                                st.toast("Favorite added")
                            else:
                                methods.remove_favorite(user_id, row['id'])
                                st.toast("Favorite removed")
                            #methods.favorites_toggle(user_id, row['id'])
                            st.rerun()
                
                        # Add to journal button
                        def add_button(user_id, row_id, loc, meal, d):
                            methods.log_meal(user_id, row_id, loc, meal, d)
                            st.toast("Meal added!")
                        col1.button(
                            "**+**", 
                            key=f"add_{loc}_{index}",
                            on_click=add_button, 
                            args=(user_id, row['id'], loc, meal, d)
                        )
                else:
                    st.write("No dishes found in menu today :(")
        st.write("* Menus may not be accurate.")
        st.write("Menus displayed on Peckish are pulled from Wellesley Fresh. Any discrepancies will be shared.")
                        
    else:
        st.subheader("No locations selected.")