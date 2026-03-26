# variables.rpy
# 全ゲーム変数の default 宣言

# プレイヤー情報
default player = {
    "name": "ヒモ太郎",
    "age": 25,
    "money": 3458,
    "stamina": 100,
    "max_stamina": 100,
    "charm": 50,
    "cleanliness": 50
}

# 日付・時間情報
default game_date = {
    "day": 1,
    "time": "morning",
    "weekday": 1       # Phase 2追加: 0=日, 1=月, ... 6=土（1日目=月曜始まり）
}

# 美咲の情報
default misaki = {
    "name": "佐藤美咲",
    "age": 25,
    "trust": 30,
    "dependence": 10,
    "stage": 1,
    "last_contact": 0,
    "met_today": False
}

# カナの情報（Phase 3追加）
default kana = {
    "name": "桜井カナ",
    "age": 21,
    "trust": 0,
    "dependence": 0,
    "stage": 0,
    "last_contact": 0,
    "met_today": False,
}

# カナ関連フラグ（Phase 3追加）
default kana_flags = {
    "met": False,
    "k01_done": False,
    "k02_done": False,
    "k03_done": False,
    "k04_done": False,
    "k05_done": False,
    "sns_risk": 0,
    "room_key": False,
}

# カナとのデート回数（v1.3追加: kana_dateとkana_visitを合算）
default kana_dates_count = 0

# 違和感カウント
default suspicion_count = 0

# イベントフラグ
default flags = {
    "tutorial_done": False,
    "first_money": False,
    "first_date": False,
    "street_unlocked": False,
    "had_doubt_moment": False,
    "doubt_event_done": False,
    "confession_done":     False,
    "confession_pending":  False,
    "confession_accepted": False,
    "confession_ambiguous": False,
    "confession_rejected": False,
    "misaki_sunday_morning": False,
    "misaki_tonight": False,
    "kana_tonight": False,
    "game_ended": False,
    "k05_accepted": False,
    "k05_ambiguous": False,
    "morning_consumed": False,
    "afternoon_consumed": False,
    "nanpa_unlocked": False,
    # Phase 4: 中盤イベントフラグ
    "midgame_busymisaki_done": False,
    "midgame_pachinko_triggered": False,
    "midgame_doublebooking_done": False,
    "midgame_sighting_done": False,
    "midgame_sighting_confronted": False,
    "midgame_kana_raid_done": False,
    "midgame_misaki_direct_done": False,
    "kana_friend_info_obtained": False,
    "misaki_saturday_promise": False,
    "misaki_tonight_broken": False,
    "qte_failed_badly": False,
    "misaki_visit_himo_room": False,   # v1.6: ヒモ太郎の部屋に美咲が来る
    "misaki_stayed_at_himo": False,    # v1.6: 美咲がヒモ太郎の部屋に泊まった
    # Phase 4 Step 2: 経済圏システム
    "izakaya_money_hangover": False,   # 居酒屋交渉の翌日疑念リスク
    "kana_morning_after": False,       # カナ泊まり翌朝イベント
    "kana_doubt_event_done": False,    # カナ版疑念イベント済み
    "kana_at_himo_room": False,        # v1.1: カナがヒモ太郎の部屋に泊まり中
    "kana_himo_room_morning": False,   # v1.1: カナがヒモ太郎の部屋に泊まった翌朝
}

# 1日ごとにリセットされるフラグ
default daily_flags = {
    "asked_money_today": False,
    "ignored_today": False,
    "date_planned_tonight": False,
    "ate_today": False,             # 食事チェック用
    "ignored_kana_today": False,
    "date_location": None,          # Phase 4: 当日のデート場所
    "date_with": None,              # Phase 4: 当日誰とデートしたか
    "sns_shown_today": False,       # Phase 4: SNS通知表示済み
    "double_booking_checked": False, # Phase 4: ダブルブッキングチェック済み
    "misaki_wants_tonight": False,  # Phase 4: 美咲が今夜会いたい
    "kana_wants_tonight": False,    # Phase 4: カナが今夜会いたい
    "money_refused_today": False,   # Phase 4 v1.2: 金銭要求を拒否された
    "kana_tonight_source": None,    # Phase 4 v1.4: "player" or "kana" or None
    "misaki_lined_only": False,     # Phase 4 v1.4: LINEのみで対面していない
    "misaki_line_last_shown": [],   # Phase 4 v1.6: 美咲LINE選択肢の前回表示分
    "kana_mood_resolved": False,    # Phase 4 Step 2: その日のご機嫌取りが済んだか
}

