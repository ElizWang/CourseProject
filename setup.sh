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
python utils/frequent_pattern_mining/build_frequent_patterns.py
