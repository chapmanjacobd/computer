function uncommit
    git reset --soft HEAD^
    git push --force-with-lease --force-if-includes
end
