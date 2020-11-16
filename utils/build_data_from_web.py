import os
from bs4 import BeautifulSoup
import urllib.request

'''
Background:
First type of URL: contains citations for all papers per year for a specific conference.
    URL formatting: https://dblp.org/db/conf/<conf-abbrev>/index.html

Second type of URL: scraped via following the "contents" hyperlink in the first type of URL.
Contains citations for all papers for a specific year for a specific conference.
    URL formatting: https://dblp.org/db/conf/<conf-abbrev>/<conf-abbrev><date>.html
'''

class DataSetBuilder:
    '''
    Builds a CSV file where each line is a list of comma separated authors and a single title.
    In other words, each line corresponds to a single paper. Note that this file is partitioned
    based on which conferences these papers were from but the conferences aren't explicitly stated
    in the file.
    '''

    def __init__(self, data_set_name, conference_abbrevs, num_events_per_conference):
        '''
        @param data_set_name: string            name of data set file to write to
        @param conference_abbrevs: list(string) conferences to parse papers from
        @param num_events_per_conference: int   # of events to parse per conference because each 
            conference is composed of multiple events (>= 1 per year)
        '''
        self.__num_events_per_conference = num_events_per_conference
        self.__conference_abbrevs = conference_abbrevs
        self.__data_set_name = data_set_name

    def build_data_set(self):
        '''
        Driver function that builds csv-separated data file. Writes all relevant paper meta-info
        per event per conference.
        '''
        data_file = open(self.__data_set_name, "w")

        for conference_name in self.__conference_abbrevs:
            events = self.__parse_conference_events(conference_name)
            content_urls = self.__parse_content_urls(events)
            
            for content_url in content_urls:
                author_title_info = self.__parse_title_author_data(content_url)
                self.__write_data_to_csv_file(data_file, author_title_info)

        data_file.close()

    def __parse_conference_events(self, conference_name):
        '''
        Pulls HTML data from a specific conference and parses it for all events (note that 
        events are displayed as "citations")

        @param conference_name: string      name of conference to pull event data from
        @return a list of all event objects, where each event is asosciated with the inputted
            conference
        '''
        CONFERENCE_BASE_URL = "https://dblp.org/db/conf/"
        CONFERENCE_INDEX_URL = "/index.html"

        conference_url = CONFERENCE_BASE_URL + conference_name + CONFERENCE_INDEX_URL
        data = urllib.request.urlopen(conference_url).read().decode("utf-8")
        return self.__parse_citations(data)

    def __parse_content_urls(self, conference_events):
        '''
        Parses URLs containing information on the papers submitted to a set number of events
        in a given conference

        @param conference_events: list(bs4 object)      events in a conference 
        @return a list of all URL strings, where each URL refers to a page containing the
            actual title/author info (aka info on papers submitted)
        '''
        content_urls = []
        for event in conference_events[ : self.__num_events_per_conference]:
            content_urls.append(event.find('a', {'class': 'toc-link'})['href'])
        return content_urls

    def __parse_title_author_data(self, submissions_url):
        '''
        Parses title/author data from a given submissions URL. Note that there can be multiple
        authors per paper but there can only be one title / paper.

        @param submissions_url: string      URL to page containing info on papers submitted 
        @return a list of (authors, title tuples), aka list((list(string), string)). Each tuple
            represents one paper. Authors of a paper are stored in a list because there can be
            multiple authors per paper. The title is stored as a string.
        '''
        data = urllib.request.urlopen(submissions_url).read().decode("utf-8")
        citations_list = self.__parse_citations(data)

        author_title_info = []
        for citation in citations_list:
            author_spans = citation.find_all('span', {'itemprop': 'author'})
            authors = []
            for author_span in author_spans:
                authors.append(author_span.find('span', {'itemprop': 'name'})['title'])

            title = citation.find('span', {'class': 'title'}).string
            author_title_info.append( (authors, title) )
        return author_title_info

    def __write_data_to_csv_file(self, data_file, author_title_data):
        '''
        Writes author title data to a csv file, where each line corresponds to a paper
        Format:
            author1, author2, author3, ... etc, Title

        @param data_file: Fle object        File object to csv file we should write to
        @param author_title_data: list((list(string), string)   List of paper metadata, where 
            tup[0] is a list of authors of the paper and tup[1] is the paper's title. 
            @see __parse_title_author_data for more info
        '''
        for authors, title in author_title_data:
            data_file.write("%s,%s\n" % (','.join(authors), title))

    def __parse_citations(self, data):
        '''
        Parses citations from raw HTML data object

        @param data: string     Raw HTML string from either a conference URL or a submissions URL
        @return a list of bs4 objects, where each object represents a "citation" -- either the data
            for an event or the data for a single paper within an event 
        '''
         # Get a list of all events for the current conference by following "cite" component
        return BeautifulSoup(data, 'html.parser').find_all('cite', {'class': 'data'})

if __name__ == "__main__":
    data_set_builder = DataSetBuilder('data.csv', ['aciids'], 2)    
    data_set_builder.build_data_set()