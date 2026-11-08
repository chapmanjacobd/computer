function git.remote.fork --description 'Keep origin as the upstream owner and point origin at my SSH fork'
    if not git rev-parse --git-dir >/dev/null 2>&1
        echo "Error: Not in a Git repository." >&2
        return 1
    end

    set -l current_url (git config --get remote.origin.url)
    if test -z "$current_url"
        echo "Error: No origin remote is configured." >&2
        return 1
    end

    set -l parsed
    if string match -q '*://*' -- "$current_url"
        set parsed (string match -r -- '^(?:https?|ssh|git)://(?:[^/@]+@)?([^/:]+)/(.*)$' "$current_url")
    else
        set parsed (string match -r -- '^(?:[^/@:]+@)?([^/:]+):(.*)$' "$current_url")
    end
    if test (count $parsed) -ne 3
        echo "Error: Cannot parse the host and repository from origin." >&2
        return 1
    end

    set -l site "$parsed[2]"
    set -l remote_path (string replace -r -- '/+$' '' "$parsed[3]")
    set -l repo (path basename -- "$remote_path")
    if test -z "$repo"; or contains -- "$repo" . ..
        echo "Error: Cannot parse the repository name from origin." >&2
        return 1
    end

    set -l new_url "git@$site:chapmanjacobd/$repo"
    if test "$current_url" != "$new_url"
        set -l upstream upstream
        set -l owner (string match -r -- '^([^/]+)/.+$' "$remote_path")
        if test (count $owner) -eq 2
            set upstream "$owner[2]"
        end
        if test "$upstream" = origin; or not git check-ref-format "refs/remotes/$upstream/HEAD" >/dev/null 2>&1
            set upstream upstream
        end
        if contains -- "$upstream" (git remote)
            echo "Error: Remote '$upstream' already exists; nothing changed." >&2
            return 1
        end

        git remote rename -- origin "$upstream"; or return $status
        if not git remote add origin "$new_url"
            git remote rename -- "$upstream" origin
            return 1
        end
    end

    set -l branch (git symbolic-ref --quiet --short HEAD)
    if contains -- "$branch" main master
        git config "branch.$branch.remote" origin; or return $status
        git config "branch.$branch.merge" "refs/heads/$branch"; or return $status
    end
    git remote -v
end
