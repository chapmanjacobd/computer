function eval-dir
    parallel --plain -j80 --line-buffer --joblog /home/xk/.jobs/s.(datestamp).log eval-file ::: (fd -tf . $argv)
end
