function tempdir
    set -l prefix temp
    if test (count $argv) -eq 1
        set prefix "temp-$argv[1]"
    end
    set -l dir /tmp/$prefix-(random)
    mkdir $dir
    cd $dir
end
