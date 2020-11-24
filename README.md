# CourseProject

## Authors
* Elizabeth Wang
* Steven Pan

## Proposal
NOTE: We've uploaded a PDF (Proposal.pdf) with the same information as we hae below:

1. What are the names and NetIDs of all your team members? Who is the captain? 
* Elizabeth Wang, eyw3, Captain
* Steven Pan, stevenp6

2. Which paper have you chosen?
We have chosen the following paper: “Generating semantic annotations for frequent patterns with context analysis”

3. Which programming language do you plan to use?
Python

4. Can you obtain the datasets used in the paper for evaluation?
No

5. If you answer “no” to Question 4, can you obtain a similar dataset (e.g. a more recent version of the same dataset, or another dataset that is similar in nature)? 
Yes, a more recent version of the dataset that derives from the dataset used in the paper can be found here: https://dblp.org/faq/1474681.html

6. If you answer “no” to Questions 4 & 5, how are you going to demonstrate that you have successfully reproduced the method introduced in the paper? 
N/A

## Setup
0. Install bs4, urllib, and nltk (if they're not already installed)
1. Run setup.sh (`sh setup.sh`) from CourseProject/ to
* Build the csv file containing all (author list, title) entries. The code that builds this data file is here: utils/build_data_from_web.py. This script will create a directory called data/ and create a csv file called data.csv within that directory -- CSV file format: author1, author2, author3, ... etc, Title (where each line in the CSV file corresponds to a single paper)
* Create the libs/ directory and download spmf.jar, which is a JAR file for the SPMF library (download link is also here: http://www.philippe-fournier-viger.com/spmf/index.php?link=download.php)
* Builds frequent patterns for authors and title terms -- data/frequent_author_patterns.txt and data/frequent_title_term_patterns.txt, where all words are mapped to unique ids and the id mapping is cached in these 2 files respectively: data/author_id_mappings.txt and data/title_term_id_mappings.txt. The code that builds these files is here: utils/frequent_pattern_mining/build_frequent_patterns.py
* Removes redundancies from sequential frequent title patterns (data/title_term_id_mappings.txt) and creates a new file called data/minimal_title_term_patterns.txt containing these minimal patterns
* Builds a file to cache all mutual information values between pairs of author patterns

RELEVANT OUTPUT FILES FOR NEXT STAGE:
* data/frequent_author_patterns.txt (ID mappings: data/author_id_mappings.txt)
* data/minimal_title_term_patterns.txt (ID mappings: data/title_term_id_mappings.txt)
* data/author_mutual_info_patterns.txt

NOTE: utils/parse_patterns.py contains utility methods to parse patterns into data structures and write them to files, you may find these methods useful
