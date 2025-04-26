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
import updating_db

user_id = st.session_state.get("user_id")

sidebar, main = st.columns((0.5, 1.5), gap="small", vertical_alignment="top")
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

# try:

names = [name[0] for name in methods.get_all_names() if name[0] != methods.get_name(user_id)]

with sidebar:
    st.image(image='crumb-the-goose.png')
    
    st.write("**Friends**")
    friends = methods.list_friends(user_id)
    if not friends:
        st.write("No friends")
    else:
        for friend in friends:
            st.write(friend)

    st.write("**Incoming Requests**")
    col1, col2, col3 = st.columns((1,0.25,0.25))
    
    requests = methods.list_friend_requests(user_id)
    if not requests:
        st.write("No requests")
    else:
        for request in requests:
            col1.write(request)
            add = col2.button("**+**", key=f"add_{request}") 
            if add:
                methods.accept_friend_request(user_id, request)
                st.toast(f"{request} added!")
            remove = col3.button("**-**", key=f"remove_{request}")
            if remove:
                methods.remove_friend_request(user_id, request)
                st.toast(f"{request} removed!")

    st.write("**Add Friend**")
    with st.form("Add Friend"):
        friend = st.selectbox('Add Friend', names, placeholder="Search for friends by name!")
        send = st.form_submit_button("Send Request")
        if send:
            methods.send_friend_request(user_id, methods.get_user_id_from_name(friend))
            st.toast(f"Friend Request sent to {friend}!")

    st.write("**Outgoing Requests**")
    outgoing = methods.list_outgoing_requests(user_id)
    if not outgoing:
        st.write("No requests")
    else:
        for request in outgoing:
            st.write(methods.get_name(request))

with main:
    st.header("Social")

    st.subheader("Recent Activity")
    st.write("Work in progress. Will add here meals you were tagged in by friends, or something else. Not sure yet.")       


# except:
#     st.warning("Activate Social in settings to access your social page.")