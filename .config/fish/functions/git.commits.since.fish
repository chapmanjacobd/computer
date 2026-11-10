function git.commits.since --description 'Print full hashes of commits since a given time'
    if test (count $argv) -eq 0
        echo "usage: git.commits.since <time>" >&2
        echo "  <time> accepts ISO 8601 output from git.commit.time, or any git date such as \"2 days ago\"" >&2
        return 1
    end

    set -l since $argv[1]

    git log --since="$since" --format=%H
end
