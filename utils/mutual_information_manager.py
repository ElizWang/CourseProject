from math import log2
import transactions_manager
from parse_patterns import parse_author_file_into_patterns, parse_sequential_title_file_into_patterns

import os

'''
Usage:
* To compute mutual information and to write to a file
    transactions = TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")
    mutual_info = MutualInformationManager(transactions, True)
    mutual_info.compute_mutual_information(author_patterns)

Output file format:
    index1 index2 MI
where index1 <= index2 for auth-auth or title-title managers
where index1 = author index and index2 = title index for auth-title or title-auth managers
(IMPORTANT: auth-title/title-auth files are formatted in the same way, where auth = index1)

* To read the mutual info file into this class and to get the mutual information given a
  pair of indices
     mutual_info = MutualInformationManager(MutualInformationManager.PatternType.X)
     mutual_info.read_mutual_information_from_file()
     mutual_info.get_mutual_information(1, 2) # to get mutual info for patterns 1 and 2

Note: We're storing one MI value per pair of AUTHOR pattern indices.
'''
class MutualInformationManager:

    class PatternType:
        AUTHOR_AUTHOR = 0
        AUTHOR_TITLE = 1
        TITLE_AUTHOR = 2
        TITLE_TITLE = 3

    AUTHOR_AUTHOR_MUTUAL_INFO_FILENAME = os.path.join("data", "author_author_mutual_info_patterns.txt")
    AUTHOR_TITLE_MUTUAL_INFO_FILENAME = os.path.join("data", "author_title_mutual_info_patterns.txt")
    TITLE_TITLE_MUTUAL_INFO_FILENAME = os.path.join("data", "title_title_mutual_info_patterns.txt")

    def __init__(self, pattern_type, transactions=None, write_to_file_during_computation=False):
        '''
        @param
            pattern_type: PatternType               type of pattern pairs to compute MI for
            transactions: TransactionManager        transaction manager storing parsed paper data
            write_to_file_during_computation: bool  true to write to MI file when computing MIs, else false
        '''
        # Dictionary of (pattern index a, pattern index b) pairs where
        # a <= b (aka a triangular matrix)
        self.__mutual_info_vals = {}
        self.__pattern_type = pattern_type
        self.__transactions = transactions
        self.__write_to_file_during_computation = write_to_file_during_computation

        if pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR:
            self.__filename =  MutualInformationManager.AUTHOR_AUTHOR_MUTUAL_INFO_FILENAME

        elif pattern_type == MutualInformationManager.PatternType.AUTHOR_TITLE or \
            pattern_type == MutualInformationManager.PatternType.TITLE_AUTHOR:
            self.__filename =  MutualInformationManager.AUTHOR_TITLE_MUTUAL_INFO_FILENAME

        elif pattern_type == MutualInformationManager.PatternType.TITLE_TITLE:
            self.__filename =  MutualInformationManager.TITLE_TITLE_MUTUAL_INFO_FILENAME

        else:
            print("ERROR: Invalid pattern type")
            assert False

    def read_mutual_information_from_file(self):
        '''
        Reads mutual information from file and populates the mutual information triangular matrix this
        class stores. Note that it assumes that the first pattern index is <= the second pattern index
        (aka that it was generated using this file)
        '''
        mutual_info_file = open(self.__filename, "r")
        is_first = True
        for line in mutual_info_file:
            if is_first:
                pattern_type = int(line.strip())
                assert pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR \
                    or pattern_type == MutualInformationManager.PatternType.AUTHOR_TITLE \
                        or pattern_type == MutualInformationManager.PatternType.TITLE_AUTHOR \
                            or pattern_type == MutualInformationManager.PatternType.TITLE_TITLE

                self.__pattern_type = pattern_type
                is_first = False
                continue

            mutual_info_lst = line.strip().split()
            assert len(mutual_info_lst) == 3

            ind_x = int(mutual_info_lst[0])
            ind_y = int(mutual_info_lst[1])
            
            if pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR \
                or pattern_type == MutualInformationManager.PatternType.TITLE_TITLE:
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
        mutual_info_file = open(self.__pattern_type, "w")
        mutual_info_file.write("%d\n" % self.__pattern_type)

        for pattern_ind_x, pattern_ind_y in self.__mutual_info_vals:
            mutual_info_file.write("%d %d %f\n" % (pattern_ind_x, pattern_ind_y, \
                self.__mutual_info_vals[(pattern_ind_x, pattern_ind_y)]))
        mutual_info_file.close()

    def compute_mutual_information(self, patterns, secondary_patterns=None):
        '''
        Computes mutual information for pattern indices (a, b) given that a <= b. In other words, it
        computes a triangular matrix of mutual information values bc MI is symmetric

        @param
            patterns: list(list(int))               List of patterns to compute MI over. MUST be author patterns
                    if pattern type is AUTHOR_TITLE or TITLE_AUTHOR

            secondary_patterns: list(list(int))?    List of secondary patterns to compute MI over if 
                    patterns != secondary patterns (then, we'd compute the MI for each (pattern, secondary pattern)
                    pair). MUST be title patterns if pattern type is AUTHOR_TITLE or TITLE_AUTHOR
        '''
        if not self.__transactions:
            print("ERROR: You can't compute mutual information with a null transactions manager")
            exit(1)

        if (secondary_patterns and self.__pattern_type != MutualInformationManager.PatternType.AUTHOR_TITLE \
            and self.__pattern_type != MutualInformationManager.PatternType.TITLE_AUTHOR) \
                or (not secondary_patterns and (self.__pattern_type == MutualInformationManager.PatternType.AUTHOR_TITLE \
                    or self.__pattern_type == MutualInformationManager.PatternType.TITLE_AUTHOR)):
            print("ERROR: You must and can only pass in a secondary pattern list if the Pattern Type is AUTHOR_TITLE")
            exit(1)
        
        if self.__write_to_file_during_computation:
            mutual_info_file = open(self.__filename, "w")
            mutual_info_file.write("%d\n" % self.__pattern_type)

        for ind_x, pattern_x in enumerate(patterns):
            if self.__pattern_type == MutualInformationManager.PatternType.AUTHOR_TITLE:
                pattern_itr = range(len(secondary_patterns))
            else:
                pattern_itr = range(ind_x, len(patterns))

            for ind_y in pattern_itr:
                self.__mutual_info_vals[(ind_x, ind_y)] = \
                    MutualInformationManager.compute_mutual_information_for_pattern_pair(self.__transactions, \
                        self.__pattern_type, pattern_x, patterns[ind_y])

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
            pattern_ind: int              Pattern index to find MI vec for. IF AUTHOR-TITLE, MUST BE AUTHOR. IF TITLE-AUTHOR, MUST
            BE TITLE
            context_model_dim: int        Dimension of context vector

        @return mutual information val, which is represented as list(float)
        '''
        mi_vec = []
        for other_pattern_ind in range(context_model_dim):
            # TITLE-AUTH and AUTH-TITle = implemented in the same way, so we need to swap the indices here when calling 
            # get_mutual_information
            if self.__pattern_type == MutualInformationManager.PatternType.TITLE_AUTHOR:
                mi_vec.append(self.get_mutual_information(other_pattern_ind, pattern_ind))
            else:
                mi_vec.append(self.get_mutual_information(pattern_ind, other_pattern_ind))            
        return mi_vec

    def get_mutual_information(self, pattern_index_x, pattern_index_y):
        '''
        Get precomputed mutual information value given 2 indices. Assumes that the mutual info matrix has been
        computed/read in. Doesn't assume that one index is greater than another.

        IMPORTANT IMPORTANT IMPORTANT 
        pattern_index_x must be for authors and pattern_index_y for titles if the pattern type is 
        author-title or title-auth

        @param
            pattern_index_x: int        Pattern index to find MI for
            pattern_index_y: int        Pattern index to find MI for

        @return mutual information val, which is represented as a float
        '''
        if self.__pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR \
            or self.__pattern_type == MutualInformationManager.PatternType.TITLE_TITLE:
            if pattern_index_x <= pattern_index_y:
                ind_tup = (pattern_index_x, pattern_index_y)
            else:
                ind_tup = (pattern_index_y, pattern_index_x)
        else:
            ind_tup = (pattern_index_x, pattern_index_y)
        return self.__mutual_info_vals[ind_tup]

    @staticmethod
    def compute_mutual_information_for_pattern_pair(transaction_manager, pattern_type, pattern_x, pattern_y):
        '''
        Computes mutual information value given patterns using the transaction manager.

        @param
            transaction_manager: TransactionManager transaction manager storing parsed paper data
            pattern_type: PatternType               type of pattern pairs to compute MI for
            pattern_x: vec[int]                     Pattern of author IDs to find MI for
            pattern_y: vec[int]                     Pattern of author IDs to find MI for

        @return mutual information val, which is represented as a float
        '''
        if not transaction_manager:
            print("You can't compute mutual information with a null transactions manager")
            return

        # Compute intersection
        pattern_x_set = set(pattern_x)
        pattern_y_set = set(pattern_y)

        # Important: Don't use sets when finding title pattern transaction ids because title patterns are
        # sequential
        if pattern_type == MutualInformationManager.PatternType.AUTHOR_AUTHOR:
            x_paper_inds = transaction_manager.find_author_pattern_transactions_ids(pattern_x_set)
            y_paper_inds = transaction_manager.find_author_pattern_transactions_ids(pattern_y_set)

        elif pattern_type == MutualInformationManager.PatternType.AUTHOR_TITLE \
            or pattern_type == MutualInformationManager.PatternType.TITLE_AUTHOR:
            x_paper_inds = transaction_manager.find_author_pattern_transactions_ids(pattern_x_set)
            y_paper_inds = transaction_manager.find_title_pattern_transactions_ids(pattern_y)

        elif pattern_type == MutualInformationManager.PatternType.TITLE_TITLE:
            x_paper_inds = transaction_manager.find_title_pattern_transactions_ids(pattern_x)
            y_paper_inds = transaction_manager.find_title_pattern_transactions_ids(pattern_y)

        x_support = len(x_paper_inds)
        y_support = len(y_paper_inds)

        x_y_intersection_len = len(x_paper_inds.intersection(y_paper_inds))
        x_y_union_len = len(x_paper_inds.union(y_paper_inds))

        num_transactions = transaction_manager.get_number_of_transactions()

        SMOOTHING_FACTOR = 0.01
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
            return p_x_y * log2(p_x_y / p_x / p_y)

        mi_x_1_y_1 = compute_mutual_information_for_pattern_pair(p_x_1_y_1, p_x_1, p_y_1)
        mi_x_1_y_0 = compute_mutual_information_for_pattern_pair(p_x_1_y_0, p_x_1, p_y_0)
        mi_x_0_y_1 = compute_mutual_information_for_pattern_pair(p_x_0_y_1, p_x_0, p_y_1)
        mi_x_0_y_0 = compute_mutual_information_for_pattern_pair(p_x_0_y_0, p_x_0, p_y_0)
        return mi_x_1_y_1 + mi_x_1_y_0 + mi_x_0_y_1 + mi_x_0_y_0

if __name__ == "__main__":
    transactions = transactions_manager.TransactionsManager("data/data.csv", "data/author_id_mappings.txt", "data/title_term_id_mappings.txt")    
    author_patterns = parse_author_file_into_patterns("data/frequent_author_patterns.txt")
    title_patterns = parse_sequential_title_file_into_patterns("data/minimal_title_term_patterns.txt")
    mutual_info = MutualInformationManager(MutualInformationManager.PatternType.TITLE_AUTHOR, transactions, True)
    mutual_info.compute_mutual_information(author_patterns, title_patterns)

    #mutual_info = MutualInformationManager(MutualInformationManager.PatternType.AUTHOR_AUTHOR, transactions, True)
    #mutual_info.compute_mutual_information(author_patterns)

    #mutual_info = MutualInformationManager()
    #mutual_info.read_mutual_information_from_file()
