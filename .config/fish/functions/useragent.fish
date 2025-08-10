# Defined interactively
function useragent
    python -c "from yt_dlp.utils.networking import random_user_agent; print(random_user_agent())"
end
