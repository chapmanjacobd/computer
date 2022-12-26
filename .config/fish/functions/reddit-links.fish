function reddit-links
    cd ~/github/o/bulk-downloader-for-reddit/
    python -m bdfr download bdfr/ --authenticate --min-score 8 --disable-module SelfPost -S top --subreddit $argv | grep -vE (reddit-links-ignore)
    python -m bdfr download bdfr/ --authenticate --min-score 8 --disable-module SelfPost -S top -t year --subreddit $argv | grep -vE (reddit-links-ignore)
    python -m bdfr download bdfr/ --authenticate --min-score 8 --disable-module SelfPost -S top -t month -L 400 --subreddit $argv | grep -vE (reddit-links-ignore)
end
