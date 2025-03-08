month=int(input("Enter birth month: "))
day=int(input("Enter birth day: "))
year=int(input("Enter birth year: "))
from sys import exit
days_in_months=(31,28,31,30,31,30,31,31,30,31,30,31)
weekdays=('Saturday','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday')
if day>days_in_months[month-1] and month!=2 and year%4!=0:
    print(f"Enter a day between 1-{days_in_months[month-1]}")
    exit()
elif day>29 and month==2:
    print("Enter a day between 1-29")
    exit()
elif year%4!=0 and month==2 and day>28:
    print("February only goes to the 28th except on Leap Years")
    exit()
elif year<1904:
    print("This calculator only works starting from 1904")
first_weekday_1904=weekday=6
weekday+=365*(year-1904)+(year-1904)//4
if year>1903:
    weekday+=int(month>2)
weekday+=sum(days_in_months[0:month-1])
weekday+=day-1
weekday%=7
print(f"Your birthday was on a {weekdays[weekday]}")
