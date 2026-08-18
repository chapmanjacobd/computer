#!/usr/bin/python3
import argparse
import os
import signal
import statistics
import time

import humanize
from library.utils.processes import exit_nicely

signal.signal(signal.SIGINT, exit_nicely)


def process_uptime(pid):
    uptimeSeconds = float(open("/proc/uptime").readline().split()[0])
    procStartJif = float(open(f"/proc/{pid}/stat").readline().split()[21])

    clockTicks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
    procStartSecondsBoot = procStartJif / clockTicks

    return uptimeSeconds - procStartSecondsBoot


def main():
    parser = argparse.ArgumentParser(description='Print IO stats about a process')
    parser.add_argument('--interval', '-d', type=int, default=2, help='Interval between updates')
    parser.add_argument('--init-bias', type=int, default=6, help='Number of intervals to rely on initial stats')

    parser.add_argument('pid', type=int, help='PID of the process')
    args = parser.parse_args()

    proc_io = f'/proc/{args.pid}/io'
    if not os.path.exists(proc_io):
        print(f"Error: PID {args.pid} does not exist")
        exit(2)

    print(f"Watching PID {args.pid} {open(f'/proc/{args.pid}/comm').read().strip()}")

    syscrs = []
    syscws = []
    rbytess = []
    wbytess = []

    def refresh() -> None:
        with open(proc_io) as f:
            rchar, wchar, syscr, syscw, rbytes, wbytes, cwbytes = [int(line.split()[1]) for line in f.readlines()]
            syscrs.append(syscr - syscrs[-1])
            syscws.append(syscw - syscws[-1])
            rbytess.append(rbytes - rbytess[-1])
            wbytess.append(wbytes - wbytess[-1])

    uptime = process_uptime(args.pid)
    with open(proc_io) as f:
        rchar, wchar, syscr, syscw, rbytes, wbytes, cwbytes = [int(line.split()[1]) for line in f.readlines()]
    syscrs = [int(syscr / (uptime / args.interval))] * args.init_bias
    syscws = [int(syscw / (uptime / args.interval))] * args.init_bias
    rbytess = [int(rbytes / (uptime / args.interval))] * args.init_bias
    wbytess = [int(wbytes / (uptime / args.interval))] * args.init_bias

    print("\n" * 4, end="")
    while os.path.exists(proc_io):
        refresh()

        print("\033[F" * 4)
        print("\033[1G\033[2K\n" * 3, end="", flush=True)  # clear full line

        print("\033[F" * 4)
        elapsed_intervals = len(syscrs)
        print(
            f'Read:    {humanize.naturalsize( rbytes, binary=True, format="%4.0f")} ({humanize.naturalsize( statistics.mean(rbytess), binary=True, format="%4.0f")} per interval)',
            f'Written: {humanize.naturalsize( wbytes, binary=True, format="%4.0f")} ({humanize.naturalsize(  statistics.mean(wbytess), binary=True, format="%4.0f")} per interval)',
            f'Syscalls: R {syscr} ({statistics.mean(syscrs):.1f} per interval) W {syscw} ({statistics.mean(syscws):.1f} per interval)',
            sep="\n",
        )

        time.sleep(args.interval)


if __name__ == "__main__":
    main()
