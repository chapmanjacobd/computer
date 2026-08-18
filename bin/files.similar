#!/usr/bin/python3
import argparse
import concurrent.futures
import os
import random
import time
from pathlib import Path


HDD_WORKERS = 10
FAST_STORAGE_WORKERS = 100


def hash_file(file_path, chunk_size=10, num_chunks=100):
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        return {b''}

    if file_size <= chunk_size:
        with open(file_path, 'rb') as f:
            return {f.read()}

    position_count = file_size - chunk_size + 1
    chunk_positions = sorted(
        random.sample(range(position_count), min(num_chunks, position_count))
    )

    hashes = set()
    with open(file_path, 'rb') as f:
        for pos in chunk_positions:
            f.seek(pos)
            hashes.add(f.read(chunk_size))
    return hashes


def process_file(file_path):
    return file_path, hash_file(file_path)


def jaccard_similarity(hashes_a, hashes_b):
    union = len(hashes_a | hashes_b)
    return len(hashes_a & hashes_b) / union if union else 0


def find_similar_files(file_hashes, threshold=0.7):
    similar_files = []
    file_paths = list(file_hashes.keys())
    if threshold <= 0:
        candidate_pairs = (
            (i, j)
            for i in range(len(file_paths))
            for j in range(i + 1, len(file_paths))
        )
    else:
        buckets = {}

        def indexed_pairs():
            for i, file_a in enumerate(file_paths):
                candidates = set()
                for chunk_hash in file_hashes[file_a]:
                    candidates.update(buckets.get(chunk_hash, ()))
                    buckets.setdefault(chunk_hash, []).append(i)
                yield from ((candidate, i) for candidate in candidates)

        candidate_pairs = indexed_pairs()

    for i, j in candidate_pairs:
        file_a, file_b = file_paths[i], file_paths[j]
        similarity = jaccard_similarity(file_hashes[file_a], file_hashes[file_b])
        if similarity >= threshold:
            similar_files.append((similarity, file_a, file_b))
    return sorted(similar_files, key=lambda t: t[0])


def rotational_storage(path):
    device = os.major(path.stat().st_dev), os.minor(path.stat().st_dev)
    sys_device = Path("/sys/dev/block") / f"{device[0]}:{device[1]}"
    try:
        current = sys_device.resolve(strict=True)
    except OSError:
        return None

    for current in (current, *current.parents):
        rotational = current / "queue" / "rotational"
        try:
            return rotational.read_text().strip() == "1"
        except OSError:
            pass
    return None


def worker_count(file_paths):
    storage_types = {rotational_storage(path) for path in file_paths}
    if True in storage_types:
        return HDD_WORKERS
    if storage_types == {False}:
        return FAST_STORAGE_WORKERS
    return None


def process_files(file_paths):
    workers = worker_count(file_paths)
    file_hashes = {}

    def collect(files, max_workers):
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_file, str(path)) for path in files]
            for future in concurrent.futures.as_completed(futures):
                path, file_hash = future.result()
                file_hashes[path] = file_hash

    if workers is not None:
        collect(file_paths, workers)
        return file_hashes

    # For storage that cannot be classified, start conservatively and raise
    # concurrency only when the initial sample completes quickly.
    initial_files = file_paths[:HDD_WORKERS]
    start = time.monotonic()
    collect(initial_files, HDD_WORKERS)
    elapsed = time.monotonic() - start
    remaining_files = file_paths[HDD_WORKERS:]
    if remaining_files:
        workers = FAST_STORAGE_WORKERS if elapsed < 0.5 else HDD_WORKERS
        collect(remaining_files, workers)
    return file_hashes


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

    file_hashes = process_files(list(yield_files(args.paths)))

    similar_files = find_similar_files(file_hashes, args.threshold)

    for similarity, file_a, file_b in similar_files:
        print('\t'.join([f"{similarity:.2f}", file_a, file_b]))


if __name__ == "__main__":
    main()
