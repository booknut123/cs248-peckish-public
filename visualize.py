import streamlit as st
from datetime import date, datetime, timedelta
import methods
import visualization_methods as vm
import numpy as np

sidebar, main = st.columns((0.5, 1.5), gap="small", vertical_alignment="top")
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

# try:
with sidebar:
        
    st.image(image='crumb-the-goose.png')
    
    test = vm.get_total_nutrients(user_id, "calories")

    d = date.today()
    today = d.weekday()

    if today == 6:
        sun = d
        sat = d + timedelta(days=6)
    else:
        sun = d + timedelta(days=-today)
        sat = d + timedelta(days=5 - today)

    # st.subheader("Customize")
        
    borderdates = methods.get_border_log_dates(user_id)
    
    stats = ["calories", "fat", "cholesterol", "sodium", "carbohydrates", "sugars", "protein"]
    selectedstats = []
    uom = []
    selectednone = True

    st.write("**Select Nutrients**")
    col1, col2 = st.columns((1.5,3))

    all = col1.button("All")
    if all:
        all=True
    
    kcal, mg, g = [], [], []

    for stat in stats:
        if all:
            selected = st.checkbox(stat, value=True)
        #elif none:
        #    selected = st.checkbox(stat, value=False)
        else:
            if stat in ["fat", "carbohydrates", "protein"]:
                selected = st.checkbox(stat, value=True)
            else:
                selected = st.checkbox(stat)
        
        if selected:
            selectednone=False
            if stat == "calories":
                kcal.append(stat)
            if stat in ["cholesterol", "sodium"]:
                mg.append(stat)
            elif stat not in ["calories", "cholesterol", "sodium"]:
                g.append(stat)
            selectedstats.append(stat)

with main:
    st.header("Visualize")

    st.write("---")

    col1, col2 = st.columns((1.5,1))

    col1.subheader("Nutritionals Graph")

    dates = col2.date_input("Select Date Range",
                                format="MM-DD-YYYY", 
                                min_value=borderdates['min'], #Can't select date before first meal logged
                                max_value=borderdates['max'], #Can't select date after last meal logged
                                value=(borderdates['min'], borderdates['max'])
                                )
    

    if (borderdates["min"] == borderdates["max"]):
        st.warning("Please log meals for more than one day to view visualizations.")
        st.stop()

    elif selectednone: #Making sure user selects atleast one nutritional before chart displays
        st.warning("Please select at least one nutrient to view your custom graph.")
    
    elif str(dates[0]) < borderdates["min"]: #Making sure user can't select date before first meal logged
            st.warning(f"Please select a date at or after your earliest meal log: {borderdates['min']}")

    elif str(dates[1]) > borderdates["max"]: #Making sure user can't select date after last meal logged
            st.warning(f"Please select a date at or before your latest meal log: {borderdates['max']}")
    
    else:

        if kcal:
            label = ", ".join([stat.capitalize() for stat in kcal])
            st.write(f"**{label}**")
            st.line_chart(vm.get_stats_by_date_range(user_id, dates[0], dates[1], kcal),
                          y_label = "kcal",
                          x_label = "date")
        if g:
            label = ", ".join([stat.capitalize() for stat in g])
            st.write(f"**{label}**")
            st.line_chart(vm.get_stats_by_date_range(user_id, dates[0], dates[1], g),
                          y_label = "mg",
                          x_label = "date")
        if mg:
            label = ", ".join([stat.capitalize() for stat in mg])
            st.write(f"**{label}**")
            st.line_chart(vm.get_stats_by_date_range(user_id, dates[0], dates[1], mg),
                          y_label = "mg",
                          x_label = "date")
        
        

    #st.write(f"Viewing: {stat}")
    st.write("---")

    col1, col2 = st.columns((3,1))
    col1.subheader("Meals per Dining Hall")
    color1 = col2.color_picker("**Chart Color**", "#5E7D57", key="color1")
    st.bar_chart(vm.dining_hall_tracker(user_id),
                    color=color1,
                    horizontal=True,
                    x_label="Number of Dishes",
                    y_label="Dining Hall")

    st.write("---")

    col1, col2 = st.columns((3,1))
    col1.subheader("Average Cals per Meal")
    color2 = col2.color_picker("**Chart Color**", "#5E7D57", key="color2")
    st.bar_chart(vm.average_cals_by_meal(user_id),
                    color=color2,
                    horizontal=True,
                    x_label="Calories",
                    y_label="Meal")

# except:
#     st.warning("Please log a meal in the Menus tab to view your visualizations.")


#import plotly express as px to use
# fig1 = px.line(vm.get_stats_by_date_range(user_id, "2025-04-20", "2025-04-21",["calories","fat"]))
    
# fig1.update_layout(
#                 paper_bgcolor='white',  # Change the color of the entire chart area
#                 plot_bgcolor='white'      # Change the color of the plotting area
#                 )

# st.write(fig1)