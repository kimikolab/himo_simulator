# time_system.rpy
# 時間管理システム（Phase 2 v2.0: 曜日・月次・ムード・美咲イニシアチブ対応）

init python:
    def advance_time():
        global game_date, player, misaki, kana

        old_time = game_date["time"]

        if game_date["time"] == "morning":
            game_date["time"] = "afternoon"
        elif game_date["time"] == "afternoon":
            game_date["time"] = "night"
        else:
            game_date["time"] = "morning"
            advance_day()

        log_action("TIME_ADVANCE", old_time + " -> " + game_date["time"])

        # パラメータ減衰
        player["stamina"] = max(0, player["stamina"] - STAMINA_DECAY_PER_TURN)
        player["cleanliness"] = max(0, player["cleanliness"] - CLEANLINESS_DECAY_PER_TURN)
        misaki["last_contact"] += 1

        # Phase 3: カナの連絡間隔も増加
        if kana_flags["met"]:
            kana["last_contact"] += 1

        # 体力低下イベント（キュー方式）
        if player["stamina"] <= 15:
            _pending_events.append(("event_low_stamina", None))

        # v1.3追加: 清潔感ペナルティ
        if player["cleanliness"] <= 0:
            _pending_events.append(("event_low_cleanliness", None))

        # v1.4注意: daily_flagsのリセットはadvance_day()のみで行う
        # ここでdaily_flagsをリセットしてはいけない（同日2回要求バグの原因になる）


    def advance_day():
        global game_date, misaki, flags, daily_flags
        global location_flags, misaki_events, misaki_streak
        global _game_over

        # v2.1: 日曜朝シーン処理（土曜宿泊フラグが立っていれば翌朝に実行）
        if flags.get("misaki_sunday_morning", False):
            location_flags["staying_at_misaki"] = True
            flags["misaki_sunday_morning"] = False
            _pending_events.append(("misaki_sunday_morning_scene", None))

        # Phase 4 v1.1: 食事回数カウント（リセット前に判定）
        if daily_flags.get("ate_today", False):
            stats["meals_eaten"] = stats.get("meals_eaten", 0) + 1

        # 食事ペナルティチェック（リセット前に判定）
        if not daily_flags["ate_today"]:
            _pending_events.append(("hunger_penalty", None))

        # v1.3.1: misaki_tonight 不履行チェック（泊まり対応）
        if flags.get("misaki_tonight", False):
            if not misaki["met_today"] and not location_flags.get("staying_at_misaki", False):
                flags["misaki_tonight_broken"] = True
            flags["misaki_tonight"] = False

        # v1.3.1: 約束不履行チェック（appointments一本化、泊まり対応）
        _misaki_appt = appointments.get("misaki", None)
        if _misaki_appt is not None and game_date["day"] >= _misaki_appt:
            if misaki["met_today"] or location_flags.get("staying_at_misaki", False):
                pass  # 約束を果たした
            else:
                _pending_events.append(("misaki_appointment_broken", None))
            appointments["misaki"] = None

        _kana_appt = appointments.get("kana", None)
        if _kana_appt is not None and game_date["day"] >= _kana_appt:
            if kana["met_today"] or location_flags.get("staying_at_kana", False):
                pass  # 約束を果たした
            else:
                _pending_events.append(("kana_appointment_broken", None))
            appointments["kana"] = None

        # v1.4修正: met_todayを保存（リセット後にstreak判定で使う）
        _met_today_prev = misaki["met_today"]
        _had_line_contact = daily_flags.get("misaki_lined_only", False)
        # DEBUG
        log_action("ADVANCE_DAY", "day={} streak={} met={} lined_only={} last_contact={}".format(
            game_date["day"], misaki_streak, _met_today_prev, _had_line_contact, misaki["last_contact"]))

        # ここから日付を進めてリセット処理
        game_date["day"] += 1
        game_date["weekday"] = (game_date["weekday"] + 1) % 7
        misaki["met_today"] = False

        # Phase 3: カナの日次リセット
        if kana_flags["met"]:
            kana["met_today"] = False

        # daily_flags リセット
        daily_flags["asked_money_today"] = False
        daily_flags["ignored_today"] = False
        daily_flags["date_planned_tonight"] = False
        daily_flags["ate_today"] = False
        daily_flags["ignored_kana_today"] = False
        # Phase 4 daily_flags リセット
        daily_flags["date_location"] = None
        daily_flags["date_with"] = None
        daily_flags["sns_shown_today"] = False
        daily_flags["double_booking_checked"] = False
        daily_flags["misaki_wants_tonight"] = False
        daily_flags["kana_wants_tonight"] = False
        daily_flags["money_refused_today"] = False
        daily_flags["kana_tonight_source"] = None
        daily_flags["misaki_lined_only"] = False
        daily_flags["misaki_line_last_shown"] = []
        # Phase 4 Step 2: ご機嫌取りフラグリセット
        daily_flags["kana_mood_resolved"] = False

        # 宿泊リセット
        location_flags["staying_at_misaki"] = False
        location_flags["staying_at_kana"] = False

        # v1.6修正: ゲーム終了日を超えたらイベントキューイングをスキップ
        # (game_endedフラグはエンディングラベルでセットされるため、
        #  ここではまだFalse。日数で直接判定する)
        if game_date["day"] > GAME_DAYS:
            return

        # 美咲ムード更新
        update_misaki_mood()

        # 街アンロック
        if game_date["day"] == 4:
            flags["street_unlocked"] = True
            renpy.notify("街に出られるようになった")
            log_notify("街に出られるようになった")

        # 月次処理（体験版30日制ではエンディングで精算するため不要）
        # 製品版（60日以上）では15日目・45日目等に中間請求を入れる
        # if game_date["day"] > 1 and (game_date["day"] - 1) % 30 == 0:
        #     _pending_events.append(("monthly_billing", None))

        # 美咲からの自発的連絡（キュー方式）
        queue_misaki_initiative()

        # v1.4修正: streak判定（queue_misaki_initiativeの後に移動）
        _initiative_contact = daily_flags.get("misaki_lined_only", False)
        _streak_before = misaki_streak
        if not _met_today_prev and not _had_line_contact and not _initiative_contact:
            misaki_streak = max(0, misaki_streak - 1)
        # DEBUG: streak変動ログ
        if _streak_before != misaki_streak:
            log_action("STREAK DOWN", "day={} {}→{} met={} line={} init={}".format(
                game_date["day"], _streak_before, misaki_streak,
                _met_today_prev, _had_line_contact, _initiative_contact))

        # Phase 3: カナからの自発的連絡
        if kana_flags["met"]:
            check_kana_initiative()

        # 美咲イベントアンロック
        check_misaki_event_unlock()

        # 疑念イベント（キュー方式）
        if game_date["day"] == DOUBT_EVENT_DAY and not flags["doubt_event_done"]:
            _pending_events.append(("misaki_doubt_event", None))

        # ランダム出費イベント（v2.2: 12%に下げた）
        if renpy.random.random() < 0.12:
            _pending_events.append(("random_expense_event", None))

        # === Phase 4 Step 2: 週間お金要求カウントのリセット ===
        if (game_date["day"] - money_request_weekly["last_reset_day"]) >= 7:
            money_request_weekly["count"] = 0
            money_request_weekly["last_reset_day"] = game_date["day"]

        # === Phase 4 Step 2: 居酒屋ボーナスの翌日リスク ===
        if flags.get("izakaya_money_hangover", False):
            flags["izakaya_money_hangover"] = False
            suspicion["misaki"] = suspicion.get("misaki", 0) + 2


    def update_misaki_mood():
        global misaki_mood

        if not is_weekend():
            misaki_mood["work_stress"] = clamp(
                misaki_mood["work_stress"] + renpy.random.randint(5, 15), 0, 100
            )
        else:
            misaki_mood["work_stress"] = clamp(
                misaki_mood["work_stress"] - 30, 0, 100
            )

        stress = misaki_mood["work_stress"]
        if stress >= 70:
            misaki_mood["today_mood"] = "stressed"
        elif stress >= 40:
            misaki_mood["today_mood"] = "tired"
        elif stress <= 15 and is_weekend():
            misaki_mood["today_mood"] = "good"
        else:
            misaki_mood["today_mood"] = "normal"


    def queue_misaki_initiative():
        """美咲の自発的連絡をキューに追加（renpy.call回避）"""
        # v1.4追加: ゲーム終了後はメッセージを送らない
        if flags.get("game_ended", False):
            return

        # v1.3追加: 信頼度ガード — 既読スルーする相手から自発的に連絡は来ない
        if misaki["trust"] < 20:
            return

        # v2.3修正: last_contactが3未満、または当日会っているなら何もしない
        if misaki["last_contact"] < 3 or misaki["met_today"]:
            return

        # 3日以上連絡なし → 美咲からLINE
        if renpy.random.random() < 0.6:
            _pending_events.append(("misaki_check_in", None))
            daily_flags["misaki_lined_only"] = True
            log_action("QUEUE_CHECKIN", "day={} lined_only=True streak={}".format(game_date["day"], misaki_streak))

        # ストレス状態のとき低確率で電話（信頼40以上）
        if (misaki["trust"] >= 40
                and misaki_mood["today_mood"] == "stressed"
                and renpy.random.random() < 0.2):
            _pending_events.append(("misaki_stress_call", None))
            daily_flags["misaki_lined_only"] = True
            log_action("QUEUE_STRESSCALL", "day={} lined_only=True streak={}".format(game_date["day"], misaki_streak))


    def check_misaki_event_unlock():
        """美咲イベントのアンロック条件を毎日チェック"""
        global misaki_events, misaki, player

        if (not misaki_events["M02_unlocked"]
                and misaki["trust"] >= 30
                and game_date["day"] >= M02_EARLIEST_DAY):
            misaki_events["M02_unlocked"] = True

        if (not misaki_events["M03_unlocked"]
                and misaki["trust"] >= 50
                and game_date["day"] >= M03_EARLIEST_DAY):
            misaki_events["M03_unlocked"] = True

        if (not misaki_events["M05_unlocked"]
                and misaki["trust"] >= 60
                and game_date["day"] >= M05_EARLIEST_DAY
                and player["money"] < 20000):
            misaki_events["M05_unlocked"] = True


    def is_weekend():
        """土日かどうか。0=日曜, 6=土曜"""
        return game_date["weekday"] in (0, 6)


    def get_weekday_string():
        return WEEKDAYS[game_date["weekday"]]


    def get_time_string():
        time_jp = {"morning": "朝", "afternoon": "昼", "night": "夜"}
        return time_jp.get(game_date["time"], "???")


