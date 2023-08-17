# Defined interactively
function seqalpha
    perl -e '$,="\n"; print ("'$argv[1]'" .. "'$argv[2]'")'
end
