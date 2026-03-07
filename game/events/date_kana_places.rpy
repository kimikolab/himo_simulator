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
    $ daily_flags["ate_today"] = True  # カナとのデートは食事込み

    # 探り・地雷・ハプニングの判定
    call check_date_incidents("kana")

    return


label kana_date_cafe:
    "カフェに入った。"
    kana_c "ここインスタ映えする〜"

    "カナがスマホを取り出して写真を撮り始めた。"

    $ change_trust_kana(5)
    $ change_dependence_kana(3)
    $ change_stamina(-10)
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 2

    return


label kana_date_karaoke:
    "カラオケに行った。"
    kana_c "何歌う？"
    himo "適当に"

    "盛り上がった。カナの歌が意外と上手い。"

    $ change_money(-500)
    $ change_trust_kana(8)
    $ change_dependence_kana(5)
    $ change_stamina(-15)
    # SNSリスクなし

    return


label kana_date_campus:
    "カナの大学の近くで会った。"
    kana_c "この辺よく来るんだ〜"

    "カナの友達とすれ違った。"
    kana_c "あ、まりちゃん！紹介するね、ヒモ太郎！"

    "...紹介された。"

    $ change_trust_kana(8)
    $ change_dependence_kana(4)
    $ change_stamina(-10)
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 1

    # 情報収集イベント
    if not flags.get("kana_friend_info_obtained", False):
        "友達と少し話す機会があった。"
        "友達「カナってさ、前の彼氏に浮気されてから男性不信なんだよね」"
        "友達「だからヒモ太郎のこと大事にしてあげてね」"
        himo "（...なるほど）"
        $ flags["kana_friend_info_obtained"] = True
        "カナの過去を知った。今後の会話で地雷を避けやすくなるかもしれない。"

    return


label kana_date_himo_room:
    "ヒモ太郎の部屋で会うことにした。"

    if player["cleanliness"] >= 50:
        kana_c "意外と綺麗にしてるじゃん"
        $ change_trust_kana(5)
    elif player["cleanliness"] >= 30:
        kana_c "...まあ、男の人の部屋ってこんなもんか"
        $ change_trust_kana(3)
    else:
        kana_c "...汚い"
        $ change_trust_kana(-3)

    $ change_dependence_kana(6)
    $ change_stamina(-5)
    # SNSリスクなし、コストなし

    # 親密スキル経験値（将来のエナマッチ用）
    $ himo_aptitude["intimacy_exp"] = himo_aptitude.get("intimacy_exp", 0) + 1

    return
