function pushpatch --description 'Commit staged changes, push to a random branch, print a git am -3 command'
    argparse 'm/message=+' 'r/remote=' 'p/prefix=' 'h/help' -- $argv
    or return 1

    if set -q _flag_help
        printf '%s\n' \
            'Usage: pushpatch [-m MESSAGE]... [-r REMOTE] [-p PREFIX]' \
            '' \
            'Commit the staged changes, push that commit to a new branch' \
            'PREFIX-<random> on REMOTE (default: origin), then print:' \
            '' \
            '  curl -L https://github.com/OWNER/REPO/commit/SHA.patch | git am -3' \
            '' \
            'The URL comes from the push URL of REMOTE. Without -m, git opens' \
            'its usual commit message editor.'
        return 0
    end

    set -l remote origin
    set -q _flag_remote; and set remote $_flag_remote
    set -l prefix patch
    set -q _flag_prefix; and set prefix $_flag_prefix

    if git diff --cached --quiet
        echo 'pushpatch: nothing staged; stage the changes first' >&2
        return 1
    end

    set -l urls (git remote get-url --push $remote 2>/dev/null)
    if test (count $urls) -eq 0
        echo "pushpatch: no such git remote: $remote" >&2
        return 1
    end
    set -l push_url $urls[1]

    # git@github.com:owner/repo.git, ssh://git@github.com/owner/repo.git and
    # https://github.com/owner/repo.git all become https://github.com/owner/repo
    set -l web (string replace -r '^git@([^:]+):' 'https://$1/' -- $push_url)
    set web (string replace -r '^ssh://([^@/]+@)?' 'https://' -- $web)
    set web (string replace -r '^git://' 'https://' -- $web)
    set web (string replace -r '^https?://[^@/]+@' 'https://' -- $web)
    set web (string replace -r '^([^:]+://[^/:]+):[0-9]+/' '$1/' -- $web)
    set web (string replace -r '\.git/*$' '' -- $web)
    set web (string replace -r '/+$' '' -- $web)

    if not string match -qr '^https?://[^/]+/[^/]+/[^/]+$' -- $web
        echo "pushpatch: cannot make a web URL from the push URL of $remote: $push_url" >&2
        return 1
    end

    # A fresh branch for each patch, so an old patch URL keeps working
    set -l branch
    for attempt in (seq 10)
        set branch "$prefix-"(random 100000 999999)
        if not git ls-remote --exit-code --heads $remote $branch >/dev/null 2>&1
            break
        end
        set branch
    end
    if not set -q branch[1]
        echo 'pushpatch: could not find an unused branch name' >&2
        return 1
    end

    set -l commit_args
    if set -q _flag_message
        for message in $_flag_message
            set -a commit_args -m $message
        end
        git commit $commit_args >&2
    else
        git commit >&2
    end
    or begin
        echo 'pushpatch: git commit failed; nothing was pushed' >&2
        return 1
    end

    set -l sha (git rev-parse --verify HEAD)
    or begin
        echo 'pushpatch: cannot read HEAD after the commit' >&2
        return 1
    end

    if not git push $remote "HEAD:refs/heads/$branch" >&2
        echo "pushpatch: push failed; commit $sha is local only" >&2
        return 1
    end

    echo "pushpatch: pushed $sha to $remote branch $branch" >&2
    printf '%s\n' "curl -L $web/commit/$sha.patch | git am -3"
end
