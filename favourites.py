import streamlit as st
import methods
import time
import datetime
from datetime import date

# import helper_methods
# helper_methods.create_database()
# st.write("Created database")
# helper_methods.weekly_update_db("4-20-2025")
# st.write("Updated weekly database")

sidebar, main = st.columns((0.01, 1.5), gap="small", vertical_alignment="top")
try:
    user_id = st.session_state.get("user_id")
except:
    col1, col2 = st.columns((0.3, 1.5))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("From CS248 '25 - Kailyn, Maya, Nina")
    
    st.warning("Not logged in.")
    st.write("Please return to home and log in with your Google account.")
    st.stop()

with main:
    st.header("Favorites")

    favs = methods.display_favorites(user_id)

    if not favs.empty:
        
        st.write("---")

        col1, col2, col3, col4, col5 = st.columns((1.5,0.5,1,1,0.5))
        col1.write("**Dish**")
        col2.write("**Likes**")
        col3.write("**Date Added**")
        col4.write("**Notification**")
        col5.write("**Delete**")
        st.write("---")


        for index, row in favs.iterrows():
            col1, col2, col3, col4, col5 = st.columns((1.5,0.5,1,1,0.5))
            col1.write(methods.get_dish_name(row["dish_id"]))
            col2.write(str(methods.get_dish_rating(row["dish_id"])))
            col3.write(row["date_added"])
            
            toggle_key = f"favorite_{index}_{row['dish_id']}"
            if toggle_key not in st.session_state:
                st.session_state[toggle_key] = False

            toggle = col4.button(
                                "🔔" if row['notification'] == 'true' else "🔕", 
                                key=f"notif {index} {row['dish_id']}"
                                )
            if toggle:
                methods.toggle_notif(user_id, row['dish_id'])
                st.rerun()

            delete = col5.button("**-**", key=f"F{index}")
            if delete:
                methods.remove_favorite(user_id, row["dish_id"])
                st.toast("Favorite Deleted")
                time.sleep(1)
                st.rerun()

        st.write("---")

        st.header("Favorites This Week")
        faves = methods.get_faves_for_week(user_id, date.today())

        if faves:
            st.write("---")

            col1, col2, col3, col4 = st.columns((2,1,1,1))
            col1.write("**Dish**")
            col2.write("**Meal**")
            col3.write("**Location**")
            col4.write("**Date**")
            st.write("---")

            for fave in faves:
                col1, col2, col3, col4 = st.columns((2,1,1,1))
                col1.write(fave)
                for f in faves[fave]:
                    
                    col2.write(f["meal"])
                    col3.write(f["location"])
                    col4.write("/".join(f["date"].split("-")[1:]))
                st.write("---")
        else:
            st.warning("Please turn on notifications for atleast one dish to see when it will be served.")

    else:
        st.warning("Please add a favorite in the Menus tab to view your favorites.")
    
    st.header("Top User Favorites")
    with st.container(border=True):
        col1, col2 = st.columns((0.5, 4.5))
        i = 1
        favorites = methods.top5favs()
        for fav in favorites:
            if fav[1] != 0:
                col1.write(f"**{i}.**")
                col2.write(f"{fav[0]} {fav[1]}")
                i += 1

    #methods.update_ratings() to make sure favorite counts are correct
    