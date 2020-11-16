import spmf_python_wrapper
import os

# NOTE: smpf uses a relative threshold for support
CSV_FILE_PATH = "data/data.csv"
INPUT_FILE_PATH = "data/temp_spmf_input.txt"
OUTPUT_FILE_PATH = "data/frequent_author_patterns.txt"

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

build_intermediate_smpf_input()
spmf_python_wrapper.run_spmf("FPClose", INPUT_FILE_PATH, OUTPUT_FILE_PATH, ["10%"])