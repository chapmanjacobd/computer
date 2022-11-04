# Defined interactively
function gdl-reddit
    cd ~/d/61_Photos_Unsorted/
    python -m bdfr download bdfr/ -S top --subreddit $argv
    python -m bdfr download bdfr/ -S top -t month -L 400 --subreddit $argv
    python -m bdfr download bdfr/ -S top -t year -L 400 --subreddit $argv
end
