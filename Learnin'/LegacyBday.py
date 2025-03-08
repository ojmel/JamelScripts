month=int(input("Enter birth month: "))
day=int(input("Enter birth day: "))
year=int(input("Enter birth year: "))
import sys
if day>31:
    print("Enter a day between 1-31")
    sys.exit()
elif day>29 and month==2:
    print("Enter a day between 1-29")
    sys.exit()
elif year%4!=0 and month==2 and day>28:
    print("February only goes to the 28th except on Leap Years")
    sys.exit()
elif month==4 and day>30 or month==6 and day>30 or month==9 and day>30 or month==11 and day>30:
    print("This month only goes to the 30th")
    sys.exit()
elif year<1904:
    print("This calculator only works starting from 1904")
elif year%4==0 and month==1 or year%4==0 and month==4 or year%4==0 and month==7:
    shift_year=((year-1904)+(year-1904)/4)%7
    weekday=(day-1+6+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif year%4==0 and month==2 or year%4==0 and month==8:
    shift_year=((year-1904)+(year-1904)/4)%7
    weekday=(day-1+2+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif year%4==0 and month==3 or year%4==0 and month==11:
    shift_year=((year-1904)+(year-1904)/4)%7
    weekday=(day-1+2+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif year%4==0 and month==6:
    shift_year=((year-1904)+(year-1904)/4)%7
    weekday=(day-1+4+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif year%4==0 and month==9 or year%4==0 and month==12:
    shift_year=((year-1904)+(year-1904)/4)%7
    weekday=(day-1+5+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif year%4==0 and month==5:
    shift_year=((year-1904)+(year-1904)/4)%7
    weekday=(day+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif year%4==0 and month==10:
    shift_year=((year-1904)+(year-1904)/4)%7
    weekday=(day-1+7+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif month==1 or month==10:
    shift_year=((year-1905)+int((year-1905)/4))%7
    weekday=(day+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif month==5:
    shift_year=((year-1905)+int((year-1905)/4))%7
    weekday=(day-1+2+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif month==8:
    shift_year=((year-1905)+int((year-1905)/4))%7
    weekday=(day-1+3+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
        if day ==20:
            print("Oh wow what a great birthday")
elif month==2 or month==3 or month==11:
    shift_year=((year-1905)+int((year-1905)/4))%7
    weekday=(day-1+4+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif month==6:
    shift_year=((year-1905)+int((year-1905)/4))%7
    weekday=(day-1+5+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif month==9 or month==12:
    shift_year=((year-1905)+int((year-1905)/4))%7
    weekday=(day-1+6+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")
elif month==4 or month==7:
    shift_year=((year-1905)+int((year-1905)/4))%7
    weekday=(day-1+7+shift_year)%7
    if weekday==0.0:
        print("Your birthday was on a Saturday")
    elif weekday==1.0:
        print("Your birthday was on a Sunday")
    elif weekday==2.0:
        print("Your birthday was on a Monday")
    elif weekday==3.0:
        print("Your birthday was on a Tuesday")
    elif weekday==4.0:
        print("Your birthday was on a Wednesday")
    elif weekday==5.0:
        print("Your birthday was on a Thursday")
    elif weekday==6.0:
        print("Your birthday was on a Friday")