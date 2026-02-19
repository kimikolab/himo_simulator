# daily_events.rpy
# 日常イベント（Phase 2: SNSバリエーション追加・週末行動追加）

label check_sns:
    "SNSのタイムラインを見た。"

    python:
        sns_posts = [
            # Phase 1から
            ("同級生・健太", "『本日付で主任に昇進しました！』", "positive"),
            ("同級生・由美", "『マイホーム購入 35年ローン頑張ります...』", "neutral"),
            ("同級生・大輔", "『転職成功！でも試用期間中緊張する』", "neutral"),
            ("バイト仲間・拓也", "『バイトだるい〜 でも気楽でいいか』", "relatable"),
            # Phase 2追加
            ("同級生・翔太", "『子ども生まれた！これからが大変だけど頑張る』", "milestone"),
            ("大学の友人・みほ", "『フリーランス2年目突入！仕事増えてきた』", "positive"),
            ("高校の先輩", "『会社の飲み会が憂鬱すぎる 毎回同じ話』", "relatable"),
            ("元バイト仲間・ケン", "『正社員になりました！給料上がった！』", "positive"),
            ("SNSのフォロワー", "『生きてるだけで丸儲けとか言うけど金はいるよな』", "relatable"),
            ("知らない人のバズポスト", "『20代のうちに貯金しとかないと老後やばいぞ』", "scary"),
        ]
        post = renpy.random.choice(sns_posts)
        poster, content, tone = post

    "[poster]の投稿:"
    "[content]"

    if tone == "positive":
        himo "おー、すげえじゃん"
        himo "でも大変そうだな"
        $ stats["optimistic_choices"] += 1

    elif tone == "neutral":
        himo "ローンとか責任とか、色々背負うんだな"
        himo "俺はそういうの無理だわ"
        $ stats["optimistic_choices"] += 1
        $ himo_aptitude["avoided_work"] += 1

    elif tone == "relatable":
        himo "わかる〜"
        himo "...って、俺バイトないんだった"
        himo "まあいっか"

    elif tone == "milestone":
        himo "子どもか..."
        "なんか、自分と全然違う人生を歩いてる人がいる。"
        himo "俺はまあ...自由でいいか"

    elif tone == "scary":
        himo "...老後"
        himo "考えてなかった"
        himo "まあ、今考えても仕方ないか！"
        $ himo_aptitude["avoided_work"] += 1

    # SNS効果（v2.0追加）
    if tone in ("milestone", "scary"):
        $ change_stamina(-3)
    elif tone == "relatable":
        $ change_charm(1)

    python:
        if misaki["stage"] >= STAGE_CLOSE and renpy.random.random() < 0.15:
            renpy.call("sns_misaki_post")

    python:
        if renpy.random.random() < 0.15 and not flags["had_doubt_moment"]:
            renpy.call("moment_of_doubt")

    return


label moment_of_doubt:
    himo "...あれ、俺このままで大丈夫かな"

    himo "まあ、何とかなるっしょ"

    $ flags["had_doubt_moment"] = True
    $ change_stamina(-3)
    return


label afternoon_street:
    scene bg_placeholder

    "街に出た。"

    if is_weekend():
        "週末の昼下がり。"
        "カップルや家族連れが多い。"
        himo "みんな楽しそうだな"
    else:
        "平日の昼下がり。"
        "スーツ姿のサラリーマンが急いで歩いてる。"

        himo "みんな忙しそうだな"
        himo "俺は自由でいいわ〜"

    menu:
        "何をする？"

        "カフェで休憩":
            # v2.6追加: 所持金チェック
            if not can_afford(500):
                himo "...財布の中身が足りない"
                jump afternoon_street

            "カフェに入った。"

            himo "平日昼のカフェ、最高"

            "周りはノーパソ開いてる人とか打ち合わせとか。"

            himo "みんな働いてんな〜"
            himo "俺はコーヒー飲むだけ！楽勝！"

            "...500円か。ちょっと痛いな。"

            $ change_money(-500)
            $ change_stamina(10)
            $ himo_aptitude["easy_choices"] += 1

        "服を見る":
            # v2.6追加: 所持金チェック
            if not can_afford(3000):
                himo "...欲しいけど、今は無理だな"
                jump afternoon_street

            "服屋に入った。"

            himo "ちょっといい服買っとくか"

            $ change_money(-3000)
            $ change_charm(5)

            himo "おっ、いい感じ"

        "100円ショップに行く":
            # v2.6追加: 所持金チェック
            if not can_afford(300):
                himo "100円ショップすら厳しいとか..."
                jump afternoon_street

            "100円ショップをぶらぶら。"

            himo "100円で色々買えるの、最高だな"

            $ change_money(-300)

        "求人情報を見る":
            call check_job_hint

        "自宅に戻る":
            himo "帰るか"

    return


label check_job_hint:
    "街角の求人情報を見た。"

    "『未経験歓迎！』"
    "『20代活躍中！』"
    "『正社員登用あり！』"

    himo "...働くって選択肢もあるんだよな"

    if stats["times_met"] > 0:
        "でも、今は美咲もいるし。"

    himo "まあ、また今度考えよう"

    $ himo_aptitude["avoided_work"] += 1

    return


# Phase 2追加: 週末の買い物
label weekend_shopping:
    scene bg_placeholder
    "週末のスーパーに来た。"
    "家族連れで賑わっている。"
    himo "週末はにぎやかだな"

    menu:
        "何を買う？"
        "食材を買う（300〜800円）":
            if not can_afford(300):
                himo "...お金が..."
                return
            python:
                cost = renpy.random.randint(300, 800)
            $ change_money(-cost)
            $ change_stamina(8)
            himo "自炊するか"

        "お菓子を買う（200〜500円）":
            if not can_afford(200):
                himo "...節約しないと"
                return
            python:
                cost = renpy.random.randint(200, 500)
            $ change_money(-cost)
            $ change_stamina(5)
            himo "まあいっか、たまには"
            $ himo_aptitude["easy_choices"] += 1

        "何も買わずに帰る":
            himo "...金使わないほうがいいか"

    return


# ========================================
# Phase 2 v2.0: SNS美咲投稿
# ========================================

label sns_misaki_post:
    "美咲の投稿が流れてきた。"
    python:
        posts = [
            "'最近なんか充実してる気がする'",
            "'仕事疲れたけど、帰ったら連絡しよう'",
            "'たまには息抜きも大事だよね'",
        ]
        post = renpy.random.choice(posts)
    "[post]"
    himo "（...俺のことかな）"
    himo "（まあ、そんなわけないか）"
    return


# ========================================
# Phase 2 v2.0: ランダム出費イベント
# ========================================

label random_expense_event:
    python:
        events = [
            ("スマホの画面が割れた", 5000, "repair"),
            ("急に体調が悪くなった", 1500, "medicine"),
            ("友人から結婚祝いを求められた", 3000, "gift"),
            ("コインランドリーに行く羽目になった", 800, "laundry"),
            ("財布を落としかけてヒヤッとした", 0, "scare"),
        ]
        ev_name, ev_cost, ev_type = renpy.random.choice(events)

    "――[ev_name]――"

    if ev_cost > 0:
        if can_afford(ev_cost):
            "[ev_cost]円かかった。"
            $ change_money(-ev_cost)
        else:
            himo "...金がない"
            if ev_type == "medicine":
                himo "薬も買えないのか"
                $ change_stamina(-15)
            elif ev_type == "repair":
                himo "画面割れたまま使うか..."
                $ change_charm(-3)
    else:
        himo "やばい、財布..."
        himo "...あった。よかった"

    return
