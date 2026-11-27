function git.blame --wraps='python3' --description 'Show diff hunks with blame metadata'
    python3 /home/xk/bin/git-diff-blame $argv | delta --syntax-theme GitHub --max-line-length 1024
    set -l pipeline_status $pipestatus
    return $pipeline_status[1]
end
