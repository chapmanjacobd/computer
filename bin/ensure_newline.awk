#!/usr/bin/awk -f
{
    print $0
}
END {
    if (NR > 0 && substr(RS, length(RS)) != "\n") {
        print ""
    }
}
