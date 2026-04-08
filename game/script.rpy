# script.rpy
# メインスクリプト（Phase 2: 30日・曜日・美咲イベント対応）
# キャラクター定義は data/characters.rpy に移動（v2.6）


label start:
    call intro_scene
    $ misaki_events["M01_done"] = True
    $ flags["day1_date_pending"] = True    # 初日専用デートフラグ

    if not flags["tutorial_done"]:
        call tutorial
        $ flags["tutorial_done"] = True

    jump main_loop


label main_loop:
    # game_endedチェックを最初に行う
    if flags.get("game_ended", False):
        return

    # ゲームオーバーチェック（破産等）
    if _game_over == "bankruptcy":
        call ending_bankruptcy_30days
        return

    # 30日経過チェック
    if game_date["day"] > GAME_DAYS:
        call ending_30days
        return

    scene bg_placeholder
    show screen status_bar
    show screen debug_overlay

    # v1.1: ターン遷移ログ
    $ log_action("TURN_START", str(game_date["day"]) + "日" + get_time_string())

    if game_date["time"] == "morning":
        call morning_actions
    elif game_date["time"] == "afternoon":
        $ log_action("AFTERNOON_ENTER")
        call afternoon_actions
        $ log_action("AFTERNOON_EXIT")
    else:
        call night_actions

    hide screen status_bar
    hide screen debug_overlay

    # 遅延イベントキュー処理（アクション中に発生したイベント）
    call process_pending_events

    $ advance_time()

    # 遅延イベントキュー処理（advance_time/advance_day中に発生したイベント）
    call process_pending_events

    jump main_loop


# renpy.call() をPython関数内から安全に実行するための遅延処理
label process_pending_events:
    if len(_pending_events) > 0:
        $ _ev = _pending_events.pop(0)
        # v1.5: 冷戦中は美咲の自発LINEイベントをスキップ
        if _ev[0] in ("misaki_check_in", "misaki_stress_call") and cold_war.get("misaki_active", False):
            $ log_action("CHECK_IN 冷戦中のためスキップ: " + _ev[0])
            jump process_pending_events
        # v1.5: 冷戦中はカナの自発イベントもスキップ
        if _ev[0] in ("kana_check_in",) and cold_war.get("kana_active", False):
            $ log_action("CHECK_IN 冷戦中のためスキップ: " + _ev[0])
            jump process_pending_events
        if _ev[1] is not None:
            call expression _ev[0] pass (_ev[1])
        else:
            call expression _ev[0]
        jump process_pending_events
    return


