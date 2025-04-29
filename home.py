
import streamlit as st
from auth import google_login
from user_profile import render_user_profile
from datetime import datetime, date, time
import pandas as pd
import requests
from db_sync import download_db_from_github
import methods
import helper_methods

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
    st.sidebar.header("Login")

    if DEBUG and "access_token" not in st.session_state:
        fake_login()

    # If already logged in
    if "access_token" in st.session_state:
        render_user_profile()

        if st.sidebar.button("Logout"):
            for key in ["access_token", "oauth_state", "user_id"]:
                st.session_state.pop(key, None)
            st.rerun()

    else:
        st.sidebar.warning("Not logged in.")
        st.sidebar.write("Please log in with your Google account:")
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

# wait for the user to login before showing anything
if "access_token" not in st.session_state:
    col1, col2, col3 = st.columns((0.5, 0.6, 0.9))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("CS248 '25")
    col2.write("Kailyn, Maya, Nina")

    st.warning("Not logged in.")    
    st.stop()
else:
    user_id = st.session_state.get("user_id")
    
    col1, col2, col3 = st.columns((0.5, 0.6, 0.9))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("CS248 '25")
    col2.write("Kailyn, Maya, Nina")

    fact = methods.generate_goose_fact()
    col3.header(f"Goose Fact #{fact[1]+1}")
    col3.write("Did you know...")
    col3.write(fact[0])

#run this (with new starting date) if you reset entire database, or else week will be empty
#helper_methods.weekly_update_db("2025-04-20")

if datetime.now().weekday() == 6:
    helper_methods.weekly_update_db(str(datetime.now()).split(" ")[0])

# if datetime.now().weekday() == 1: ## current day for debugging purposes
#     helper_methods.weekly_update_db("2025-4-20")
now = datetime.now().time()
is_weekend = datetime.now().weekday() >= 5  # 5=Saturday, 6=Sunday

# Lulu Schedule
if is_weekend:
    lulu_meal = "Lunch" if time(10,30) <= now < time(14,0) else \
               "Dinner" if time(17,0) <= now < time(23,0) else \
               "Lunch" if now < time(10,30) else "Dinner" 
else:
    lulu_meal = "Breakfast" if time(7,0) <= now < time(10,0) else \
               "Lunch" if time(11,30) <= now < time(14,0) else \
               "Dinner" if time(17,0) <= now < time(23,0) else \
               "Breakfast" if now < time(7,0) else "Lunch" 

# Bates/Tower/StoneD Schedule (same for all three)
if is_weekend:
    other_meal = "Lunch" if time(10,30) <= now < time(14,0) else \
                "Dinner" if time(17,0) <= now < time(18,30) else \
                "Lunch" if now < time(10,30) else "Dinner"
else:
    other_meal = "Breakfast" if time(7,0) <= now < time(10,0) else \
                "Lunch" if time(11,30) <= now < time(14,0) else \
                "Dinner" if time(17,0) <= now < time(20,0) else \
                "Breakfast" if now < time(7,0) else "Lunch"

# st.header("Today's Favorites:")
# favs = st.columns(1, gap = "small", vertical_alignment="top", border=True)
# with favs:
#     #for fav in favorites for user check if it is in today's menu
#     allDishes = pd.DataFrame()
#     bates = methods.get_menu("bates", other_meal, date.today())
#     lulu = methods.get_menu("lulu", lulu_meal, date.today())




st.header(f"Current Menus: {lulu_meal} {date.today()}")
col1, col2, col3, col4 = st.columns(4, gap="small", vertical_alignment="top", border=True)

def streamlit_print(df):
    for index, row in df.iterrows():
        if methods.check_is_favorite(user_id, row['dish_id']):
            st.write(f":heart: {row['dish_name']}")
        else:
            st.write(row["dish_name"])
with col1:
    st.subheader("Bates")
    streamlit_print(methods.print_menu([], [], "Bates", other_meal, date.today()))
with col2:
    st.subheader("Lulu")
    streamlit_print(methods.print_menu([], [], "Lulu", lulu_meal, date.today()))
with col3:
    st.subheader("Tower")
    streamlit_print(methods.print_menu([], [], "Tower", other_meal, date.today()))
with col4:
    st.subheader("StoneD")
    streamlit_print(methods.print_menu([], [], "StoneD", other_meal, date.today()))


col1, col2 = st.columns((3.25,1))

col1.write("* Menus may not be accurate.")
col1.write("Menus displayed on Peckish are pulled from Wellesley Fresh. Any discrepancies will be shared.")

url = "http://www.wellesleyfresh.com/connect-with-us.html"
col2.link_button("Contact the Manager", url)
st.divider()
st.header("Credits:")
st.write("We want to thank all the dining service workers, AVI, Professor Mustafaraj,"
         + " and everyone who assisted us in the development of our app from research surveys to user testing!")