from spmf_python_wrapper import run_spmf
import os

class FrequentPatternBuilder():
    '''
    Builds frequent pattern files for authors and title terms. The authors' frequent
    patterns are based off of the FPClose algorithm and the titles terms' frequent patterns
    are based off of Clospan.

    Note that all strings are mapped to non-negative integers (and the author and title term
    mappings are completely separate) -- SMPF, the library we're using, requires that all input
    files contain integers rather than strings for efficiency.

    The following files are generated
        data/frequent_author_patterns.txt       Frequent author patterns (via fpclose)
        data/frequent_title_term_patterns.txt   Frequent title term patterns (via clospan)
        data/author_id_mappings.txt             Mapping from author ID to author name 
        data/title_term_id_mappings.txt         Mapping from title term ID to title term 
    '''
    CSV_FILE_PATH = "data/data.csv"

    AUTHORS_INPUT_FILE_PATH = "data/authors_temp_input.txt"
    TITLE_TERMS_INPUT_FILE_PATH = "data/title_temp_input.txt"

    AUTHORS_OUTPUT_FILE_PATH = "data/frequent_author_patterns.txt"
    TITLE_TERMS_OUTPUT_FILE_PATH = "data/frequent_title_term_patterns.txt"

    AUTHOR_ID_FILE_PATH = "data/author_id_mappings.txt"
    TITLE_TERM_ID_FILE_PATH = "data/title_term_id_mappings.txt"

    def __init__(self, fp_close_thresh=0.05, clospan_thresh=0.075, display_transaction_nums=False):
        '''
        @param fp_close_thresh          Min relative (percentage) support for FPClose
        @param clospan_thresh           Min relative (percentage) support for CloSpan
        @param display_transaction_nums True if output file should display the transaction ids the elements
            in the frequent patterns were from, False otherwise (useful when debugging only). DON'T SET THIS
            TO TRUE WHEN GENERATING PATTERN FILES TO PARSE INTO ANNOTATOR
        '''
        self.__fp_close_thresh = fp_close_thresh
        self.__clospan_thresh = clospan_thresh
        self.__display_transaction_nums = display_transaction_nums

    def build_frequent_pattern_files(self):
        '''
        Driver function that builds intermediate input files from raw authors/title file and builds final
        pattern files.
        '''
        author_id_mapping, title_term_id_mapping = self.__build_intermediate_smpf_input()

        FrequentPatternBuilder.__write_word_id_mapping(author_id_mapping, FrequentPatternBuilder.AUTHOR_ID_FILE_PATH)
        FrequentPatternBuilder.__write_word_id_mapping(title_term_id_mapping, FrequentPatternBuilder.TITLE_TERM_ID_FILE_PATH)

        display_transaction_nums_str = str(self.__display_transaction_nums).lower()

        run_spmf("FPClose", FrequentPatternBuilder.AUTHORS_INPUT_FILE_PATH, \
            FrequentPatternBuilder.AUTHORS_OUTPUT_FILE_PATH, \
                [str(self.__fp_close_thresh) + "%", display_transaction_nums_str])

        run_spmf("CloSpan", FrequentPatternBuilder.TITLE_TERMS_INPUT_FILE_PATH, \
            FrequentPatternBuilder.TITLE_TERMS_OUTPUT_FILE_PATH, \
                [str(self.__clospan_thresh) + "%", display_transaction_nums_str])   
         
    def clean_intermediate_files(self):
        '''
        Delete input files built specifically for SPMF
        '''
        def delete_file(input_file):
            if os.path.exists(input_file):
                print("Deleting %s" % input_file)
                os.remove(input_file)
            else:
                print("Warning: %s was not found" % input_file)
        delete_file(FrequentPatternBuilder.AUTHORS_INPUT_FILE_PATH)
        delete_file(FrequentPatternBuilder.TITLE_TERMS_INPUT_FILE_PATH)

    def __build_intermediate_smpf_input(self):
        '''
        Build intermediate files (title and author files). Note that the format for CloSpan
        input files is different because we need to account for itemsets and transactions
        rather than just transactions.

        IMPORTANT: Each title term is considered a separate itemset (so in other words, all
        the itemsets are 1-itemsets). There's no way to distinguish whehter specific words in
        a title should be in different itemsets and the paper doens't clarify this, so we 
        need to either put everything per title into 1 itemset (which doesn't make sense because
        then our patterns wouldn't be sequential) or make every word its own itemset.

        @return (map(int, string), map(int, string))    Tuple of maps where the first map 
            is a mapping between all unique author names to their author ids and the second 
            is a mapping between all unique title terms to their title ids. NOTE: The mappings
            are completely independent -- so auth_map["foo"] has no relation to title_map["foo"]

        Documentation on input files for the 2 algorithms:
        * https://www.philippe-fournier-viger.com/spmf/CloSpan.php
        * http://www.philippe-fournier-viger.com/spmf/FPClose.php
        '''
        authors_input_file = open(FrequentPatternBuilder.AUTHORS_INPUT_FILE_PATH, "w")
        title_terms_input_file = open(FrequentPatternBuilder.TITLE_TERMS_INPUT_FILE_PATH, "w")
        data_csv_file = open(FrequentPatternBuilder.CSV_FILE_PATH, "r")
        
        author_id_mapping = {}
        curr_author_id = 0

        title_term_id_mapping = {}
        curr_title_term = 0
        
        # Repeating some code so we can iterate through the raw data file (big) one time
        for line in data_csv_file:
            # Note: Titles are guaranteed to not have commas
            line_as_lst = line.split(',')
            authors = line_as_lst[ : -1]
            author_ids = []

            for author in authors:
                if author not in author_id_mapping:
                    author_id_mapping[author] = curr_author_id
                    curr_author_id += 1
                author_ids.append(author_id_mapping[author])
            author_ids.sort()
            authors_input_file.write("%s\n" % ' '.join([str(auth_id) for auth_id in author_ids]))
            
            title = line_as_lst[-1]
            term_ids = []
            # TODO remove periods and commas????
            for title_term in title.split():
                if title_term not in title_term_id_mapping:
                    title_term_id_mapping[title_term] = curr_title_term
                    curr_title_term += 1
                term_ids.append(str(title_term_id_mapping[title_term]))
                # -1 indicates the end of an itemset within a transaction
                term_ids.append(str(-1))

            # -2 indicates the end of a transaction
            term_ids.append(str(-2))
            title_terms_input_file.write("%s\n" % ' '.join(term_ids))

        data_csv_file.close()
        title_terms_input_file.close()
        authors_input_file.close()

        return author_id_mapping, title_term_id_mapping

    @staticmethod
    def __write_word_id_mapping(word_id_mapping, output_file_path):
        '''
        Writes a mapping between each id and each unique word to a file

        Format:
            <id> <word>
        Ex: 1 good
            2 so
        
        @param word_id_mapping: map(word, int)  Mapping between unique words 
            and their corresponding ids
        @param output_file_path: string         Path to write mapping to
        '''
        word_id_file = open(output_file_path, "w")
        for word in word_id_mapping:
            word_id_file.write("%d %s\n" % (word_id_mapping[word], word))
        word_id_file.close()

if __name__ == "__main__":
    pattern_builder = FrequentPatternBuilder()
    pattern_builder.build_frequent_pattern_files()
    # pattern_builder.clean_intermediate_files()