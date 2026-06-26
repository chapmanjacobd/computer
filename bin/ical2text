#!/bin/bash

BIN="$(cd "$(dirname "$0")" || exit ; pwd)"

source "${BIN}/lib-verbose.sh"

function awk_script() {
  cat <<'EOT'
BEGIN {
  fields = "";
}
{
  gsub(/\r$/, "");
  file = $1;
  key = $2;
  value = $3;
}
key == "BEGIN" && value == "VEVENT" {
  marker = file;
  gsub(/[_@].*/, "", marker);
  fields = "Marker:" marker "|File: " file;
  next;
}
key == "END" && value == "VEVENT" {
  print fields;
  marker = file;
  gsub(/[_@].*/, "", marker);
  fields = "Marker:" marker "|File: " file;
  next;
}
/^ / {
  gsub(/^ /, "");
  fields = fields $0;
  next;
}
{
  gsub(/;.*/, "", key);
  fields = fields "|" key ": " value;
}
EOT
}

grep -E '.?' /dev/null "$@" | awk -F ':' "$(awk_script)"
