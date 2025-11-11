'''
    Calculate Pays

Use time clock data in csv to calculate estimate next payout
'''
from operator import ifloordiv

import pandas as pd
import os
import notifications as noti
import datetime
#from datetime import date
import sys

if __name__ == '__main__':

    neededHours = 520

    device = "computer"
    #print(sys.argv)    # debug iPhone

    # file directories
    data_dir = 'data'
    #output_dir = 'output'

    # file
    file_name = 'timeclocks.csv'

    # build file location
    path = os.path.join(data_dir, file_name)
    #print("Path: " + path)    # debug

    # read csv into data frame
    orig = pd.read_csv(path)
    orig['date'] = orig['date'].astype('string')
    orig['weekday'] = orig['weekday'].astype('string')

    # clean up data
    # data = orig.dropna()
    data = orig

    # time variables relative to present moment
    this_day = datetime.datetime.now()
    today = str(this_day.month) + '/' + (str(this_day.day) if int(str(this_day.day)) >= 10 else '0' + str(this_day.day))
    yesterday = str(this_day - datetime.timedelta(days=1))
    yesterday = yesterday.split('-')
    yesterday = yesterday[1] + '/' + yesterday[2][:2]

    this_hour = str(this_day.hour)
    this_min = str(this_day.minute) if this_day.minute >= 10 else '0' + str(this_day.minute)

    # print('this_hour: ' + this_hour)    # debug
    # print('this_min: ', this_day.minute)      # debug

    # array of weekdays
    weekdays = ["M", "T", "W", "TH", "F", "SAT", "SUN"]

    # timeclock dictionary
    timeclock = {}
    weeks = []
    curr_week = 0

    # create an array from each row
    for rows in range(data.shape[0]):
        df = data.iloc[rows]
        if not pd.isna(df['clocked_in']) and not pd.isna(df['clocked_out']):
            timeclock[df['date']] = str(int(df['clocked_in'])) + " - " + str(int(df['clocked_out']))
        elif not pd.isna(df['clocked_in']) and pd.isna(df['clocked_out']):
            if df['date'] == today:
                timeclock[df['date']] = str(int(df['clocked_in'])) + " - " + this_hour + this_min
            else:
                timeclock[df['date']] = str(int(df['clocked_in'])) + " - " + str(100)
        elif pd.isna(df['clocked_in']) and not pd.isna(df['clocked_out']):
            timeclock[df['date']] = str(1630) + " - " + str(int(df['clocked_out']))
        else:
            timeclock[df['date']] = str(1630) + " - " + str(100)
            # print(df['date'], ":", timeclock[df['date']])     # debug

        # build week associations
        new_week = len(weeks) == 0 or df['weekday'] == 'M' or df['weekday'] in weeks[curr_week]

        if new_week:
            if rows != 0:
                # increment week
                curr_week += 1

            weeks.append(curr_week)

            # initialize dictionary for new week
            weeks[curr_week] = {}

        # add current date to dictionary
        weeks[curr_week][df['weekday']] = timeclock[df['date']]

    def printOrNotify(message):
        print(message) if device == "computer" else noti.send_notification(noti.Notification(message))

    def clockIn(file_path, day_of_week, curr_hour, curr_min, message):
        with open(file_path, 'a') as file:
            file.write('\"' + today + '\"'
                       + ',\"' + weekdays[datetime.datetime.today().weekday()] + '\"'
                       + ',' + this_hour + this_min)

        printOrNotify(message)

    def clockOut(file_path, curr_hour, curr_min, message):
        with open(file_path, 'a') as file:
            file.write(',' + curr_hour + curr_min
                       + '\n')

            printOrNotify(message)

    '''
    Calculate the amount of hours worked from a formated string:
    
    "hh:mm - hh:mm"
    
    Round to the nearest ones place. Return the amount of hours
    rounded.
    '''
    def calcDayHours(shift):
        # grab clock in time
        clocked_times = shift.split(' - ')
        clock_in = clocked_times[0]
        clock_out = clocked_times[1]

        # 00:00 check
        if int(clock_in) < 10:
            clock_in = '00' + str(clock_in)
        elif int(clock_in) < 100:
            clock_in = '0' + str(clock_in)

        if int(clock_out) < 10:
            clock_out = '00' + str(clock_out)
        elif int(clock_out) < 100:
            clock_out = '0' + str(clock_out)

        #print(clock_in, clock_out)    # debug

        # minutes til equal
        minute_diff = 0
        curr = int(clock_in[-2:])
        while curr != int(clock_out[-2:]):
            curr += 1

            if curr == 60:   # minute max
                curr = 0
                minute_diff += 1
                clock_in = str(int(clock_in) + minute_diff + 40) if int(clock_in) >= 1000 and int(clock_in) <= 2300 else str(int(0))
            else:
                minute_diff += 1

        # hours til equal
        hour_diff = 0
        curr = int(clock_in[:2]) if int(clock_in) >= 1000 else int(clock_in[0])
        while curr != (int(clock_out[:2]) if int(clock_out) >= 1000 else int(clock_out[0])):
            curr += 1

            if curr == 24:   # hour max
                curr = 0
                hour_diff += 1
            else:
                hour_diff += 1

        # remove lunch break if worked more than 6 hours
        if hour_diff >= 6:
            if minute_diff < 30:
                hour_diff -= 1
                minute_diff = 60 - (30 - minute_diff)
            else:
                minute_diff -= 30

        # print("This day was a", hour_diff, "hour(s) and", minute_diff, "minute shift.")   # debug
        return hour_diff + round((minute_diff / 60), 2)

    def calcWeekHours(week):
        monday = calcDayHours(week['M']) if 'M' in week else 0
        tuesday = calcDayHours(week["T"]) if 'T' in week else 0
        wednesday = calcDayHours(week["W"]) if 'W' in week else 0
        thursday = calcDayHours(week["TH"]) if 'TH' in week else 0
        friday = calcDayHours(week["F"]) if 'F' in week else 0

        return round(monday + tuesday + wednesday + thursday + friday, 2)

    def calcTotalHours(timeclock):
        sum = 0
        for hours in timeclock.values():
            sum += calcDayHours(hours)

        return round(sum, 2)

    def calcWeekPay(week, hourly):
        hours = calcWeekHours(week)

        if hours > 40:
            gross = hourly * 40
            overtimeHourly = hourly + (hourly/2)
            overtimeHours = hours - 40
            overtimePay = overtimeHourly * overtimeHours
            gross = gross + overtimePay
        else:
            gross = hourly * hours

        soc_sec_ee = 00.062 * gross
        med_ee = 0.014 * gross
        federal_wh = 0.076 * gross
        vt_wh = 0.03 * gross
        vt_cc_ee = 0.001 * gross

        net = gross - (soc_sec_ee + med_ee + federal_wh + vt_wh + vt_cc_ee)

        all_earnings = [round(hours,2), round(net,2), round(gross,2)]

        return all_earnings
    
    hours_total = calcTotalHours(timeclock)

    user_input = input("Clock In(in), Clock Out(out), Info(info), Search(search) Pay(pay)") if device == "computer" else (sys.argv[1] if len(sys.argv) > 1 else 'info')
    # user_input = "search"   # debug
    
    if user_input == 'in':
        message = "Welcome to work, partner 😏"

        if today not in timeclock:  # if today not in timeclock

            # check for yesterday
            try:
                hasYesterday = pd.isna(orig[orig['date'] == yesterday]['clocked_in']).item
                if hasYesterday:
                    if not pd.isna(orig[orig['date'] == yesterday]['clocked_out']).item():
                        clockIn(path, weekdays[this_day.weekday()], this_hour, this_min, message)
                    else:
                        message = "You haven't clocked out from yesterday's shift yet"
                        printOrNotify(message)
            except ValueError:  # no clock in for yesterday
                clockIn(path, weekdays[this_day.weekday()], this_hour, this_min, message)

        else:   # today IS in timeclock
            message = "You've already clocked in once today"
            printOrNotify(message)
    elif user_input == 'out':
        message = "Good work today, get some rest"

        # print("Today is: " + today + "\nYesterday was: " + yesterday)    # debug

        if yesterday in timeclock and pd.isna(orig[orig['date'] == yesterday]['clocked_out']).item():
            clockOut(path, this_hour, this_min, message)
        elif today in timeclock:
            df = orig[orig['date'] == today]
            if pd.isna(df['clocked_out']).item():
                clockOut(path, this_hour, this_min, message)
            else:
                message = "You've already clocked out for today's shift"
                printOrNotify(message)
        else:
            message = "You haven't clocked in yet today"
            printOrNotify(message)
    elif user_input == 'info':
        # return hours of today's shift
        hours_today = calcDayHours(timeclock[today]) if today in timeclock else 0

        # return hours of latest week
        hours_this_week = calcWeekHours(weeks[len(weeks) - 1])
        
        delim = '\t'

        message = "Today: " + str(hours_today) + delim + "Week: " + str(hours_this_week) + delim + "Total: " + str(hours_total)
        printOrNotify(message)
    elif user_input == 'search':
        search_for = input("date, week, or total: ") if device == "computer" else sys.argv[2]
        # search_for = "week"   # debug
        if search_for == 'date':
            day = input("Enter date (mm/dd): ").split('/') if device == "computer" else sys.argv[3].split('/')
            searching = day[0] + '/' + (day[1] if int(day[1]) >= 10 else '0' + str(int(day[1])))

            try:
                hours = calcDayHours(timeclock[searching])
                message = "This was a " + str(hours) + " hour shift"
            except KeyError:
                hours = 0
                message = "Shift not found"
            finally:
                printOrNotify(message)

        elif search_for == 'week':
            searching = int(input("Week # (1-" + str(len(weeks)) + "): ")) if device == "computer" else int(sys.argv[3])
            # print(searching)    # debug

            if searching > 0:
                try:
                    hours = calcWeekHours(weeks[searching - 1])     # match week to array index
                    message = "\nYou worked " + str(hours) + " hours for the selected week"
                except IndexError:
                    hours = 0
                    message = "Invalid week number. Please try again."
            else:
                message = "You're not serious.."

            printOrNotify(message)

        elif search_for == 'total':
            hours = calcTotalHours(timeclock)
            remHours = round(neededHours - hours, 2)
            remDays = round(remHours / 8, 2)

            message = str(hours) + "/" + str(neededHours) + "\nHours Rem: " + str(remHours) + "\nDays Rem: " + str(remDays)
            printOrNotify(message)
    elif user_input == 'pay':
        week = int(input("Week #: ")) if device == "computer" else int(sys.argv[2])
        hourly = float(input("Hourly pay: ")) if device == "computer" else float(sys.argv[3])

        message = "Hours: " + str(calcWeekPay(weeks[week-1], hourly)[0]) + "\tNet: " + str(calcWeekPay(weeks[week-1], hourly)[1]) + "\tGross: " + str(calcWeekPay(weeks[week-1], hourly)[2])
        printOrNotify(message)
