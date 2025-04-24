import streamlit as st
import methods as m

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
    st.header("Settings")
    st.divider()

    data = m.get_user_allergens_preferences(user_id)
    if data:
        userA = data[0]
        userP = data[1]
    else:
        userA = ""
        userP = ""
 
    try:
        a = ["Dairy", "Egg", "Fish", "Peanut", "Sesame", "Shellfish", "Soy", "Tree Nut", "Wheat"]
        p = ["Gluten Sensitive", "Vegan", "Vegetarian"]
         
        st.subheader("Set Allergens & Preferences")
 
        col1, col2, col3 = st.columns((1,2,1))
 
        with col1:
            selected_a = []
            col1.write("**Allergens**")
            for i, aller in enumerate(a):
                sel = False
                if userA:
                    if aller in userA:
                        sel = True
                if st.checkbox(aller, value=sel):
                    selected_a.append(aller)
 
        with col2:
            selected_p = []
            col2.write("**Preferences**",)
            for i, pref in enumerate(p):
                sel = False
                if userP:
                    if pref in userP:
                        sel = True
                if st.checkbox(pref, value=sel):
                    selected_p.append(pref)
             
            st.write("")
            if st.button("Update"):
                    m.update_user_allergens_preferences(user_id, selected_a, selected_p)

            st.write("* Selections will filter menus shown in the Menus tab.")
 

        st.divider()

        st.write("")
        st.subheader("Set Account Username")
        
        col1, col2 = st.columns((1,1.5))
        
        with col1:
            with st.form("Update Username"):
                newname = st.text_input("New Username:")
                submitted = st.form_submit_button("Submit")
                if submitted:
                    m.set_username(user_id, newname)
            st.write(f"**Username**: {m.get_username(user_id)}")


        st.divider()

        st.subheader("Usage Data")
        st.write(f"Date joined: {m.get_user_join_date(user_id)}")
        st.write(f"Total dishes logged: {m.get_total_dishes_logged(user_id)}")
        
        st.divider()

        st.write("Website credits to:")
        st.write("- Nina Howley '27")
        st.write("- Kailyn Lau '28")
        st.write("- Maya Gurewitz '26")
        st.write("- The students of CS 248 Spring '25")


    except:
        st.write("Something went wrong.")