import sys
import os
import heapq
import argparse
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from transactions_manager import TransactionsManager
from mutual_information_manager import MutualInformationManager
from parse_patterns import parse_author_file_into_patterns, parse_sequential_title_file_into_patterns
from cosine_similarity import compute_cosine_similarity

class StrongestContextIndicatorExtractor:
    # From: https://stackoverflow.com/questions/2501457/what-do-i-use-for-a-max-heap-implementation-in-python
    class ContextIndicatorHeapEntry(object):
        '''
        Pattern index object used to implement a maxheap. Stores the cosine similarity, which is used
        for comparisions and the pattern index, which keeps track of which transaction the mutual information
        belongs to
        '''
        def __init__(self, id, sim):
            self.id = id
            self.sim = sim

        def __lt__(self, other):
            return self.sim > other.sim

        def __eq__(self, other):
            return self.sim == other.sim

    def __init__(self, mutual_info_manager, transaction_manager, patterns, pattern_type):
        '''
        @param
            transaction_mananger: TransactionsManager       Object storing all transactions (every line from data.csv)
            mutual_info_manager: MutualInformationManager   Object storing a set of all author-author mutual information vals
            patterns: list(list(int))                       List of all SSP patterns
            pattern_type: PatternType                       Type of pattern pairs to compute MI for
        '''
        self.__transaction_manager = transaction_manager
        self.__mutual_info_manager = mutual_info_manager
        self.__patterns = patterns
        assert pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR \
            or pattern_type == MutualInformationManager.PatternType.TITLE_TITLE
        self.__pattern_type = pattern_type

    def find_strongest_context_indicators(self, pattern_id, k):
        '''
        @param pattern_id int:
            id for which we are trying to find the strongest context indicators for
        @param k int:
            number of strongest context indicators to find
        @return list(int):
            k strongest context indicators, sorted in descending strength (measured by mutual information)
        '''
        mutual_info_vector = self.__mutual_info_manager.get_mutual_information_vector(pattern_id, len(self.__patterns))
        strongest_context_indicators = []
        for id in range(len(mutual_info_vector)):
            heapq.heappush(strongest_context_indicators, StrongestContextIndicatorExtractor.ContextIndicatorHeapEntry(id, mutual_info_vector[id]))

        ids = []
        for index in range(k):
            top_entry_id = heapq.heappop(strongest_context_indicators).id
            ids.append(top_entry_id)
        return ids

    def pretty_print(self, pattern_id, top_patterns):
        '''
        Takes in a list of pattern ids and converts them to pattern names.

        @param top_patterns list(int):
            ids of patterns to print out
        '''
        pattern = self.__patterns[pattern_id]

        if self.__pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR:
            pattern_words = [self.__transaction_manager.get_author_name(word_id) for word_id in pattern]
        elif self.__pattern_type == MutualInformationManager.PatternType.TITLE_TITLE:
            pattern_words = [self.__transaction_manager.get_title_term(word_id) for word_id in pattern]

        print("Input pattern: %s" % ' '.join(pattern_words))
        for pattern_id in top_patterns:
            top_pattern = self.__patterns[pattern_id]

            if self.__pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR:
                top_pattern_words = [self.__transaction_manager.get_author_name(word_id) for word_id in top_pattern]
            elif self.__pattern_type == MutualInformationManager.PatternType.TITLE_TITLE:
                top_pattern_words = [self.__transaction_manager.get_title_term(word_id) for word_id in top_pattern]
            print("Pattern: %s" % ' '.join(top_pattern_words))

if __name__ == '__main__':
    '''
    Usage: py strongest_context_indicator_extractor.py [target_id] [k] [is author experiment]
    '''
    target_id = int(sys.argv[1])
    k = int(sys.argv[2])
    is_auth_experiment = sys.argv[3] == "True"

    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")

    if is_auth_experiment:
        mutual_info = MutualInformationManager(MutualInformationManager.PatternType.AUTHOR_AUTHOR)
        mutual_info.read_mutual_information_from_file()

        author_patterns = parse_author_file_into_patterns("data/frequent_author_patterns.txt")
        extractor = StrongestContextIndicatorExtractor(mutual_info, transactions, author_patterns, \
            MutualInformationManager.PatternType.AUTHOR_AUTHOR)
    else:
        mutual_info = MutualInformationManager(MutualInformationManager.PatternType.TITLE_TITLE)
        mutual_info.read_mutual_information_from_file()

        title_patterns = parse_sequential_title_file_into_patterns("data/minimal_title_term_patterns.txt")
        extractor = StrongestContextIndicatorExtractor(mutual_info, transactions, title_patterns, \
            MutualInformationManager.PatternType.TITLE_TITLE)
    
    strongest_indicators = extractor.find_strongest_context_indicators(target_id, k)
    extractor.pretty_print(target_id, strongest_indicators)
