# time_system.rpy
# 時間管理システム（Phase 2 v2.0: 曜日・月次・ムード・美咲イニシアチブ対応）

init python:
    def advance_time():
        global game_date, player, misaki, kana

        if game_date["time"] == "morning":
            game_date["time"] = "afternoon"
        elif game_date["time"] == "afternoon":
            game_date["time"] = "night"
        else:
            game_date["time"] = "morning"
            advance_day()

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


    def advance_day():
        global game_date, misaki, flags, daily_flags
        global location_flags, misaki_events, misaki_streak
        global weekend_promised, _game_over

        # v2.1: 日曜朝シーン処理（土曜宿泊フラグが立っていれば翌朝に実行）
        if flags.get("misaki_sunday_morning", False):
            location_flags["staying_at_misaki"] = True
            flags["misaki_sunday_morning"] = False
            _pending_events.append(("misaki_sunday_morning_scene", None))

        # 食事ペナルティチェック（リセット前に判定）
        if not daily_flags["ate_today"]:
            _pending_events.append(("hunger_penalty", None))

        # 週末の約束チェック（v2.1修正: 月曜になったタイミングで判定）
        if game_date["weekday"] == 0:   # 現在日曜 → 翌日が月曜
            if weekend_promised:
                if not flags.get("met_misaki_this_weekend", False):
                    _pending_events.append(("misaki_broken_promise", None))
                flags["met_misaki_this_weekend"] = False
                weekend_promised = False

        # 連続会った日数リセット（met_todayリセット前に判定）
        if not misaki["met_today"]:
            misaki_streak = max(0, misaki_streak - 1)

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

        # 宿泊リセット
        location_flags["staying_at_misaki"] = False
        location_flags["staying_at_kana"] = False

        # 美咲ムード更新
        update_misaki_mood()

        # 街アンロック
        if game_date["day"] == 4:
            flags["street_unlocked"] = True
            renpy.notify("街に出られるようになった")

        # 月次処理（キュー方式）
        if game_date["day"] > 1 and (game_date["day"] - 1) % 30 == 0:
            _pending_events.append(("monthly_billing", None))

        # 美咲からの自発的連絡（キュー方式）
        queue_misaki_initiative()

        # Phase 3: カナからの自発的連絡
        if kana_flags["met"]:
            check_kana_initiative()

        # 美咲イベントアンロック
        check_misaki_event_unlock()

        # 疑念イベント（キュー方式）
        if game_date["day"] == DOUBT_EVENT_DAY and not flags["doubt_event_done"]:
            _pending_events.append(("misaki_doubt_event", None))

        # ランダム出費イベント（v2.2: 12%に下げた）
        import random
        if random.random() < 0.12:
            _pending_events.append(("random_expense_event", None))


    def update_misaki_mood():
        import random
        global misaki_mood

        if not is_weekend():
            misaki_mood["work_stress"] = clamp(
                misaki_mood["work_stress"] + random.randint(5, 15), 0, 100
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
        import random

        # v2.3修正: last_contactが3未満、または当日会っているなら何もしない
        if misaki["last_contact"] < 3 or misaki["met_today"]:
            return

        # 3日以上連絡なし → 美咲からLINE
        if random.random() < 0.6:
            _pending_events.append(("misaki_check_in", None))

        # ストレス状態のとき低確率で電話（信頼40以上）
        if (misaki["trust"] >= 40
                and misaki_mood["today_mood"] == "stressed"
                and random.random() < 0.2):
            _pending_events.append(("misaki_stress_call", None))


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