label morning_actions:
    # v1.1: 防御クリア（前日から持ち越されないように）
    $ flags["morning_consumed"] = False

    # v1.4修正: 強制朝イベントを最優先で処理
    # （中盤イベントより前に呼ぶ。翌朝フラグは内部で無条件クリアされる）
    call check_forced_morning_event

    # 強制イベントが発生してターンが消費された場合は通常行動をスキップ
    if flags.get("morning_consumed", False):
        $ flags["morning_consumed"] = False
        return

    # Phase 4追加: SNS受動通知
    $ check_sns_notification()

    # Phase 4追加: 中盤イベントチェック
    python:
        midgame_fired = check_midgame_events()

    # v1.4修正: Trueの場合のみターン消費。"notify"はターン消費せず通常メニューへ
    if midgame_fired == True:
        return

    # v1.4: notify型イベントはここで先に処理（ターンは消費しない）
    call process_pending_events

    "――朝、10時――"

    # v1.5: 朝テキストのバリエーション（テキストバリエーション改善で拡充）
    if is_weekend():
        python:
            _weekend_morning = renpy.random.choice([
                "週末の朝か。最高すぎる",
                "休日の朝。何の予定もない。最高",
                "土日は最高。二度寝してもいい",
                "休みの日は目覚めが違う...毎日休みだけど",
                "なんとなく、空気が違う気がする",
                "隣の部屋から掃除機の音。世間は活動的だな",
                "俺は...もうちょっと寝よ",
            ])
        himo "[_weekend_morning]"
    else:
        python:
            _morning_lines = [
                ("...よし、起きるか", "平日の朝10時。サラリーマンはもう満員電車。", "俺は自由だわ〜"),
                ("...あと5分", "結局30分寝てた。まあ誰にも怒られないし。", "自由って最高"),
                ("...今日も予定なし", "窓の外、スーツ姿が急いでる。", "俺は急ぐ必要ないけどな"),
                ("んー...起きた", "スマホの時計。10時半。", "遅刻という概念がない生活"),
                ("...目覚ましかけてないのに目が覚めた", "体内時計が10時にセットされてる気がする", "まあ、急ぐ理由もないけどな"),
                ("スマホの通知で起きた。広告だった", "起きる理由が今日もない", "でもまあ、生きてるから起きるか"),
                ("...夢を見てたな。なんか、働いてる夢", "現実に戻ってきた。無職だった", "夢の中では真面目に働いてたな...最も恐ろ"),
            ]
            _m1, _m2, _m3 = renpy.random.choice(_morning_lines)
        himo "[_m1]"
        "[_m2]"
        himo "[_m3]"

    menu:
        "【[game_date['day']]日目([get_weekday_string()])・朝】何をする？"

        "シャワーを浴びる":
            "シャワーを浴びた。"
            himo "平日昼間のシャワー、最高！"
            $ change_stamina(-3)
            $ change_cleanliness(35)

        "美咲に連絡する" if game_date["day"] > 1:
            "美咲にLINEするか。"
            call contact_misaki

        "カナに連絡する" if kana_flags["met"]:
            call contact_kana

        # Phase 4 Step 2.5: 謝罪メニュー
        "美咲に謝りに行く" if cold_war.get("misaki_apology_available", False):
            call apology_event("misaki")

        "カナに謝りに行く" if cold_war.get("kana_apology_available", False):
            call apology_event("kana")

        "二度寝する":
            "もうちょっと寝よう。"
            himo "これが自由ってやつだ"

            if game_date["day"] >= 4:
                "...って、これでいいのか？"
                himo "まあいっか！寝よ寝よ"

            $ change_stamina(25)
            $ himo_aptitude["easy_choices"] += 1

    return


