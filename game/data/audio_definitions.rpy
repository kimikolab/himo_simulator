# audio_definitions.rpy
# BGM定義ファイル
# 曲ファイルが未生成のものは silence.mp3 を指す。
# Ace Stepで曲ができたら右辺のファイル名を差し替える。

# === タイトル・メインメニュー ===
# イメージ: 軽快＋少し怠惰、コメディ寄り
# ※ options.rpy の config.main_menu_music も同じファイルに揃えること
define audio.bgm_title = "audio/bgm/bgm_title.mp3"

# === 日常 ===
# イメージ: のんびり、ローファイ風。自室・街などの通常時
define audio.bgm_daily = "audio/bgm/bgm_daily.mp3"

# === デート（楽しい） ===
# イメージ: 軽快、明るい。通常デート進行中
define audio.bgm_date_good = "audio/bgm/bgm_date_good.mp3"

# === デート（緊張） ===
# イメージ: コミカルな緊張感。地雷会話・探り会話
define audio.bgm_date_tense = "audio/bgm/bgm_date_tense3.mp3"

# === エナマッチ・アウトファイト ===
# イメージ: 探り合い、ジャブの応酬感
define audio.bgm_enamatch_out = "audio/bgm/bgm_enamatch_out.mp3"

# === エナマッチ・インファイト（美咲用） ===
# イメージ: 接近戦、ボルテージMAX感
define audio.bgm_enamatch_in = "audio/bgm/bgm_enamatch_in.mp3"

# === エナマッチ・インファイト（カナ用） ===
define audio.bgm_enamatch_in_kana = "audio/bgm/bgm_enamatch_in2.mp3"

# === 修羅場（将来用・現時点では未使用） ===
# イメージ: 不穏、緊迫
define audio.bgm_shuraba = "audio/bgm/bgm_shuraba.mp3"

# === エンディング ===
# Goodエンド: 温かみ、余韻
define audio.bgm_ending_good = "audio/bgm/bgm_ending_good.mp3"
# Grayエンド: アンビバレント、苦味
define audio.bgm_ending_gray = "audio/bgm/bgm_ending_gray.mp3"
# Badエンド: 寂寥、虚無
define audio.bgm_ending_bad = "audio/bgm/bgm_ending_bad.mp3"

# === デモエンド ===
define audio.bgm_demo_end = "audio/bgm/bgm_demo_end.mp3"
