# Defined interactively
function redditadd --argument reddit_db
    lb redditadd --subreddits -v $reddit_db $argv[2..-1]

    ~/github/xk/reddit_mining/links/
    for subreddit in $argv[2..-1]
        if not test -e "$subreddit.csv"
            echo "octosql -o csv \"select path,score,'$subreddit' as subreddit from `../reddit_links.parquet` where lower(playlist_path) = '$subreddit' order by score desc \" > $subreddit.csv"
        end
    end | parallel -j6

    for subreddit in $argv[2..-1]
        sqlite.utils upsert --pk path --alter --csv --detect-types $reddit_db media $subreddit.csv
    end

    #fd -S-300K -S+2B -tf . ~/github/xk/reddit_mining/links/ -x rm
    #fd -S+99MB -tf . ~/github/xk/reddit_mining/links/ -x rm
end
