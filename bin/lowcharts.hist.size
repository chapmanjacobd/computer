#!/usr/bin/python3
import argparse
import sys
from pathlib import Path
from typing import List, Tuple

import numpy as np
from library.utils import strings


def create_fixed_bins_histogram(data: List[int]) -> Tuple[np.ndarray, np.ndarray]:
    if not data:
        return np.array([]), np.array([])

    base_edges = [2, 5, 10]
    multipliers = base_edges + [n * 10 for n in base_edges] + [n * 100 for n in base_edges]

    unit_multiplier = 1024
    units = [1, unit_multiplier, unit_multiplier**2, unit_multiplier**3, unit_multiplier**4]  # Bytes, KB, MB, GB, TB

    start = 0
    bin_edges = [start]
    for unit in units[1:]:  # start from KB
        for m in multipliers:
            bin_edges.append(int(m * unit))
    bin_edges.append(float('inf'))  # type: ignore

    bin_counts, bin_edges = np.histogram(data, bins=bin_edges)
    return bin_counts, bin_edges


def format_histogram(bin_counts: np.ndarray, bin_edges: np.ndarray, bar_char: str = "#", max_width: int = 50) -> str:
    if not bin_counts.size:
        return "No data to display."

    output = []
    max_count = max(bin_counts) if bin_counts.size > 0 else 0

    labels = []
    for i in range(len(bin_edges) - 1):
        start_val = bin_edges[i]
        end_val = bin_edges[i + 1]

        if end_val == float('inf'):
            labels.append("1PB+")
        else:
            start_str = strings.file_size(start_val)
            end_str = strings.file_size(end_val)
            labels.append(f"{start_str} - {end_str}")

    max_label_len = max(len(s) for s in labels)

    first_positive_index = -1
    last_positive_index = -1
    for i, count in enumerate(bin_counts):
        if count > 0:
            if first_positive_index == -1:
                first_positive_index = i
            last_positive_index = i

    if first_positive_index != -1:
        for i in range(first_positive_index, last_positive_index + 1):
            count = bin_counts[i]
            bar_length = int(max_width * (count / max_count)) if max_count > 0 else 0
            bar = bar_char * bar_length
            output.append(f"{labels[i].ljust(max_label_len)} | {bar} {count}")

    return "\n".join(output)


def main(args: argparse.Namespace):
    if args.path == '-':
        data = [int(line.strip()) for line in sys.stdin.readlines() if line.strip().isdigit()]
    else:
        data = [int(line.strip()) for line in Path(args.path).read_text().splitlines() if line.strip().isdigit()]

    if not data:
        print("No data received.  Make sure the input file contains only integers representing file sizes in bytes.")
        return

    bin_counts, bin_edges = create_fixed_bins_histogram(data)

    if bin_counts.size > 0:
        histogram_output = format_histogram(bin_counts, bin_edges, args.bar, args.width)
        print(histogram_output)
    else:
        print("Could not generate histogram.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a histogram with fixed size bins from data")
    parser.add_argument("-w", "--width", type=int, default=50, help="Maximum width of the histogram")
    parser.add_argument("--bar", type=str, default="#", help="Character to use for the histogram bars")

    parser.add_argument("path", help="Path to the file containing file sizes in bytes (one per line)")
    args = parser.parse_args()
    main(args)
