import sys 
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from transactions_manager import TransactionsManager
from mutual_information_manager import MutualInformationManager
from parse_patterns import parse_file_into_patterns

class RepresentativeTransactionExtractor:
    def __init__(self, transaction_mananger, patterns, is_author):
        self.__transaction_manager = transaction_mananger
        self.__patterns = patterns
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
        self.__compute_paper_context_models()

if __name__ == "__main__":
    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")    
    author_patterns = parse_file_into_patterns("data/frequent_author_patterns.txt")
    extractor = RepresentativeTransactionExtractor(transactions, author_patterns, True)
    extractor.find_representative_transactions()