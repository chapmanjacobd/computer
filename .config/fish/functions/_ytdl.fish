function _ytdl
    yt-dlp \
        -o "%(ie_key,extractor_key,extractor)s/%(uploader,uploader_id,channel,channel_id,creator,artist,author,album)s/%(title).200B_%(view_count)3.2D_[%(id).60B].%(ext)s" \
        --download-archive ~/.local/share/yt_archive.txt --retries 13 --extractor-retries 13 \
        --extractor-args youtubetab:skip=authcheck --embed-metadata \
        --no-progress --sleep-requests 1 \
        --reject-title "Trailer|Sneak Peek|Preview|Review|Teaser|Promo|Live |Stream|Twitch|Crypto|Meetup|Montage|Bitcoin|Makeup|Apology|Clip |Top 10|Top Ten|Panel|Red Carpet Premiere|Now Playing|In Theaters| Scene |Announcement|First Look|Final Look|Outtakes|360|World Premiere|Event|TV Spot|Advert|campaign|Horror|Graphics Card| GPU | Terror| AWARD|Ceremony" \
        # --cookies-from-browser firefox \
        # --user-agent "Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0" \
        $argv
end
