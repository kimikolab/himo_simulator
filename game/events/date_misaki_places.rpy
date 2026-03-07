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

    # 探り・地雷・ハプニングの判定
    call check_date_incidents("misaki")

    return


label misaki_date_famires:
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

    return


label misaki_date_izakaya:
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["izakaya"] = stats["date_locations"].get("izakaya", 0) + 1
    "居酒屋に入った。"
    misaki_c "たまにはこういうのもいいね"

    "お酒が入って、美咲の口数が増える。"
    "美咲が奢ってくれた。"

    $ change_trust(5)
    $ change_dependence(5)
    $ change_stamina(-15)
    $ change_stamina(20)   # 食事による体力回復（差し引き+5）

    return


label misaki_date_room:
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["misaki_room"] = stats["date_locations"].get("misaki_room", 0) + 1
    "美咲の部屋に行った。"
    misaki_c "散らかっててごめんね"
    himo "いいっていいって"

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

    return


label misaki_date_fancy:
    $ stats["date_locations"] = stats.get("date_locations", {})
    $ stats["date_locations"]["fancy"] = stats["date_locations"].get("fancy", 0) + 1
    "少しいい店に入った。"
    "自分から奢りを申し出た。"
    misaki_c "え、いいの？"
    himo "たまにはな"

    misaki_c "...ありがとう"
    "美咲が嬉しそうに笑った。"

    $ change_money(-3000)
    $ change_trust(10)
    $ change_dependence(3)
    $ change_stamina(-10)
    $ change_stamina(25)   # いい店なので満足度高い（差し引き+15）

    return
