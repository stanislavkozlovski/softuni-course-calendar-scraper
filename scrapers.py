from html.parser import HTMLParser

class LectureNameandDateScraper(HTMLParser):
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

class CourseTitleScraper(HTMLParser):
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
