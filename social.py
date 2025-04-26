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

users = [name for name in methods.get_all_users() if name[0] != user_id and methods.get_optin(name[0])]

if methods.get_optin(user_id):

    with sidebar:
        st.image(image='crumb-the-goose.png')
        
        st.write("**Friends**")
        friends = methods.list_friends(user_id)
        if not friends:
            st.write("No friends")
        else:
            for friend in friends:
                st.write(methods.get_username(friend))

        st.write("**Incoming Requests**")
        col1, col2, col3 = st.columns((1,0.25,0.25))
        
        requests = methods.list_friend_requests(user_id)
        if not requests:
            st.write("No requests")
        else:
            for request in requests:
                name = methods.get_username(request)
                col1.write(name[2])
                add = col2.button("**+**", key=f"add_{request}") 
                if add:
                    methods.accept_friend_request(user_id, request)
                    st.toast(f"{name[2]} added!")
                remove = col3.button("**-**", key=f"remove_{request}")
                if remove:
                    methods.remove_friend_request(user_id, request)
                    st.toast(f"{name[2]} removed!")

        st.write("**Add Friend**")
        with st.form("Add Friend"):
            friend = st.selectbox('Add Friend', users, format_func=lambda x: x[2], placeholder="Search for friends by name!")
            send = st.form_submit_button("Send Request")
            if send:
                methods.send_friend_request(user_id, friend[0])
                st.toast(f"Friend Request sent to {friend[2]}!")

        st.write("**Outgoing Requests**")
        outgoing = methods.list_outgoing_requests(user_id)
        if not outgoing:
            st.write("No requests")
        else:
            for request in outgoing:
                st.write(methods.get_username(request))

    with main:
        st.header("Social")

        updating_db.update_db_stuff()

        st.subheader("Recent Activity")
        st.write("Work in progress. Will add here meals you were tagged in by friends, or something else. Not sure yet.")       

else:
    st.warning("Activate Social in settings to access your Social page.")

# except:
#     st.warning("Activate Social in settings to access your social page.")