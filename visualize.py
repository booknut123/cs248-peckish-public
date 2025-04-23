import streamlit as st
from datetime import date, datetime, timedelta
import methods
import visualization_methods as vm
import numpy as np
import plotly.express as px
import pandas as pd

sidebar, main = st.columns((0.5, 1.5), gap="small", vertical_alignment="top")

try:
    user_id = int(st.session_state.get("user_id"))
except:
    col1, col2 = st.columns((0.5, 1.5))
    col1.image(image='crumb-the-goose.png')
    col2.header("Peckish")
    col2.write("Welcome to Peckish!")
    col2.write("From CS248 '25 - Kailyn, Maya, Nina")
    
    st.warning("Not logged in.")
    st.write("Please return to home and log in with your Google account.")
    st.stop()

with main:

    try:

        st.header("Visualize")

        with sidebar:
            
            st.image(image='crumb-the-goose.png')
            
            test = vm.get_total_nutrients(user_id, "calories")

            d = date.today()
            today = d.weekday()
            if(today == 6):
                sun = d
                sat = d + timedelta(days=sun + 6)
            else:
                sun = d + timedelta(days= -today)
                sat = d + timedelta(days= 5 - today)

            st.subheader("Customize")
             
            borderdates = methods.get_border_log_dates(user_id)

            dates = st.date_input("**Select Dates**",
                                 format="MM-DD-YYYY", 
                                 min_value=borderdates['min'], #Can't select date before first meal logged
                                 max_value=borderdates['max'], #Can't select date after last meal logged
                                 value=(borderdates['min'], borderdates['max'])
                                 )
            
            stats = ["calories", "fat", "cholesterol", "sodium", "carbohydrates", "sugars", "protein"]
            selectedstats = []
            uom = []
            selectednone = True

            st.write("**Select Nutrients**")
            col1, col2 = st.columns((1.5,3))

            all = col1.button("All")
            if all:
                all=True
            
            none = col2.button("None")
            if none:
                none=True
            

            for stat in stats:
                if all:
                    selected = st.checkbox(stat, value=True)
                elif none:
                    selected=st.checkbox(stat)
                elif stat == "fat" or stat == "carbohydrates" or stat == "protein":
                    selected = st.checkbox(stat, value=True)
                else:
                    selected = st.checkbox(stat)
                if selected:
                    selectednone=False
                    if stat == "calories":
                        uom.append("kcal")
                    elif stat == "cholesterol" or stat == "sodium" and "mg" not in uom:
                        uom.append("mg")
                    elif "g" not in uom:
                        uom.append("g")
                    selectedstats.append(stat)

            colors = ["#0B3954", "#FF6663", "#247BA0", "#70C1B3", "#FFCB77", "#9D6A89", "#D4A5A5"]
            colors = colors[:len(selectedstats)]
            
            uom = " / ".join(uom)
            color = st.color_picker("**Chart Color** :)", "#5E7D57")

        if (borderdates["min"] == borderdates["max"]):
            st.warning("Please log meals for more than one day to view your visualizations.")
            st.stop()

        if selectednone: #Making sure user selects atleast one nutritional before chart displays
            st.warning("Please select at least one nutritional to display.")
            st.stop()
        
        if str(dates[0]) < borderdates["min"]: #Making sure user can't select date before first meal logged
                st.warning(f"Please select a date at or after your earliest meal log: {borderdates['min']}")
                st.stop()

        if str(dates[1]) > borderdates["max"]: #Making sure user can't select date after last meal logged
                st.warning(f"Please select a date at or before your latest meal log: {borderdates['max']}")
                st.stop()

        st.line_chart(vm.get_stats_by_date_range(user_id, dates[0], dates[1], selectedstats),  
            y_label = f"{uom}", 
            x_label="date",
            color = colors
            )

        #st.write(f"Viewing: {stat}")
        st.write("---")
        st.header("Lifetime dining hall breakdown")
        st.bar_chart(vm.dining_hall_tracker(user_id), color=color, horizontal=True)

        st.write("---")
        st.header("Average calories by meal")
        st.bar_chart(vm.average_cals_by_meal(user_id), color=color, horizontal=True)

    except:
        st.warning("Please log a meal in the Menus tab to view your visualizations.")

    # fig1 = px.line(vm.get_stats_by_date_range(user_id, "2025-04-20", "2025-04-21",["calories","fat"]))
     
    # fig1.update_layout(
    #                 paper_bgcolor='white',  # Change the color of the entire chart area
    #                 plot_bgcolor='white'      # Change the color of the plotting area
    #                 )

    # st.write(fig1)