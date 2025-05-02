# == Run streamlit from here!!! ==

import streamlit as st

st.set_page_config(
        page_title="Peckish",
        page_icon="crumb-the-goose.png",
        initial_sidebar_state="expanded",
        layout="wide")

# Pages configuration setup - will show as part of the sidebar
pages = {
    "Menu": [
        st.Page("home.py", title="Home"),
        st.Page("log.py", title="Log Meal"),
        st.Page("journal.py", title="Journal"),
        st.Page("visualize.py", title="Visualize"),
        st.Page("favorites.py", title="Favorites"),
        st.Page("social.py", title="Social"),
        st.Page("settings.py", title="Settings")
    ]
}

pg = st.navigation(pages)
pg.run()