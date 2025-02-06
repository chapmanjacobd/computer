#!/usr/bin/python3
import argparse
import os
import time
import pathlib
import subprocess
import concurrent.futures

def get_mount_info_linux(path):
    """Get mount point and options for the given path using the `mount` command (Linux-specific).
       Correctly parses mount options even in formats like 'device: on mountpoint type fstype (options)'
    """
    path = os.path.abspath(path)
    try:
        result = subprocess.run(['mount'], capture_output=True, text=True, check=True)
        mount_output = result.stdout
    except subprocess.CalledProcessError as e:
        return "Error executing mount command", f"Error: {e}"

    mount_point = "Mount point not found"
    mount_options = "N/A"

    best_match_len = 0
    best_match_options = None
    best_match_mountpoint = None

    for line in mount_output.strip().splitlines():
        parts = line.split(maxsplit=5) # Split into at most 6 parts, handles spaces in options

        if len(parts) >= 4: # Need at least device, 'on', mountpoint, 'type'
            mount_p_candidate_index = -1
            options_start_index = -1

            # Heuristic to find mountpoint and options based on common 'mount' output patterns
            if parts[1] == 'on': # Format like 'device on mountpoint type ... (options)'
                mount_p_candidate_index = 2
                options_start_index = 3 # Options might start from index 3 or later depending on 'type' and 'fstype' fields

            elif ':' in parts[0] and parts[1] == 'on': # Format like 'device: on mountpoint type ... (options)'
                mount_p_candidate_index = 2
                options_start_index = 3

            if mount_p_candidate_index != -1:
                mount_p = parts[mount_p_candidate_index]


                if path.startswith(mount_p):
                    if len(mount_p) > best_match_len: # Find the longest prefix match
                        best_match_len = len(mount_p)
                        best_match_mountpoint = mount_p

                        options_str = ""
                        # Reconstruct options string by joining parts from options_start_index onwards
                        for i in range(options_start_index, len(parts)):
                            options_str += parts[i] + " "
                        options_str = options_str.strip() # Remove trailing space

                        # Extract options within parentheses if present (common format)
                        if '(' in options_str and ')' in options_str:
                            start_paren = options_str.find('(')
                            end_paren = options_str.rfind(')') # in case of nested parens, take last ')'
                            best_match_options = options_str[start_paren+1:end_paren] # Extract content between parentheses
                        else:
                            best_match_options = options_str # If no parentheses, use the whole remaining string


    if best_match_mountpoint:
        mount_point = best_match_mountpoint
        mount_options = best_match_options
    else:
        mount_point = "Mount point not found in mount output"
        mount_options = "N/A"


    return mount_point, mount_options

def read_chunk(file_path, offset, chunk_size):
    """Reads a chunk of a file from a given offset and size."""
    try:
        with open(file_path, 'rb') as f:
            f.seek(offset)
            return f.read(chunk_size)
    except Exception as e:
        return f"Error reading chunk from {file_path} at offset {offset}: {e}"

def perform_stat(file_path):
    """Performs os.stat() on a file and handles potential exceptions."""
    try:
        return os.stat(file_path)
    except Exception as e:
        return f"Error statting {file_path}: {e}"

def read_partial(file_path):
    """Reads the first 128KB of a file and handles exceptions."""
    try:
        with open(file_path, 'rb') as f:
            return f.read(128 * 1024)
    except Exception as e:
        return f"Error reading 128KB from {file_path}: {e}"


