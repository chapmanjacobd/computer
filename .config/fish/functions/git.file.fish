# Defined via `source`
function git.file
    git show "$argv[1]":"$argv[2..-1]"
end
