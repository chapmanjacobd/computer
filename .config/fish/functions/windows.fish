# Defined interactively
function windows
    wmctrl -G -l | awk -v OFS='\t' '{print $1, $2","$3","$4","$5","$6, substr($0, index($0,$7))}' | column -t -s \t
end
