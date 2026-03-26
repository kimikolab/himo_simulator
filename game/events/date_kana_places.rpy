# date_kana_places.rpy
# カナデート — 場所選択で展開が変わる

label kana_date_with_location:
    scene bg_placeholder

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

    # 探り・地雷・ハプニングの判定
    call check_date_incidents("kana")

    # === ステップ2追加: 夜デートの場合、泊まり判定 ===
    if game_date["time"] == "night" and kana["trust"] >= 30:
        call kana_stay_offer

    return


label kana_date_cafe:
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["cafe"] = stats["date_locations"].get("cafe", 0) + 1
    "カフェに入った。"
    kana_c "ここインスタ映えする〜"

    "カナがスマホを取り出して写真を撮り始めた。"
    "カナが奢ってくれた。"

    $ change_trust_kana(4)    # v1.3: 5→4
    $ change_dependence_kana(3)
    $ change_stamina(-10)
    $ change_stamina(15)   # カフェの軽食（差し引き+5）
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 2

    return


label kana_date_karaoke:
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

    return


label kana_date_campus:
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["campus"] = stats["date_locations"].get("campus", 0) + 1
    "カナの大学の近くで会った。"
    kana_c "この辺よく来るんだ〜"

    "カナの友達とすれ違った。"
    kana_c "あ、まりちゃん！紹介するね、ヒモ太郎！"

    "...紹介された。"
    "近くの店でご飯を食べた。カナが奢ってくれた。"

    $ change_trust_kana(6)    # v1.3: 8→6
    $ change_dependence_kana(4)
    $ change_stamina(-10)
    $ change_stamina(20)   # 食事（差し引き+10）
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 1

    # 情報収集イベント
    if not flags.get("kana_friend_info_obtained", False):
        "友達と少し話す機会があった。"
        "友達「カナってさ、前の彼氏に浮気されてから男性不信なんだよね」"
        "友達「だからカナのこと大事にしてあげてね」"
        himo "（...なるほど）"
        $ flags["kana_friend_info_obtained"] = True
        "カナの過去を知った。今後の会話で地雷を避けやすくなるかもしれない。"

    return


label kana_date_himo_room:
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["himo_room"] = stats["date_locations"].get("himo_room", 0) + 1
    "ヒモ太郎の部屋で会うことにした。"

    if player["cleanliness"] >= 50:
        kana_c "意外と綺麗にしてるじゃん"
        $ change_trust_kana(4)    # v1.3: 5→4
    elif player["cleanliness"] >= 30:
        kana_c "...まあ、男の人の部屋ってこんなもんか"
        $ change_trust_kana(2)    # v1.3: 3→2
    else:
        kana_c "...汚い"
        $ change_trust_kana(-3)

    $ change_dependence_kana(6)
    $ change_stamina(-5)
    # SNSリスクなし、コストなし

    # 親密スキル経験値（将来のエナマッチ用）
    $ himo_aptitude["intimacy_exp"] = himo_aptitude.get("intimacy_exp", 0) + 1

    return
