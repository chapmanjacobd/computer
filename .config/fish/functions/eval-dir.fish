function eval-dir
    parallel --plain -j80 --line-buffer eval-file ::: (fd -tf . $argv)
end
