function timestamp
    date -Iminutes | cut -d+ -f1 | makeValidFilename
end
