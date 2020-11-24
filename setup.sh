#!/bin/bash

if [ -d "data" ] 
then
  echo "data/ directory exists. WARNING: May override existing data.csv file" 
else
  echo "data/ directory doesn't exist. Creating directory now"
  mkdir data
fi

echo "Building data.csv file from DBLP dataset"
python utils/build_data_from_web.py

if [ -d "libs" ]
then
  echo "libs/ directory exists. WARNING: May override existing spmf.jar file" 
else
  echo "libs/ directory doesn't exist. Creating directory now"
  mkdir libs 
fi

echo "Downloading spmf.jar file to mine frequent patterns"
cd libs
wget http://www.philippe-fournier-viger.com/spmf/download-spmfjar.php -O spmf.jar
cd ..

echo "Mining frequent patterns"
python utils/frequent_pattern_mining/build_frequent_patterns.py

echo "Removing redudancies from sequential title term patterns"
python utils/remove_redundant_patterns.py

echo "Computing author-author pattern mutual information cache"
python utils/mutual_information_manager.py

echo "Checking to make sure all required files exist"
declare -a required_files=("data/frequent_author_patterns.txt" "data/author_id_mappings.txt" "data/title_term_id_mappings.txt" "data/title_term_id_mappings.txt", "data/author_mutual_info_patterns.txt")
for i in "${required_files[@]}"
do
if [ -e $i ]
then
    echo "$i exists!"
else
    echo "ERROR: $i doesn't exist" 
    exit
fi
done
echo "Success (everything was set up/generated correctly!)"
