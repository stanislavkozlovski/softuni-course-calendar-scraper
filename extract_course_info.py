'''
This module takes care of scraping the webpage and filtering out the lecture names and dates
'''
import urllib.request
import urllib.parse
from html.parser import HTMLParser
import pprint

BULGARIAN_DATE_HEX = '\\xd0\\x94\\xd0\\xb0\\xd1\\x82\\xd0\\xb0:'  # this is Дата: in hexadecimal format and is used to find the date/time of a lecture


"""
Expected array after scraping the HTML is:

[some useless stuff]
Lecture Name
bullet-points (if any)
Lecture date and time
Lecture Name
bullet-points (if any)
Lecture date and time
... and so on for each lecture until the end

What we are doing is getting all that information and saving only the lecture name and date.
We get the date just by searcing for the hex version of Дата:
We get the lecture name with get_last_element_after_date by
iterating backwards in the array of lines and finding the last element before a date line.
Naturally, this means that the first lecture does not have a date behind it and we kind of handle
that
"""

class LectureDateTimeParser(HTMLParser):
    recording = 0  # this tells us if we want to scrape the data
    data = []  # this will hold the data we've scraped
    def __init__(self):
        HTMLParser.__init__(self)
        self.lectures = 0

    def handle_starttag(self, tag, attributes):
        if tag != 'div' and tag != 'strong':
            # we dont want information from other tags"""
            return
        if self.recording:
            self.recording += 1
            return
        for name, value in attributes:
            if name == 'class' and value == 'lecture-paragraph html-raw-wrapper':
                self.lectures += 1
                break
            elif tag == 'strong':
                break
            else:
                return
        self.recording = 1

    def handle_endtag(self, tag):
        if (tag == 'div' or tag == 'strong') and self.recording:
            self.recording -= 1

    def handle_data(self, data):
        if self.recording:
            self.data.append(data)

class LectureTitleScraper(HTMLParser):
    recording = False  # this tells us if we want to scrape the data
    title = ''  # this will hold the data we've scraped

    def __init__(self):
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attributes):
        if tag == 'title':
            self.recording = True

    def handle_endtag(self, tag):
        if tag == 'title':
            self.recording = False

    def handle_data(self, data):
        if self.recording:
            self.title = data

def is_number(s):
    ''' quick method to check if a string is a number. It's used because we get some of these
    garbage(to us) values in scraping the HTML, like : '5.00' '''
    try:
        float(s)
        return True
    except ValueError:
        return False

def get_last_element_after_date(raw_data, index):
    ''' this function goes backwards in the array to find the last element that is after an element with date information
    ex: ["DATE_INFO1",
         "LECTURE",
         "WTF",
         "DATE_INFO2" <---------- if we're at here, this function will go back and get LECTURE
         We'll basically traverse back to the DATE_INFO1 and return i+1, which is LECTURE
    '''
    for i in range(index, 0, -1):
        if BULGARIAN_DATE_HEX in raw_data[i]:
            return i + 1

    # in case we haven't found a date string
    # if we're at the first lecture, we still get screwed because there's no date text before it.
    # this is quite the duct-tape approach, but we will get the last text that's before any bulgarian text
    while('\\xd' not in raw_data[index]):
        index -= 1

    return index + 1  # because the index will always be one behind, due to the fact that we end the loop with its decrementation

# TODO: Delete last date for retake exam, by converitng to datetime and seeing if there is more than 30 days apart

def convert_byte_to_string(i):
    """
    this function tests if the bytes are valid and can be converted to utf-8.
    If they can't be, we handle the error by adding an extra byte to the position that it can't find another one.
    In case of multiple errors, we use recursion to handle them all until there are no more

    Finally, after handling all the errors, we convert it to a string successfully and return it
    :param i: type: bytes
    """
    try:
        decoded_string = str(i, 'utf-8')
        return decoded_string
    except UnicodeDecodeError as e:
        # get the position of the error
        if e.reason == 'invalid start byte':
            start_pos = e.args[-3]
            end_pos = e.args[-2]
            i = i[0:start_pos] + i[end_pos:]
        elif e.reason == 'invalid continuation byte':
            print(e.reason)
            bad_position = e.args[-2]
            i = i[0:bad_position] + b'\xa0' + i[bad_position:]
        return convert_byte_to_string(i)

def decode_data(raw_data):
    '''
    This function iterates through the array and decodes all the escaped latin1 characters
    Example:
    input = ['\\xd0\\xb8\\xd0\\xb7\\xd0\\xbf\\xd0\\xb8\\xd1\\x82']
    returns: ['изпит']
    :param array: an array with the encoded/escaped characters as string
    :return: an array with the decoded strings
    '''
    decoded_lectures = []
    for i in raw_data:
        # convert it to bytes, remove the unicode escapes and encode it back into latin1
        i = bytes(i, 'latin1').decode('unicode_escape').encode('latin1')

        decoded_lectures.append(convert_byte_to_string(i))

    return decoded_lectures


regex_pattern = r'.*?softuni.bg\/trainings\/\d+?\/(.+?)-(january|february|march|april|may|june|july|august|september|october|november|decemder)-\d{4}'

with urllib.request.urlopen('https://softuni.bg/trainings/1425/web-fundamentals-html-css-august-2016') as response:
    html_file = str(response.read())
    lparser = LectureDateTimeParser()
    lparser.feed(html_file)

    raw_data = lparser.data  # this hold the somewhat filtered data from the HTML file
    lectures_data_raw = []  # this will hold the data for lecture/time but it will have some values that are not lectures
    lectures_count = lparser.lectures  # this is the count of the lectures

    for i in range(1, len(raw_data)):
        if BULGARIAN_DATE_HEX not in raw_data[i]:
            if i+1 < len(raw_data):  # check to not go beyond the range of the array
                if BULGARIAN_DATE_HEX in raw_data[i+1]:
                    """ Only gets values from raw_data that are TEXT[i] followed by A DATE TEXT[i+1]"""

                    lecture_index = get_last_element_after_date(raw_data, i)
                    lecture = raw_data[lecture_index]
                    time = raw_data[i + 1]  # i+1 is always a date, otherwise we wouldn't get in this if

                    if is_number(lecture):  # if the lecture is only something like 5.00, it's invalid and there's no reason to continue
                        continue

                    lectures_data_raw.append(lecture)
                    lectures_data_raw.append(time)
'''
because we do not have any empty values at the end of the array and the only empty values we have are at the start before the lectures start
appearing, we can just get the last [LECTURES_COUNT]*2 elements from the array.
It's multiplied by two, because each lecture is followed by a string containing the date and time of the lecture'''

raw_data = lectures_data_raw[-lectures_count * 2:]

# TODO: add the course name to each lecture name using regex most likely
lectures_data = decode_data(raw_data)

# TODO: If the lecture name can't be parsed properly, say Unknown
pprint.pprint(lectures_data)
print(lectures_count)
print(len(raw_data))
