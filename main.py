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
    
    file_name = 'timeclocks 2'
    
    file_extension = '.csv'
    
    file_delim = ','

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
                file.write("date,weekday,clocked_in,lunch_in,lunch_out,clocked_out\n")

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
    minute = str(present.minute) if present.minute >= 10 else '0' + str(present.minute)

    # array of weekdays
    weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    # timeclock dictionary
    timeclock = {}
    weeks = []
    curr_week = 0
        
    # define clock in
    def clockIn():
        
        # open file in append mode
        with open(path, 'a') as file:
            
            # clock in
            file.write(f"\"{today}\"{file_delim}\'{weekdays[present.weekday()]}\'{file_delim}{hour}{minute}")
    
    # define clock out
    def clockPunch():
        
        # open file in append mode
        with open(path, 'a') as file:
            # write current hour & minute
            file.write(f"{hour}{minute}")
        
    def printDelim():
        
        # open file in append mode
        with open(path, 'a') as file:
            file.write(file_delim)  # write delimiter character
        
    # prompt
    action = input("Clock in(ci), Lunch in(li), Lunch out(lo), Clock out(co), Info(i), Pay(p): ")

    if action == "ci" or action == "li" or action == "lo" or action == "co" or action == "i" or action == "p":

        # empty data value
        null_val = 'null'

        # load timeclock data into array
        for rows in range(data.shape[0]):

            df = data.iloc[rows]    # store current row in df

            times = [df['clocked_in'], df['lunch_in'], df['lunch_out'], df['clocked_out']]
            timeclock['date'] = [null_val, null_val, null_val, null_val]

            for  i in range (data.shape[1] - 2):
                timeclock['date'][i] = str(times[i]) if not pd.isna(times[i]) else null_val
                print(timeclock['date'][i])


        def checkPunch(punch):
            if data.iloc[0][punch] != null_val:
                return True
            else:
                return False


        if action == 'ci':      # clock in

            # if clocked in == null
            if not checkPunch('clocked_in'):
                clockIn()
                printDelim()
                message = "[Welcome message]"
            else:
                message = "[Clock In failed message]"

            notify(message)

        elif action == 'li':    # begin lunch
            if checkPunch('clocked_in') and not checkPunch('lunch_in'):
                clockPunch()
                printDelim()
                message = "Hungry?"
            elif not checkPunch('clocked_in'):
                message = "You're not even on the clock..."
            elif checkPunch('lunch_in'):
                message = "Eating began at " + str(data.iloc[0]['lunch_in']) + ", remember?"
            else:
                message = "[Error slipping out to lunch]"

            notify(message)

        elif action == 'lo':    # end lunch
            if checkPunch('clocked_in') and checkPunch('lunch_in') and not checkPunch('lunch_out'):
                clockPunch()
                printDelim()
                message = "The developing continues :)"
            elif not checkPunch('clocked_in'):
                message = "You're not even on the clock..."
            elif not checkPunch('lunch_in'):
                message = "You must begin your lunch to end your lunch."
            elif checkPunch('lunch_out'):
                message = "Lunch can't end twice. Focus up on the project."
            else:
                message = "[Error lunch not ended]"

            notify(message)
            
        elif action == 'co':    # clock out
            if checkPunch('clocked_in') and checkPunch('lunch_in') and checkPunch('lunch_out') and not checkPunch('clocked_out'):
                clockPunch()
                message = "Nice work. Let's develop some more tomorrow!"
            elif not checkPunch('clocked_in'):
                message = "You're not even on the clock..."
            elif not checkPunch('lunch_in'):
                message = "You must being your lunch to end your lunch."
            elif not checkPunch('lunch_out'):
                message = "End your lunch first"
            elif checkPunch('clocked_out'):
                message = "You're already off the clock. Seems you're tired, rest up."
            else:
                message = "Aw, great. You broke something."

            notify(message)

        elif action == 'i':     # info
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
        # handle error message
        notify("Yup, you messed something up buddy.")

    
        
