
import datetime
from calendar import weekday, Calendar, month_name, month_abbr, day_name, day_abbr
from math import floor, ceil, fabs
from .. import errors
from ..subtypes import date, integer, string, double, boolean, empty
from ..subtypes.date import encode_date, encode_time, decode_date


default_system_first_day_of_week=2 # Monday
default_system_first_week_of_year=2 # FirstFourDays


def get_week_count(firstdayofweek, firstweekofyear, year, month, day):
	cl = Calendar(firstdayofweek)
	data = cl.monthdayscalendar(year, 1)
	week_cnt = 0
	day_cnt = 0
	# counting for first month
	for i in range(0, 7):
		if data[0][i] != 0:
			day_cnt += 1
	if (firstweekofyear == 2 and day_cnt < 4) or (firstweekofyear == 3 and day_cnt < 7):
		week_cnt = -1
	if month != 1:
		week_cnt += len(data)
		if data[len(data)-1][6] == 0:
			week_cnt -= 1
		#counting for other monthes
		for m in range(2, month):
			data = cl.monthdayscalendar(year, m)
			week_cnt += len(data)
			if data[len(data)-1][6] == 0:
				week_cnt -= 1
	#here we have week count in week_cnt before current month
	data = cl.monthdayscalendar(year, month)
	for week in range(0, len(data)):
		week_cnt += 1
		if day in data[week]:
			break
	return week_cnt

def is_leap_year(year):
	return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def max_dayin_month(year, month):
	if month in (4, 6, 9, 11):
		return 30
	elif month==2 and is_leap_year(year):
		return 29
	elif month==2:
		return 28
	else:
		return 31

def inc_month(year, month, day, cnt):
	""" Increments/Decrements month on cnt, adjusting date correspondingly """
	month += cnt
	if month > 12 or month < 0:
		year += month // 12
		month = month % 12
	elif month == 0:
		year -= 1
		month = 12
	return year, month, min(day, max_dayin_month(year, month))

def inc_day(year, month, day, cnt):
	""" Increments/Decrements day on cnt, adjusting date correspondingly """
	day += cnt
	ymMax = max_dayin_month(year, month)
	while not day in range(1, ymMax+1):
		if day > 0:
			day -= ymMax
			month += 1
			if month > 12:
				year += 1
				month = 1
		elif day < 0:
			day += ymMax
			month -= 1
			if month < 1:
				year -= 1
				month = 12
		else:
			month -= 1
			if month < 1:
				year -= 1
				month = 12
			day = max_dayin_month(year, month)
		ymMax = max_dayin_month(year, month)
	return year, month, day

def inc_hour(year, month, day, hour, cnt):
	""" Increments/Decrements hour on cnt, adjusting date correspondingly """
	hour += cnt
	if not hour in range(1, 25):
		daydiff, hour = hour // 24, hour % 24
		year, month, day = inc_day(year, month, day, daydiff)
	return year, month, day, hour

def inc_minute(year, month, day, hour, minute, cnt):
	""" Increments/Decrements minute on cnt, adjusting date and time correspondingly """
	minute += cnt
	if not minute in range(1, 61):
		hourdiff, minute = minute // 60, minute % 60
		year, month, day, hour = inc_hour(year, month, day, hour, hourdiff)
	return year, month, day, hour, minute

def inc_second(year, month, day, hour, minute, second, cnt):
	""" Increments/Decrements second on cnt, adjusting date and time correspondingly """
	second += cnt
	if not second in range(1, 61):
		mindiff, second = second // 60, second % 60
		year, month, day, hour, minute = inc_minute(year, month, day, hour, minute, mindiff)
	return year, month, day, hour, minute, second


def v_date():
	return date(datetime.datetime.today().toordinal()-693594)

def v_time():
	value=datetime.datetime.today()
	return date(encode_time(value.hour, value.minute, value.second))

def v_now():
	value=datetime.datetime.today()
	return date(encode_date(value.year, value.month, value.day,
		value.hour, value.minute, value.second))


def v_timer():
	value=datetime.datetime.today()
	return integer(value.hour*3600+value.minute*60+value.second)


