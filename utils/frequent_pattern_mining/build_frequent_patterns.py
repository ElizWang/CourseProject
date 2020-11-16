from spmf_python_wrapper import run_spmf

CSV_FILE_PATH = "data/data.csv"

AUTHORS_INPUT_FILE_PATH = "data/authors_temp_input.txt"
TITLE_TERMS_INPUT_FILE_PATH = "data/title_temp_input.txt"

AUTHORS_OUTPUT_FILE_PATH = "data/frequent_author_patterns.txt"
TITLE_TERMS_OUTPUT_FILE_PATH = "data/frequent_title_term_patterns.txt"

AUTHOR_ID_FILE_PATH = "data/author_id_mappings.txt"
TITLE_TERM_ID_FILE_PATH = "data/title_term_id_mappings.txt"

def build_intermediate_smpf_input():
    '''
    Build intermediate files
    '''
    authors_input_file = open(AUTHORS_INPUT_FILE_PATH, "w")
    title_terms_input_file = open(TITLE_TERMS_INPUT_FILE_PATH, "w")
    data_csv_file = open(CSV_FILE_PATH, "r")
    
    author_id_mapping = {}
    curr_author_id = 0

    title_term_id_mapping = {}
    curr_title_term = 0

    for line in data_csv_file:
        print(line)
        # Note: Titles are guaranteed to not have commas
        line_as_lst = line.split(',')
        authors = line_as_lst[ : -1]
        author_ids = []

        for author in authors:
            if author not in author_id_mapping:
                author_id_mapping[author] = curr_author_id
                curr_author_id += 1
            author_ids.append(str(author_id_mapping[author]))
        authors_input_file.write("%s\n" % ' '.join(author_ids))
        
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

        title_terms_input_file.write("%s\n" % ' '.join(term_ids))

    data_csv_file.close()
    title_terms_input_file.close()
    authors_input_file.close()

    return author_id_mapping, title_term_id_mapping

def write_word_id_mapping(word_id_mapping, output_file_path):
    word_id_file = open(output_file_path, "w")
    for word in word_id_mapping:
        word_id_file.write("%d %s\n" % (word_id_mapping[word], word))
    word_id_file.close()

if __name__ == "__main__":
    author_id_mapping, title_term_id_mapping = build_intermediate_smpf_input()

    write_word_id_mapping(author_id_mapping, AUTHOR_ID_FILE_PATH)
    write_word_id_mapping(title_term_id_mapping, TITLE_TERM_ID_FILE_PATH)

    run_spmf("FPClose", AUTHORS_INPUT_FILE_PATH, AUTHORS_OUTPUT_FILE_PATH, ["10%"])
    run_spmf("CloSpan", TITLE_TERMS_INPUT_FILE_PATH, TITLE_TERMS_OUTPUT_FILE_PATH, ["10%"])