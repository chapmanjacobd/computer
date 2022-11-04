function rgYTdl
    rg $argv | string sub --start=-11 | sed -e 's/^/https\:\/\/www\.youtube\.com\/watch\?v=/' | xargs youtube-dl -i --youtube-skip-dash-manifest
end
