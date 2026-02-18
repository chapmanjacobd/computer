#!/usr/bin/python3
import sqlite3
import sys
from collections import defaultdict

from library.utils import nums, printing, strings


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 script.py <database_path> [table_name]")
        sys.exit(1)

    db_path = sys.argv[1]
    table_name = sys.argv[2] if len(sys.argv) > 2 else "media"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        cursor.execute(f"SELECT path, size FROM {table_name}")
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")
        sys.exit(1)

    groups = defaultdict(list)
    for row in cursor:
        path = row['path']
        size = row['size']
        if path and size is not None:
            sentence = strings.path_to_sentence(path)
            words = sentence.split()
            for word in set(words):  # Use set() to avoid double-counting if a word appears twice in one path
                groups[word].append(size)
    conn.close()

    results = []
    for key, sizes in groups.items():
        total_size = sum(sizes)
        median_size = nums.safe_median(sizes)
        results.append(
            {
                'name': key,
                'total': total_size,
                'median': median_size,
                'count': len(sizes),
            }
        )
    results.sort(key=lambda x: x['total'])
    for result in results:
        result["total"] = strings.file_size(result["total"])
        result["median"] = strings.file_size(result["median"])
    printing.table(results)


if __name__ == "__main__":
    main()