# 食事ペナルティ
label hunger_penalty:
    "（そういえば昨日ろくに食べていない）"
    "（腹が減って体が重い）"
    $ change_stamina(-HUNGER_PENALTY_PER_DAY)
    return

# 体力低下イベント
label event_low_stamina:
    # v2.4修正: エンディング後はスタミナ警告を表示しない
    if flags.get("game_ended", False):
        return
    "（体が重い...）"
    "（疲れすぎてる。少し休まないと）"
    return

# v1.3追加: 清潔感ペナルティ
label event_low_cleanliness:
    if flags.get("game_ended", False):
        return

    "（体が臭い気がする...）"
    "（さすがに不潔すぎる）"

    python:
        # 美咲・カナと会う予定がある日はペナルティ強化
        if flags.get("misaki_tonight") or flags.get("kana_tonight"):
            renpy.notify("美咲: 「...ちょっと、大丈夫？」")
            log_notify("美咲: 「...ちょっと、大丈夫？」")
            change_trust(-3)
        else:
            change_charm(-2)

    return


# 月次請求イベント
label monthly_billing:
    scene bg_placeholder with fade
    "――月が変わった――"
    "スマホに通知が来た。"
    "『家賃引き落とし: ¥50,000』"
    "『通信費引き落とし: ¥3,000』"

    python:
        total_bill = MONTHLY_RENT + PHONE_BILL
        can_pay_rent = player["money"] >= total_bill

    if can_pay_rent:
        $ change_money(-total_bill)
        "合計¥[total_bill:,]が引き落とされた。"
        himo "...払えた。ギリギリだけど"
    else:
        "残高不足で引き落とせなかった。"
        himo "やばい...どうすんだこれ"
        $ _game_over = "bankruptcy"

    return
