#!/usr/bin/env bash
# https://gist.github.com/fdietze/6768a0970d7d732b7fbd7930ccceee2a

set -Eeuo pipefail # https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/#:~:text=set%20%2Du,is%20often%20highly%20desirable%20behavior.
shopt -s expand_aliases

SOURCE_LANG=$1
TARGET_LANG=$2
TEXT=$3
ENGINE=${4-google}

CACHEFILE="$HOME/.cache/trans_cache.sqlite"
q() { sqlite3 -column -init "" "$CACHEFILE" "$@"; }

if [ ! -s "$CACHEFILE" ]; then
rm -f "$CACHEFILE"
cat << EOF | sqlite3 -init "" "$CACHEFILE"
.bail on

CREATE TABLE translations(
  sourcelang TEXT NOT NULL,
  targetlang TEXT NOT NULL,
  engine TEXT NOT NULL,
  text TEXT NOT NULL,
  translation TEXT NOT NULL,

  PRIMARY KEY (sourcelang, targetlang, text, engine)
);
CREATE INDEX translations_sourcelang_idx ON translations (sourcelang);
CREATE INDEX translations_targetlang_idx ON translations (targetlang);
CREATE INDEX translations_engine_idx ON translations (engine);
CREATE INDEX translations_text_idx ON translations (text);
EOF
fi


# https://en.wikipedia.org/wiki/Unicode_equivalence#Combining_and_precomposed_characters
# https://www.effectiveperlprogramming.com/2011/09/normalize-your-perl-source/
alias nfc="perl -MUnicode::Normalize -CS -ne 'print NFC(\$_)'" # composed characters

# Normalize different unicode space characters to the same space
# https://stackoverflow.com/a/43640405
alias normalize_spaces="perl -CSDA -plE 's/[^\\S\\t]/ /g'"
alias normalize_unicode="normalize_spaces | nfc"

TEXT_ESCAPED=$(echo "$TEXT" | sed "s/'/''/g" | normalize_unicode) # escape single quotes for sqlite
TRANSLATED=$(q "SELECT translation FROM translations WHERE sourcelang = '$SOURCE_LANG' AND targetlang = '$TARGET_LANG' AND engine = '$ENGINE' AND text = '$TEXT_ESCAPED' LIMIT 1" | sed 's/\s*$//')

if [ -z "$TRANSLATED" ]; then
    TRANSLATED=$(trans -brief -from "$SOURCE_LANG" -to "$TARGET_LANG" -engine "$ENGINE" "$TEXT" | head -1 | sed 's/\s*$//' | normalize_unicode)
    if [ -n "$TRANSLATED" ]; then
        TRANSLATED_ESCAPED=$(echo "$TRANSLATED" | sed "s/'/''/g")
        q "INSERT OR IGNORE INTO translations (sourcelang, targetlang, engine, text, translation) VALUES ('$SOURCE_LANG', '$TARGET_LANG', '$ENGINE', '$TEXT_ESCAPED', '$TRANSLATED_ESCAPED')"
    fi
fi

echo "$TRANSLATED"
