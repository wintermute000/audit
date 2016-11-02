#!/bin/bash
FILES=./*.log
for f in $FILES
do
  echo "Processing $f file..."
  # take action on each file. $f store current file name
  dos2unix $f
  python ./get-ospf-adj.py $f
done