# 美咲イベント進行フラグ（Phase 2追加）
default misaki_events = {
    "M01_done": False,
    "M02_done": False,
    "M02_unlocked": False,
    "M03_done": False,
    "M03_unlocked": False,
    "M04_done": False,
    "M05_done": False,
    "M05_unlocked": False
}

# 場所フラグ（Phase 2追加）
default location_flags = {
    "misaki_room_unlocked": False,
    "staying_at_misaki": False,
    "staying_at_kana": False
}

# 月次管理（Phase 2追加）
default monthly = {
    "rent_paid": False,
    "total_months": 1
}

# 美咲イニシアチブ：ムードシステム（v2.0追加）
default misaki_mood = {
    "work_stress": 0,       # 0〜100
    "today_mood": "normal"  # "good" / "normal" / "tired" / "stressed"
}

# 美咲イニシアチブ：依存度管理（v2.0追加）
default misaki_streak    = 0      # 連続で会った日数
default money_refused_streak = 0  # v2.1: 金銭要求連続拒否カウント

# 遅延イベントキュー（renpy.call をPython関数内から安全に呼ぶため）
default _pending_events = []

# ゲームオーバーフラグ（Python関数内からjumpできないため）
default _game_over = ""

# エンディング種別記録（テスト・実績・デバッグ用）
# 値: "good" / "gray" / "normal" / "bad_bankruptcy" / "demo"
default _ending_type = ""

# 統計
default stats = {
    "total_earned": 0,
    "times_met": 0,
    "times_asked_money": 0,
    "lies_told": 0,
    "optimistic_choices": 0,
    "pachinko_wins": 0,
    "pachinko_losses": 0,
    "pachinko_profit": 0,
    # Phase 4 v1.1追加
    "lie_puzzles_faced": 0,
    "lie_puzzles_busted": 0,
    "meals_eaten": 0,
    "date_locations": {},
    # Phase 4 Step 2: カナの交換経済
    "kana_benefits_received": 0,    # カナから恩恵を受けた回数
    "kana_ena_given": 0,            # カナにエナを使った回数（ステップ3で使用）
    "kana_gokiragen_success": 0,    # ご機嫌取り成功回数
    "kana_gokiragen_failed": 0,     # ご機嫌取り失敗回数
    "kana_stayed_over": 0,          # カナの部屋に泊まった回数
    # v1.1追加: 経済圏追跡カウンタ
    "negotiation_attempts": 0,       # 対面交渉の試行回数
    "negotiation_success": 0,        # 対面交渉の成功回数
    "negotiation_total_earned": 0,   # 対面交渉の総収入
    "line_request_attempts": 0,      # LINE要求の試行回数
    "line_request_success": 0,       # LINE要求の成功回数
    "kana_stayed_himo_room": 0,      # カナがヒモ太郎の部屋に泊まった回数
}

# ヒモ適性診断
default himo_aptitude = {
    "easy_choices": 0,
    "money_requests": 0,
    "lies": 0,
    "honest_moments": 0,
    "avoided_work": 0,
    "showed_concern": 0,
    "lie_skill": 0,
    "intimacy_exp": 0,
}

# Phase 4 v1.3: 約束日管理
default appointments = {
    "misaki": None,    # 約束がある日（整数 or None）
    "kana": None
}

# === Phase 4 追加変数 ===

# 疑念度（キャラ別）
default suspicion = {
    "misaki": 0,
    "kana": 0
}

# === 美咲の対面交渉（Phase 4 Step 2）===
default money_request_weekly = {
    "count": 0,              # 週間お金要求回数（LINE＋対面合算）
    "last_reset_day": 1      # 最後にリセットした日
}

# 嘘パズル
default lie_puzzle = {
    "active": False,
    "bare_gauge": 0,
    "previous_answers": [],
    "time_limit": 5.0,
    "result": None
}
default lie_puzzle_timeout = False

# セリフログ用リスト
default dialogue_log_entries = []
