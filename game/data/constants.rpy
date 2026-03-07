# constants.rpy
# ゲーム内定数

# 背景プレースホルダー（画像ファイルなし）
define bg_placeholder = Solid("#1a1a2e")

# 時間関連
define TIMES_OF_DAY = ["morning", "afternoon", "night"]
define WEEKDAYS = ["日", "月", "火", "水", "木", "金", "土"]

# 固定費（Phase 2: 月払いに変更）
define MONTHLY_RENT = 50000
define PHONE_BILL = 3000

# パラメータ減衰率（v2.0調整）
define STAMINA_DECAY_PER_TURN = 5       # v1.0: 3 → 5（食事の重要性UP）
define CLEANLINESS_DECAY_PER_TURN = 4

# 食事ペナルティ（食事を取らなかった翌朝）
define HUNGER_PENALTY_PER_DAY = 15

# 関係ステージ
define STAGE_ACQUAINTANCE = 1
define STAGE_FRIEND = 2
define STAGE_CLOSE = 3
define STAGE_DATING = 4
define STAGE_OSHI = 4          # カナ専用ステージ（美咲のSTAGE_DATINGに相当）

# ゲーム期間（Phase 2: 30日に拡張）
define GAME_DAYS = 30

# 疑念イベント発生日（Phase 2: 12日目に変更）
define DOUBT_EVENT_DAY = 12

# 美咲イベント発生日の目安（Phase 2追加）
define M02_EARLIEST_DAY = 5
define M03_EARLIEST_DAY = 14
define M05_EARLIEST_DAY = 20

# 依存度マイルストーン（美咲イニシアチブ / v2.0追加）
define DEPEND_MILD   = 40   # 軽い干渉開始
define DEPEND_MEDIUM = 60   # 約束の強制
define DEPEND_HEAVY  = 80   # 行動制限

# カナ関連定数（Phase 3追加）
define KANA_CHARM_CAP = 70        # カナ魅力値上限

# === Phase 4 追加定数 ===

# 疑念度の閾値
define SUSPICION_PROBE_THRESHOLD = 1     # 探り発生の最低疑念度
define SUSPICION_SHURABA_THRESHOLD = 3   # 修羅場イベント発生の疑念度
define SUSPICION_MAX = 100

# 所持金バレリスク閾値
define MONEY_SUSPICION_THRESHOLD = 40000   # v1.2: 30000→40000

# 嘘パズル設定
define LIE_TIME_LV0 = 5.0
define LIE_TIME_LV1 = 7.0
define LIE_TIME_LV2 = 10.0

# バレ度上昇量
define BARE_CONTRADICTION = 35    # 矛盾回答
define BARE_SILENCE = 40          # 時間切れ
define BARE_WEAK = 10             # 弱い回答
define BARE_PERFECT = 3           # 完璧でも微増
define BARE_MAX = 100             # バレ確定

# QTE設定
define QTE_TIME_LIMIT = 12.0

# SNS通知の最大表示数/日
define SNS_MAX_PER_DAY = 2

# デバッグモード（リリース前に False に変更）
define DEBUG_MODE = True
