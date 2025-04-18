import streamlit as st
from auth.auth import google_login
from auth.user_profile import render_user_profile
from datetime import datetime, date, time
import pandas as pd
import requests
import db_sync
import methods

# This is needed to get the database
# download_db_from_github()

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
            for key in ["access_token", "oauth_state"]:
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


col1, col2 = st.columns((0.3, 1.5))
col1.image(image='crumb-the-goose.png')
col2.header("Peckish")
col2.write("Welcome to Peckish!")
col2.write("From CS248 '25 - Kailyn, Maya, Nina")

# wait for the user to login before showing anything
if "access_token" not in st.session_state:
    st.stop()

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

st.header(f"Current Menus: {lulu_meal} {date.today()}")
col1, col2, col3, col4 = st.columns(4, gap="small", vertical_alignment="top", border=True)

def print_menu(df):
    for index, row in df.iterrows():
        st.write(row["name"])
with col1:
    st.subheader("Bates")
    print_menu(methods.get_filtered_menu([], [], "Bates", other_meal, date.today()))
with col2:
    st.subheader("Lulu")
    print_menu(methods.get_menu("Lulu", lulu_meal, date.today()))
with col3:
    st.subheader("Tower")
    print_menu(methods.get_menu("Tower", other_meal, date.today()))
with col4:
    st.subheader("StoneD")
    print_menu(methods.get_menu("StoneD", other_meal, date.today()))


st.write("* Menus may not be accurate.")
st.write("Menus displayed on Peckish are pulled from Wellesley Fresh. Any discrepancies will be shared.")