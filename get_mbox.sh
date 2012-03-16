#!/bin/bash

for year in 2010 2011
do
  for month in January February March April May June July August September October November December
  do
    wget http://lists.fedoraproject.org/pipermail/devel/$year-$month.txt.gz
  done
done

for month in January February March
do
wget http://lists.fedoraproject.org/pipermail/devel/2012-$month.txt.gz
done

gunzip *.gz --force
