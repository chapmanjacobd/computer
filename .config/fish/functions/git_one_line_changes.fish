# Defined interactively
function git_one_line_changes
    git log --pretty='SHA %H' --numstat |
        awk '/^SHA/ {sha = $2} NF == 3 && $1 == 1 && $2 == 1 {print "git show --oneline --unified=0", sha, "--", $3}' |
        sh |
        sed -n '/^- /{;s/^-[ \t]*//;h;};/^+ /{s/^+[ \t]*//;H;g;s/\n/$/;p;}' |
        sort |
        uniq -c |
        sort -rn | less -FSRXc
end
