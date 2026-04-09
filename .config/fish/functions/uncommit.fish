function uncommit
    git reset --soft HEAD^
    echo git push --force-with-lease --force-if-includes
end
