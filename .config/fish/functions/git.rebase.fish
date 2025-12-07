# Defined interactively
function git.rebase
    git -c rebase.instructionFormat='%s%nexec GIT_COMMITTER_DATE="%cD" git commit --amend --no-edit' rebase $argv
end
