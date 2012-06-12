# Create your views here.
"""
Extra handlers and generic functions mostly used to switch the way months and dates are displayed and worked out.
Also contains a NON template tag version of the humantime template filter.
"""
def month_display(month):
	months={
		"jan": "January",
		"feb": "February",
		"mar": "March",
		"apr": "April",
		"may": "May",
		"jun": "June",
		"jul": "July",
		"aug": "August",
		"sep": "September",
		"oct": "October",
		"nov": "November",
		"dec": "December",
	}

	return months[month]

def quarters(quarter):
	quarterlist={
		"1": ["jan", "feb", "mar"],
		"2": ["apr", "may", "jun"],
		"3": ["jul", "aug", "sep"],
		"4": ["oct", "nov", "dec"],
	}

	return months[month]

def month_number(month):
	months={
		"jan": '01',
		"feb": '02',
		"mar": '03',
		"apr": '04',
		"may": '05',
		"jun": '06',
		"jul": '07',
		"aug": '08',
		"sep": '09',
		"oct": '10',
		"nov": '11',
		"dec": '12',
	}

	return months[month]

def number_month(month):
	months={
		"1": 'jan',
		"2": 'feb',
		"3": 'mar',
		"4": 'apr',
		"5": 'may',
		"6": 'jun',
		"7": 'jul',
		"8": 'aug',
		"9": 'sep',
		"10": 'oct',
		"11": 'nov',
		"12": 'dec',
	}
	month = str(month)
	return months[month]

def month_list():
	months = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
	return months

def humantime(value):
	if value is None:
	    return ''
	if not type(value)==int:
	    return ''
	value = int(value)
	if value > 0:
	    hours = value / 60
	    minutes = value - (hours*60)

	    return "%i:%02i" % (hours, minutes)
	else:
	    return