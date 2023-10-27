# Defined via `source`
function mam_dl
    load_env_mam
    ~/Downloads/
    for id in $argv
        curl -OJs -b mam_id=$MAM_COOKIE https://www.myanonamouse.net/tor/download.php?tid=$id
    end
end
