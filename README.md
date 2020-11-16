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
0. Install bs4 and urllib (if they're not already installed)
1. Run setup.sh (`sh setup.sh`) from CourseProject/ to build the csv file containing all (author list, title) entries. The code that builds this data file is here: utils/build_data_from_web.py. This script will create a directory called data/ and create a csv file called data.csv within that directory

CSV file format: author1, author2, author3, ... etc, Title (where each line in the CSV file corresponds to a single paper)