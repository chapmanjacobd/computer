function files.modified.hist --description 'Plot or list outlier recursive file modification times'
    argparse h/help o/outliers 'a/changed-after=' 'b/changed-before=' 'w/changed-within=' -- $argv
    or return

    if set -q _flag_help
        printf '%s\n' \
            'Usage: files.modified.hist [OPTIONS] DIR...' \
            '' \
            'Plot recursive regular-file modification times, one chart per path.' \
            'Defaults to the current directory when DIR is omitted.' \
            'With --outliers, print timestamps and paths outside the 1.5x IQR fences.' \
            '' \
            '  -a, --changed-after DATE|DURATION' \
            '  -b, --changed-before DATE|DURATION' \
            '  -w, --changed-within DURATION' \
            '  -o, --outliers'
        return
    end

    set -l changed_after ''
    set -l changed_before ''
    set -l changed_within ''
    if set -q _flag_changed_after
        set changed_after $_flag_changed_after
    end
    if set -q _flag_changed_before
        set changed_before $_flag_changed_before
    end
    if set -q _flag_changed_within
        set changed_within $_flag_changed_within
    end

    set -l dirs $argv
    if test (count $dirs) -eq 0
        set dirs .
    end

    for dir in $dirs
        printf '%s\n' "$dir"
        find -- "$dir" -type f -printf '%T@\0%p\0' |
            python -c '
import datetime
import os
import re
import statistics
import sys


def cutoff(value):
    if not value:
        return None
    if value.startswith("@"):
        return float(value[1:])

    duration = re.fullmatch(
        r"([0-9]+(?:\.[0-9]+)?)(seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h|days?|d|weeks?|w)",
        value,
        re.IGNORECASE,
    )
    if duration:
        amount = float(duration.group(1))
        unit = duration.group(2).lower()
        factors = {
            "s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1,
            "m": 60, "min": 60, "mins": 60, "minute": 60, "minutes": 60,
            "h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600,
            "d": 86400, "day": 86400, "days": 86400,
            "w": 604800, "week": 604800, "weeks": 604800,
        }
        return datetime.datetime.now().timestamp() - amount * factors[unit]

    parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed.timestamp()


after = cutoff(sys.argv[1])
before = cutoff(sys.argv[2])
within = cutoff(sys.argv[3])
if within is not None:
    after = within

raw = sys.stdin.buffer.read().split(b"\0")
records = []
for index in range(0, len(raw) - 1, 2):
    if not raw[index] or not raw[index + 1]:
        continue
    timestamp = float(raw[index])
    if after is not None and timestamp <= after:
        continue
    if before is not None and timestamp >= before:
        continue
    records.append((timestamp, os.fsdecode(raw[index + 1])))

if sys.argv[4] == "outliers":
    if len(records) < 2:
        raise SystemExit

    values = sorted(timestamp for timestamp, _ in records)
    quartiles = statistics.quantiles(values, n=4, method="inclusive")
    lower, upper = quartiles[0], quartiles[2]
    spread = upper - lower
    if spread == 0:
        is_outlier = lambda timestamp: timestamp != lower
    else:
        is_outlier = lambda timestamp: (
            timestamp < lower - 1.5 * spread
            or timestamp > upper + 1.5 * spread
        )

    for timestamp, path in sorted(records):
        if is_outlier(timestamp):
            stamp = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            print(f"{stamp}\t{path}")
else:
    for timestamp, _ in records:
        print(f"{timestamp:.6f}")
' "$changed_after" "$changed_before" "$changed_within" (if set -q _flag_outliers; echo outliers; else; echo graph; end) |
            if set -q _flag_outliers
                cat
            else
                lowcharts timehist -w 80
            end
    end
end
