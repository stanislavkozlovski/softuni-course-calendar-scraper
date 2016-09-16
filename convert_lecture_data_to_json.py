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
import datetime
import math
import re


SOFTUNI_ADDRESS = 'Software University, Sofia'
SOFIA_TIMEZONE = 'Europe/Sofia'
BULGARIAN_MONTHS = {'януари': 1, 'февруари': 2, 'март': 3, 'април': 4, 'май': 5, 'юни': 6, 'юли': 7, 'август': 8, 'септември': 9, 'октомври': 10, 'ноември': 11, 'декември': 12}

def convert_lectures(lectures: list):
    return list(map(lambda x: convert_lecture_to_json(x), lectures))

def convert_lecture_to_json(lecture):
    ''' creates the JSON object '''
    lecture_name = lecture[0]
    lecture_start_date, lecture_end_date = convert_date_to_iso8601(lecture[1])

    event = {
        'summary': lecture_name,
        'location': SOFTUNI_ADDRESS,
        'start': {
            'dateTime': lecture_start_date,
            'timeZone': SOFIA_TIMEZONE
        },
        'end': {
            'dateTime': lecture_end_date,
            'timeZone': SOFIA_TIMEZONE
        }
    }

    return event

def convert_date_to_iso8601(date) -> tuple:
    """ converts the date to a string object with the iso8601 format, which we give to the google API as a string"""
    ''' if there are two dates, like for a retake exam, only the first one will be taken'''
    date_pattern = r'Дата:\s+(\d{1,2}).*?(януари|февруари|март|април|май|юни|юли|август|септември|октомври|ноември|декември).+?(\d{1,2}(:|;)\d{1,2}).+?(\d{1,2}(:|;)\d{1,2})'
    match = re.match(date_pattern, date)

    date_day = match.group(1).zfill(2)  # 04

    date_month = BULGARIAN_MONTHS[match.group(2)] # Октомври -> !0  type: str

    date_year = str(datetime.datetime.now().year)
    # there are typos in some lectures where it's 18;30 instead of 18:30
    start_time = (match.group(3) + ':00').replace(';', ':')  # 18:30:00
    end_time = (match.group(5) + ':00').replace(';', ':') # 22:00:00

    utc_offset = get_utc_offset()  # type: str

    start_date = '{year}-{month}-{day}T{time}{utc_offset}'.format(year=date_year, month=date_month, day=date_day,
                                                            time=start_time, utc_offset=utc_offset)
    end_date = '{year}-{month}-{day}T{time}{utc_offset}'.format(year=date_year, month=date_month, day=date_day,
                                                            time=end_time, utc_offset=utc_offset)

    return (start_date, end_date)

def get_utc_offset() -> str:
    '''
    function gets the difference between our timezones in hours and returns a string that will be put into the iso8601 format
    if we're 3 hours ahead, we will return +03:00
    if we're 3 hours behind, we will return -03:00
    :return:
    '''
    now = datetime.datetime.now()
    local_hour = now.hour
    utc_hour = now.utcnow().hour
    utc_offset = local_hour - utc_hour

    str_preamble = '+' if utc_offset >= 0 else '-'

    # convert the fraction and the whole to a string. Works for ints and floats
    fraction, whole = math.modf(utc_offset)
    fraction = str(fraction)[2:].zfill(2)  # from 0.5 get 05 only
    whole = str(int(whole)).zfill(2)

    return '{preamble}{whole}:{fraction}'.format(preamble=str_preamble, whole=whole, fraction=fraction)
