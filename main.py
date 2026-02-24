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
    mobile = ['iOS', 'iPadOS', 'Android']  # mobile systems    
    if platform.system() in mobile:
        import sys
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
    
    employer_dir = 'testing'
    
    file_name = 'timeclocks'
    
    file_extension = '.csv'
    
    file_delim = ','

    file_full = file_name + file_extension
    
    # build path
    path = os.path.join(parent_dir, data_dir, employer_dir, file_full)

    directory_name = f"{data_dir}{dir_delim}{employer_dir}"
    
    try:
        os.makedirs(os.path.join(parent_dir, directory_name), exist_ok=True)
        
        with open(f"{directory_name}{dir_delim}{file_full}", 'x', encoding='utf-8') as file:    # x mode safely creates new file, abort if already exists
            file.write("date,weekday,clocked_in,lunch_in,lunch_out,clocked_out\n")

    except FileExistsError:
        pass

    except PermissionError:
        notify(f"Permission denied: Unable to create '{directory_name}'.")

    except Exception as e:
        notify(f"An error occured: {e}")

    # section csv data using pandas
    data = pd.read_csv(path)

    # time variables
    date_delim = '.'
    present = dt.datetime.now()
    today = str(present.strftime('%y')) + date_delim + (str(present.month) if present.month >= 10 else '0' + str(present.month)) + date_delim + (str(present.day) if present.day >= 10 else '0' + str(present.day))

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
        
    # define clock punches
    def clockPunch():
        
        # open file in read-write binary mode
        with open(path, 'r+b') as file:

            file.seek(-1, 2)            # seek to the last byte

            if file.read(1) == b'\n':
                file.seek(-1, 2)        # go back one byte
                file.truncate()         # remove the newline

            # write current hour & minute
            file.write(f"{hour}{minute}".encode('utf-8'))
        
    def printChar(char):
        
        # open file in append mode
        with open(path, 'a') as file:
            file.write(char)  # write character
        
    # prompt
    action = input("Clock in(ci), Lunch in(li), Lunch out(lo), Clock out(co), Info(i), Pay(p): ") if platform.system() not in mobile else sys.argv[1]

    if action == "ci" or action == "li" or action == "lo" or action == "co" or action == "i" or action == "p":

        # empty data value
        null_val = 'null'

        # load timeclock data into array
        for rows in range(data.shape[0]):

            df = data.iloc[rows]    # store current row in df

            times = [df['clocked_in'], df['lunch_in'], df['lunch_out'], df['clocked_out']]
            timeclock[df['date']] = [null_val, null_val, null_val, null_val]

            for  i in range (data.shape[1] - 2):
                timeclock[df['date']][i] = str(times[i]) if not pd.isna(times[i]) else null_val
                #print(timeclock['date'][i])

        # if today not in timeclock
        if today not in timeclock:
            timeclock[today] = [null_val, null_val, null_val, null_val]

        def checkPunch(punch):
            if timeclock[today][punch - 1] != null_val:
                return True
            else:
                return False

        # Tax Percentages (VT 2025)
        hourlyRate = 15                 # update for user input
        hoursPerPayPeriod = 40          # update for user input (default)
        grossPay = hourlyRate * hoursPerPayPeriod
        payFreq = "Biweekly"            # update for user input
        if payFreq == "Weekly":
            payPeriodsPerYear = 52
        elif payFreq == "Biweekly":
            payPeriodsPerYear = 26
            hoursPerPayPeriod *= 2
        elif payFreq == "Monthly":
            payPeriodsPerYear = 12
            hoursPerPayPeriod *= 4

        # Federal Income Tax Withholding
        grossAnnualSalary = grossPay * payPeriodsPerYear
        allowances = 0                  # update for user input
        allowanceWithholding = allowances * 4300
        adjustedAnnualIncome = grossAnnualSalary - allowanceWithholding
        
        # Apply federal tax brackets (2025)


        VCC = 0.001     # Vermont Child Care EE
        MED = 0.015     # Medicare
        VTW = 0.028     # Vermont State W/H
        FWT = 0.040     # Federal W/H
        SSC = 0.062     # Social Security
        
        # declare constant missing clock in message
        MISSING_CI_MSG = "You're not even on the clock..."
        MISSING_LI_MSG = "You must begin your lunch to end your lunch."
        MISSING_LO_MSG = "End your lunch first."
        #MISSING_CO_MSG = "You haven't ended your previous shift."

        # declare constant clock in messages (indicators/notifications)
        CI_SUCCESS_MSG = "[Welcome message]"
        CI_EXISTS_MSG = "[Duplicate clock in message]"
        CI_GENERIC_MSG = "Clock in failed to unknown reasons. Investigate."

        # declare constant lunch in messages
        LI_SUCCESS_MSG = "[Lunch in success messge]"
        LI_EXISTS_MSG = "Today's lunch was at " + str(timeclock[today][1]) + ", remember?"
        LI_GENERIC_MSG = "Lunch in failed to unknown reasons. Investigate."

        # declare constant lunch out messages
        LO_SUCCESS_MSG = "The developing continues :)"
        LO_EXISTS_MSG = "Lunch can't end twice. Focus up on the project."
        LO_GENERIC_MSG = "Lunch out failed to unknown reasons. Investigate."

        # declare constant clock out messages
        CO_SUCCESS_MSG = "Nice work. Let's develop some more tomorrow!"
        CO_EXISTS_MSG = "You're already off the clock. Seems you're tired, rest up."
        CO_GENERIC_MSG = "Clock out failed to unknown reasons. Investigate."
        
        if action == 'ci':      # clock in

            # if clocked in == null
            if not checkPunch(1):   # if not clocked in

                # open file in append mode
                with open(path, 'a') as file:
                     
                    # add new day info
                    file.write(f"\"{today}\"{file_delim}\'{weekdays[present.weekday()]}\'{file_delim}")

                clockPunch()
                printChar(file_delim)
                message = CI_SUCCESS_MSG
            elif checkPunch(1):     # if clocked in (maybe check if clocked out of last shift?)
                message = CI_EXISTS_MSG
            else:
                message = CI_GENERIC_MSG

            notify(message)

        elif action == 'li':    # begin lunch
            if checkPunch(1) and not checkPunch(2): # if clocked in and lunch not began
                clockPunch()
                printChar(file_delim)
                message = LI_SUCCESS_MSG 
            elif not checkPunch(1) or checkPunch(4): # if not clocked in or already clocked out
                message = MISSING_CI_MSG
            elif checkPunch(2):         # if already began lunch
                message = LI_EXISTS_MSG
            else:                       # any uncovered fail
                message = LI_GENERIC_MSG

            notify(message)

        elif action == 'lo':    # end lunch
            if checkPunch(1) and checkPunch(2) and not checkPunch(3):   # if clocked in and lunch began and lunch not ended
                clockPunch()
                printChar(file_delim)
                message = LO_SUCCESS_MSG
            elif not checkPunch(1):     # if not clocked in
                message = MISSING_CI_MSG 
            elif not checkPunch(2):     # if lunch not began
                message = MISSING_LI_MSG
            elif checkPunch(3):         # if already ended lunch
                message = LO_EXISTS_MSG
            else:                       # any uncovered fail
                message = LO_GENERIC_MSG

            notify(message)
            
        elif action == 'co':    # clock out
            if checkPunch(1) and checkPunch(2) and checkPunch(3) and not checkPunch(4):     # if clocked in and began lunch and ended lunch and not clocked out
                clockPunch()
                printChar('\n')
                message = CO_SUCCESS_MSG
            elif not checkPunch(1):     # if not clocked in
                message = MISSING_CI_MSG
            elif checkPunch(2) and not checkPunch(3):     # if lunch began and not ended
                message = MISSING_LO_MSG
            elif checkPunch(4):         # if already clocked out
                message = CO_EXISTS_MSG
            else:                       # any uncovered fail
                message = CO_GENERIC_MSG 

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
