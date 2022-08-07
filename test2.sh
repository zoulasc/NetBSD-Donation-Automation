#!/bin/sh
for i
do
        python3 test.py $i >> donorDetails.txt
done
python database.py donorDetails.txt
