def main [path: string] {
    if ($path | wc -c) == 0 {
        echo "Usage: nu script.nu <path_to_xlsx_file>"
        exit
    }

    open $path | transpose k v | each { |row|
        let sheet_name = $row.k
        let sheet_data = $row.v

        $"($sheet_name) " + ($sheet_data | headers | to csv)
    } | to text
}
