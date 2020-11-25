import sys
import os
import heapq
import numpy as np

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from transactions_manager import TransactionsManager
from mutual_information_manager import MutualInformationManager
from parse_patterns import parse_author_file_into_patterns
from cosine_similarity import compute_cosine_similarity

class SemanticallySimilarPatternExtractor:
    class SemanticSimilarityHeapEntry(object):
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

    def __init__(self, mutual_info_manager, transaction_manager,patterns):
        '''
        @param
            transaction_mananger: TransactionsManager       Object storing all transactions (every line from data.csv)
            mutual_info_manager: MutualInformationManager   Object storing a set of all author-author mutual information vals
            patterns: list(list(int))                       List of all SSP patterns
        '''
        self.__transaction_manager = transaction_manager
        self.__mutual_info_manager = mutual_info_manager
        self.__patterns = patterns

    def find_semantically_similar_patterns(self, pattern_id, k):
        '''
        @param pattern_id int:
            id for which we are trying to find semantically similar patterns for
        @param k int:
            number of semantically similar patterns to find
        @return list(int):
            k most semantically similar patterns, sorted in decreasing similarity
        '''
        pattern_id_mutual_info_vector = self.__mutual_info_manager.get_mutual_information_vector(pattern_id, len(self.__patterns))
        strongest_context_indicators = []
        for idx in range(len(pattern_id_mutual_info_vector)):
            idx_mutual_info_vector = self.__mutual_info_manager.get_mutual_information_vector(idx, len(self.__patterns))
            cosine_similarity = compute_cosine_similarity(pattern_id_mutual_info_vector, idx_mutual_info_vector)
            heapq.heappush(strongest_context_indicators, SemanticallySimilarPatternExtractor.SemanticSimilarityHeapEntry(idx, cosine_similarity))

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
        pattern_words = [self.__transaction_manager.get_author_name(word_id) for word_id in pattern]
        print("Input pattern: %s" % ' '.join(pattern_words))
        for pattern_id in top_patterns:
            top_pattern = self.__patterns[pattern_id]
            top_pattern_words = [self.__transaction_manager.get_author_name(word_id) for word_id in top_pattern]
            print("Pattern: %s" % ' '.join(top_pattern_words))


if __name__ == '__main__':
    '''
    Usage: py strongest_context_indicator_extractor.py [target_id] [k]
    '''
    target_id = int(sys.argv[1])
    k = int(sys.argv[2])

    mutual_info = MutualInformationManager(MutualInformationManager.PatternType.AUTHOR_AUTHOR)
    mutual_info.read_mutual_information_from_file()

    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")
    author_patterns = parse_author_file_into_patterns("data/frequent_author_patterns.txt")

    extractor =  SemanticallySimilarPatternExtractor(mutual_info, transactions, author_patterns)
    strongest_similarity = extractor.find_semantically_similar_patterns(target_id, k)
    extractor.pretty_print(target_id, strongest_similarity)
