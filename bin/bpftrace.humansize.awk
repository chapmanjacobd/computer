#!/usr/bin/gawk -f
@include "/home/xk/bin/lib_human_size.awk"

BEGIN { FS = ": " }
{ print $1, human($2) }
