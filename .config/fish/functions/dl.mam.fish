# Defined via `source`
function dl.mam
    load.env.mam
    ~/Downloads/
    for id in $argv
        set id (echo $id | grep -i '.net/t/' | sed 's|https://www.myanonamouse.net/t/||')
        curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid=$id
        sleep 2
    end
end
