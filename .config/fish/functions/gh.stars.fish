# Defined via `source`
function gh.stars
    for user in (cb | sed "s|https://github.com/\([^/?]*\)/\?.*|\1|")

        for lang in rust c lua shell python c%2B%2B c%23 markdown html
            printf '%s\n' https://github.com/$user?language=$lang&tab=stars
        end
    end
end
