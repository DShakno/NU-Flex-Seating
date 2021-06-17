from uuid import uuid4
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import matplotlib.dates as mdates
from datetime import datetime
from datetime import timedelta
from copy import copy

sns.set()

# load csv
df_student = pd.read_csv("nuflex_ds3000_Mar5_noname-1.csv")

def pseudonymize_col(df, col):
    """ pseudonymizes given col
    Args:
        df (dataFrame): input dataframe
        col (string): inputed column to pseudonymizes
    
    Returns:
        temp_dict (dict): dictionary of the keys from the orginial dataframe with their new pseudonyms
    """
    
    # create empty dict
    temp_dict = {}
    
    # drop duplicates
    df_temp = df.drop_duplicates(subset= col).reset_index()
    
    # fill dictionary with orinigal keys and their new pseudonyms
    for i in range(len(df_temp)):
        pseudo = str(uuid4())[:6]
        temp_dict[df_temp.loc[i, col]] = pseudo
    
    # replace orginal keys with their new pseudonyms 
    df = df.replace(temp_dict)
    
    return temp_dict

# discard all columns which are exclusively NaN
df_student = df_student.dropna(1, how = 'all')

# replace all occurences of "Yes" in the df with True
df_student = df_student.replace("Yes", True)

# replace all occurences of "No" in the df with False
df_student = df_student.replace("No", False)

def get_week_start(dates):
    """ takes the starting day from a week's range
    Args:
        dates (string): input a week's range
    
    Returns:
        temp_datetime (datetime): first day from a week's range
    """
    # split the range to take first day
    first_date = dates.split("-")[0]
    
    # convert the string to a datetime
    temp_datetime = datetime.datetime.strptime(first_date, "%m/%d/%Y")
    
    return temp_datetime

# create new dataframe that contains a modified column from df_student
df_week_start = df_student['Week'].map(get_week_start)

# add new column "week start" to df_student 
df_student['week start'] = df_week_start

def get_inp_permit(permit):
    """ takes a permit value and returns correlated boolean
    Args:
        permit (string): input a permit's value
    
    Returns:
        True (boolean): boolean correlated with the permit's value 
        False (boolean): boolean correlated with the permit's value
    """
    # Case 1: INP Yes
    if(permit == "INP Yes"):
        return True
    # Case 2: INP No
    elif(permit == "INP No"):
        return False
    # Case 3: REM Yes
    elif(permit == "REM Yes"):
        return False
    # Case 4: Rem No
    elif(permit == "REM No"):
        return True
    
def get_inp_request(request):
    """ takes a request value and returns correlated boolean
    Args:
        request (string): input a request's value
    
    Returns:
        True (boolean): boolean correlated with the request's value 
        False (boolean): boolean correlated with the request's value
    """
    # Case 1: INP Yes
    if(request == "INP Yes"):
        return True
    # Case 2: INP No
    elif(request == "INP No"):
        return True
    # Case 3: Rem Yes
    elif(request == "REM Yes"):
        return False
    # Case 4: Rem No
    elif(request == "REM No"):
        return False
    
# create new dataframes that contains a modified column from df_student   
df_Tue_INP_Request = df_student['Tue'].map(get_inp_request)
df_Tue_INP_Permit = df_student['Tue'].map(get_inp_permit)
df_Fri_INP_Request = df_student['Fri'].map(get_inp_request)
df_Fri_INP_Permit = df_student['Fri'].map(get_inp_permit)

# add new columns to df_student
df_student['Tue:INP Request'] = df_Tue_INP_Request
df_student['Tue:INP Permit'] = df_Tue_INP_Permit
df_student['Fri:INP Request'] = df_Fri_INP_Request
df_student['Fri:INP Permit'] = df_Fri_INP_Permit

# delete redundant columns
del df_student['Week']
del df_student['Subject']
del df_student['Course Name']
del df_student['Tue']
del df_student['Fri']

def get_next_weekday(date, weekday):
    """ gets closest date which is a given day of the week (mon, tues, ...)
    
    weekday encoding convention taken from:
    https://docs.python.org/3/library/datetime.html#datetime.date.weekday
    
    Args:
        date (datetime.date): input date
        weekday (int): 0 is monday and 6 is Sunday
    
    Returns:
        date_out (datetime.date): closest input date
            which is a given weekday
    """
    # check that input weekday is valid
    assert weekday in list(range(7)), 'invalid weekday'
    
    # we copy input date so we don't modify its internal state
    date_out = copy(date)
    
    # add a day until we're at a given weekday
    while date_out.weekday() != weekday:
        date_out += timedelta(days=1)
    
    return date_out

# this is a Friday (weekday=4)
date = datetime(year=2021, month=3, day=5).date()

# this is closest thursday which follows (weekday=3)
date_out_expected = datetime(year=2021, month=3, day=11).date()

date_out = get_next_weekday(date, weekday=3)

assert date_out == date_out_expected, 'get_next_weekday() error'

# create temporary list
temp_student_list = []

# loop through all values in df_student 
for i in range(len(df_student)):
    # create empty dictionary for this weeks's Tuesday and Friday
    temp_dict_tue = dict()
    temp_dict_fri = dict()
    
    # Create new tuesday entry
    temp_dict_tue["CRN"] = df_student.at[i, "CRN"]
    temp_dict_tue["Remote Learner"] = df_student.at[i, "Remote Learner"]
    temp_dict_tue["Student ID"] = df_student.at[i, "Student ID"]
    temp_dict_tue["Remote Learner"] = df_student.at[i, "Remote Learner"]
    temp_dict_tue["date"] = get_next_weekday(pd.to_datetime(df_student.at[i, "week start"]), 2)
    temp_dict_tue["permit"] = df_student.at[i, "Tue:INP Permit"]
    temp_dict_tue["request"] = df_student.at[i, "Tue:INP Request"]
    
    # Create new friday entry
    temp_dict_fri["CRN"] = df_student.at[i, "CRN"]
    temp_dict_fri["Remote Learner"] = df_student.at[i, "Remote Learner"]
    temp_dict_fri["Student ID"] = df_student.at[i, "Student ID"]
    temp_dict_fri["Remote Learner"] = df_student.at[i, "Remote Learner"]
    temp_dict_fri["date"] = get_next_weekday(pd.to_datetime(df_student.at[i, "week start"]), 5)
    temp_dict_fri["permit"] = df_student.at[i, "Fri:INP Permit"]
    temp_dict_fri["request"] = df_student.at[i, "Fri:INP Request"]
    
    # append each entry to bigger temporary list
    temp_student_list.append(temp_dict_tue)
    temp_student_list.append(temp_dict_fri)
    
# create temporary dataframe
df_end_student = pd.DataFrame(temp_student_list)

# Change True to 1 and False to 0
df_end_student = df_end_student.replace(True, 1)
df_end_student = df_end_student.replace(False, 0)

# set df_student to equal temporary dataframe
df_student = df_end_student

# create new line plot
student_plot = sns.lineplot(data = df_student, x = 'date', y = 'permit', ci = None)
sns.lineplot(data = df_student, x = 'date', y = 'request', ci = None)

student_plot.set(xlabel='Date', ylabel='Num Students')
student_plot.legend(['permit', 'request'])

# format x tick labels using strptime/strftime format string
my_fmt = mdates.DateFormatter('%b-%d')

# plot number of students permited to join vs requested to join
plt.gca().xaxis.set_major_formatter(my_fmt)

