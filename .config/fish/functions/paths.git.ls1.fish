function paths.git.ls1
    git ls-files --sparse --full-name -z | xargs -0 -I FILE -P 20 git log -1 --date=iso-strict-local --format='%ad %>(14) %cr %<(5) %an  %h ./FILE' -- FILE | sort --general-numeric-sort
end
