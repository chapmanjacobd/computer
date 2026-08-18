#!/usr/bin/awk -f

{
    # Check if the line contains at least one space
    if (gsub(/ /, " ") < 1) {
        next
    }

    # Check if the line contains at least one alphabetic character
    if (!/[a-zA-Z]/) {
        next
    }

    # If both conditions are satisfied, print the line
    print
}
