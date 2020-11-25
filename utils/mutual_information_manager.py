from math import log2
import transactions_manager
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
        if not self.__transactions:
            print("You can't compute mutual information with a null transactions manager")
            return

        if self.__write_to_file_during_computation:
            mutual_info_file = open(MutualInformationManager.AUTHOR_MUTUAL_INFO_FILENAME, "w")

        num_patterns = len(patterns)
        for ind_x, pattern_x in enumerate(patterns):
            for ind_y in range(ind_x, num_patterns):
                self.__mutual_info_vals[(ind_x, ind_y)] = \
                    MutualInformationManager.compute_mutual_information_for_pattern_pair(self.__transactions, \
                        pattern_x, patterns[ind_y])

                if self.__write_to_file_during_computation:
                    mutual_info_file.write("%d %d %f\n" % (ind_x, ind_y, \
                        self.__mutual_info_vals[(ind_x, ind_y)]))
        if self.__write_to_file_during_computation:
            mutual_info_file.close()

    def get_mutual_information_vector(self, pattern_ind, context_model_dim):
        '''
        Gets mutual information vector from precomputed mutual information cache. Assumes that the mutual info matrix has been
        computed/read in. 

        @param
            pattern_ind: int              Pattern index to find MI vec for
            context_model_dim: int        Dimension of context vector

        @return mutual information val, which is represented as list(float)
        '''
        mi_vec = []
        for other_pattern_ind in range(context_model_dim):
            mi_vec.append(self.get_mutual_information(pattern_ind, other_pattern_ind))
        return mi_vec

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

    @staticmethod
    def compute_mutual_information_for_pattern_pair(transaction_manager, pattern_x, pattern_y):
        '''
        Computes mutual information value given patterns using the transaction manager.

        @param
            pattern_x: vec[int]        Pattern of author IDs to find MI for
            pattern_y: vec[int]        Pattern of author IDs to find MI for

        @return mutual information val, which is represented as a float
        '''
        if not transaction_manager:
            print("You can't compute mutual information with a null transactions manager")
            return

        # Compute intersection
        pattern_x_set = set(pattern_x)
        pattern_y_set = set(pattern_y)

        x_paper_inds = transaction_manager.find_author_pattern_transactions_ids(pattern_x_set)
        y_paper_inds = transaction_manager.find_author_pattern_transactions_ids(pattern_y_set)
        x_support = len(x_paper_inds)
        y_support = len(y_paper_inds)

        x_y_intersection_len = len(x_paper_inds.intersection(y_paper_inds))
        x_y_union_len = len(x_paper_inds.union(y_paper_inds))

        num_transactions = transaction_manager.get_number_of_transactions()

        SMOOTHING_FACTOR = 0.001
        def get_smoothed_probability(num, denom):
            return (num + SMOOTHING_FACTOR) / (denom + 4 * SMOOTHING_FACTOR)

        p_x_1 = get_smoothed_probability(x_support, num_transactions)
        p_y_1 = get_smoothed_probability(y_support, num_transactions)        
        p_x_0 = get_smoothed_probability(num_transactions - x_support, num_transactions)
        p_y_0 = get_smoothed_probability(num_transactions - y_support, num_transactions)

        p_x_1_y_1 = get_smoothed_probability(x_y_intersection_len, num_transactions)
        p_x_0_y_1 = get_smoothed_probability(y_support - x_y_intersection_len, num_transactions)
        p_x_1_y_0 = get_smoothed_probability(x_support - x_y_intersection_len, num_transactions)
        p_x_0_y_0 = get_smoothed_probability(num_transactions - x_y_union_len, num_transactions)
        
        def compute_mutual_information_for_pattern_pair(p_x_y, p_x, p_y):
            #if p_x_y == 0:
            #    return 0
            return p_x_y / log2(p_x_y / p_x / p_y)

        mi_x_1_y_1 = compute_mutual_information_for_pattern_pair(p_x_1_y_1, p_x_1, p_y_1)
        mi_x_1_y_0 = compute_mutual_information_for_pattern_pair(p_x_1_y_0, p_x_1, p_y_0)
        mi_x_0_y_1 = compute_mutual_information_for_pattern_pair(p_x_0_y_1, p_x_0, p_y_1)
        mi_x_0_y_0 = compute_mutual_information_for_pattern_pair(p_x_0_y_0, p_x_0, p_y_0)
        return mi_x_1_y_1 + mi_x_1_y_0 + mi_x_0_y_1 + mi_x_0_y_0

if __name__ == "__main__":
    transactions = transactions_manager.TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")    
    author_patterns = parse_file_into_patterns("data/frequent_author_patterns.txt")
    mutual_info = MutualInformationManager(transactions, True)
    mutual_info.compute_mutual_information(author_patterns)
    
    #mutual_info = MutualInformationManager()
    #mutual_info.read_mutual_information_from_file()
