function chrome-profile
    set -l dir ~/.chrome-profile/$argv[1]
    mkdir $dir
    env google-chrome --user-data-dir=$dir
end
