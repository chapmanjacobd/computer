function eval-dir
    parallel --plain -j80 --line-buffer --joblog /home/xk/.jobs/joblog_jobs.log repeat eval-file ::: (fd -tf . $argv)
end
