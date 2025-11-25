# Defined via `source`
function lt.args
    echo "listen
-w
play_count=0
-k
delete-if-audiobook
--local-media-only
--fetch-siblings
if-audiobook
--fetch-siblings-max
2
/home/xk/lb/audio.db"
end
