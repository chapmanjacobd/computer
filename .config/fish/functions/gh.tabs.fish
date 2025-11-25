# Defined via `source`
function gh.tabs
    for user in (cb | sed "s|https://github.com/\([^/?]*\)/\?.*|\1|")

        for lang in rust c lua shell python c%2B%2B c%23 markdown html
            printf '%s\n' https://github.com/$user?language=$lang&tab=stars
        end

        echo "https://github.com/$user?tab=repositories&type=source
https://gist.github.com/$user
https://gist.github.com/$user/starred"
    end | lb linksdb ~/mc/links.db -c p1 --skip-extract -
end
