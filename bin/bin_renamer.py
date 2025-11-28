#!/usr/bin/python3
import argparse
import json
import os
import subprocess
import sys

DEFAULT_BIN_DIR = os.path.expanduser("~/bin")
RENAMES_FILE = "bin_renames.jsonl"
FILE_ENCODING = "utf-8"
HELP_TIMEOUT = 2


def load_renames(args):
    """Loads previous renames from the JSONL file."""
    renames = []
    try:
        with open(args.renames_file, 'r', encoding=FILE_ENCODING) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        renames.append(json.loads(line))
                    except json.JSONDecodeError:
                        print(f"[WARN] Skipped malformed JSONL line in {args.renames_file}.")
        return renames
    except FileNotFoundError:
        print(f"[{RENAMES_FILE}] No previous renames file found. Starting fresh.")
        return []
    except Exception as e:
        print(f"Error loading renames from {args.renames_file}: {e}. Starting fresh.")
        return []


def save_rename_entry(original_name, new_name, entry_type, args):
    entry = {"type": entry_type, "original_name": original_name}

    if entry_type == "rename":
        entry["new_name"] = new_name

    try:
        with open(args.renames_file, 'a', encoding=FILE_ENCODING) as f:
            f.write(json.dumps(entry) + '\n')
        print(f"[LOG] Action '{entry_type}' saved to {args.renames_file}.")
    except Exception as e:
        print(f"[ERROR] Failed to save rename entry: {e}")


def get_file_details(filepath):
    """Get details about a file in ~/bin/."""
    filename = os.path.basename(filepath)
    file_size = os.path.getsize(filepath)

    # Try to read as text
    try:
        with open(filepath, 'r', encoding=FILE_ENCODING) as f:
            content = f.read()
        return filename, content, file_size, True
    except UnicodeDecodeError:
        # Binary file - try to get help output
        return filename, None, file_size, False


def get_help_output(filepath):
    """Try to get help output from a binary/script."""
    try:
        result = subprocess.run([filepath, "--help"], capture_output=True, text=True, timeout=HELP_TIMEOUT)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "[TIMEOUT] Command did not complete within 2 seconds."
    except Exception as e:
        return f"[ERROR] Could not execute: {e}"


def process_files(args):
    bin_dir = os.path.abspath(args.bin_dir)

    if not os.path.isdir(bin_dir):
        print(f"[FATAL] Directory not found: {bin_dir}")
        print("Please check the path or use the --bin-dir argument.")
        sys.exit(1)

    all_renames = load_renames(args)
    all_files = [f for f in os.listdir(bin_dir) if os.path.isfile(os.path.join(bin_dir, f))]

    mv_commands = []
    for i, filename in enumerate(sorted(all_files)):
        filepath = os.path.join(bin_dir, filename)

        # Check if already processed
        is_already_known = False
        for r in all_renames:
            if r.get('type') == 'skip' and r.get('original_name') == filename:
                is_already_known = True
                break

            if r.get('original_name') == filename:
                command = f"mv {bin_dir}/{filename} {bin_dir}/{r.get('new_name')}"
                mv_commands.append(command)
                is_already_known = True
                break
            elif r.get('new_name') == filename:
                is_already_known = True
                break

        if is_already_known:
            continue

        print(f"\n({i + 1}/{len(all_files)}) Processing: {filename}")
        print(f"\033[92m{filename}\033[0m")

        original_name, content, file_size, is_text = get_file_details(filepath)

        if is_text:
            print()
            print(content)
        else:
            # Binary file
            print(f"[Binary file, size: {file_size} bytes]")
            print()
            help_output = get_help_output(filepath)
            print(help_output)

        new_name = input(f"\nEnter new name: ").strip()
        if not new_name:
            new_name = filename.replace("-", ".").replace("_", ".")
        elif new_name != filename:
            new_name = new_name.replace("-", ".").replace("_", ".")

        if new_name == filename:
            save_rename_entry(filename, "", "skip", args)
            print("[SKIP] No new name entered. Logged as skip.")
        else:
            command = f"mv {bin_dir}/{filename} {bin_dir}/{new_name}"
            mv_commands.append(command)
            save_rename_entry(filename, new_name, "rename", args)

    if mv_commands:
        print("\n" + "=" * 50)
        print("Copy the lines below and run them in your shell:")
        print("=" * 50)
        for cmd in mv_commands:
            print(cmd)
        print("=" * 50)
    else:
        print("\n[INFO] No new rename commands were recorded this session.")


def main():
    """Parses arguments and starts the process."""
    parser = argparse.ArgumentParser(
        description="Interactive ~/bin File Renamer and Logger.", formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-d',
        '--bin-dir',
        type=str,
        default=DEFAULT_BIN_DIR,
        help=f"Path to the bin directory.\n(Default: {DEFAULT_BIN_DIR})",
    )
    parser.add_argument(
        '-r',
        '--renames-file',
        type=str,
        default=RENAMES_FILE,
        help=f"File to save the rename history (JSONL format).\n(Default: ./{RENAMES_FILE})",
    )

    args = parser.parse_args()

    process_files(args)


if __name__ == "__main__":
    main()
