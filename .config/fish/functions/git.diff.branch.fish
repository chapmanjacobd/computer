function git.diff.branch
    set -l base_branch (git main)
    set -l diff_args $argv
    if test (count $argv) -gt 0; and not string match -q -- '-*' $argv[1]
        set base_branch $argv[1]
        set diff_args $argv[2..-1]
    end

    git diff $base_branch...HEAD $diff_args
end
