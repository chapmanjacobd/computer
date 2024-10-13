#!/usr/bin/python3
import argparse
import concurrent.futures
import os
import random
from pathlib import Path


def hash_file(file_path, chunk_size=10, num_chunks=100):
    hashes = set()
    file_size = os.path.getsize(file_path)
    chunk_positions = sorted(random.sample(range(0, file_size - chunk_size), num_chunks))

    with open(file_path, 'rb') as f:
        for pos in chunk_positions:
            f.seek(pos)
            chunk = f.read(chunk_size)
            hashes.add(chunk)
    return hashes


def process_file(file_path):
    file_hash = hash_file(file_path)
    return file_path, file_hash


def jaccard_similarity(set_a, set_b):
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return intersection / union if union != 0 else 0


def find_similar_files(file_hashes, threshold=0.7):
    similar_files = []
    file_paths = list(file_hashes.keys())
    for i, file_a in enumerate(file_paths):
        for file_b in file_paths[i + 1 :]:
            similarity = jaccard_similarity(file_hashes[file_a], file_hashes[file_b])
            if similarity >= threshold:
                similar_files.append((similarity, file_a, file_b))
    return sorted(similar_files, key=lambda t: t[0])


def yield_files(paths):
    for path in paths:
        if path.is_file():
            yield path
        elif path.is_dir():
            for entry in path.rglob('*'):
                if entry.is_file():
                    yield entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', type=Path, help="Paths to files or folders to compare.")
    parser.add_argument('--threshold', '-t', type=float, default=0.01, help="Similarity threshold")
    args = parser.parse_args()

    file_hashes = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        futures = {executor.submit(process_file, str(path)): path for path in yield_files(args.paths)}

        for future in concurrent.futures.as_completed(futures):
            path, file_hash = future.result()
            file_hashes[path] = file_hash

    similar_files = find_similar_files(file_hashes, args.threshold)

    for similarity, file_a, file_b in similar_files:
        print('\t'.join([f"{similarity:.2f}", file_a, file_b]))


if __name__ == "__main__":
    main()
