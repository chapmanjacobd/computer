#!/usr/bin/python3
import argparse
import json
import re
import subprocess
from glob import glob
from typing import Dict, List


def get_block_device_info() -> List[Dict[str, str]]:
    block_devices = glob('/sys/block/*')
    udev_output = subprocess.check_output(['udevadm', 'info', '--json=short', *block_devices], text=True)
    udev_output = [json.loads(l) for l in udev_output.splitlines()]

    devices = [
        d
        for d in udev_output
        if not d["DEVPATH"].startswith("/devices/virtual") and (d.get("ID_FS_TYPE") or '') != "swap"
    ]
    return devices


def filter_and_sort_devices(devices: List[Dict[str, str]]) -> List[Dict[str, str]]:
    filtered_devices = []
    # grep -vE '^DEVNAME=/dev/(loop|zram)'
    for device in devices:
        if not re.match(r'^/dev/(loop|zram)', device['DEVNAME']):
            filtered_devices.append(device)

    # Convert USEC_INITIALIZED to an integer for numerical sorting
    sorted_devices = [
        d['DEVNAME'] for d in sorted(filtered_devices, key=lambda x: int(x.get('USEC_INITIALIZED', 0)), reverse=True)
    ]

    return sorted_devices


def get_mountpoints():
    lsblk_output = subprocess.check_output(['lsblk', '-J', '-o', 'PATH,MOUNTPOINT'], text=True)
    data = json.loads(lsblk_output)
    return {
        d["path"]: d["mountpoint"]
        for d in data['blockdevices']
        if not d["mountpoint"] or (d["mountpoint"] and d["mountpoint"] != "[SWAP]")
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Finds and displays block devices/partitions, sorted by initialization time"
    )
    parser.add_argument('--mountpoints', action='store_true')
    parser.add_argument('--unmounted', action='store_true')

    args = parser.parse_args()

    device_data = get_block_device_info()
    sorted_devices = filter_and_sort_devices(device_data)
    mounts = get_mountpoints()

    for base_path in sorted_devices:
        base_mount = {part_path: mountpoint for part_path, mountpoint in mounts.items() if part_path == base_path}
        partition_mounts = {
            part_path: mountpoint
            for part_path, mountpoint in mounts.items()
            if part_path.startswith(base_path) and part_path != base_path
        }

        if not partition_mounts:
            for dev_path, mountpoint in base_mount.items():
                if args.mountpoints and mountpoint:
                    print(mountpoint)
                else:
                    if args.unmounted:
                        if not mountpoint:
                            print(dev_path)
                    else:
                        print(dev_path)
        else:
            for part_path, mountpoint in partition_mounts.items():
                if args.mountpoints and mountpoint:
                    print(mountpoint)
                else:
                    if args.unmounted:
                        if not mountpoint:
                            print(part_path)
                    else:
                        print(part_path)
