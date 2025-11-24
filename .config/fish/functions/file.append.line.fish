# Defined interactively
function file.append.line
    echo $argv[2..-1] >>$argv[1]
end
