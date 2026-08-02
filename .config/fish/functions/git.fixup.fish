# Defined interactively
function git.fixup --argument-names target
    if test -n "$target"
        set commit $target
    else
        set commit (git.select.commit "fixup commit > ")
    end

    if test -z "$commit"
        return
    end

    set -l target_subject (git log -1 --format=%s $commit)
    set -l clean_subject (string replace -r '^(fixup! |squash! |amend! )+' '' $target_subject)
    
    git commit -m "fixup! $clean_subject"
    # git push
end
