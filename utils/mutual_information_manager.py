from math import log2
from transactions_manager import TransactionsManager
from parse_patterns import parse_file_into_patterns

class MutualInformationManager:
    def __init__(self, transactions):
        # Dictionary of (pattern index a, pattern index b) pairs where
        # a <= b (aka a triangular matrix)
        self.__mutual_info_vals = {}
        self.__transactions = transactions

    def read_mutual_information_from_file(self, filename):
        pass

    def compute_mutual_information(self, patterns):
        num_patterns = len(patterns)
        mi = []
        for ind_x, pattern_x in enumerate(patterns):
            for ind_y in range(ind_x, num_patterns):

                self.__mutual_info_vals[(ind_x, ind_y)] = \
                    self.__compute_mutual_information(pattern_x, patterns[ind_y])
                mi.append(self.__mutual_info_vals[(ind_x, ind_y)])
        print(max(mi))
        print(min(mi))

    def __compute_mutual_information(self, pattern_x, pattern_y):
        # Compute intersection
        pattern_x_set = set(pattern_x)
        pattern_y_set = set(pattern_y)

        x_y_intersection_support = self.__transactions.find_author_pattern_support(\
            pattern_x_set.intersection(pattern_y_set))
        x_y_union_support = self.__transactions.find_author_pattern_support(\
            pattern_x_set.union(pattern_y_set))
        x_support = self.__transactions.find_author_pattern_support(pattern_x_set)
        y_support = self.__transactions.find_author_pattern_support(pattern_y_set)

        num_transactions = self.__transactions.get_number_of_transactions()

        p_x = x_support / num_transactions
        p_y = y_support / num_transactions
        p_x_1_y_1 = x_y_intersection_support / num_transactions
        p_x_0_y_1 = (y_support - x_y_intersection_support) / num_transactions
        p_x_1_y_0 = (x_support - x_y_intersection_support) / num_transactions
        p_x_0_y_0 = (num_transactions - x_y_union_support) / num_transactions

        def compute_mutual_info_given_probs(p_x_y):
            return (p_x_y + 1) * log2((p_x_y + 1) / ((p_x + 1) * (p_y + 1)))

        return compute_mutual_info_given_probs(p_x_1_y_1) \
            + compute_mutual_info_given_probs(p_x_0_y_1) \
            + compute_mutual_info_given_probs(p_x_1_y_0) \
            + compute_mutual_info_given_probs(p_x_0_y_0)

if __name__ == "__main__":
    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")    
    author_patterns = parse_file_into_patterns("data/frequent_author_patterns.txt")
    mutual_info = MutualInformationManager(transactions)
    mutual_info.compute_mutual_information(author_patterns)