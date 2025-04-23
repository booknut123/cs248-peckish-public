import streamlit as st
import methods
import time

# import helper_methods
# helper_methods.create_database()
# st.write("Created database")
# helper_methods.weekly_update_db("4-20-2025")
# st.write("Updated weekly database")

sidebar, main = st.columns((0.01, 1.5), gap="small", vertical_alignment="top")
try:
    user_id = int(st.session_state.get("user_id"))
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

        col1, col2, col3, col4 = st.columns((3,0.5,1,1))
        col1.write("**Dish**")
        col2.write("**Total**")
        col3.write("**Date Added**")
        col4.write("**Delete**")

        for index, row in favs.iterrows():
            col1, col2, col3, col4 = st.columns((3,0.5,1,1))
            col1.write(methods.get_dish_name(row["dish_id"]))
            col2.write(str(methods.get_dish_rating(row["dish_id"])))
            col3.write(row["date_added"])
            delete = col4.button("**-**", key=f"F{index}")
            if delete:
                methods.remove_favorite(user_id, row["dish_id"])
                st.toast("Favorite Deleted")
                time.sleep(1)
                st.rerun()

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
    