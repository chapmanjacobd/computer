import argparse
import subprocess
import os

def list_partitions(device):
    try:
        output = subprocess.check_output(['lsblk', '-no', 'NAME', device]).decode().strip().split()
        return [f"{device}{part}" for part in output if part != device.split('/')[-1]]
    except subprocess.CalledProcessError as e:
        print(f"Error listing partitions for {device}: {e}")
        return []

def is_mounted(partition):
    with open("/proc/mounts", "r") as f:
        mounts = f.readlines()
        return any(partition in line for line in mounts)

def mount_partition(partition):
    try:
        subprocess.check_output(['udisksctl', 'mount', '-b', partition], stderr=subprocess.STDOUT)
        print(f"Mounted {partition}")
    except subprocess.CalledProcessError as e:
        print(f"Error mounting {partition}: {e.output.decode().strip()}")

def main():
    parser = argparse.ArgumentParser(description='Mount partitions of given devices.')
    parser.add_argument('devices', nargs='+', help='Block devices (e.g., /dev/sdb)')
    args = parser.parse_args()

    for device in args.devices:
        partitions = list_partitions(device)

        if not partitions:
            print(f"{device} has no partitions.")
            continue

        for partition in partitions:
            print(f"Device: {device}, Partition: {partition}", end=' ')
            if is_mounted(partition):
                print(f"is already mounted.")
            else:
                print(f"is not mounted. Mounting now...")
                mount_partition(partition)

if __name__ == "__main__":
    main()

