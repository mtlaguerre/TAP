'''
    TimeAndPay
    
    Track hours on the clock with your own clocking machine.
    Track expected net pay each pay period too!
'''
import os
import platform
import pandas as pd
import datetime as dt

if __name__ == '__main__':
    
    # if mobile, enable notifications
    is_mobile = 'iOS' or 'iPadOS' or 'Android'  # mobile systems    
    if platform.system() == is_mobile:
        import notifications
        
        dir_delim = '/'
        
        # use notifications to display messages
        def notify(message):
            notifications.send_notification(notifications.Notification(message))
    else:
        dir_delim = '\\' if platform.system() == "Windows" else '/'
        
        def notify(message):
            print(message)
    
    # file directory structure
    parent_dir = os.path.abspath(__file__)  # full path to current file
    parent_dir = os.path.dirname(parent_dir)   # parent directory of current file
    
    data_dir = 'data'
    
    employer_dir = 'skillstorm'
    
    file_name = 'timeclocks'
    
    file_extension = '.csv'

    file_full = file_name + file_extension
    
    # build path
    path = os.path.join(parent_dir, data_dir, employer_dir, file_full)

    directory_name = f"{data_dir}{dir_delim}{employer_dir}"

    # if path doesn't exists, create it    
    if not os.path.exists(path):
        try:
            os.makedirs(f"{directory_name}", exist_ok=True)
            # print(f"Directory '{directory_name}' created successfully.")
        except PermissionError:
            notify(f"Permission denied: Unable to create '{directory_name}'.")
        except Exception as e:
            notify(f"An error occured: {e}")
        finally:
            with open(f"{directory_name}{dir_delim}{file_full}", 'x', encoding='utf-8') as file:   # x mode safely creates new file, abort if already exists
                file.write("date,weekday,clocked_in,lunch_in,lunch_out,clocked_out")

    # section csv data using pandas
    data = pd.read_csv(path)

    # time variables
    date_delim = '.'
    present = dt.datetime.now()
    today = str(present.strftime('%y')) + date_delim + str(present.month) + date_delim + str(present.day)

    def daysAgo(numOfDays):
        date_of_day = str(present - dt.timedelta(days=numOfDays)).split('-')
        date_of_day = date_of_day[0][2:] + date_delim + date_of_day[1] + date_delim + date_of_day[2][:2]

        return date_of_day

    yesterday = daysAgo(1)

    hour = str(present.hour)
    minute = str(present.minute)

    # array of weekdays
    weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    # timeclock dictionary
    timeclock = {}
    weeks = []
    curr_week = 0

    # create an array from each row
    #
    #
    #
    #

    def clockIn(lastChar):
        # clock in
        with open(path, 'a') as file:

            # if not clocked in (not on clock)
            if last_char != file_delim:
                # clock in
                file.write(f"\"{today}\"{file_delim}\'{weekdays[present.weekday()]}\'{file_delim}{hour}{minute}{file_delim}")

                # return confirmation message
                message = "Software Developing Time!"

            else:
                # return reason of failure
                message = "Unable to clock in."
            notify(message)

    def clockOut()
        # if clocked in
        if timeclock(today) and not pd.isna(data == today][clocked_in]):
            # clock out
            with open(path, 'a') as file:
                file.write(f"{hour}{minute}\n")
            # return confirmation message
            message = "Nice work! Let's develop some more another time."
        else:
            # return reason of failure clock out
            message = "Are you even allowed to clock out right now?"
        notify(message)



    # prompt
    action = input("Clock in(ci), Lunch in(li), Lunch out(lo), Clock out(co), Info(i), Pay(p): ")
    file_delim = ','

    if action == 'ci':

        with open(path, 'r+') as file:

            file_str = file.read()
            last_char = file_str[-1]

            clockIn(last_char)

            
    elif action == 'li':
        # if on clock
            # punch out for lunch
            # return confirmation message
        # else
            # return reason of failure
        notify("Lunch In")
    elif action == 'lo':
        # if off clock
            # punch in from lunch
            # return confirmation message
        # else
            # return reason of failure
        notify("Lunch Out")
    elif action == 'co':
       clockOut() 

        notify("Clock Out")
    elif action == 'i':
        info_type = input("Generic(g) or Search(s): ")

        if info_type == 'g':
            # do something
            notify("Gathering generic info...")
        elif info_type == 's':
            # do something
            notify("Calculating searched info...")
        else:
            # error handling
            notify("Somthing went wrong... :(")
        # do sumn
    elif action == 'p':
        # do things
        notify("Pay")
    else:
        # error handling
        notify("Yup, something definitely went wrong.. :(")
