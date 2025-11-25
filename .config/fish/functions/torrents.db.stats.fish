# Defined interactively
function torrents.db.stats
    lb playlists ~/lb/torrents.db -pa
    duckdb ~/lb/torrents.db "select tracker, count(*), format_bytes(sum(size)::BIGINT) size from playlists WHERE time_deleted=0 group by 1 order by sum(size)"
    python ~/bin/lowcharts_size_hist.py (lb playlists ~/lb/torrents.db -pf --cols size | psub -s csv)
end
