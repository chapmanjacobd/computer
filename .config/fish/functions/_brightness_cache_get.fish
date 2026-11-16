function _brightness_cache_get --argument-names file now
    # Cache files hold "<nanosecond timestamp> <value>" and live in
    # XDG_RUNTIME_DIR. A short TTL keeps a held key from re-querying KScreen on
    # every step while still noticing changes made by other apps between holds.
    test -f $file; or return 1
    read -l timestamp value <$file
    test -n "$timestamp"; and test -n "$value"; or return 1

    set -l ttl 1000000000
    set -q BRIGHTNESS_CACHE_MS; and set ttl (math "$BRIGHTNESS_CACHE_MS * 1000000")
    test (math $now - $timestamp) -le $ttl; or return 1
    echo $value
end
