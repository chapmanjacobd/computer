# Defined in /home/xk/.config/fish/functions/gitls.fish @ line 1
function gitls
    git ls-files --sparse --full-name -z | xargs -0 -I FILE -P 20 git log -1 --date=iso-strict-local --format='%ad %>(14) %cr %<(5) %an  %h ./FILE' -- FILE | sort --general-numeric-sort
end
