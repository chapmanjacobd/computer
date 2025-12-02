# Defined interactively
function torrents.db.stats
    lb playlists ~/lb/torrents.db -pa
    duckdb ~/lb/torrents.db "select tracker, count(*) count, format_bytes(sum(size)::BIGINT) total_size, format_bytes(min(size)::BIGINT) min_size, format_bytes(max(size)::BIGINT) max_size from playlists WHERE time_deleted=0 group by 1 order by sum(size)"
    python ~/bin/lowcharts_size_hist.py (lb playlists ~/lb/torrents.db -pf --cols size | psub -s csv)
end
