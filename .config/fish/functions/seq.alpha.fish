# Defined interactively
function seq.alpha
    perl -e '$,="\n"; print ("'$argv[1]'" .. "'$argv[2]'")'
end
