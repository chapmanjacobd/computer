# Defined interactively
function filterfile
    set word $argv[(count $argv)] # last arg
    set files $argv[1..-2]

    for file in $files
        grep -i $word $file
        grep -iv $word $file | sponge $file
    end
end
