# Mostly Prof Eni's code, with some edits by Kailyn (add_user())
# Used to grant user's access to the app

import streamlit as st
import requests
from methods import users_methods

# ## === TO CONNECT TO PECKISH.DB === ##
import sqlite3
# import os
# from pathlib import Path
# import sys

# parent_dir = str(Path(__file__).parent.parent)  # Goes up 2 levels if needed

# # Add it to sys.path
# sys.path.append(parent_dir)

# # Now import from the parent folder
# from parent_dir import module_name

# # Get the parent folder path
# PARENT_DIR = Path(__file__).parent.parent
import db_sync
def get_db_connection():
    # """Connect to peckish.db in the parent folder"""
    # db_path = os.path.join(PARENT_DIR, "peckish.db")
    path = db_sync.get_db_path()
    st.write("📂 Connected to DB:", path)
    return sqlite3.connect(path)

## ENI'S CODE ##

@st.cache_data(ttl=3600)
def get_user_info(access_token):
    """Fetch and cache user profile info from Google."""
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.warning(f"User info fetch failed: {e}")
    return None

# Commented for the moment, so that I can use the version with Fake User
# def render_user_profile():
#     """Render user profile photo and a greeting, if user opts in."""
#     access_token = st.session_state.get("access_token")
#     if not access_token:
#         return

#     show_profile = st.sidebar.checkbox("Show profile info", value=True)

#     if show_profile:
#         user = get_user_info(access_token)
#         if user:
#             first_name = user.get("given_name") or user.get("name", "there").split()[0]
#             col1, col2 = st.sidebar.columns([1, 4])
#             with col1:
#                 st.image(user.get("picture"), width=40)
#             with col2:
#                 st.markdown(f"**Hello, {first_name}!**")
#         else:
#             st.sidebar.success("Logged in ✅")
#     else:
#         st.sidebar.success("Logged in ✅")



# VERSION that I'm using for DEBUGGING
def render_user_profile():
    """Render user profile photo and greeting, if user opts in."""
    access_token = st.session_state.get("access_token")
    if not access_token:
        return

    #for now
    show = True

    if show:
        if "fake_user_name" in st.session_state:
            first_name = st.session_state["fake_user_name"]
            picture = st.session_state["fake_user_picture"]
        else:
            user = get_user_info(access_token)
            st.session_state["user_id"] = user["sub"]  # Google's unique ID
            add_user(user)
            st.session_state["username"] = user.get("email") or user.get("name")
            #st.sidebar.write("DEBUG: User info", user)
            if not user:
                st.sidebar.success("Logged in ✅")
                return
            first_name = user.get("given_name") or user.get("name", "there").split()[0]
            picture = user.get("picture")

        col1, col2 = st.sidebar.columns([1, 4])
        with col1:
            st.image(picture, width=40)
            
        with col2:
            st.markdown(f"**Hello, {first_name}!**")
    else:
        st.sidebar.success("Logged in ✅")

def add_user(user_info): # == added by Kailyn ==
    new_user = False
    """Insert or update user in peckish.db using Google auth info"""
    
    db_sync.download_db_from_github()
    conn = sqlite3.connect(db_sync.get_db_path())
    cur = conn.cursor()
    
    try:
        # First try to find existing user by google_id
        google_id = user_info["sub"]
        
        user_id = str(google_id)
        
        cur.execute(
            "SELECT user_id FROM users WHERE user_id = ?", 
            (user_id,)
        )
        result = cur.fetchone()

        if result:
            # Existing user - update and return existing user_id
            user_id = result[0]
            conn.execute("""
                UPDATE users SET
                    email = ?,
                    name = ?,
                    given_name = ?,
                    picture_url = ?,
                    last_login = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (
                user_info.get("email"),
                user_info.get("name"),
                user_info.get("given_name"),
                user_info.get("picture"),
                user_id
            ))

            cur.execute(f"SELECT user_name FROM users WHERE user_id = ?", (user_id,))
            name = cur.fetchone()
            if name[0] == None:
                cur.execute("UPDATE users SET user_name = ? WHERE user_id = ?", ("".join(user_info.get("name").split(" ")), user_id))
                conn.commit()
        else:
            name = "".join((user_info.get("name")).split(" "))

            cur.execute("""
                INSERT INTO users 
                (user_id, email, name, user_name, given_name, picture_url, first_seen, last_login, optin)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)""", (
                user_id,
                user_info.get("email"),
                user_info.get("name"),
                name,
                user_info.get("given_name"),
                user_info.get("picture"),
                "true"
            ))
            
            new_user = True
        conn.commit()
        st.session_state["user_id"] = user_id
        
    finally:
        conn.close()
        db_sync.push_db_to_github()
        if (new_user):
            users_methods.new_user_welcome()
        return user_id
    
    
    