def benchmark_folder(folder_path):
    """Performs read-only benchmark on the given folder."""

    print(f"Benchmarking folder: {folder_path}")

    mount_point, mount_options = get_mount_info_linux(folder_path)
    print(f"Mount Point: {mount_point}")
    print(f"Mount Options: {mount_options}")
    print("-" * 40)

    folder_p = pathlib.Path(folder_path)

    # 1. Time to rglob(*)
    start_time = time.perf_counter()
    all_files = list(folder_p.rglob('*')) # Force iterator to evaluate and time
    rglob_time = time.perf_counter() - start_time
    print(f"Time to rglob('*'): {rglob_time:.4f} seconds")

    file_paths = [f for f in all_files if f.is_file()]
    num_files_rglob = len(file_paths)
    print(f"Number of files found by rglob(*): {num_files_rglob}")

    if not file_paths:
        print("No files found in the specified folder. Benchmark incomplete.")
        return

    # 2. Time to stat() all nested files - Parallelized
    stat_time = 0
    stat_error_count = 0
    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor: # Default worker count is usually CPU count, good for stat
        futures_stat = [executor.submit(perform_stat, file_path) for file_path in file_paths]
        concurrent.futures.wait(futures_stat)
        stat_time = time.perf_counter() - start_time

        for future in futures_stat:
            if isinstance(future.result(), str) and future.result().startswith("Error"):
                print(future.result())
                stat_error_count += 1


    print(f"Time to stat() {num_files_rglob} files (Parallel): {stat_time:.4f} seconds")
    if stat_error_count > 0:
        print(f"Warning: {stat_error_count} stat() errors occurred.")


    # 3. Time to read the first 128kb of the largest 10000 files - Parallelized
    file_sizes = [(f, f.stat().st_size) for f in file_paths] # need file sizes for sorting again
    file_sizes.sort(key=lambda item: item[1], reverse=True) # Sort by size descending
    largest_files_for_partial_read = file_sizes[:min(10000, len(file_sizes))]

    partial_read_total_size_kb = 0
    partial_read_count = 0
    partial_read_time = 0
    partial_read_error_count = 0


    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor() as executor: # Default worker count is usually CPU count, good for IO bound partial reads
        futures_partial_read = [executor.submit(read_partial, file_p) for file_p, size in largest_files_for_partial_read]
        concurrent.futures.wait(futures_partial_read)
        partial_read_time = time.perf_counter() - start_time


        for future in futures_partial_read:
            result = future.result()
            if isinstance(result, str) and result.startswith("Error"):
                print(result)
                partial_read_error_count += 1
            else:
                partial_read_total_size_kb += 128
                partial_read_count += 1


    print(f"Time to read first 128KB of largest {partial_read_count} files ({partial_read_total_size_kb/1024:.2f}MB total) (Parallel): {partial_read_time:.4f} seconds")
    if partial_read_error_count > 0:
         print(f"Warning: {partial_read_error_count} partial read errors occurred.")


    # 4. Time to read() the largest file - Parallelized (already parallelized in previous version)
    largest_file_path = file_sizes[0][0] # Already sorted, first is largest
    largest_file_size = file_sizes[0][1]
    largest_file_size_mb = largest_file_size / (1024*1024)
    parallel_chunk_size = 256 * 1024 * 1024 # 256MB
    num_streams = 4
    parallel_read_total_size_mb = (parallel_chunk_size * num_streams) / (1024 * 1024)
    parallel_read_time = 0

    start_time = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_streams) as executor:
        futures = []
        offsets = [0, largest_file_size // 4, largest_file_size // 2, largest_file_size * 3 // 4] # Beginning, quarter, half, three-quarter
        for i in range(num_streams):
            offset = offsets[i]
            if offset + parallel_chunk_size > largest_file_size: # Adjust chunk size if near end of file
                chunk_size_adjusted = max(0, largest_file_size - offset)
            else:
                chunk_size_adjusted = parallel_chunk_size

            if chunk_size_adjusted > 0: # Only submit task if there's something to read
                futures.append(executor.submit(read_chunk, largest_file_path, offset, chunk_size_adjusted))

        concurrent.futures.wait(futures) # Wait for all tasks to complete
        parallel_read_time = time.perf_counter() - start_time

        error_count = 0
        for future in futures:
            if isinstance(future.result(), str) and future.result().startswith("Error"): # Check for error result
                print(future.result()) # Print error message
                error_count += 1

        if error_count == 0: # Only print time if no errors occurred during parallel read
            print(f"Time to parallel read largest file '{largest_file_path.name}' ({largest_file_size_mb:.2f}MB) - {num_streams} streams x {parallel_chunk_size/(1024*1024):.0f}MB ({parallel_read_total_size_mb:.2f}MB total requested): {parallel_read_time:.4f} seconds")
        else:
            parallel_read_time = 0 # Set to 0 to avoid misleading time in case of errors


    print("-" * 40)
    print("Benchmark Complete.")


def main():
    parser = argparse.ArgumentParser(description="Perform read-only benchmark on a folder (Linux-specific) with parallel operations.") # Updated description
    parser.add_argument("folder_path", help="Path to the folder to benchmark.")
    args = parser.parse_args()

    folder_path = args.folder_path
    if not os.path.isdir(folder_path):
        print(f"Error: '{folder_path}' is not a valid directory.")
        return

    benchmark_folder(folder_path)

if __name__ == "__main__":
    main()
