function fileExtStatistics
    awk -F'.' '{print $NF}' | sort | uniq -c | sort -g
end
