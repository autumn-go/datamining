import os
import sys
import re

if __name__ == '__main__':
    handler = sys.stdin
    for line in handler:
        if not line:
            continue
        terms = line.strip().split(" ")
        wdict = {}
        for i in terms:
            if i not in wdict:
                wdict[i] = 1
            else:
                wdict[i] += 1
        for j in wdict:
            print j, wdict[j]

