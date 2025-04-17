import streamlit as st

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
    
st.header("[Currently in progress. Come back soon!]")
st.write("Features:")
st.write("Set diet/allergen preferences")
st.write("Customize name")
st.write("Get usage data")