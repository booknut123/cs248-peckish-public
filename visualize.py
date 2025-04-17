import streamlit as st
from datetime import date, datetime, timedelta
import methods
import visualization_methods as vm

sidebar, main = st.columns((0.5, 1.5), gap="small", vertical_alignment="top")

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

with sidebar:
    st.image(image='crumb-the-goose.png')

    d = date.today()
    today = d.weekday()
    if(today == 6):
        sun = d
        sat = d + timedelta(days=sun + 6)
    else:
        sun = d + timedelta(days= -today)
        sat = d + timedelta(days= 5 - today)

    st.subheader("Customize")

    dates = st.date_input(
        
    "Date Range", (sun, sat),
    format="MM-DD-YYYY")

    color = st.color_picker("Chart Color :)", "#CB1A62")



with main:
    st.subheader("Nutrient Chart")
    stats = ["calories", "fat", "cholesterol", "sodium", "carbohydrates", "sugars", "protein"]
    stat = st.selectbox("Select a Nutrient to Display", stats)
    
    if stat == "calories":
        uom = "kcal"
    elif stat == "sodium" or stat == "cholesterol":
        uom = "mg"
    else:
        uom = "g"

    st.line_chart(vm.visualize_total_stats(user_id, stat), color=color, y_label = f"{stat} ({uom})", x_label="dish")
    
    total = vm.get_total_nutrients(user_id, stat)
    st.write(f"Total {stat}: {str(total[0])} {uom}")
    st.write(f"Average {stat} per dish: {str(total[1])} {uom}")

    #st.write(f"Viewing: {stat}")
    st.write("")
    st.subheader("Lifetime dining hall breakdown")
    st.bar_chart(vm.dining_hall_tracker(user_id), color=color, horizontal=True)

    st.subheader("Average calories by meal")
    st.bar_chart(vm.average_cals_by_meal(user_id), color=color, horizontal=True)
