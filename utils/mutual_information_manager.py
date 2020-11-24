from math import log2
from transactions_manager import TransactionsManager
from parse_patterns import parse_file_into_patterns

import os

'''
Usage:
* To compute mutual information and to write to a file
    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")    
    mutual_info = MutualInformationManager(transactions, True)
    mutual_info.compute_mutual_information(author_patterns)

Output file format:
    index1 index2 MI
where index1 <= index2

* To read the mutual info file into this class and to get the mutual information given a
  pair of indices
     mutual_info = MutualInformationManager()
     mutual_info.read_mutual_information_from_file()
     mutual_info.get_mutual_information(1, 2) # to get mutual info for patterns 1 and 2

Note: We're storing one MI value per pair of AUTHOR pattern indices.
'''
class MutualInformationManager:

    # TODO pass this in as a param, make this code more flexible st we can use it for authors and
    # title patterns
    AUTHOR_MUTUAL_INFO_FILENAME = os.path.join("data", "author_mutual_info_patterns.txt")

    def __init__(self, transactions=None, write_to_file_during_computation=False):
        '''
        @param
            transactions: TransactionManager        transaction manager storing parsed paper data
            write_to_file_during_computation: bool  true to write to MI file when computing MIs, else false
        '''
        # Dictionary of (pattern index a, pattern index b) pairs where
        # a <= b (aka a triangular matrix)
        self.__mutual_info_vals = {}
        self.__transactions = transactions
        self.__write_to_file_during_computation = write_to_file_during_computation

    def read_mutual_information_from_file(self):
        '''
        Reads mutual information from file and populates the mutual information triangular matrix this
        class stores. Note that it assumes that the first pattern index is <= the second pattern index 
        (aka that it was generated using this file)
        '''
        mutual_info_file = open(MutualInformationManager.AUTHOR_MUTUAL_INFO_FILENAME, "r")
        for line in mutual_info_file:
            mutual_info_lst = line.strip().split()
            assert len(mutual_info_lst) == 3

            ind_x = int(mutual_info_lst[0])
            ind_y = int(mutual_info_lst[1])
            assert ind_x <= ind_y

            self.__mutual_info_vals[(ind_x, ind_y)] = float(mutual_info_lst[2])
        mutual_info_file.close()

    def write_mutual_information_to_file(self):
        '''
        Writes mutual information computed to a file. Assumes that mutual info has already been computed
        '''
        if self.__write_to_file_during_computation:
            print("You've already written this information to a file")
            return

        # Format: pattern_ind_1 pattern_ind_2 MI
        mutual_info_file = open(MutualInformationManager.AUTHOR_MUTUAL_INFO_FILENAME, "w")
        for pattern_ind_x, pattern_ind_y in self.__mutual_info_vals:
            mutual_info_file.write("%d %d %f\n" % (pattern_ind_x, pattern_ind_y, \
                self.__mutual_info_vals[(pattern_ind_x, pattern_ind_y)]))
        mutual_info_file.close()

    def compute_mutual_information(self, patterns):
        '''
        Computes mutual information for pattern indices (a, b) given that a <= b. In other words, it
        computes a triangular matrix of mutual information values bc MI is symmetric
        '''
        if not transactions:
            print("You can't compute mutual information with a null transactions manager")
            return

        if self.__write_to_file_during_computation:
            mutual_info_file = open(MutualInformationManager.AUTHOR_MUTUAL_INFO_FILENAME, "w")

        num_patterns = len(patterns)
        for ind_x, pattern_x in enumerate(patterns):
            for ind_y in range(ind_x, num_patterns):
                self.__mutual_info_vals[(ind_x, ind_y)] = self.compute_mutual_information_for_pattern_pair(pattern_x, patterns[ind_y])

                if self.__write_to_file_during_computation:
                    mutual_info_file.write("%d %d %f\n" % (ind_x, ind_y, \
                        self.__mutual_info_vals[(ind_x, ind_y)]))
        if self.__write_to_file_during_computation:
            mutual_info_file.close()
                  
    def get_mutual_information(self, pattern_index_x, pattern_index_y):
        '''
        Get precomputed mutual information value given 2 indices. Assumes that the mutual info matrix has been
        computed/read in. Doesn't assume that one index is greater than another

        @param
            pattern_index_x: int        Pattern index to find MI for
            pattern_index_y: int        Pattern index to find MI for

        @return mutual information val, which is represented as a float
        '''
        if pattern_index_x <= pattern_index_y:
            ind_tup = (pattern_index_x, pattern_index_y)
        else:
            ind_tup = (pattern_index_y, pattern_index_x)
        return self.__mutual_info_vals[ind_tup]

    def compute_mutual_information_for_pattern_pair(self, pattern_x, pattern_y):
        '''
        Computes mutual information value given patterns using the transaction manager.

        @param
            pattern_x: vec[int]        Pattern of author IDs to find MI for
            pattern_y: vec[int]        Pattern of author IDs to find MI for

        @return mutual information val, which is represented as a float
        '''
        if not transactions:
            print("You can't compute mutual information with a null transactions manager")
            return

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
    mutual_info = MutualInformationManager(transactions, True)
    mutual_info.compute_mutual_information(author_patterns)
    mutual_info.write_mutual_information_to_file()
    # mutual_info = MutualInformationManager()
    # mutual_info.read_mutual_information_from_file()