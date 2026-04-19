# date_misaki_places.rpy
# 美咲デート — 場所選択で展開が変わる

label misaki_date_with_location:
    scene bg_placeholder

    "美咲と会うことになった。"

    menu:
        "どこに行く？"

        "ファミレス（安い・安全）":
            $ daily_flags["date_location"] = "famires"
            call misaki_date_famires

        "居酒屋（本音が出やすい）":
            $ daily_flags["date_location"] = "izakaya"
            call misaki_date_izakaya

        "美咲の部屋（親密・依存UP）" if misaki["stage"] >= STAGE_CLOSE:
            $ daily_flags["date_location"] = "misaki_room"
            call misaki_date_room

        "ちょっといい店（自腹・信頼大幅UP）" if can_afford(3000):
            $ daily_flags["date_location"] = "fancy"
            call misaki_date_fancy

    # デート後の共通処理
    $ misaki["met_today"] = True
    $ stats["times_met"] += 1
    $ daily_flags["date_with"] = "misaki"
    $ daily_flags["ate_today"] = True
    $ reset_contact()
    # v1.3: 既読スルーカウントをリセット
    $ stats["misaki_ignored_count"] = 0
    # Phase 4 v1.2: misaki_tonight フラグを消費
    if flags.get("misaki_tonight", False):
        $ flags["misaki_tonight"] = False
    # 探り・地雷・ハプニングの判定
    call check_date_incidents("misaki")

    return


label misaki_date_famires:
    scene bg_famiresu
    show misaki casual smile with dissolve
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["famires"] = stats["date_locations"].get("famires", 0) + 1
    "ファミレスに入った。"
    misaki_c "ここ落ち着くよね"
    himo "安いしな"

    "美咲が奢ってくれた。"

    $ change_trust(3)
    $ change_dependence(2)
    $ change_stamina(-10)
    $ change_stamina(20)   # 食事による体力回復（差し引き+10）

    # Phase 4 Step 3: プレゼントを渡す
    if inventory.get("bouquet", False) or inventory.get("accessory", False):
        menu:
            "プレゼントを渡す":
                call give_present("misaki")
            "渡さない":
                pass

    # === 対面交渉の切り出しチャンス ===
    if misaki["trust"] >= 35 and money_request_weekly["count"] < NEGOTIATION_WEEKLY_LIMIT and not daily_flags.get("asked_money_today", False):
        menu:
            "会話が落ち着いてきた。"

            "お金の話を切り出す":
                call misaki_negotiation_start

            "このまま楽しむ":
                # v1.2: お金の話をしなかった→好印象
                if suspicion.get("misaki", 0) >= 6:
                    himo "（今日はお金の話はやめとこう）"
                $ reduce_suspicion("misaki", 1, "デート楽しむ")

    return


