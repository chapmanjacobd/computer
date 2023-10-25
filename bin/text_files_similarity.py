#!/usr/bin/python3

import itertools
import math
import sys
from collections import Counter

def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x]**2 for x in vec1.keys()])
    sum2 = sum([vec2[x]**2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        returnval = 0.0
    else:
        returnval = float(numerator) / denominator

    return returnval

def file_words(a):
    text = []
    for line in open(a).readlines():
        for word in line.strip().split():
            text.append(word)
    return text

for a, b in itertools.combinations(sys.argv[1:], 2):
    similarity = get_cosine(Counter(file_words(a)), Counter(file_words(b)))

    if similarity > 0.73:
        print(f"{similarity:.2f}% similarity between {a} and {b}")
