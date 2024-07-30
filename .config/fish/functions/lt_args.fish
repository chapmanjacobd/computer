# Defined via `source`
function lt_args
    echo "listen
-w
play_count=0
-k
delete-if-audiobook
--local-media-only
--fetch-siblings
if-audiobook
/home/xk/lb/audio.db"
end
