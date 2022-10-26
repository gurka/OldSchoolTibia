#!/bin/bash
if [ "$#" -ne 1 ]
then
  echo "usage: $0 replay-directory"
  exit 1
fi

find "$1" -type f -name "*.trp" | sed 's/.*\/\(.*\)\/\(.*\)\.trp/\1\t\2.rec/' > replays.csv
