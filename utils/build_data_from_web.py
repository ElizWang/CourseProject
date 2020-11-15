import os
from bs4 import BeautifulSoup
import urllib.request

'''
First type of URL: contains citations for all papers per year for a specific conference.
    URL formatting: https://dblp.org/db/conf/<conf-abbrev>/index.html

Second type of URL: scraped via following the "contents" hyperlink in the first type of URL.
Contains citations for all papers for a specific year for a specific conference.
    URL formatting: https://dblp.org/db/conf/<conf-abbrev>/<conf-abbrev><date>.html
'''

class DataSetBuilder:
    def __init__(self, num_events_per_conference, conference_abbrevs):
        self.__num_events_per_conference = num_events_per_conference
        self.__conference_abbrevs = conference_abbrevs

    def build_data_set(self, data_set_name):
        for conference_name in self.__conference_abbrevs:
            events = self.__get_conference_events(conference_name)
            content_urls = self.__get_content_urls(events)
            print(content_urls)

    def __get_conference_events(self, conference_name):
        CONFERENCE_BASE_URL = "https://dblp.org/db/conf/"
        CONFERENCE_INDEX_URL = "/index.html"

        conference_url = CONFERENCE_BASE_URL + conference_name + CONFERENCE_INDEX_URL
        data = urllib.request.urlopen(conference_url).read().decode("utf-8")
        # Get a list of all events for the current conference by following "cite" component
        return BeautifulSoup(data, 'html.parser').find_all('cite', {'class': 'data'})

    def __get_content_urls(self, conference_events):
        content_urls = []
        for event in conference_events[ : self.__num_events_per_conference]:
            content_urls.append(event.find_all('a', {'class': 'toc-link'}))
        return content_urls

if __name__ == "__main__":
    data_set_builder = DataSetBuilder(2, ['aciids'])
    data_set_builder.build_data_set("b")