# Defined in /tmp/fish.OvX88S/12hrCSVto24hr.fish @ line 1
function 12hrCSVto24hr
    awk -F',' -vOFS=',' '
function fail() {
        printf "Bad data at line %d: ", NR
        print
        next
    }
    {
        if (split($3, date_time, " ") != 3) fail()
        if (split(date_time[1], date, "/") != 3) fail()
        if (split(date_time[2], time, ":") != 3) fail()
        if (time[1] == 12) time[1] = 0
        if (date_time[3] == "PM") time[1] += 12
        $3 = sprintf("%.4d%.2d%.2d %.2d:%.2d:%.2d", date[3], date[1], date[2], time[1], time[2], time[3])
        print
    }'
end
