# Defined in /tmp/fish.KoRf4I/yt.big.fish @ line 2
function yt.big
    yt -f bestvideo[height<=1080][filesize<8000M]+bestaudio/best[height<=1080][filesize<8000M] --no-match-filter $argv
end
