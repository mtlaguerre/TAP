'''
    TAP - Time And Pay

    A time-tracking & payroll automation system for your personal needs.
'''
import os
import platform
import pandas as pd
import datetime as dt

if __name__ == '__main__':

    # file extension
    fileExt = ".csv"
   
    # default directory delimiter for majority operating systems
    dirDelim = '/'

    # file delimiter separating the data
    fileDelim = ','

    # if mobile, enable notifications
    mobile = ['iOS', 'iPadOS', 'Android'] # mobile systems
    if platform.system() in mobile:
        import sys
        import notifications
        
        # use notifications to display messages
        def notify(message):
            notifications.send_notification(notifications.Notification(message))
    else:
        dirDelim = '\\' if platform.system() == "Windows" else '/'

        def notify(message):
            print(message)

    def validateDirectory(_headDir, _dirPath, _filename):
        
        try:
            os.makedirs(os.path.join(_headDir, _dirPath), exist_ok=True)

            with open(f"{_dirPath}{dirDelim}{_filename}", 'x', encoding='utf-8') as f:      # x mode safely creates new file, abort if already exists
                f.write("date,weekday,clocked_in,started_lunch,ended_lunch,clocked_out\n")

        except FileExistsError:
            pass
        
        except PermissionError:
            notify(f"Permission denied: Unabled to create '{_dirPath}'.")

        except Exception as e:
            notify(f"An error occured: {e}")

    '''
        Folder Structure Setup:
        _headDir
            |
            _timesheetDir
                |
                _filename + _fileExt

        _file Delim = symbol separating data in file
    '''
    def setupStructure(_headDir, _timesheetDir, _filename):

        currFile = os.path.abspath(__file__) # full path to current file
        parentDir = os.path.dirname(currFile) # parent directory of current file
       
        # full file name
        file = _filename + fileExt

        # build path
        bPath = os.path.join(parentDir, _headDir, _timesheetDir, file)

        # relative directory path
        relativeDir = f"{_headDir}{dirDelim}{_timesheetDir}"

        # build path if missing
        validateDirectory(parentDir, relativeDir, file)

        return bPath  # future use (pandas)


    # Path Setup
    path = setupStructure('data', 'genspark', 'timeclocks')

    '''
        Section csv data using Pandas
        data being split:

        date > weekday > clocked_in > started_lunch > ended_lunch > clocked_out
    '''
    # store csv into a dataframe (secitoned)
    data = pd.read_csv(path)

    ''' Time Variables '''
    dateDelim = '.'
    present = dt.datetime.now()
    
    # days
    today = str(present.strftime('%y')) + dateDelim + (str(present.month) if present.month >= 10 else '0' + str(present.month)) + dateDelim + (str(present.day) if present.day >= 10 else '0' + str(present.day))
    def daysAgo(_numOfDays):
        dateOfDay = str(present - dt.timedelta(days=_numOfDays)).split('-')
        dateOfDay = dateOfDay[0][2:] + dateDelim + dateOfDay[1] + dateDelim + dateOfDay[2][:2]

        return dateOfDay
    yesterday = daysAgo(1)
    
    # hours & minutes
    hour = str(present.hour)
    minute = str(present.minute) if present.minute >= 10 else '0' + str(present.minute)

    WEEKDAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    # timeclock dictionary 
    timeclock = {}

    # weeks
    weeks = []

    '''
        Timepunch function

        writes the current time to the end of the file
    '''
    def timepunch():

        # open file in read-write binary mode
        with open(path, 'r+b') as f:

            f.seek(-1, 2)           # seek to the last byte

            if f.read(1) == b'\n':
                f.seek(-1, 2)       # go back one byte
                f.truncate()        # remove the newline

            # write current hour & minute
            f.write(f"{hour}{minute}".encode("utf-8"))

    '''
        PrintChar function

        writes a character to the end of the file
    '''
    def printChar(_char):

        # open file in append mode
        with open(path, 'a') as f:
            f.write(_char)           # write character


    # prompt
    action = input ("Clock In(ci), Clock Out(co), Start Lunch(sl), End Lunch(el), Info(i): ") if platform.system() not in mobile else sys.argv[1]

    options = ["ci", "co", "sl", "el", "i"]

    # if valid selection, load timeclock (faster start)
    if action in options:

        # emtpy data value
        nullVal = "null"

        # store csv data into an array
        for rows in range(data.shape[0]):
            
            df = data.iloc[rows]    # store current row in df

            punches = [df['clocked_in'], df['started_lunch'], df['ended_lunch'], df['clocked_out']]
            timeclock[df['date']] = [nullVal, nullVal, nullVal, nullVal]    # fill current timepunch slots with "null" (creates the slot)

            for i in range(data.shape[1] - 2):
                timeclock[df['date']][i] = str(punches[i]) if not pd.isna(punches[i]) else nullVal  # populate array with csv values, otherwise "null"

        # if today not in timeclock array
        if today not in timeclock:
            timeclock[today] = [nullVal, nullVal, nullVal, nullVal]     # create row for today with no timepunches ("null" values)

        '''
            CheckPunchExists

            checks if selected puch is a duplicate
            1 = clocked_in
            2 = started_lunch
            3 = ended_lunch
            4 = clocked_out
        '''
        def checkPunchExists(_punch):
            res = 0
            if timeclock[today][_punch - 1] != nullVal:
                res = True
            else:
                res = False

            return res

        ''' Business Logic '''

        DUPLICATE_PUNCH_ERROR_MSG = "FAILED: Duplicate Punch"

        if action == 'ci':      # clocking in

            # if not yet clocked in
            if not checkPunchExists(1):

                # open file in append mode
                with open(path, 'a') as f:

                    # add new day info
                    f.write(f"\"{today}\"{fileDelim}\'{WEEKDAYS[present.weekday()]}\'{fileDelim}")       # "Date",'DAY',

                timepunch()             # HH:MM
                printChar(fileDelim)

                message = "SUCCESSFUL: Clocked In"
            else:   # already clocked in
                message = DUPLICATE_PUNCH_ERROR_MSG

            notify(message)

        elif action == 'co':      # clocking out
            
            # if clocked in AND lunch ended AND NOT clocked out
            if checkPunchExists(1) and checkPunchExists(3) and not checkPunchExists(4):

                timepunch()
                printChar('\n') # end day

                message = "SUCCESSFUL: Clocked Out"
            # if clocked in AND lunch NOT yet started AND NOT clocked out
            elif checkPunchExists(1) and not checkPunchExists(2) and not checkPunchExists(4):

                printChar(fileDelim)    # skip start lunch
                printChar(fileDelim)    # skip end lunch

                timepunch()
                printChar('\n')     # end day

                message = "SUCCESSFUL: Clocked Out"
            # if NOT yet clocked in
            elif not checkPunchExists(1):
                message = "FAILED: Missing \"Clock In\""
            # if lunch started AND lunch NOT ended
            elif checkPunchExists(2) and not checkPunchExists(3):
                message = "FAILED: Missing \"Ended Lunch\""
            # if already clocked out
            elif checkPunchExists(4):
                message = DUPLICATE_PUNCH_ERROR_MSG

            notify(message)

        elif action == 'sl':

            # if clocked in AND lunch NOT yet started
            if checkPunchExists(1) and not checkPunchExists(2):

                timepunch()
                printChar(fileDelim)

                message = "SUCCESSFUL: Started Lunch"
            # if NOT yet clocked in
            elif not checkPunchExists(1):
                message = "FAILED: Missing \"Clock In\""
            # if lunch already started
            elif checkPunchExists(2):
                message = DUPLICATE_PUNCH_ERROR_MSG
            # if clocked out
            elif checkPUnchExists(4):
                message = "FAILED: Current Status - Clocked Out"
            
            notify(message)

        elif action == 'el':

            # if clocked in AND started lunch AND lunch NOT yet ended
            if checkPunchExists(1) and checkPunchExists(2) and not checkPunchExists(3):

                timepunch()
                printChar(fileDelim)

                message = "SUCCESSFUL: Ended Lunch"
            # if NOT yet clocked in
            elif not checkPunchExists(1):
                message = "FAILED: Missing \"Clock In\""
            # if clocked in AND lunch NOT yet started
            elif not checkPunchExists(2):
                message = "FAILED: Missing \"Started Lunch\""
            # if clocked out
            elif checkPunchExists(4):
                message = "FAILED: Current Status - Clocked Out"

            notify(message)