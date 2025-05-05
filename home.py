
import streamlit as st
from auth import google_login
from user_profile import render_user_profile
from datetime import datetime, date, time
from zoneinfo import ZoneInfo
from db_sync import download_db_from_github

import methods.database_menu_methods as dm
import methods.dishes_log_methods as dl
import methods.favorites_methods as f
import methods.misc_methods as m
import methods.visualization_methods as v

# == Prof Eni's code == #
# This is needed to get the database
download_db_from_github()

DEBUG = False # keep False when testing Google Login
#DEBUG = True # set to True, when you don't want to go through authentication

def fake_login():
    """Sets a fake access token and user info for debugging."""
    st.session_state["access_token"] = "fake-token"
    st.session_state["fake_user_name"] = "Test Student"
    st.session_state["fake_user_picture"] = "https://i.pravatar.cc/60?img=25"  # random placeholder

def render_sidebar():
    """A function to handle the login in the sidebar."""

    if DEBUG and "access_token" not in st.session_state:
        fake_login()

    # If already logged in
    if "access_token" in st.session_state:
        # Removed by Team Peckish
        # st.session_state["show"] = st.sidebar.checkbox("Show profile info")

        # st.sidebar.write(st.session_state["show"])
        # if st.session_state["show"]:
        #     render_user_profile()

        render_user_profile()

        if st.sidebar.button("Logout"):
            for key in ["access_token", "oauth_state", "user_id"]:
                st.session_state.pop(key, None)
            st.rerun()

    else:
        st.sidebar.header("Login")
        st.sidebar.warning("Not logged in.")
        logged_in = google_login()
        if logged_in:
            st.rerun()

#===================================================================

# Clear state if user navigates away
if "selected_dining_hall" not in st.session_state:
    st.session_state.selected_dining_hall = None
if "selected_meal" not in st.session_state:
    st.session_state.selected_meal = None

# Always render sidebar, otherwise it will be rewritten
render_sidebar()

# == TEAM PECKISH CODE BELOW == #
# wait for the user to login before showing anything
if "access_token" not in st.session_state: # warning screen
    col1, col2, col3 = st.columns((0.5, 0.6, 0.9))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("CS248 '25")
    col2.write("Kailyn, Maya, Nina")

    st.warning("Not logged in.")    
    st.stop()
else: # intro screen
    user_id = st.session_state.get("user_id")
    
    col1, col2, col3 = st.columns((0.5, 0.6, 0.9))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("CS248 '25")
    col2.write("Kailyn, Maya, Nina")

    fact = m.generate_goose_fact()
    col3.header(f"Goose Fact #{fact[1]+1}")
    col3.write("Did you know...")
    col3.write(fact[0])

# run this (with new starting date) if you reset entire database, or else week will be empty

# == TOP RATES == #
st.header("This Week...")
col1, col2 = st.columns((2), border=True)
col1.subheader("Top Rated Meal")
i = 1
favorite = f.weeklyTop5favs()[0]
with col1.container():
    col1.write(f"{favorite[0]}: ❤️ {favorite[1]} ")

with col2.container():
    col2.subheader("Top Dining Hall")
    hall = v.hall_popularity_last_7_days()
    tophall = max(hall, key=hall.get)
    col2.write(f"{tophall}: {hall[tophall]} meals logged")

if datetime.now().weekday() == 0:
    dm.weekly_update_db(str(datetime.now()).split(" ")[0])

# == QUICK LOOK == #
eastern = ZoneInfo("America/New_York")
current_time_est = datetime.now(eastern).time()
is_weekend = datetime.now(eastern).weekday() >= 5  # 5=Saturday, 6=Sunday

# Lulu Schedule
if is_weekend:
    lulu_meal = "Lunch" if time(10,30) <= current_time_est < time(14,0) else \
               "Dinner" if time(14,0) <= current_time_est < time(23,59) else \
               "Lunch" 
    #if current_time_est < time(10,30) else "Dinner" 
else:
    lulu_meal = "Breakfast" if time(7,0) <= current_time_est < time(10,0) else \
               "Lunch" if time(11,30) <= current_time_est < time(14,0) else \
               "Dinner" if time(14,0) <= current_time_est < time(23,59) else \
               "Breakfast" 
    #if current_time_est < time(7,0) else "Lunch" 

# Bates/Tower/StoneD Schedule (same for all three)
if is_weekend:
    other_meal = "Lunch" if time(10,30) <= current_time_est < time(14,0) else \
                "Dinner" if time(14,0) <= current_time_est < time(23,59) else \
                "Lunch" 
    #if current_time_est < time(10,30) else "Dinner"
else:
    other_meal = "Breakfast" if time(7,0) <= current_time_est < time(10,0) else \
                "Lunch" if time(11,30) <= current_time_est < time(14,0) else \
                "Dinner" if time(14,0) <= current_time_est < time(23,59) else \
                "Breakfast" 
    #if current_time_est < time(7,0) else "Lunch"

date = datetime.now(eastern).date()

st.header(f"Current Menus: {lulu_meal} {date}")
col1, col2, col3, col4 = st.columns(4, gap="small", vertical_alignment="top", border=True)

def streamlit_print(df):
    for index, row in df.iterrows():
        dupes = dl.get_dupe_dishIDs(row['dish_name'])
        if f.check_is_favorite(user_id, row['dish_id']):
            st.write(f":heart: {row['dish_name']}")
        else:
            fav = False
            for dish in dupes:
                if f.check_is_favorite(user_id, dish[0]):
                    fav = True
            if fav:
                st.write(f":heart: {row['dish_name']}")
            else:
                st.write(row["dish_name"])
with col1:
    st.subheader("Bates")
    menu = dm.print_menu([], [], "Bates", other_meal, date)
    if not menu.empty:
        streamlit_print(menu)
    else:
        st.write("No menu items.")
with col2:
    st.subheader("Lulu")
    menu = dm.print_menu([], [], "Lulu", lulu_meal, date)
    if not menu.empty:
        streamlit_print(menu)
    else:
        st.write("No menu items.")
with col3:
    st.subheader("Tower")
    menu = dm.print_menu([], [], "Tower", lulu_meal, date)
    if not menu.empty:
        streamlit_print(menu)
    else:
        st.write("No menu items.")
with col4:
    st.subheader("StoneD")
    menu = dm.print_menu([], [], "StoneD", lulu_meal, date)
    if not menu.empty:
        streamlit_print(menu)
    else:
        st.write("No menu items.")

col1, col2 = st.columns((3.25,1))

# == DISCLAIMERS/LINK == #
col1.write("* Menus may not be accurate.")
col1.write("Menus displayed on Peckish are pulled from Wellesley Fresh. Any discrepancies will be shared.")

url = "http://www.wellesleyfresh.com/connect-with-us.html"
col2.link_button("Contact the Manager", url)
st.divider()
st.header("Credits:")
st.write("We want to thank all the dining service workers, AVI, Professor Mustafaraj,"
         + " and everyone who assisted us in the development of our app from research surveys to user testing!")