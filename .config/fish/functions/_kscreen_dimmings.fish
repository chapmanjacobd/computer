function _kscreen_dimmings
    kscreen-doctor -o 2>&1 |
        sed -E 's/\x1B\[[0-9;]*m//g' |
        awk '
            function emit() {
                if (enabled) printf "%s\t%s\n", name, (dimming == "" ? 100 : dimming)
            }
            /^Output: / {
                emit()
                name = $3
                enabled = 0
                dimming = ""
                next
            }
            /^\tenabled$/ { enabled = 1 }
            /Brightness control:/ {
                if (match($0, /dimming to [0-9]+%/)) {
                    dimming = substr($0, RSTART, RLENGTH)
                    gsub(/[^0-9]/, "", dimming)
                }
            }
            END { emit() }
        '
end