label afternoon_actions:
    # v1.1: 防御クリア（前ターンから持ち越されないように）
    $ flags["afternoon_consumed"] = False

    # Phase 4追加: SNS受動通知（朝に出なかった場合のみ）
    $ check_sns_notification()

    # Phase 4追加: 中盤イベントチェック
    python:
        midgame_fired = check_midgame_events()

    # v1.4修正: Trueの場合のみターン消費
    if midgame_fired == True:
        return

    # v1.4: notify型イベントはここで先に処理
    call process_pending_events

    # afternoon_consumed チェック（カナ急な呼び出し等で消費された場合）
    if flags.get("afternoon_consumed", False):
        $ flags["afternoon_consumed"] = False
        return

    "――昼、14時――"

    # v1.5: 昼テキストのバリエーション（テキストバリエーション改善で拡充）
    if is_weekend():
        python:
            _weekend_afternoon = renpy.random.choice([
                "週末の昼か。最高すぎる",
                "休日の昼。自由な時間だ",
                "のんびりした昼下がりだな",
                "休日の昼下がり。街は賑やかだ",
                "いい天気だな。出かけたい気もするけど、どうしよ",
                "週末の昼。カップルも多い...見なかったことにしよ",
            ])
        himo "[_weekend_afternoon]"
    else:
        python:
            _afternoon_lines = [
                ("ランチタイムも終わりか", "俺はこれから昼飯でも食うかな"),
                ("昼過ぎ。腹減ったな", "何しよっかな"),
                ("14時。世間は仕事中だろうな", "俺は...まあ自由だ"),
                ("昼下がり。いい天気だ", "外に出るか、ゴロゴロするか"),
                ("窓の外、サラリーマンがコンビニに急いでる", "昼休みか"),
                ("スマホの時計を見た。14時", "今日もやることない"),
                ("テレビがいつもの昼ドラ", "主婦向けだよな...これ"),
                ("腹は減ってるけど", "動くのが面倒だ"),
                ("昼下がり。外は暑い（寒い）", "出かけたくないな"),
            ]
            _a1, _a2 = renpy.random.choice(_afternoon_lines)
        "平日の昼下がり。"
        himo "[_a1]"
        himo "[_a2]"

    menu:
        "【[game_date['day']]日目([get_weekday_string()])・昼】何をする？"

        "街に出る" if flags["street_unlocked"]:
            call afternoon_street

        # Phase 2追加: 週末限定
        "買い物に行く（週末）" if is_weekend():
            call weekend_shopping

        "美咲に連絡する" if game_date["day"] > 1:
            call contact_misaki

        # Phase 4 v1.3: 土日は美咲を昼に誘える（v1.5: 冷戦中は非表示）
        "美咲を昼デートに誘う" if (is_weekend() and not misaki["met_today"] and game_date["day"] > 1 and not cold_war.get("misaki_active", False)):
            call misaki_daytime_date_request

        # Phase 3: カナに連絡する
        "カナに連絡する" if kana_flags["met"]:
            call contact_kana

        # Phase 3: カナの部屋に行く（昼・Stage 2以上）
        "カナの部屋に行く" if (kana_flags["met"] and kana["stage"] >= 2):
            call kana_visit

            # K-02トリガー（信頼20以上・未発生）
            if kana["trust"] >= 20 and not kana_flags["k02_done"]:
                call k02_insta_story

            # K-03トリガー（信頼35以上・未発生）
            if kana["trust"] >= 35 and not kana_flags["k03_done"]:
                call k03_money_talk

            # K-05トリガー（v1.3: 依存度50以上 + 25日目以降 or デート12回以上 + 25日目以降）
            if ((kana["dependence"] >= 50 or kana_dates_count >= 12) and game_date["day"] >= 25 and not kana_flags["k05_done"]):
                call k05_do_you_like_me

        # Phase 4 Step 2.5: 謝罪メニュー
        "美咲に謝りに行く" if cold_war.get("misaki_apology_available", False):
            call apology_event("misaki")

        "カナに謝りに行く" if cold_war.get("kana_apology_available", False):
            call apology_event("kana")

        "コンビニに行く":
            call convenience_store

        "昼寝する":
            "昼寝タイム。"
            himo "最高の贅沢だな、これ"
            $ change_stamina(35)
            $ himo_aptitude["easy_choices"] += 1

        "ステータス確認":
            call screen status_detail
            jump afternoon_actions

    return