label misaki_date_izakaya:
    scene bg_izakaya
    show misaki casual normal with dissolve
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["izakaya"] = stats["date_locations"].get("izakaya", 0) + 1
    "居酒屋に入った。"

    # v1.2: 回数に応じてセリフを変える
    python:
        _izakaya_count = stats.get("date_locations", {}).get("izakaya", 0)

    if _izakaya_count <= 1:
        misaki_c "たまにはこういうのもいいね"
    elif _izakaya_count <= 3:
        python:
            _iz_line = renpy.random.choice([
                "また居酒屋？笑 好きだね〜",
                "ここ、落ち着くよね",
                "今日は何飲む？",
            ])
        misaki_c "[_iz_line]"
    elif _izakaya_count <= 6:
        python:
            _iz_line = renpy.random.choice([
                "いつもの席、空いてるかな",
                "もう常連だね、ここ",
                "店員さんに覚えられてそう",
            ])
        misaki_c "[_iz_line]"
    else:
        python:
            _iz_line = renpy.random.choice([
                "...またここ？たまには別の店行かない？",
                "いつもの、でいい？もう分かるでしょ",
                "ヒモ太郎って居酒屋好きすぎない？笑",
            ])
        misaki_c "[_iz_line]"

    # 訪問回数で飲み方・奢りテキストにバリエーション
    python:
        _iz_visit = stats.get("date_locations", {}).get("izakaya", 0)

        _drink_texts = [
            "お酒が入って、美咲の口数が増える。",
        ]
        if _iz_visit >= 3:
            _drink_texts.append("二杯目あたりから、美咲の顔が赤くなってきた。")
            _drink_texts.append("美咲がグイグイ飲んでいる。お酒と生きてるタイプだ。")
        if _iz_visit >= 5:
            _drink_texts.append("もう何杯目だろう。美咲のペースが上がっている。")
            _drink_texts.append("今日の美咲は飲むペースが速い。仕事で何かあったのかもしれない。")
        _dt = renpy.random.choice(_drink_texts)

        _treat_texts = [
            "美咲が奢ってくれた。",
        ]
        if _iz_visit >= 3:
            _treat_texts.append("会計は美咲がさらっと済ませた。自然にそうなっている。")
            _treat_texts.append("美咲がカードを出した。「経費で落とす」は冗談だと思うけど。")
        if _iz_visit >= 5:
            _treat_texts.append("美咲が伝票を取った。何も言わずに。")
            _treat_texts.append("「いつも悪いな」「...いいの、楽しいから」")
        _tt = renpy.random.choice(_treat_texts)

    "[_dt]"
    show misaki casual happy
    "[_tt]"

    $ change_trust(5)
    $ change_dependence(5)
    $ change_stamina(-15)
    $ change_stamina(20)   # 食事による体力回復（差し引き+5）

    # === 対面交渉の切り出しチャンス ===
    if misaki["trust"] >= 35 and money_request_weekly["count"] < NEGOTIATION_WEEKLY_LIMIT and not daily_flags.get("asked_money_today", False):
        menu:
            "会話が落ち着いてきた。"

            "お金の話を切り出す":
                call misaki_negotiation_start

            "このまま楽しむ":
                # v1.2: お金の話をしなかった→好印象
                if suspicion.get("misaki", 0) >= 6:
                    himo "（今日はお金の話はやめとこう）"
                $ reduce_suspicion("misaki", 1, "デート楽しむ")

    return


label misaki_date_room:
    scene bg_misaki_room
    show misaki casual normal with dissolve
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["misaki_room"] = stats["date_locations"].get("misaki_room", 0) + 1
    $ misaki_room_visit_count += 1

    "美咲の部屋に行った。"

    # v1.7: 訪問回数でテキスト分岐
    if misaki_room_visit_count == 1:
        misaki_c "散らかっててごめんね"
        himo "いいっていいって"
    elif misaki_room_visit_count <= 3:
        python:
            _mr_txt = renpy.random.randint(0, 1)
        if _mr_txt == 0:
            misaki_c "今日は片付けたんだ...ちょっとだけ"
            himo "お、きれいじゃん"
        else:
            misaki_c "何飲む？お茶しかないけど"
            himo "お茶でいい"
    else:
        python:
            _mr_txt = renpy.random.randint(0, 1)
        if _mr_txt == 0:
            "もう勝手知ったる美咲の部屋。"
            himo "ただいま"
            misaki_c "...おかえり"
        else:
            misaki_c "そろそろスリッパ買おうかな。ヒモ太郎用の"
            himo "え、いいの？"
            misaki_c "...冗談"

    "2人きりの空間。"
    "美咲が何か作ってくれた。"

    $ change_trust(5)
    $ change_dependence(8)
    $ change_stamina(-10)
    $ change_stamina(15)   # 軽い食事
    $ change_cleanliness(15)  # シャワー借りれる

    # 翌日の日曜朝イベントフラグ
    python:
        weekday_index = game_date.get("weekday", 0)
        if weekday_index == 6 and game_date["time"] == "night":  # 土曜の夜
            flags["misaki_sunday_morning"] = True
            # v1.4追加: カナの翌朝フラグをクリア（排他制御）
            flags["kana_morning_after"] = False
            flags["kana_himo_room_morning"] = False
            location_flags["staying_at_kana"] = False
            flags["kana_at_himo_room"] = False

    # === 対面交渉の切り出しチャンス ===
    if misaki["trust"] >= 35 and money_request_weekly["count"] < NEGOTIATION_WEEKLY_LIMIT and not daily_flags.get("asked_money_today", False):
        menu:
            "会話が落ち着いてきた。"

            "お金の話を切り出す":
                call misaki_negotiation_start

            "このまま楽しむ":
                # v1.2: お金の話をしなかった→好印象
                if suspicion.get("misaki", 0) >= 6:
                    himo "（今日はお金の話はやめとこう）"
                $ reduce_suspicion("misaki", 1, "デート楽しむ")

    return


