#!/usr/bin/python3
import argparse
from collections import Counter, defaultdict
from typing import Dict, List


def get_canonical_form(word: str) -> str:
    return "".join(sorted(word.lower()))


def build_word_map(dictionary_path: str) -> Dict[str, List[str]]:
    word_map = defaultdict(list)
    try:
        with open(dictionary_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                word = line.strip().lower()
                if word and word.isalpha():
                    canonical = get_canonical_form(word)
                    word_map[canonical].append(word)
        return dict(word_map)
    except FileNotFoundError:
        print(f"Error: Dictionary file not found at {dictionary_path}")
        return {}


def find_anagrams_generalized(phrase: str, word_map: Dict[str, List[str]], max_words: int):
    cleaned_phrase = "".join(filter(str.isalpha, phrase)).lower()
    initial_counts = Counter(cleaned_phrase)

    if not initial_counts:
        print("Input phrase is empty or contains no letters.")
        return

    # Precompute canonical Counter objects
    canonical_counters = {canonical: Counter(canonical) for canonical in word_map}

    found = set()

    def search(remaining_counts: Counter, current_words: List[str]):
        # Base case: no letters left
        if not remaining_counts:
            anagram = " ".join(current_words)
            if anagram not in found:
                found.add(anagram)
                print(anagram)
            return

        # Too many words
        if len(current_words) >= max_words:
            return

        # Try every word whose canonical letters fit inside remaining_counts
        for canonical, words in word_map.items():
            counts_needed = canonical_counters[canonical]

            # Skip if we can't subtract this set of letters
            if any(counts_needed[c] > remaining_counts[c] for c in counts_needed):
                continue

            # Valid → try using each actual word
            for word in words:
                new_remaining = remaining_counts - Counter(word)
                search(new_remaining, current_words + [word])

    search(initial_counts, [])


def main():
    parser = argparse.ArgumentParser(
        description="Finds anagrams for an input phrase using a dictionary file, supporting N-word anagrams."
    )
    parser.add_argument('-n', '--words', type=int, default=3, help="Maximum number of words allowed in the anagram")
    parser.add_argument('--dictionary', type=str, default='/usr/share/dict/words', help="Path to the dictionary file.")

    parser.add_argument('phrase', type=str, help="The input phrase to find anagrams for (e.g., 'elvis')")
    args = parser.parse_args()

    word_map = build_word_map(args.dictionary)
    if not word_map:
        return

    max_words = max(1, args.words)
    find_anagrams_generalized(args.phrase, word_map, max_words)


if __name__ == '__main__':
    main()
