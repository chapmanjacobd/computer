function chrome-profile
    set -l dir ~/.chrome-profile/$argv[1]
    mkdir -p $dir
    env google-chrome --user-data-dir=$dir
end
