# Defined interactively
function link.gcs
    set urlpath (string replace 'gs://' '' "$argv")

    echo https://console.cloud.google.com/storage/browser/$urlpath
end
