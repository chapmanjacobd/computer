function dl_daily
    sed -i '$ d' .gitignore

    pip install --upgrade gallery-dl

    for dfolder in 61_Photos_Unsorted 91_New_Art 95_Memes
        ~/d/$dfolder/
        gallery-dl --input-file (sed 's|^|https://www.instagram.com/\0|' ~/mc/$dfolder-instagram.txt | shuf | head -20 | psub)
    end

    for db in ~/lb/reddit/*.db
        lb redditupdate $db --lookback 2
    end
    library redditupdate ~/lb/fs/tax.db --lookback 2
end
