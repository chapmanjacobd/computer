# Defined interactively
function redditadd --argument reddit_db
    set subreddits (echo $argv[2..-1] | string lower)
    lb redditadd --subreddits -v $reddit_db $subreddits

    ~/github/xk/reddit_mining/links/
    for subreddit in $subreddits
        if not test -e "$subreddit.csv"
            echo "octosql -o csv \"select path,score,'https://old.reddit.com/r/$subreddit/' as playlist_path from `../reddit_links.parquet` where lower(playlist_path) = '$subreddit' order by score desc \" > $subreddit.csv"
        end
    end | parallel -j8

    for subreddit in $subreddits
        sqlite-utils upsert --pk path --alter --csv --detect-types $reddit_db media $subreddit.csv
    end

    fd -S-300K -S+2B -tf . ~/github/xk/reddit_mining/links/ -x rm
    fd -S+99MB -tf . ~/github/xk/reddit_mining/links/ -x rm
end
