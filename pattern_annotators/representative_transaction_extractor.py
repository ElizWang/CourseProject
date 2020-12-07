import heapq

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from transactions_manager import TransactionsManager
from mutual_information_manager import MutualInformationManager
from parse_patterns import parse_author_file_into_patterns, parse_sequential_title_file_into_patterns
from cosine_similarity import compute_cosine_similarity

'''
Extracts representative transactions and pretty prints them
'''
class RepresentativeTransactionExtractor:
    # From: https://stackoverflow.com/questions/2501457/what-do-i-use-for-a-max-heap-implementation-in-python
    class TransactionSimilarity(object):
        '''
        Transaction similarity object used to implement a maxheap. Stores the cosine similarity, which is used
        for comparisions and the transaction index, which keeps track of which transaction the cosine similarity
        belongs to
        '''
        def __init__(self, cosine_sim, transaction_ind):
            self.cosine_sim = cosine_sim
            self.transaction_ind = transaction_ind

        def __lt__(self, other):
            return self.cosine_sim > other.cosine_sim

        def __eq__(self, other):
            return self.cosine_sim == other.cosine_sim

    def __init__(self, transaction_mananger, mutual_info_manager, patterns, pattern_type, num_transactions):
        '''
        @param
            transaction_mananger: TransactionsManager       Object storing all transactions (every line from data.csv)
            mutual_info_manager: MutualInformationManager   Object storing a set of all author-author mutual information vals
            patterns: list(list(int))                       List of all SSP patterns
            pattern_type: PatternType                       Type of pattern pairs to compute MI for
            num_transactions: int                           Top k most representative transactions to find
        '''
        self.__transaction_manager = transaction_mananger
        self.__mutual_info_manager = mutual_info_manager

        self.__patterns = patterns
        assert pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR \
            or pattern_type == MutualInformationManager.PatternType.TITLE_TITLE
        self.__pattern_type = pattern_type

        self.__num_transactions = num_transactions

    def find_representative_transactions(self, pattern_id, k):
        '''
        Finds the top num_transactions representative transactions for each pattern inputted in the constructor

        @param pattern_id int:
            id for which we are trying to find semantically similar patterns for
        @param k int:
            number of semantically similar patterns to find
        @return list(int):
            k most semantically similar patterns, sorted in decreasing similarity
        '''
        if self.__pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR:
            paper_context_models = self.__transaction_manager.compute_author_context_models(self.__patterns)
        elif self.__pattern_type == MutualInformationManager.PatternType.TITLE_TITLE:
             paper_context_models = self.__transaction_manager.compute_title_context_models(self.__patterns)

        context_model_dim = len(self.__patterns)

        similarities_max_q = []

        # Read in the context model vector
        pattern_context_model = self.__mutual_info_manager.get_mutual_information_vector(pattern_id, context_model_dim)

        for transaction_ind, transaction_vec in enumerate(paper_context_models):
            cosine_sim = compute_cosine_similarity(pattern_context_model, transaction_vec)
            heapq.heappush(similarities_max_q, RepresentativeTransactionExtractor.TransactionSimilarity(cosine_sim, transaction_ind))

        pattern_transactions = []
        for _ in range(self.__num_transactions):
            transaction_ind = heapq.heappop(similarities_max_q).transaction_ind
            pattern_transactions.append(transaction_ind)
        return pattern_transactions

    def display_pretty(self, pattern_id, top_transactions):
        '''
        Prints the representative transactions out per pattern. All patterns and transactions are represented
        as words rather than their ids.

        @param
        top_patterns list(int):             ids of patterns to print out
        top_transactions list(int):         list of all indices (aka ids) of the papers ordered from
            most representative to least representative and of size num_transactions
        '''
        if self.__pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR:
            self.__display_pretty_authors_pattern_title_transactions(pattern_id, top_transactions)
        elif self.__pattern_type == MutualInformationManager.PatternType.TITLE_TITLE:
            self.__display_pretty_title_pattern_transactions(pattern_id, top_transactions)

    def __display_pretty_authors_pattern_title_transactions(self, pattern_id, top_transactions):
        pattern = self.__patterns[pattern_id]

        pattern_words = [self.__transaction_manager.get_author_name(word_id) for word_id in pattern]
        print("Input pattern: %s" % ' '.join(pattern_words))
        self.__display_title_terms(top_transactions)

    def __display_pretty_title_pattern_transactions(self, pattern_id, top_transactions):
        pattern = self.__patterns[pattern_id]

        pattern_words = [self.__transaction_manager.get_title_term(word_id) for word_id in pattern]
        print("Input pattern: %s" % ' '.join(pattern_words))

        self.__display_title_terms(top_transactions)

        for transaction_ind in top_transactions:
            transaction_auth_ids = self.__transaction_manager.get_paper_authors(transaction_ind)
            transaction_auth_words = [self.__transaction_manager.get_author_name(word_id) \
                for word_id in transaction_auth_ids]
            print("Most representative title transactions %d: %s" % \
                (transaction_ind, ' '.join(transaction_auth_words)))
        print()

    def __display_title_terms(self, top_transactions):
        for transaction_ind in top_transactions:
            transaction_title_ids = self.__transaction_manager.get_paper_title_terms(transaction_ind)
            transaction_title_words = [self.__transaction_manager.get_title_term(word_id) \
                for word_id in transaction_title_ids]
            print("Most representative title transactions %d: %s" % \
                (transaction_ind, ' '.join(transaction_title_words)))
        print()

if __name__ == "__main__":
    '''
    Usage: py pattern_annotators/representative_transaction_extractor.py [target_id] [k] [is author experiment]
    '''
    # We pull only the first 100 lines to speed up computation.
    MAXIMUM_LINE_COUNT = 100
    target_id = int(sys.argv[1])
    k = int(sys.argv[2])
    is_auth_experiment = sys.argv[3] == "True"

    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt", MAXIMUM_LINE_COUNT)

    if is_auth_experiment:
        mutual_info = MutualInformationManager(MutualInformationManager.PatternType.AUTHOR_AUTHOR)
        mutual_info.read_mutual_information_from_file()

        author_patterns = parse_author_file_into_patterns("data/frequent_author_patterns.txt")
        extractor = RepresentativeTransactionExtractor(transactions, mutual_info, author_patterns, \
            MutualInformationManager.PatternType.AUTHOR_AUTHOR, k)
    else:
        mutual_info = MutualInformationManager(MutualInformationManager.PatternType.TITLE_TITLE)
        mutual_info.read_mutual_information_from_file()

        title_patterns = parse_sequential_title_file_into_patterns("data/minimal_title_term_patterns.txt")
        extractor = RepresentativeTransactionExtractor(transactions, mutual_info, title_patterns, \
            MutualInformationManager.PatternType.TITLE_TITLE, k)

    repr_transactions = extractor.find_representative_transactions(target_id, k)
    extractor.display_pretty(target_id, repr_transactions)
