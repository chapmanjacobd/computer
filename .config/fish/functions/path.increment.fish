# Defined in - @ line 2
function path.increment -a file
    # A counter followed by an extension: foo.2.txt -> foo.3.txt
    set -l match (string match -r '^(.*)\.(\d+)\.([^.]+)$' -- $file)
    if test $status -eq 0
        echo $match[2].(math $match[3] + 1).$match[4]
        return
    end

    # A counter with no extension: foo.2 -> foo.3
    set match (string match -r '^(.*)\.(\d+)$' -- $file)
    if test $status -eq 0
        echo $match[2].(math $match[3] + 1)
        return
    end

    # No counter yet: .hidden -> .hidden.1, foo -> foo.1, a.tar.gz -> a.tar.1.gz
    set -l ext (string replace -r '^\.' '' -- (path extension -- $file))
    if test -z "$ext"
        echo $file.1
    else
        set -l root (string replace -r -- '\.[^.]*$' '' $file)
        echo $root.1.$ext
    end
end