label night_actions:
    "――夜、21時――"

    # ★初日専用デート（最優先）
    if flags.get("day1_date_pending", False):
        $ flags["day1_date_pending"] = False
        call misaki_date_day1
        return

    # v1.2: 告白ペンディングチェック（朝・昼にSTAGE_DATING移行した場合、夜に発火）
    if flags.get("confession_pending", False) and not flags.get("confession_done", False):
        $ flags["confession_pending"] = False
        call misaki_confession

    # v1.5修正: 約束がある夜の処理

    # 1. ダブルブッキングチェックを最初に行う
    if flags.get("misaki_tonight") and flags.get("kana_tonight"):
        call double_booking_event
        # double_booking_event内でどちらかのフラグがFalseになる
        # その後は通常の2番・3番の処理へ続く

    # 2. 美咲の約束のみある場合
    if flags.get("misaki_tonight") and not flags.get("kana_tonight"):
        # v1.6追加: ヒモ太郎の部屋に美咲が来る場合
        if flags.get("misaki_visit_himo_room", False):
            "今夜は美咲がうちに来る。"
            $ flags["misaki_tonight"] = False
            $ flags["misaki_visit_himo_room"] = False
            call misaki_visit_himo_room
            return

        "今夜は美咲と約束がある。"
        $ flags["misaki_tonight"] = False
        call misaki_date_with_location
        return

    # 3. カナの約束のみある場合（v1.4: プレイヤー主導なら確定、カナ主導のみドタキャンリスク）
    if flags.get("kana_tonight") and not flags.get("misaki_tonight"):
        "今夜はカナと約束がある。"
        $ flags["kana_tonight"] = False
        python:
            source = daily_flags.get("kana_tonight_source", "kana")
            if source == "player":
                kana_shows_up = True
            else:
                trust = kana["trust"]
                if trust >= 50:   success_rate = 0.95
                elif trust >= 35: success_rate = 0.85
                elif trust >= 20: success_rate = 0.75
                else:             success_rate = 0.60
                kana_shows_up = renpy.random.random() < success_rate
        $ daily_flags["kana_tonight_source"] = None
        if kana_shows_up:
            call kana_date_with_location
        else:
            kana_c "ごめん、やっぱり今日バイト入っちゃって"
            himo "そっか、しゃーない"
            $ change_trust_kana(-2)
        return

    # 4. 約束なし → 通常の夜メニュー
    if is_weekend():
        himo "週末の夜か。自由だな〜"
    elif game_date["day"] <= 5:
        "夜9時。サラリーマンは終電心配してる時間。"
        himo "大変だなあ"

    menu:
        "【[game_date['day']]日目([get_weekday_string()])・夜】何をする？"

        # Phase 2: M-02 終電後の電話
        "美咲と電話する" if (misaki_events["M02_unlocked"] and not misaki_events["M02_done"]):
            call misaki_event_M02

        # Phase 2: M-03 週末の部屋（初回イベント）
        "美咲の部屋に行く" if (is_weekend() and misaki_events["M03_unlocked"] and not misaki_events["M03_done"]):
            call misaki_event_M03

        # Phase 2 v2.0: 美咲宅訪問（M-03完了後、週末定期行動）（v1.5: 冷戦中は非表示）
        "美咲の部屋に行く（週末）" if (is_weekend() and misaki_events["M03_done"] and location_flags["misaki_room_unlocked"] and not misaki["met_today"] and not cold_war.get("misaki_active", False)):
            call misaki_room_visit

        # Phase 2 v2.0: 美咲宅訪問（平日、関係CLOSE以上）（v1.5: 冷戦中は非表示）
        "美咲の部屋に行く" if (misaki["stage"] >= STAGE_CLOSE and misaki_events["M03_done"] and not is_weekend() and not misaki["met_today"] and not cold_war.get("misaki_active", False)):
            call misaki_room_visit

        "美咲を誘う" if (not misaki["met_today"] and not cold_war.get("misaki_active", False)):
            call misaki_date_request

        # Phase 3: カナを誘う
        "カナを誘う" if (kana_flags["met"] and not kana["met_today"]):
            call kana_date_request

        "美咲に連絡する":
            call contact_misaki

        # Phase 4 Step 2.5: 謝罪メニュー
        "美咲に謝りに行く" if cold_war.get("misaki_apology_available", False):
            call apology_event("misaki")

        "カナに謝りに行く" if cold_war.get("kana_apology_available", False):
            call apology_event("kana")

        "コンビニに行く":
            call convenience_store

        "風呂入って寝る":
            $ change_cleanliness(50)
            $ change_stamina(50)

    return


# ========================================
# v1.5追加: ダブルブッキングイベント
# ========================================

label double_booking_event:
    "スマホを見ると、二つの約束が重なっていることに気づいた。"
    "美咲とカナ、両方と今夜の約束が入っている。"
    himo "...やばい"

    menu:
        "どちらを優先する？"

        "美咲を優先":
            "カナにLINEを送った。"
            himo "ごめん、今日急用が入って"
            kana_c "え〜、そうなんだ。まあいいけど"
            $ flags["kana_tonight"] = False
            # misaki_tonightはTrueのまま → 美咲デートへ
            $ change_trust_kana(-5)
            $ change_dependence_kana(3)

        "カナを優先":
            "美咲にLINEを送った。"
            himo "ごめん、今日急用が入って"
            misaki_c "...そうなんだ。分かった"
            $ flags["misaki_tonight"] = False
            # kana_tonightはTrueのまま → カナデートへ
            $ change_trust(-8)
            $ change_dependence(5)
            $ add_suspicion("contact_delay")

        "両方すっぽかす":
            himo "...両方に謝るか"
            "美咲とカナ、両方に言い訳のLINEを送った。"
            $ flags["misaki_tonight"] = False
            $ flags["kana_tonight"] = False
            $ change_trust(-5)
            $ change_trust_kana(-5)
            $ himo_aptitude["lies"] += 1
            # 両方Falseなので通常メニューへ

    return
