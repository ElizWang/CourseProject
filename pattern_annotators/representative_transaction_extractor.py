import heapq

import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from transactions_manager import TransactionsManager
from mutual_information_manager import MutualInformationManager
from parse_patterns import parse_file_into_patterns
from cosine_similarity import compute_cosine_similarity

class RepresentativeTransactionExtractor:
    # From: https://stackoverflow.com/questions/2501457/what-do-i-use-for-a-max-heap-implementation-in-python
    class TransactionSimilarity(object):
        def __init__(self, cosine_sim, transaction_ind): 
            self.cosine_sim = cosine_sim
            self.transaction_ind = transaction_ind

        def __lt__(self, other): 
            return self.cosine_sim > other.cosine_sim

        def __eq__(self, other): 
            return self.cosine_sim == other.cosine_sim

    def __init__(self, transaction_mananger, mutual_info_manager, patterns, num_transactions, is_author):
        self.__transaction_manager = transaction_mananger
        self.__mutual_info_manager = mutual_info_manager

        self.__patterns = patterns
        self.__num_transactions = num_transactions
        self.__is_author = is_author

    def __compute_paper_context_models(self):
        # TODO implement context models when is_author is false
        context_models = []

        for paper_id in range(2): #self.__transaction_manager.get_number_of_transactions()):
            paper_context_model = []

            for pattern in self.__patterns:
                paper_authors = self.__transaction_manager.get_paper_authors(paper_id)
                mutual_info = \
                    MutualInformationManager.compute_mutual_information_for_pattern_pair(self.__transaction_manager, \
                        pattern, paper_authors)
                paper_context_model.append(mutual_info)

            context_models.append(paper_context_model)
        return context_models

    def find_representative_transactions(self):
        paper_context_models = self.__compute_paper_context_models()
        context_model_dim = len(self.__patterns)

        similarities_max_q = []

        repr_transactions = {}

        for pattern_ind in range(context_model_dim):
            # Read in the context model vector
            pattern_context_model = self.__mutual_info_manager.get_mutual_information_vector(pattern_ind, context_model_dim)

            for transaction_ind, transaction_vec in enumerate(paper_context_models):
                cosine_sim = compute_cosine_similarity(pattern_context_model, transaction_vec)
                # Negate cosine sim bc we want to implement max heap and heapq == min heap
                heapq.heappush(similarities_max_q, RepresentativeTransactionExtractor.TransactionSimilarity(cosine_sim, transaction_ind))             

            pattern_transactions = []
            for _ in range(self.__num_transactions):
                transaction_ind = heapq.heappop(similarities_max_q).transaction_ind
                pattern_transactions.append(transaction_ind)
            repr_transactions[pattern_ind] = pattern_transactions
        return repr_transactions

if __name__ == "__main__":
    mutual_info = MutualInformationManager()
    mutual_info.read_mutual_information_from_file()    

    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")    
    author_patterns = parse_file_into_patterns("data/frequent_author_patterns.txt")
    
    extractor = RepresentativeTransactionExtractor(transactions, mutual_info, author_patterns, 3, True)
    extractor.find_representative_transactions()