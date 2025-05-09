import streamlit as st

import methods.dishes_log_methods as dl
import methods.friends_requests_methods as fr
import methods.users_methods as u

user_id = st.session_state.get("user_id")

if not u.check_id(user_id):
    col1, col2 = st.columns((0.3, 1.5))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("From CS248 '25 - Kailyn, Maya, Nina")
    
    st.warning("Not logged in.")
    st.write("Please return to home and log in with your Google account.")
    st.stop()
 
st.header("Settings")
st.divider()

# === ALLERGENS AND PREFERENCES === #
data = u.get_user_allergens_preferences(user_id)
if data:
    userA = data[0]
    userP = data[1]
else:
    userA = ""
    userP = ""

try:
    a = ["Dairy", "Egg", "Fish", "Peanut", "Sesame", "Shellfish", "Soy", "Tree Nut", "Wheat"]
    p = ["Gluten Sensitive", "Vegan", "Vegetarian", "Pescatarian"]
        
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
                u.update_user_allergens_preferences(user_id, selected_a, selected_p)

        st.write("* Selections will filter menus shown in the Menus tab.")

    st.divider()
    
    # === PRIVACY/SECURITY === #

    st.write("")
    
    col1, col2, col3 = st.columns((1,0.25,1))
    
    def toggle_optin(user_id):
        fr.toggle_optin(user_id)

    with col1:
            st.subheader("Activate Social")
            social = st.checkbox("Opt-In", value = fr.get_optin(user_id), on_change=toggle_optin, args=(user_id,))
            st.write("By opting into Social, you become searchable and can be added by others as a friend.")
            st.write("Users are searchable by username. You can change your username at any time.")

    with col3:
        st.subheader("Update Username")
        with st.form("Update Username"):
            newname = st.text_input("New Username:", label_visibility="hidden", autocomplete=u.get_username(user_id))
            submitted = st.form_submit_button("Update")
            if submitted:
                if newname == None or newname == "" or str.isspace(newname):
                    st.warning("Blank username not allowed.")
                else:
                    u.set_username(user_id, newname)
        st.write(f"**Username**: {u.get_username(user_id)}")
    
    st.divider()

    # === EXTRA === #
    st.subheader("Usage Data")
    st.write(f"Date joined: {u.get_user_join_date(user_id)}")
    st.write(f"Total dishes logged: {dl.get_total_dishes_logged(user_id)}")
    st.write(f"Total friends: {len(fr.list_friends(user_id))}")
    
    st.divider()

    st.write("Website credits to:")
    st.write("- Nina Howley '27")
    st.write("- Kailyn Lau '28")
    st.write("- Maya Gurewitz '26")
    st.write("- The students of CS 248 Spring '25")

except:
    st.write("Something went wrong.")