# Defined interactively
function fileTypeVideos
    grep -E $argv 'avi$|mp4$|m4a$|m4v$|mov$|mkv$|webm$|ogv$|flv$|wmv$|ogm$'
end
