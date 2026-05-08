# date_kana_places.rpy
# カナデート — 場所選択で展開が変わる

label kana_date_with_location:
    # BGM: デート開始
    play music bgm_date_good fadein 1.0

    "カナと会うことになった。"

    menu:
        "どこに行く？"

        "カフェ（奢り・SNSリスクあり）":
            $ daily_flags["date_location"] = "cafe"
            call kana_date_cafe

        "カラオケ（¥500・SNSリスクなし）" if can_afford(500):
            $ daily_flags["date_location"] = "karaoke"
            call kana_date_karaoke

        "カナの大学付近（情報収集・奢り）":
            $ daily_flags["date_location"] = "campus"
            call kana_date_campus

        "ヒモ太郎の部屋（コスト0・清潔感依存）":
            $ daily_flags["date_location"] = "himo_room"
            call kana_date_himo_room

    # デート後の共通処理
    $ kana["met_today"] = True
    $ kana["last_contact"] = 0
    $ daily_flags["date_with"] = "kana"
    # Phase 4 v1.1: ate_today は場所別に設定（部屋以外は食事あり）
    if daily_flags["date_location"] != "himo_room":
        $ daily_flags["ate_today"] = True

    # Phase 4 Step 3: プレゼントを渡す
    if inventory.get("bouquet", False) or inventory.get("accessory", False) or (inventory.get("kana_goods", False)):
        menu:
            "プレゼントを渡す":
                call give_present("kana")
            "渡さない":
                pass

    # 探り・地雷・ハプニングの判定
    call check_date_incidents("kana")

    # === ステップ2追加: 夜デートの場合、泊まり判定 ===
    if game_date["time"] == "night" and kana["trust"] >= 30:
        call kana_stay_offer

    # BGM: デート終了 → 日常に戻す
    stop music fadeout 1.0
    play music bgm_daily fadein 1.0

    return


label kana_date_cafe:
    scene bg_cafe
    show kana happy with dissolve
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["cafe"] = stats["date_locations"].get("cafe", 0) + 1
    $ kana_date_location_count["cafe"] = kana_date_location_count.get("cafe", 0) + 1

    "カフェに入った。"

    # v1.7: 訪問回数でテキスト分岐
    python:
        _cafe_count = kana_date_location_count["cafe"]

    if _cafe_count == 1:
        kana_c "ここインスタ映えする〜"
        "カナがスマホを取り出して写真を撮り始めた。"
    elif _cafe_count == 2:
        kana_c "また来ちゃった"
        kana_c "ここのパンケーキが好きなんだよね"
    else:
        python:
            _cafe_txt = renpy.random.randint(0, 2)
        if _cafe_txt == 0:
            kana_c "ここ来すぎじゃない？笑"
            himo "カナが好きなんだろ"
        elif _cafe_txt == 1:
            kana_c "今日は新メニュー出てるよ"
        else:
            "店員に顔を覚えられていた。"
            "店員「いつものお席ですか？」"
            himo "（常連扱い...）"

    "カナが奢ってくれた。"

    $ change_trust_kana(4)    # v1.3: 5→4
    $ change_dependence_kana(3)
    $ change_stamina(-10)
    $ change_stamina(15)   # カフェの軽食（差し引き+5）
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 2

    hide kana
    return


label kana_date_karaoke:
    scene bg_karaoke
    show kana excited with dissolve
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["karaoke"] = stats["date_locations"].get("karaoke", 0) + 1
    "カラオケに行った。"
    kana_c "何歌う？"
    himo "適当に"

    "盛り上がった。カナの歌が意外と上手い。"
    "途中で軽く食べた。"

    $ change_money(-500)
    $ change_trust_kana(6)    # v1.3: 8→6
    $ change_dependence_kana(5)
    $ change_stamina(-15)
    $ change_stamina(10)   # 軽食（差し引き-5。はしゃいだので消耗の方が大きい）

    hide kana
    return


label kana_date_campus:
    scene bg_campus
    show kana university happy with dissolve
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["campus"] = stats["date_locations"].get("campus", 0) + 1
    $ kana_date_location_count["university"] = kana_date_location_count.get("university", 0) + 1

    "カナの大学の近くで会った。"

    # v1.7: 訪問回数でテキスト分岐
    python:
        _campus_count = kana_date_location_count["university"]

    if _campus_count == 1:
        kana_c "この辺よく来るんだ〜"
        "カナの友達とすれ違った。"
        kana_c "あ、まりちゃん！紹介するね、ヒモ太郎！"
        "...紹介された。"
    elif _campus_count == 2:
        "カナの友達とすれ違った。"
        kana_c "あ、まりちゃん！この前の人！"
        "まりちゃん「あ〜、カナの彼氏？」"
        himo "（彼氏...?）"
    else:
        python:
            _campus_txt = renpy.random.randint(0, 2)
        if _campus_txt == 0:
            kana_c "今日はまりちゃんいないね"
            himo "そっか"
        elif _campus_txt == 1:
            "遠くにカナの知り合いが見える。"
            kana_c "あ、知り合い。...今日は紹介しなくていいや"
            himo "（助かる）"
        else:
            kana_c "この辺のラーメン屋おいしいんだよね"
            himo "行こう"

    "近くの店でご飯を食べた。カナが奢ってくれた。"

    $ change_trust_kana(6)    # v1.3: 8→6
    $ change_dependence_kana(4)
    $ change_stamina(-10)
    $ change_stamina(20)   # 食事（差し引き+10）
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 1

    # 情報収集イベント（初回のみ）
    if not flags.get("kana_friend_info_obtained", False):
        "友達と少し話す機会があった。"
        "友達「カナってさ、前の彼氏に浮気されてから男性不信なんだよね」"
        "友達「だからカナのこと大事にしてあげてね」"
        himo "（...なるほど）"
        $ flags["kana_friend_info_obtained"] = True
        "カナの過去を知った。今後の会話で地雷を避けやすくなるかもしれない。"

    hide kana
    return


label kana_date_himo_room:
    scene bg_himo_room
    show kana normal with dissolve
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["himo_room"] = stats["date_locations"].get("himo_room", 0) + 1
    # v1.2追加: カナ用のhimo_roomカウンタも更新
    $ stats["date_locations"]["himo_room_kana"] = stats["date_locations"].get("himo_room_kana", 0) + 1
    "ヒモ太郎の部屋で会うことにした。"

    # 清潔感チェック
    if player["cleanliness"] >= 50:
        show kana pleased
        kana_c "意外と綺麗にしてるじゃん"
        $ change_trust_kana(3)
    elif player["cleanliness"] < 30:
        show kana angry
        kana_c "...汚い"
        $ change_trust_kana(-3)

    # v2.0: 3ラウンド自宅デートシステム（会話・泊まり判定を一括処理）
    call home_date("kana")

    # 共通処理
    $ change_stamina(-5)
    $ himo_aptitude["intimacy_exp"] = himo_aptitude.get("intimacy_exp", 0) + 1

    hide kana
    return
