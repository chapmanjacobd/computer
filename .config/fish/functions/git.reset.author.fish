# Defined interactively
function git.reset.author
    git -c rebase.instructionFormat='%s%nexec GIT_COMMITTER_DATE="%cD" GIT_COMMITTER_NAME="%cn" GIT_COMMITTER_EMAIL="%ce"  git commit --amend --no-edit --reset-author --date="%cD"' rebase -i $argv
end