# ========================================
# v1.6追加: ヒモ太郎の部屋に美咲が来るイベント
# ========================================

label misaki_visit_himo_room:
    scene bg_himo_room
    show misaki casual normal with dissolve

    # === Phase 4 Step 2.5: 痕跡チェック ===
    $ _evidence_trace_passed = False
    if flags.get("kana_stayed_himo_this_week", False) and not flags.get("evidence_trace_done_this_week", False):
        call evidence_trace_event("misaki")
        $ flags["evidence_trace_done_this_week"] = True
        if cold_war.get("misaki_active", False):
            return

        # === v1.3追加: 嘘パズル成功でも空気が変わった演出 ===
        "..."
        "美咲が少し黙り込んだ。"
        misaki_c "...ごめん、気にしすぎだよね"
        himo "...いや、俺の方こそごめん"
        "ぎこちない空気のまま、夜を過ごした。"
        $ _evidence_trace_passed = True

    if not _evidence_trace_passed:
        # 痕跡イベントがなかった場合のみ来訪テキストを表示
        "チャイムが鳴った。"

    # 清潔感チェック
    if player["cleanliness"] >= 60:
        show misaki casual pleased
        misaki_c "あ、結構きれいにしてるんだね"
        himo "まあな"
        $ change_trust(3)
    elif player["cleanliness"] < 35:
        show misaki casual shock
        misaki_c "...ヒモ太郎、ちょっとこれは..."
        himo "ごめん..."
        $ change_trust(-5)
        show misaki casual sad
        "美咲が少し引いている。"

    # Phase 4 Step 3: プレゼントを渡す
    if inventory.get("bouquet", False) or inventory.get("accessory", False):
        menu:
            "プレゼントを渡す":
                call give_present("misaki")
            "渡さない":
                pass

    # v2.0: 3ラウンド自宅デートシステム（会話・泊まり・交渉を一括処理）
    call home_date("misaki")

    # 共通処理
    $ misaki["met_today"] = True
    $ stats["times_met"] += 1
    $ daily_flags["date_with"] = "misaki"
    $ daily_flags["date_location"] = "himo_room"
    $ reset_contact()

    # 探り・ハプニング
    call check_date_incidents("misaki")

    return


label misaki_date_fancy:
    scene bg_restaurant
    show misaki casual smile with dissolve
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["fancy"] = stats["date_locations"].get("fancy", 0) + 1
    "少しいい店に入った。"
    "自分から奢りを申し出た。"
    show misaki casual surprised
    misaki_c "え、いいの？"
    himo "たまにはな"

    show misaki casual happy
    misaki_c "...ありがとう"
    "美咲が嬉しそうに笑った。"

    $ change_money(-3000)
    $ change_trust(10)
    $ change_dependence(3)
    $ change_stamina(-10)
    $ change_stamina(25)   # いい店なので満足度高い（差し引き+15）

    # === 対面交渉の切り出しチャンス ===
    if misaki["trust"] >= 35 and money_request_weekly["count"] < NEGOTIATION_WEEKLY_LIMIT and not daily_flags.get("asked_money_today", False):
        menu:
            "会話が落ち着いてきた。"

            "お金の話を切り出す":
                call misaki_negotiation_start

            "このまま楽しむ":
                # v1.2: お金の話をしなかった→好印象
                if suspicion.get("misaki", 0) >= 6:
                    himo "（今日はお金の話はやめとこう）"
                $ reduce_suspicion("misaki", 1, "デート楽しむ")

    return
