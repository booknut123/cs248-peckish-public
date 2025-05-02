import streamlit as st
import methods
from datetime import date
import visualization_methods as vm

user_id = st.session_state.get("user_id")

if not methods.check_id(user_id):
    col1, col2 = st.columns((0.3, 1.5))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("From CS248 '25 - Kailyn, Maya, Nina")
    
    st.warning("Not logged in.")
    st.write("Please return to home and log in with your Google account.")
    st.stop()

st.header("Favorites")

favs = methods.display_favorites(user_id)

if not favs.empty:
    st.write("---")

    col1, col2, col3, col4 = st.columns((0.5,2,0.75,0.5))
    col1.write("**Notify**")
    col2.write("**Dish**")
    col3.write("**Date Added**")
    col4.write("**Delete**")
    st.write("---")

    # == NOTIFICATIONS == #
    for index, row in favs.iterrows():
        col1, col2, col3, col4 = st.columns((0.5,2,0.75,0.5))
        
        toggle_key = f"favorite_{index}_{row['dish_id']}"
        if toggle_key not in st.session_state:
            st.session_state[toggle_key] = False

        toggle = col1.button(
                            "🔔" if row['notification'] == 'true' else "🔕", 
                            key=f"notif {index} {row['dish_id']}"
                            )
        if toggle:
            methods.toggle_notif(user_id, row['dish_id'])
            st.rerun()
        
        col2.write(methods.get_dish_name(row["dish_id"]))
        col3.write(row["date_added"])

        delete = col4.button("**-**", key=f"F{index}")
        if delete:
            methods.remove_favorite(user_id, row["dish_id"])
            st.toast("Favorite Deleted")
            st.rerun()

    st.write("---")

    st.header("Favorites This Week")
    faves = methods.get_faves_for_week(user_id, date.today())

    if faves:
        st.write("---")

        col1, col2, col3, col4 = st.columns((1.75,0.75,0.75,0.75))
        col1.write("**Dish**")
        col2.write("**Meal**")
        col3.write("**Hall**")
        col4.write("**Date**")
        st.write("---")

        for fave in faves:
            col1, col2, col3, col4 = st.columns((1.75,0.75,0.75,0.75))
            col1.write(fave)
            for f in faves[fave]:
                    
                col2.write(f["meal"])
                col3.write(f["location"])
                col4.write("/".join(f["date"].split("-")[1:]))
            st.write("---")
    else:
        st.warning("Please turn on notifications for atleast one dish to see when it will be served.")
        st.warning("If you have notifications on and are seeing this warning, none of the dishes are being served this week!")

    # === TOP 5 === #
    st.header("This Week...")
    st.write("")
    col1, col2 = st.columns((2))
    col1.subheader("Top Rated Meals")
    with col1.container():
        c1, c2 = st.columns((0.25, 3))
        i = 1
        favorites = methods.weeklyTop5favs()
        for fav in favorites:
            if fav[1] != 0:
                c1.write(f"**{i}.**")
                c2.write(f"{fav[0]}: ❤️ {fav[1]}")
                i += 1
    col2.subheader("Top Dining Halls")
    with col2.container():
                    st.bar_chart(vm.hall_popularity_last_7_days(), 
                     horizontal=True, 
                     height=240,
                     width=250,
                     x_label="Number of Logs",
                     )

else:
    st.warning("Please add a favorite in the Log tab to view your favorites.")

#methods.update_ratings() to make sure favorite counts are correct
    