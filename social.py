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

sidebar, main = st.columns((0.75, 1.5), gap="small", vertical_alignment="top")
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

# updating_db.update_db_stuff()

# methods.accept_friend_request("117172280817080874657", "103701573573617392189")

users = [name for name in methods.get_all_users() if methods.get_optin(name[0]) and name[0] != user_id]
if methods.get_optin(user_id):

    with sidebar:
        st.image(image='crumb-the-goose.png')
        
        st.write("**Friends**")
        friends = methods.list_friends(user_id)
        if not friends:
            st.write("No friends")
        else:
            for i, friend in zip(range(len(friends)),friends):
                col1, col2 = st.columns((0.15,1), vertical_alignment="center")
                unfriend = col1.button("**-**", key=f"remove_{i}_{friend}")
                if unfriend:
                    methods.remove_friend(user_id, friend)
                    st.toast(f"{methods.get_username(friend)} removed.")
                    st.rerun()
                col2.write(methods.get_username(friend))
                
        if methods.list_friend_requests(user_id):
            st.write("**Incoming Requests 🔴**")
        else:
            st.write("**Incoming Requests**")
        
        requests = methods.list_friend_requests(user_id)
        if not requests:
            st.write("No requests")
        else:
            for request in requests:
                col1, col2, col3 = st.columns((0.15,0.15,0.75), vertical_alignment="center")
                name = methods.get_username(request)
                add = col1.button("**+**", key=f"add_{request}") 
                if add:
                    methods.accept_friend_request(user_id, request)
                    st.toast(f"{name} added!")
                    st.rerun()
                remove = col2.button("**-**", key=f"remove_{request}")
                if remove:
                    methods.remove_friend_request(user_id, request)
                    st.toast(f"{name} removed.")
                    st.rerun()
                col3.write(name)
                

        st.write("**Add Friend**")
        with st.form("Add Friend"):
            friend = st.selectbox('Add Friend', users, format_func=lambda x: x[2], placeholder="Search for friends by name!")
            send = st.form_submit_button("Send Request")
            if send:
                methods.send_friend_request(user_id, friend[0])
                st.toast(f"Friend request sent to {friend[2]}!")
                st.rerun()

        st.write("**Outgoing Requests**")
        outgoing = methods.list_outgoing_requests(user_id)
        if not outgoing:
            st.write("No requests")
        else:
            for request in outgoing:
                col1, col2 = st.columns((0.15,1), vertical_alignment="center")
                removerequest = col1.button("**-**", key = f"remove_request_{request}")
                if removerequest:
                    methods.remove_friend_request(request, user_id)
                    st.toast("Friend request removed.")
                    st.rerun()
                col2.write(methods.get_username(request))

    with main:
        st.header("Social")

        st.subheader("Friend Activity")

        friends = methods.list_friends(user_id)
        if not friends:
            st.warning("You must have atleast one friend added to view activity.")
        else:
            for friend in friends:
                with st.container(border=True):
                    col1, col2 = st.columns((0.1,1), vertical_alignment="center")
                    image = methods.get_user_icon(friend)
                    col1.image(methods.get_user_icon(friend), width=30)
                    col2.write(f"**{methods.get_username(friend)}**")
                    with st.expander("**Shared Favorites**"):

                        sharedfaves = methods.compare_favorites(user_id, friend)

                        if not sharedfaves:
                            st.write("No shared favorites.")

                        else:
                            for fave in sharedfaves:
                                friendname = methods.get_username(friend)
                                dishname = methods.get_dish_name(fave)
                                st.write(f"-- {dishname}")
                                st.write(f"**Date Added** You: {methods.get_fave_date(user_id, fave)} | {friendname}: {methods.get_fave_date(user_id, fave)}")
                                st.write(f"**Last Logged** You: {methods.get_last_logged_date(user_id, dishname)} | {friendname}: {methods.get_last_logged_date(friend, dishname)}")
                                st.write("")
                    with st.expander("**Tag History**"):
                        st.write("**Friend Tags**")
                        taghistory = methods.get_tag_history(user_id, friend)
                        if taghistory:
                            for date in taghistory:
                                tags = ", ".join(methods.get_username(tag) for tag in taghistory[date][1])
                                st.write(f"**{date}**: {tags}")
                                note = taghistory[date][0]
                                if note:
                                    st.write(note)
                                else:
                                    st.write("No note.")

                        else:
                            st.write("This friend has not tagged you.")

                        st.divider()

                        st.write("**Your Tags**")
                        taghistory = methods.get_tag_history(friend, user_id)
                        if taghistory:
                            for date in taghistory:
                                tags = ", ".join(methods.get_username(tag) for tag in taghistory[date][1])
                                st.write(f"**{date}**: {tags}")
                                note = taghistory[date][0]
                                if note:
                                    st.write(note)
                                else:
                                    st.write("No note.")

                        else:
                            st.write("You have not tagged this friend.")
                        
                    methods.get_tag_history(user_id, friend)
else:
    st.warning("Activate Social in settings to access your Social page.")

# except:
#     st.warning("Activate Social in settings to access your social page.")