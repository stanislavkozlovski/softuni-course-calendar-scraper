'''
This module takes care of scraping the webpage and filtering out the lecture names and dates
'''
import re
import urllib.request
import urllib.parse
from scrapers import CourseTitleScraper, LectureNameandDateScraper

BULGARIAN_DATE_HEX = '\\xd0\\x94\\xd0\\xb0\\xd1\\x82\\xd0\\xb0:'  # this is Дата: in hexadecimal format and is used to find the date/time of a lecture


def extract_course_info(url: str) -> list:
    with urllib.request.urlopen(url) as response:
        html_file = str(response.read())

    lparser = LectureNameandDateScraper()
    lparser.feed(html_file)
    raw_data = lparser.data  # this holds the somewhat filtered data from the HTML file
    lectures_count = lparser.lectures  # this is the count of the lectures

    # get the course title
    course_title = extract_course_title(html_file)

    # this will hold the data for lecture/time
    lectures_data_raw = extract_lecture_data(raw_data, lectures_count)  # type: list
    lectures_data = polish_lecture_data(lectures_data_raw, course_title)

    return lectures_data

def polish_lecture_data(lectures_data: list, course_title: str) -> list:
    ''' polish the lecture data by decoding it, grouping it, removing invalid names and etc'''
    # decode the data into utf-8
    lectures_data = decode_data(lectures_data)
    # covert the list into a list of tuples (Lecture name, Lecture Date)
    lectures_data = group_lectures(lectures_data)
    # combine lectures with identical dates
    lectures_data = combine_identical_lectures(lectures_data)
    # remove invalid lecture names
    lectures_data = remove_invalid_lecture_names(lectures_data)
    # add the course title in front of every lecture name
    lectures_data = add_course_title_to_lectures(lectures_data, course_title)

    return lectures_data

def extract_lecture_data(raw_data, lectures_count):
    """
           Expected array after scraping the HTML is:

           [a lot of useless stuff]
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
    raw_lecture_data = []
    for i in range(1, len(raw_data)):
        if BULGARIAN_DATE_HEX not in raw_data[i]:
            if i + 1 < len(raw_data):  # check to not go beyond the range of the array
                if BULGARIAN_DATE_HEX in raw_data[i + 1]:
                    """ Only gets values from raw_data that are TEXT[i] followed by A DATE TEXT[i+1]"""
                    lecture_index = get_last_element_after_date(raw_data, i)

                    lecture = raw_data[lecture_index]
                    time = raw_data[i + 1]  # i+1 is always a date

                    if is_number(lecture):
                        # if the lecture is only something like 5.00, it's invalid and there's no reason to append it
                        continue

                    raw_lecture_data.append(lecture)
                    raw_lecture_data.append(time)

    '''
        because we do not have any empty values at the end of the array and the only empty values we have are at the start before the lectures start
        appearing, we can just get the last [LECTURES_COUNT]*2 elements from the array.
        It's multiplied by two, because each lecture is followed by a string containing the date and time of the lecture'''
    return raw_lecture_data[-lectures_count * 2:]


def extract_course_title(html):
    ''' returns the title of the course'''
    course_title_scraper = CourseTitleScraper()
    course_title_scraper.feed(html)
    course_title = decode_data([course_title_scraper.title])[0]  # decode it into utf-8
    course_title = filter_course_title(course_title)  # filter the course title

    return course_title

def group_lectures(lectures: list):
    """ this function groups the expected list's contents into tuples of (lecture_name,lecture_date)
    expected input: ['Data Definition and Datatypes',
                    'Дата: 26-ти септември, 18:00 - 22:00']

    output: [('Data Definition and Datatypes', 'Дата: 26-ти септември, 18:00 - 22:00')]
    """
    if len(lectures) % 2 != 0:
        raise Exception
    else:
        lectures = [(lectures[x], lectures[x+1]) for x in range(0, len(lectures), 2)]
    return lectures


def combine_identical_lectures(lectures: list):
    """
    this function combines lectures that have the absolute same date into one lecture
    """
    combined_lectures = []
    for idx, tupl in enumerate(lectures):
        if tupl:
            lecture_name = tupl[0]
            lecture_date = tupl[1]

            # search for the same date
            for search_idx in range(idx+1, len(lectures)):
                if lectures[search_idx][1] == lecture_date:
                    # combine the two names into one
                    lecture_name += '; {other_lecture}'.format(other_lecture=lectures[search_idx][0])
                    # if we find it, convert it to none
                    lectures[search_idx] = None
            combined_lectures.append((lecture_name, lecture_date))

    return combined_lectures


def remove_invalid_lecture_names(lectures: list):
    ''' this function goes through the array and replaces an invalid lecture name with Unknown
        Currently, we know that in some courses, the program puts the lecture name the same as the date,
        this function is specifically done to combat that. Further testing will hopefully find out more
        cases in which the lecture names might be invalid'''
    return [(lecture_name if 'Дата:' not in lecture_name else "Unknown", lecture_date) for lecture_name, lecture_date in lectures]


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

        decoded_lectures.append(convert_byte_to_string(i).strip())

    return decoded_lectures


def filter_course_title(title:str):
    """ This function strips the course title from unecessary information
        example, given: Express.js Development - октомври 2016 - Софтуерен университет
        we return: Express.js Development
    """

    regex_pattern = r'(.+?)(\s|\s-\s)(януари|февруари|март|април|май|юни|юли|август|септември|октомври|ноември|декември).+'
    modified_title = re.match(regex_pattern, title).group(1)

    return modified_title


def add_course_title_to_lectures(lectures_data: list, course_title: str):
    """ This function goes through the list with data from lectures and adds
    the course name in front of each lecture name"""

    return [("{title} - {lname}".format(title=course_title, lname=lecture_name), lec_date) for lecture_name, lec_date in lectures_data]

