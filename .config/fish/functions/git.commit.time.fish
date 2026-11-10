function git.commit.time --description 'Print the committer time of a commit (default: HEAD) in ISO 8601'
    set -l commit HEAD
    if test (count $argv) -gt 0
        set commit $argv[1]
    end

    # %cI is strict ISO 8601 with the committer's timezone, which
    # git.commits.since (and `git log --since`) accepts directly.
    git show -s --format=%cI $commit
end
