import streamlit as st

st.set_page_config(
        page_title="Peckish",
        page_icon="crumb-the-goose.png",
        initial_sidebar_state="expanded",
        layout="wide")

pages = {
    "Menu": [
        st.Page("home.py", title="Home"),
        st.Page("menus.py", title="Menus"),
        st.Page("journal.py", title="Journal"),
        st.Page("visualize.py", title="Visualize"),
        st.Page("favorites.py", title="Favorites"),
        st.Page("settings.py", title="Settings")
    ]
}

pg = st.navigation(pages)
pg.run()