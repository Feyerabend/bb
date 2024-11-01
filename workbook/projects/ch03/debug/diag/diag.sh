#!/bin/sh
clear
python3 dvm.py --input sample.b > log.txt
python3 diag.py < log.txt
