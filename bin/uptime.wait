#!/usr/bin/python3
import time
import argparse

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return uptime_seconds

def wait_until_uptime(target_uptime):
    current_uptime = get_uptime()
    if current_uptime < target_uptime:
        sleep_duration = target_uptime - current_uptime
        time.sleep(sleep_duration)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Wait until system uptime reaches a specified value.")
    parser.add_argument("target_uptime", type=float, help="Target uptime in seconds")

    args = parser.parse_args()

    wait_until_uptime(args.target_uptime)
