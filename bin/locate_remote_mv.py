#!/usr/bin/python3
import argparse
import os
import shlex
import stat
from copy import deepcopy
from pathlib import Path
from statistics import mean

from library.utils import arggroups, devices, path_utils, printing, processes, remote_processes, strings
from library.utils.iterables import flatten
from library.utils.log_utils import log


def locate_remote(args, hostname):
    import paramiko

    with paramiko.SSHClient() as ssh:
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        ssh.connect(hostname)

        r = remote_processes.cmd(ssh, "locate", "--existing", "--literal", "--ignore-case", *args.query, strict=False)
        paths = r.stdout.splitlines()
        if not paths:
            return

        files = []
        with ssh.open_sftp() as sftp:
            for path in paths:
                try:
                    file_stat = sftp.lstat(path)
                except FileNotFoundError:
                    log.debug('%s not found. Skipping!', path)
                    continue

                exclude_cond = all if args.strict_exclude else any
                if args.exclude and exclude_cond(ex in path.lower() for ex in args.exclude):
                    log.debug("matched path-exclude: %s", path)
                    continue

                if file_stat.st_mode and not stat.S_ISREG(file_stat.st_mode):
                    continue
                files.append({"path": path, "size": file_stat.st_size, "time_modified": file_stat.st_mtime})

            if not files:
                return

            files = sorted(files, key=lambda d: d['size'])

            table = deepcopy(files)
            table.append(
                {
                    "path": 'Total',
                    "size": sum(f["size"] for f in files),
                    "time_modified": mean(f["time_modified"] for f in files),
                }
            )
            table = [
                {
                    **d,
                    "size": strings.file_size(d['size']),
                    "time_modified": strings.relative_datetime(d['time_modified']),
                }
                for d in table
            ]
            printing.table(table)

            if devices.confirm(f'Move from {hostname}?'):
                if len(files) > 1:
                    selected_paths = processes.fzf_select([d['path'] for d in files])
                    files = [d for d in files if d['path'] in selected_paths]

                for d in files:
                    remote_path = d['path']
                    local_path = Path(args.prefix) / path_utils.parent(d['path']) / path_utils.basename(d['path'])
                    local_path.parent.mkdir(exist_ok=True)

                    if (
                        os.path.exists(remote_path)
                        and os.path.exists(local_path)
                        and os.path.samefile(remote_path, local_path)
                    ):
                        continue

                    print(remote_path)
                    print("-->", local_path)
                    sftp.get(remote_path, bytes(local_path))
                    os.utime(local_path, (d['time_modified'], d['time_modified']))
                    sftp.remove(remote_path)


def main():
    parser = argparse.ArgumentParser(description="SSH into hosts, locate files, and move them.")
    parser.add_argument("--exclude", '-E', nargs="+", default=[], action="extend", help="Exclude matching paths")
    parser.add_argument("--strict-exclude", action="store_true", help="All exclude args must resolve true")

    parser.add_argument("--flex", action='store_true', help="Split query on spaces")
    parser.add_argument("--hosts", nargs="+", help="Hosts to SSH into")
    parser.add_argument("--prefix", default="~/sync/video/", help="Local directory to move files to")
    arggroups.debug(parser)

    parser.add_argument("query", nargs="+", help="Query for the locate command")
    args = parser.parse_args()

    if args.flex:
        args.query = list(flatten(s for xs in args.query for s in shlex.split(xs) if s))
    args.exclude = [s.lower() for s in args.exclude]

    args.prefix = os.path.expanduser(args.prefix)
    os.makedirs(args.prefix, exist_ok=True)

    for hostname in args.hosts:
        locate_remote(args, hostname)


if __name__ == "__main__":
    main()
