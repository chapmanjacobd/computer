function getdev
    scp -F ~/.ssh/config_dev 'dev@unli.xyz:/home/dev/*' ./
end
