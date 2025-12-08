package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"sort"
	"strings"
	"sync"
)

type CharCount [26]byte

func getCanonicalForm(word string) string {
	runes := []rune(strings.ToLower(word))
	sort.Slice(runes, func(i, j int) bool { return runes[i] < runes[j] })
	return string(runes)
}

func stringToCharCount(s string) CharCount {
	var counts CharCount
	for _, r := range strings.ToLower(s) {
		if r >= 'a' && r <= 'z' {
			counts[r-'a']++
		}
	}
	return counts
}

func (c CharCount) canSubtract(other CharCount) bool {
	for i := 0; i < 26; i++ {
		if other[i] > c[i] {
			return false
		}
	}
	return true
}

func (c CharCount) subtract(other CharCount) CharCount {
	var result CharCount
	for i := 0; i < 26; i++ {
		result[i] = c[i] - other[i]
	}
	return result
}

func (c CharCount) isEmpty() bool {
	for i := 0; i < 26; i++ {
		if c[i] != 0 {
			return false
		}
	}
	return true
}

type WordMap struct {
	data            map[string][]string
	canonicalCounts map[string]CharCount
}

func buildWordMap(dictionaryPath string) (*WordMap, error) {
	file, err := os.Open(dictionaryPath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	wordMap := make(map[string][]string)
	scanner := bufio.NewScanner(file)

	for scanner.Scan() {
		word := strings.TrimSpace(strings.ToLower(scanner.Text()))
		if word == "" {
			continue
		}

		// Check if word contains only letters
		isAlpha := true
		for _, r := range word {
			if r < 'a' || r > 'z' {
				isAlpha = false
				break
			}
		}

		if isAlpha {
			canonical := getCanonicalForm(word)
			wordMap[canonical] = append(wordMap[canonical], word)
		}
	}

	if err := scanner.Err(); err != nil {
		return nil, err
	}

	// Precompute canonical character counts
	canonicalCounts := make(map[string]CharCount, len(wordMap))
	for canonical := range wordMap {
		canonicalCounts[canonical] = stringToCharCount(canonical)
	}

	return &WordMap{
		data:            wordMap,
		canonicalCounts: canonicalCounts,
	}, nil
}

func cleanPhrase(phrase string) string {
	var sb strings.Builder
	for _, r := range strings.ToLower(phrase) {
		if r >= 'a' && r <= 'z' {
			sb.WriteRune(r)
		}
	}
	return sb.String()
}

func findAnagrams(phrase string, wordMap *WordMap, maxWords int) {
	cleanedPhrase := cleanPhrase(phrase)
	if cleanedPhrase == "" {
		fmt.Println("Input phrase is empty or contains no letters.")
		return
	}

	initialCounts := stringToCharCount(cleanedPhrase)

	// Use a map for deduplication with mutex for concurrent-safe access
	found := make(map[string]bool)
	var mu sync.Mutex

	// Pre-filter word map to only include words that could possibly fit
	validCanonicals := make([]string, 0, len(wordMap.data))
	for canonical := range wordMap.data {
		if initialCounts.canSubtract(wordMap.canonicalCounts[canonical]) {
			validCanonicals = append(validCanonicals, canonical)
		}
	}

	// Sort canonicals by length (longer first) for better pruning
	sort.Slice(validCanonicals, func(i, j int) bool {
		return len(validCanonicals[i]) > len(validCanonicals[j])
	})

	var search func(remaining CharCount, currentWords []string)
	search = func(remaining CharCount, currentWords []string) {
		// Base case: no letters left
		if remaining.isEmpty() {
			anagram := strings.Join(currentWords, " ")
			mu.Lock()
			if !found[anagram] {
				found[anagram] = true
				fmt.Println(anagram)
			}
			mu.Unlock()
			return
		}

		// Too many words
		if len(currentWords) >= maxWords {
			return
		}

		// Try every word whose canonical letters fit inside remaining
		for _, canonical := range validCanonicals {
			countsNeeded := wordMap.canonicalCounts[canonical]

			// Skip if we can't subtract this set of letters
			if !remaining.canSubtract(countsNeeded) {
				continue
			}

			// Valid → try using each actual word
			for _, word := range wordMap.data[canonical] {
				newRemaining := remaining.subtract(stringToCharCount(word))
				newWords := make([]string, len(currentWords), len(currentWords)+1)
				copy(newWords, currentWords)
				newWords = append(newWords, word)
				search(newRemaining, newWords)
			}
		}
	}

	search(initialCounts, []string{})
}

func main() {
	maxWords := flag.Int("n", 3, "Maximum number of words allowed in the anagram")
	dictionaryPath := flag.String("dictionary", "/usr/share/dict/words", "Path to the dictionary file")
	flag.Parse()

	if flag.NArg() < 1 {
		fmt.Println("Usage: anagram [options] <phrase>")
		flag.PrintDefaults()
		os.Exit(1)
	}

	phrase := flag.Arg(0)

	wordMap, err := buildWordMap(*dictionaryPath)
	if err != nil {
		fmt.Printf("Error: Dictionary file not found or could not be read: %v\n", err)
		return
	}

	if *maxWords < 1 {
		*maxWords = 1
	}

	findAnagrams(phrase, wordMap, *maxWords)
}
