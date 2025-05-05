import streamlit as st
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import methods.database_menu_methods as dm
import methods.dishes_log_methods as dl
import methods.favorites_methods as f
import methods.users_methods as u

eastern = ZoneInfo("America/New_York")

sidebar, main = st.columns((0.5, 1.5), gap="small", vertical_alignment="top")
user_id = st.session_state.get("user_id")

if not u.check_id(user_id):
    col1, col2 = st.columns((0.3, 1.5))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("From CS248 '25 - Kailyn, Maya, Nina")
    
    st.warning("Not logged in.")
    st.write("Please return to home and log in with your Google account.")
    st.stop()

with sidebar: # Location, meal, date, filters - control tab
    st.image(image='crumb-the-goose.png')
        
    st.subheader("Selection")
    locations = ["Bates", "Lulu", "Tower", "StoneD"]
    selected_locations = st.pills("**Location**", options=locations, selection_mode="multi", default=locations)
    
    meal = st.selectbox(
        "**Meal**",
        ("Breakfast", "Lunch", "Dinner"),
    )
    
    d = datetime.now(eastern).date()
    today = d.weekday() # Monday, Tuesday, Wednesday, etc.
    if(today == 6):
        today = -1
    values = [-1, 0, 1, 2, 3, 4, 5] # our week starts on Sunday which is index -1 in lables
    labels = ['Monday','Tuesday','Wednesday','Thursday', 'Friday', 'Saturday', 'Sunday']   
    selection = st.select_slider(
        "**Day**", values, value=today,
        format_func=(lambda x:labels[x]),
        )

    d += timedelta(days=selection - today)

    data = u.get_user_allergens_preferences(user_id)
    if data:
        userA = data[0]
        userP = data[1]
    else:
        userA = ""
        userP = ""

    st.subheader("**Filter**")

    with st.expander("Allergens"):
        allergens = ["Dairy", "Egg", "Fish", "Peanut", "Sesame", "Shellfish", "Soy", "Tree Nut", "Wheat"]
        selected_allergens = []
        for i, aller in enumerate(allergens):
            sel = False
            if userA:
                if aller in userA:
                    sel = True
            if st.checkbox(aller, value=sel):
                    selected_allergens.append(aller)
        
    with st.expander("Preferences"):
        preferences = ["Vegan", "Vegetarian", "Gluten Sensitive", "Pescatarian"]
        selected_preferences = []
        for i, pref in enumerate(preferences):
            sel = False
            if userP:
                if pref in userP:
                    sel = True
            if st.checkbox(pref, value=sel):
                selected_preferences.append(pref)
    
with main: # menu display - item, add, favorite
    if selected_locations:
        st.subheader(f"{meal}")
        st.write(f"{labels[selection]}, {d} {'(Today)' if str(d) == str(date.today()) else ''}")
        
        for loc in selected_locations:
            with st.container(border=True):
                st.subheader(loc)
                df = dm.print_menu(selected_allergens, selected_preferences, loc, meal, d)
                if not df.empty:
                    # Header row
                    col1, col2, col3 = st.columns((0.75, 3.25, 0.5), vertical_alignment="top")
                    col1.write("**Favorite**")
                    col2.write("**Dish**")
                    col3.write("**Log**")

                    stats = ["calories", "fat", "cholesterol", "sodium", "carbohydrates", "sugars", "protein"]

                    for index, row in df.iterrows():
                        col1, col2, col3 = st.columns((0.75, 3.25, 0.5), vertical_alignment="top")

                        # == FAVORITE TOGGLE (empty/filled heart) ==
                        heart_key = f"favorite_{loc}_{index}"
                        if heart_key not in st.session_state:
                            st.session_state[heart_key] = False

                        numfaves = str(dl.get_dish_rating(row['dish_id']))
                        heart_clicked = col1.button(
                            f"❤️ {numfaves}" if f.check_is_favorite(user_id, row['dish_id']) else f"🤍 {numfaves}",
                            key=f"btn_{heart_key}"
                        )

                        if heart_clicked:
                            st.session_state[heart_key] = not st.session_state[heart_key]
                            if st.session_state[heart_key]:
                                f.add_favorite(user_id, row['dish_id'])
                                st.toast("Favorite added")
                                st.rerun()
                            else:
                                f.remove_favorite(user_id, row['dish_id'])
                                st.toast("Favorite removed")
                                st.rerun()
                        # == DESCRIPTION == #
                        with col2.expander(row['dish_name']):
                            info = dl.get_dish_info(row['dish_id'])[7:]
                            descr = dl.get_dish_info(row['dish_id'])[2]
                            if descr:
                                st.write(f"*{descr}*")
                            else:
                                st.write("*No description available.*")
                            
                            for i, stat in zip(info, stats):
                                uom = "g"
                                if stat == "calories":
                                    uom = "kcal"
                                elif stat == "cholesterol" or stat == "sodium":
                                    uom = "mg"
                                st.write(f"{stat}: {i} {uom}")
                        
                        # == ADD == #
                        def add_button(user_id, row_id, loc, meal, d):
                            if dl.log_meal(user_id, row_id, loc, meal, d):
                                st.toast("Meal added!")
                            else:
                                st.toast("This dish has already been logged in this meal.")
                        col3.button(
                            "**+**", 
                            key=f"add_{loc}_{index}",
                            on_click=add_button, 
                            args=(user_id, row['dish_id'], loc, meal, d)
                        )

                else:
                    st.write("No dishes found in menu today :(")
        st.write("* Menus may not be accurate.")
        st.write("Menus displayed on Peckish are pulled from Wellesley Fresh. Any discrepancies will be shared.")
                        
    else:
        st.subheader("No locations selected.")
