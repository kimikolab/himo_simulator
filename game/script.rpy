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

    if not flags["tutorial_done"]:
        call tutorial
        $ flags["tutorial_done"] = True

    jump main_loop


label main_loop:
    # ゲームオーバーチェック（破産等）
    if _game_over == "bankruptcy":
        jump ending_bankruptcy_30days

    # 30日経過チェック
    if game_date["day"] > GAME_DAYS:
        jump ending_30days

    scene bg_placeholder
    show screen status_bar

    if game_date["time"] == "morning":
        call morning_actions
    elif game_date["time"] == "afternoon":
        call afternoon_actions
    else:
        call night_actions

    hide screen status_bar

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

        "SNSを見る":
            call check_sns

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

    if is_weekend():
        himo "週末の夜か。自由だな〜"
    else:
        "夜9時。サラリーマンは終電心配してる時間。"
        himo "大変だなあ"

    menu:
        "【[game_date['day']]日目([get_weekday_string()])・夜】何をする？"

        "美咲と会う（約束してる）" if not misaki["met_today"] and (game_date["day"] == 1 or daily_flags.get("date_planned_tonight", False)):
            call misaki_meet_planned

        # Phase 2: M-02 終電後の電話
        "美咲と電話する" if (misaki_events["M02_unlocked"] and not misaki_events["M02_done"] and not daily_flags["date_planned_tonight"]):
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

        "美咲を誘う" if (not misaki["met_today"] and not daily_flags["date_planned_tonight"]):
            call misaki_date_request

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