def v_dateserial(year, month, day):
	year, month, day=year.as_integer, month.as_integer, day.as_integer
	if year<0 or year>9999: raise errors.invalid_procedure_call(name=u"dateserial")
	if year<100: year+=1900 # TODO: Update to close support modern years
	if month<1 or month>12: year, month, day=inc_month(year, month, 1, 0)
	if day<1 or day>max_dayin_month(year, month): year, month, day=inc_day(year, month, day, 0)
	return date(encode_date(year, month, day))

def v_timeserial(hour, minute, second):
	hour, minute, second=hour.as_integer, minute.as_integer, second.as_integer
	if hour<0 or hour>23: raise errors.invalid_procedure_call(name=u"timeserial")
	if minute<0 or minute>59: raise errors.invalid_procedure_call(name=u"timeserial")
	if second<0 or second>59: raise errors.invalid_procedure_call(name=u"timeserial")
	return date(encode_time(hour, minute, second))

def v_datevalue(value):
	return date(value.as_string)

def v_timevalue(value):
	return date(value.as_string)

def v_datepart(interval, value, firstdayofweek=None, firstweekofyear=None):
	interval, value=interval.as_string, value.as_date
	firstdayofweek=1 if firstdayofweek is None else firstdayofweek.as_integer
	firstweekofyear=1 if firstweekofyear is None else firstweekofyear.as_integer
	year, month, day, hour, minute, second=decode_date(value)
	if firstdayofweek==0:
		firstdayofweek=default_system_first_day_of_week
	if firstdayofweek<1 or firstdayofweek>7:
		raise errors.invalid_procedure_call(name=u"datepart")
	if firstweekofyear==0:
		firstweekofyear=default_system_first_week_of_year
	if firstweekofyear<1 or firstweekofyear>3:
		raise errors.invalid_procedure_call(name=u"datepart")
	if interval==u"yyyy":
		return integer(year)
	elif interval==u"q":
		return integer((month-1)//3+1)
	elif interval==u"m":
		return integer(month)
	elif interval==u"y":
		return integer(day+sum(max_dayin_month(year, i) for i in range(1, month)))
	elif interval==u"d":
		return integer(day)
	elif interval==u"w":
		value=weekday(year, month, day)+3-firstdayofweek
		return integer(value+7 if value<1 else value-7 if value>7 else value)
	elif interval==u"ww":
		value=firstdayofweek-2
		value=6 if value==-1 else value
		count=get_week_count(value, firstweekofyear, year, month, day)
		if count==0: count=get_week_count(wd, firstweekofyear, year-1, 12, 31)
		return integer(count)
	elif interval==u"h":
		return integer(hour)
	elif interval==u"n":
		return integer(minute)
	elif interval==u"s":
		return integer(second)
	else:
		raise errors.invalid_procedure_call(name=u"datepart")

def v_year(value):
	return integer(decode_date(value.as_date)[0])

def v_month(value):
	return integer(decode_date(value.as_date)[1])

def v_day(value):
	return integer(decode_date(value.as_date)[2])

def v_weekday(value, firstdayofweek=None):
	value=value.as_date
	firstdayofweek=1 if firstdayofweek is None else firstdayofweek.as_integer
	if firstdayofweek<1 or firstdayofweek>7:
		raise errors.invalid_procedure_call(name=u"weekday")
	year, month, day, hour, minute, second=decode_date(value)
	result=datetime.date(year, month, day).weekday()+2
	if result==8: result=1
	result-=firstdayofweek-1
	if result<0: result+=7
	return integer(result)

def v_hour(value):
	return integer(decode_date(value.as_date)[3])

def v_minute(value):
	return integer(decode_date(value.as_date)[4])

def v_second(value):
	return integer(decode_date(value.as_date)[5])


def v_dateadd(interval, number, value):
	interval, number, value=interval.as_string, number.as_integer, value.as_date
	year, month, day, hour, minute, second=decode_date(value)
	dt_value=datetime.datetime(year, month, day, hour, minute, second)
	if interval==u"yyyy":
		year+=number
		day=min(max_dayin_month(year, month), day)
	elif interval==u"q":
		year, month, day=inc_month(year, month, day, number*3)
	elif interval==u"m":
		year, month, day=inc_month(year, month, day, number)
	elif interval==u"y":
		year, month, day=inc_day(year, month, day, number)
	elif interval==u"d":
		year, month, day=inc_day(year, month, day, number)
	elif interval==u"w":
		year, month, day=inc_day(year, month, day, number)
	elif interval==u"ww":
		year, month, day=inc_day(year, month, day, number*7)
	elif interval==u"h":
		year, month, day, hour=inc_hour(year, month, day, hour, number)
	elif interval==u"n":
		year, month, day, hour, minute=inc_minute(year, month, day, hour, minute, number)
	elif interval==u"s":
		year, month, day, hour, minute, second=inc_second(year, month, day, hour, minute, second, number)
	else:
		raise errors.invalid_procedure_call(name=u"dateadd")
	return date(encode_date(year, month, day, hour, minute, second))

def v_datediff(interval, value1, value2, firstdayofweek=None, firstweekofyear=None):
	# TODO: Author didnt understand the use of "firstweekofyear" parameter
	interval=interval.as_string
	value1, value2=value1.as_date, value2.as_date
	firstdayofweek=1 if firstdayofweek is None else firstdayofweek.as_integer
	firstweekofyear=1 if firstweekofyear is None else firstweekofyear.as_integer
	year1, month1, day1, hour1, minute1, second1=decode_date(value1)
	year2, month2, day2, hour2, minute2, second2=decode_date(value2)
	sign=1 if value1<value2 else -1
	if firstdayofweek<1 or firstdayofweek>7:
		raise errors.invalid_procedure_call(name=u"datediff")
	if interval==u"yyyy":
		return integer(year2-year1)
	elif interval==u"q":
		q1=(month1-1)//3+1 # Getting quarter of first date
		q2=(month2-1)//3+1 # Getting quarter of second date
		return integer(q2-q1+(year2-year1)*4)
	elif interval==u"m":
		return integer(month2-month1+(year2-year1)*12)
	elif interval==u"y":
		return integer(int(value2)-int(value1))
	elif interval==u"d":
		return integer(int(value2)-int(value1))
	elif interval==u"w":
		return integer(fabs(int(value2)-int(value1))//7*sign)
	elif interval==u"ww":
		delta=sign*(weekday(year1, month1, day1)-weekday(year2, month2, day2))
		return integer((fabs(int(value2)-int(value1))//7+1 if delta>0 else 0)*sign)
	elif interval==u"h":
		s2=1 if value2>=0 else -1
		s1=1 if value1>=0 else -1
		d2=fabs(value2*86400)//3600*s2
		d1=fabs(value1*86400)//3600*s1
		return integer(d2-d1)
	elif interval==u"n":
		s2=1 if value2>=0 else -1
		s1=1 if value1>=0 else -1
		d2=fabs(value2*86400)//60*s2
		d1=fabs(value1*86400)//60*s1
		return integer(d2-d1)
	elif interval==u"s":
		return integer(int((value2-value1)*86400))
	else:
		raise errors.invalid_procedure_call(name=u"datediff")


def v_monthname(month, abbreviate=None):
	month=month.as_integer
	abbreviate=False if abbreviate is None else abbreviate.as_boolean
	if month<1 or month>12: raise errors.invalid_procedure_call(name=u"monthname")
	return string(month_abbr[month]) if abbreviate else string(month_name[month])

def v_weekdayname(weekday, abbreviate=None, firstdayofweek=None):
	weekday=weekday.as_integer
	firstdayofweek=1 if firstdayofweek is None else firstdayofweek.as_integer
	abbreviate=False if abbreviate is None else abbreviate.as_boolean
	if firstdayofweek<1 or firstdayofweek>7:
		raise errors.invalid_procedure_call(name=u"weekday")
	result=weekday+firstdayofweek-1
	result=result-7 if result>7 else result
	result-=2
	result=6 if result==-1 else result
	return string(day_abbr[result]) if abbreviate else string(day_name[result])
