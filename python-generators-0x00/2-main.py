#!/usr/bin/python3
import sys
processing = __import__('1-batch_processing')

##### print processed users in a batch of 50
try:
    processing.batch_processing(50)
except BrokenPipeError:
    sys.stderr.close()

# window command: python 2-main.py | powershell -Command "$Input | Select-Object -First 5"
# linux command:  ./2-main.py | head -n 5
