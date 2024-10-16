#!/usr/bin/python3
import sys
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-multilingual-cased")

for l in sys.stdin.readlines():
    tokens = tokenizer.tokenize(l)
    print(tokens)
