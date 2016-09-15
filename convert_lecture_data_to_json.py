'''
here we convert the data from the list of tuples into a json string that will be given to google's calendar API
a sample of how it should look like:
 event = {
        'summary': "JS Intro",
        'location': 'ул Тинтява 15-7, етаж 2, 1113 Sofia, Bulgaria',
        'start': {
            'dateTime': '2016-09-15T07:00:00+03:00',
            'timeZone': 'Europe/Sofia',
        },
        'end': {
            'dateTime': '2016-09-15T08:00:00+03:00',
            'timeZone': 'Europe/Sofia',
        }
    }
'''

SOFTUNI_ADDRESS = 'ул. Тинтява 15-17, етаж 2, 1113 Sofia, Bulgaria'

def convert_lectures(lectures: list):
    return list(map(lambda x: convert_lecture_to_json(x), lectures))

def convert_lecture_to_json(lecture):
    lecture_name = lecture[0]
    lecture_date = lecture[1]
    pass

def convert_date_to_iso8601(date):
    regex_pattern = r'Дата:\s+(\d{1,2}).*(януари|февруари|март|април|май|юни|юли|август|септември|октомври|ноември|декември).+?(\d{1,2}:\d{1,2}).+?(\d{1,2}:\d{1,2})'
    import re
    match = re.match(regex_pattern, date)

    date_day = match.group(2)  # 4
    date_month = convert_bulgarian_month_to_number(match.group(3))  # Октомври -> !0  type: int
    start_time = match.group(4)  # 18:30
    end_time = match.group(5)  # 22:00
    pass

def convert_bulgarian_month_to_number(month):
    '''
    this function converts a bulgarian month string into the number of the corresponding month
    October in bulgarian is Октомври, which will return the number 10
    :param month: a string in bulgarian, containing the month
    :return: int, the month's number
    '''
    month_number = 0

    if month == 'януари':
        month_number = 1
    elif month == 'февруари':
        month_number = 2
    elif month == 'март':
        month_number = 3
    elif month == 'април':
        month_number = 4
    elif month == 'май':
        month_number = 5
    elif month == 'юни':
        month_number = 6
    elif month == 'юли':
        month_number = 7
    elif month == 'август':
        month_number = 8
    elif month == 'септември':
        month_number = 9
    elif month == 'октомври':
        month_number = 10
    elif month == 'ноември':
        month_number = 11
    elif month == 'декември':
        month_number = 12

    if not month_number:
        raise Exception

    return month_number