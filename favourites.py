import streamlit as st
import methods
import time

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
        st.write("Please add a favorite to view.")