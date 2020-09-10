import os
import sys
import re

if __name__ == '__main__':
    handler = sys.stdin
    old_key = ""
    count = 0
    for line in handler:
        if not line:
            continue
        terms = line.strip().split(" ")
        key = terms[0]
        if key != old_key:
            if old_key:
                print old_key, count
                count = 0
        old_key = key
        count += 1
    if old_key:
        print old_key, count
        count = 0


