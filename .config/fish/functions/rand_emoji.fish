# Defined interactively
function rand_emoji
    set -l suffix_chars "🃁" "🃂" "🃍" "🃎" "🍞" "🌎" "🌍" "🌏" "🌌" "🌭" "🌮" "🌯" "🌝" "🌞" "🌟" "🌠" "🐘" "🐄" "🎅" "🧋" "🌸" "🌺" "🧁" "🦋" "🍭" "🍓" "🌾" "🌻" "☕" "✨" "🐑" "🍓" "🍯" "🍂" "🥧" "🍰" "🍪" "🍙" "🥐" "🥨" "🥞" "🍮" "🍋" "🍉" "🐻" "🐈" "🍊" "🧇" "❤️"

    random choice $suffix_chars
end
