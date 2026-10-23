function git.blame --description 'Show diff hunks with blame metadata'
    python3 /home/xk/bin/git-blame-diff.py $argv | delta --syntax-theme GitHub --max-line-length 1024
    set -l pipeline_status $pipestatus
    return $pipeline_status[1]
end
