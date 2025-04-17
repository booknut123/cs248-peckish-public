from helper_methods import *
from methods import *

def testing():
    clear_db()

    get_menu("Bates","Lunch", date.today())

    log_meal(1, 15862, "Bates", "Lunch", date.today())
    log_meal(1, 15864, "Bates", "Lunch", date.today())

    get_menu("Bates", "Dinner", date.today())

    log_meal(1, 19306, "Bates", "Dinner", date.today())

    print(get_user_dishes(1, date.today()))

#testing()

# print(get_filtered_menu([], [], "Bates", "Lunch", date.today()))
# print(get_filtered_menu(["Dairy"], ["Vegetarian"], "Bates", "Lunch", date.today()))

delete_meal(12, 20533)