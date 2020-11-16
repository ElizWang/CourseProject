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
