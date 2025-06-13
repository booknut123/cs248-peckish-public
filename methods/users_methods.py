import db_sync
import streamlit as st
import time

import methods.database_menu_methods as dm

def update_user_allergens_preferences(userID, allergens, preferences):
    """
    * userID: int
    * allergens: list of strings, [Dairy, Egg, Fish, Peanut, Sesame, Shellfish, Soy, Tree Nut, Wheat]
    * preferences: list of strings, [Gluten Sensitive, Vegan, Vegetarian]
    Updates the user's allergens and preferences.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    allergens = ",".join(allergens)
    preferences = ",".join(preferences)

    cur.execute("UPDATE users SET allergens = ? WHERE user_id = ? ", (allergens, userID))
    cur.execute("UPDATE users SET preferences = ? WHERE user_id = ? ", (preferences, userID))

    conn.commit()
    conn.close()
    
    db_sync.push_db_to_github()

def get_user_allergens_preferences(userID):
     """
     * userID: int
     Returns the user's allergens and preferences as a tuple (allergens, preferences)
     """
     conn = dm.connect_db()
     cur = conn.cursor()
 
     cur.execute(f"SELECT allergens, preferences FROM users where user_id = ?", (userID,))
     stuff = cur.fetchone()
 
 
     conn.close()
     return stuff

def get_username(userID):
    """
    * userID: string
    Returns the username associated with a given userID
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    cur.execute(f"SELECT user_name FROM users WHERE user_id = ?", (userID,))
    username = cur.fetchone()
    return username[0]
 
def set_username(userID, username):
    """
    * userID: string
    Updates the username associated with a given userID
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    cur.execute("UPDATE users SET user_name = ? WHERE user_id = ?", (username, userID))
    conn.commit()
    conn.close()

def get_user_join_date(userID):
    """
    * userID: string
    Returns the join date associated with a given userID
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    date = cur.execute("SELECT first_seen FROM users WHERE user_id = ?", (userID,)).fetchone()[0]
    return date.split(" ")[0]

def get_name(userID):
    """
    * userID: string
    Returns the name associated with a given userID
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    name = cur.execute("SELECT name FROM users WHERE user_id = ?", (userID,)).fetchone()

    return name[0]
  
def get_all_names():
    """
    Returns the names of all users in the database.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    names = cur.execute("SELECT DISTINCT name FROM users").fetchall()

    return names

def check_id(userID): # By Kailyn
    """
    * userID: string
    Checks whether the given userID is in the database.
    """
    conn = dm.connect_db()
    cur = conn.cursor()
    match = cur.execute("SELECT user_id FROM users WHERE user_id = ?", (userID, )).fetchone()
    return (match != None)

def new_user_welcome(): # By Kailyn - used in user_profile
    """
    Writes a welcome page for users who are new to the database.
    """
    user_welcomed = False
    placeholder = st.empty()
    with placeholder.container():
        col1, col2 = st.columns((0.5, 2.5), )
        col1.image(image='crumb-the-goose.png')
        col2.header ("Welcome to Peckish!")
        col2.subheader("We're so glad you're here.")
        
        st.write("""At Peckish, our mission is to make campus dining work better for you - your schedule, your preferences, your community.
                    Peckish isn’t about micromanaging your meals. We don’t track your diet — we help you track your experiences.
                    """)
        st.write("Ready to explore?")
        go = st.button("Let's get started! 🪿")
        #st.write(go)
        while not go:
            time.sleep(1)
            #st.write(go)
        user_welcomed = True
        st.write(user_welcomed)
    placeholder.empty()

def get_all_users():
    """
    Returns a list of user_id, name and user_name of all users in the database.
    [(user_id, name, user_name)]
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    users = cur.execute("SELECT user_id, name, user_name FROM users").fetchall()

    return users

def get_user_id_from_name(name):
    """
    * name: string
    Returns the first userID associated with a name in the database.
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    id = cur.execute("SELECT user_id FROM users WHERE user_name = ?", (name,)).fetchone()
    
    return id[0]

def get_user_icon(userID):
    """
    * userID: string
    Returns the profile picture / icon associated with a given userID
    """
    conn = dm.connect_db()
    cur = conn.cursor()

    image = cur.execute("SELECT picture_url FROM users where user_id = ?", (userID,)).fetchone()

    if image:
        return image[0]
    else:
        return None