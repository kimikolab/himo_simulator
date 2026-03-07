# script.rpy
# メインスクリプト（Phase 2: 30日・曜日・美咲イベント対応）
# キャラクター定義は data/characters.rpy に移動（v2.6）

# Phase 2: 曜日表示付きステータスバー
screen status_bar():
    frame:
        xalign 0.5
        yalign 0.02
        padding (15, 8)

        hbox:
            spacing 30

            text "[game_date['day']]日目([get_weekday_string()])" size 24
            text get_time_string() size 24
            text "所持金: ¥[player['money']:,]" size 24 color "#FFD700"
            text "信頼: [misaki['trust']]" size 22 color "#87CEEB"
            text "依存: [misaki['dependence']]" size 22 color "#FF69B4"

            if player["stamina"] < 30:
                text "[[疲労]" size 20 color "#ff6b6b"
            if player["cleanliness"] < 20:
                text "[[不潔]" size 20 color "#4ecdc4"


label start:
    call intro_scene
    $ misaki_events["M01_done"] = True
    $ flags["misaki_tonight"] = True

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

    if game_date["time"] == "morning":
        call morning_actions
    elif game_date["time"] == "afternoon":
        call afternoon_actions
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
        if _ev[1] is not None:
            call expression _ev[0] pass (_ev[1])
        else:
            call expression _ev[0]
        jump process_pending_events
    return


label morning_actions:
    # Phase 4追加: SNS受動通知
    $ check_sns_notification()

    # Phase 4追加: 中盤イベントチェック
    python:
        midgame_fired = check_midgame_events()

    if midgame_fired:
        return

    # v1.1追加: 強制朝イベントのチェック
    call check_forced_morning_event

    # 強制イベントが発生してターンが消費された場合は通常行動をスキップ
    if flags.get("morning_consumed", False):
        $ flags["morning_consumed"] = False
        return

    "――朝、10時――"

    if is_weekend():
        himo "週末の朝か。最高すぎる"
    else:
        himo "...よし、起きるか"
        "平日の朝10時。サラリーマンはもう満員電車。"
        himo "俺は自由だわ〜"

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
    # Phase 4追加: SNS受動通知（朝に出なかった場合のみ）
    $ check_sns_notification()

    # Phase 4追加: 中盤イベントチェック
    python:
        midgame_fired = check_midgame_events()

    if midgame_fired:
        return

    # afternoon_consumed チェック（カナ急な呼び出し等で消費された場合）
    if flags.get("afternoon_consumed", False):
        $ flags["afternoon_consumed"] = False
        return

    "――昼、14時――"

    if is_weekend():
        himo "週末の昼か。最高すぎる"
    else:
        "平日の昼下がり。"
        himo "ランチタイムも終わりか"
        himo "俺はこれから昼飯でも食うかな"

    menu:
        "【[game_date['day']]日目([get_weekday_string()])・昼】何をする？"

        "街に出る" if flags["street_unlocked"]:
            call afternoon_street

        # Phase 2追加: 週末限定
        "買い物に行く（週末）" if is_weekend():
            call weekend_shopping

        "美咲に連絡する" if game_date["day"] > 1:
            call contact_misaki

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

            # K-05トリガー（v1.6: 依存度30以上 or デート12回以上・未発生）
            if (kana["dependence"] >= 30 or kana_dates_count >= 12) and not kana_flags["k05_done"]:
                call k05_do_you_like_me

        "コンビニで昼飯を買う（500円）":
            if not can_afford(500):
                himo "...財布が軽すぎる"
                jump afternoon_actions
            $ change_money(-500)
            $ change_stamina(10)
            $ daily_flags["ate_today"] = True
            "コンビニ飯で腹を満たした。"
            himo "まあ生きていけるな"

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
        "今夜は美咲と約束がある。"
        $ flags["misaki_tonight"] = False
        call misaki_date_with_location
        return

    # 3. カナの約束のみある場合（v1.6: 成功率チェック追加）
    if flags.get("kana_tonight") and not flags.get("misaki_tonight"):
        "今夜はカナと約束がある。"
        $ flags["kana_tonight"] = False
        python:
            trust = kana["trust"]
            if trust >= 50:   success_rate = 0.90
            elif trust >= 35: success_rate = 0.75
            elif trust >= 20: success_rate = 0.65
            else:             success_rate = 0.50
            kana_shows_up = renpy.random.random() < success_rate
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

        # Phase 2 v2.0: 美咲宅訪問（M-03完了後、週末定期行動）
        "美咲の部屋に行く（週末）" if (is_weekend() and misaki_events["M03_done"] and location_flags["misaki_room_unlocked"] and not misaki["met_today"]):
            call misaki_room_visit

        # Phase 2 v2.0: 美咲宅訪問（平日、関係CLOSE以上）
        "美咲の部屋に行く" if (misaki["stage"] >= STAGE_CLOSE and misaki_events["M03_done"] and not is_weekend() and not misaki["met_today"]):
            call misaki_room_visit

        "美咲を誘う" if (not misaki["met_today"]):
            call misaki_date_request

        # Phase 3: カナを誘う
        "カナを誘う" if (kana_flags["met"] and not kana["met_today"]):
            call kana_date_request

        "美咲に連絡する":
            call contact_misaki

        "コンビニ飯（700円）":
            if not can_afford(700):
                himo "...財布の中身が足りない"
                jump night_actions
            "コンビニ弁当を買ってきた。"
            $ change_money(-700)
            $ change_stamina(12)
            $ daily_flags["ate_today"] = True

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
