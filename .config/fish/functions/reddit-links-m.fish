function reddit-links-m
    cd ~/github/o/bulk-downloader-for-reddit/
    python -m bdfr download bdfr/ --authenticate --min-score 8 --disable-module SelfPost -S top -t month -L 500 --subreddit $argv | grep -vE (reddit-links-ignore)
end
