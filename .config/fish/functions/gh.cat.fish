function gh.cat
    curl -s -H "Accept:application/vnd.github.v3.raw" https://api.github.com/repos/$argv/contents/ |
        jq .[].download_url -r |
        xargs curl 2>/dev/null |
        bat
end
