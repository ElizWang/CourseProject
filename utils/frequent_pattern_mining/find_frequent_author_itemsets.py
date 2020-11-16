import spmf_python_wrapper
import os

'''
Generate a file (data/frequent_author_patterns.txt) containing all frequent author patterns via SMPF
-- this file encodes authors as IDs for efficiency (according to SMPF, which also requires that all
input files contain numbers rather than words). Generates a file containing the mappings between 
author names and authors IDs, which we can use later to display our results.

NOTE: Must run this file from the project's root directory for the paths to work
'''

CSV_FILE_PATH = "data/data.csv"
INPUT_FILE_PATH = "data/temp_spmf_input.txt"
OUTPUT_FILE_PATH = "data/frequent_author_patterns.txt"
AUTHOR_ID_FILE_PATH = "data/author_id_mappings.txt"

# TODO move elsewhere, build multiple files so we only have to traverse data.csv once
def build_intermediate_smpf_input():
    input_file = open(INPUT_FILE_PATH, "w")
    csv_file = open(CSV_FILE_PATH, "r")
    
    author_id_mapping = {}
    curr_id = 0
    paper_count = 0 # For building relative threshold

    for line in csv_file:
        # Note: Titles are guaranteed to not have commas
        authors = line.split(',')[ : -1]
        author_ids = []

        for author in authors:
            if author not in author_id_mapping:
                author_id_mapping[author] = curr_id
                curr_id += 1
            author_ids.append(str(author_id_mapping[author]))

        input_file.write("%s\n" % ' '.join(author_ids))
        paper_count += 1
        
    csv_file.close()
    input_file.close()
    return author_id_mapping

def write_author_id_mapping(author_id_mapping):
    author_id_file = open(AUTHOR_ID_FILE_PATH, "w")
    for author in author_id_mapping:
        author_id_file.write("%d %s\n" % (author_id_mapping[author], author))
    author_id_file.close()

if __name__ == "__main__":
    author_id_mapping = build_intermediate_smpf_input()
    write_author_id_mapping(author_id_mapping)
    spmf_python_wrapper.run_spmf("FPClose", INPUT_FILE_PATH, OUTPUT_FILE_PATH, ["10%"])