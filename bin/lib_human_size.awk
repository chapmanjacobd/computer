function human(bytes) {
    units = "B KB MB GB TB PB EB ZB YB"
    split(units, u_array, " ")

    i = 1
    while (bytes >= 1024 && i < length(u_array)) {
        bytes /= 1024
        i++
    }
    return sprintf("%.2f %s", bytes, u_array[i])
}
