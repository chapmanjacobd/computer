# Defined interactively
function common_prefix
    string split ' ' "$argv" | sed -e 'N;s/^\(.*\).*\n\1.*$/\1\n\1/;D'
end
