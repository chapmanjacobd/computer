function mkcd --wraps='mkdir'
    mkdir $argv[1]
    cd $argv[1]
end
