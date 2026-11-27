# Defined interactively
function seq.alpha --wraps='perl'
    perl -e '$,="\n"; print ("'$argv[1]'" .. "'$argv[2]'")'
end
