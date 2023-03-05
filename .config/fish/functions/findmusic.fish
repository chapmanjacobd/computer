# Defined in - @ line 2
function findmusic
    set x (fd $argv[1] ~/Music/)
    echo $x
    cd $x[1]
end
