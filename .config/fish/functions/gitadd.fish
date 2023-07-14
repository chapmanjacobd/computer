# Defined via `source`
function gitadd
    set size (git status --short | grep -v '^ D' | awk '{print substr($0,4)}' | xargs -n 1 du -b | awk '{print $1}' | sum)
    if test $size -lt 1048576 # 1MiB
        git add .
    else
        echo Untracked files are (numfmt --to=iec $size)

        git status --short | grep -v '^ D' | awk '{print substr($0,4)}' | xargs -n 1 du -h
        git diff --stat --relative
        return 1
    end
end
