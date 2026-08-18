BEGIN {
    indent = "    "
}
{
    # Remove leading and trailing whitespace from the line
    line = $0
    sub(/^[[:space:]]+/, "", line)
    sub(/[[:space:]]+$/, "", line)

    # Check for empty lines, comments, or section headers
    if (line ~ /^$/ || line ~ /^;/ || line ~ /^#/ || line ~ /^\[.*\]$/) {
        print line
    } else {
        # This is likely a key-value pair, indent it
        print indent line
    }
}
