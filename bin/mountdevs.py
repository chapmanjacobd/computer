#!/usr/bin/python3
import argparse
import re
import subprocess
from collections import defaultdict

import psutil


def list_partitions(device):
    try:
        output = subprocess.check_output(['lsblk', '-nplo', 'NAME', device]).decode().strip().split()
        return [s for s in output if s != device]
    except subprocess.CalledProcessError as e:
        print(f"Error listing partitions for {device}: {e}")
        return []


def get_mounts():
    partitions = psutil.disk_partitions(all=False)

    mounts = defaultdict(list)
    for partition in partitions:
        mounts[partition.device].append(partition.mountpoint)

    return mounts


def mount_partition(partition):
    try:
        output = subprocess.check_output(['sudo', 'udisksctl', 'mount', '-b', partition])
        output_decoded = output.decode().strip()
        match = re.search(r"Mounted (.*) at (.*)\.", output_decoded)
        if match:
            mount_point = match.group(2)
            return mount_point
        else:
            print(f"Mounted, but could not parse mount point from output: {output_decoded}")
            raise ValueError
    except subprocess.CalledProcessError as e:
        print(f"Error mounting {partition}: {e.output.decode().strip()}")


def main():
    parser = argparse.ArgumentParser(description='Mount partitions of given devices.')
    parser.add_argument('devices', nargs='+', help='Block devices (e.g., /dev/sdb)')
    args = parser.parse_args()

    mounts = get_mounts()
    for device in args.devices:
        partitions = list_partitions(device)

        if not partitions:  # assume partition-less disk
            partitions = [device]

        for partition in partitions:
            if partition not in mounts:
                mount_point = mount_partition(partition)
                mounts[partition].append(mount_point)


if __name__ == "__main__":
    main()
