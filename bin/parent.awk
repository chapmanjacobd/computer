#!/usr/bin/awk -f
{
    if (match($0, /\/(.*)\//)) {
        print substr($0, RSTART, RLENGTH)
    } else {
        # print $0
    }
}
