function uncommit
    git reset --soft HEAD^
    git push -f
end
