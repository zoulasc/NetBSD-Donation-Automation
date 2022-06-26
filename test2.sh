#!/bin/sh
echo "Donor Details">> donorDetails.txt
for i
do
	python3 test2.py $i >> donorDetails.txt
done
