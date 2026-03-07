# sns_system.rpy
# SNS受動通知システム — 行動枠を消費せず情報が流れる

init python:
    def check_sns_notification():
        """朝・昼の行動メニュー前に呼び出す"""
        import random

        if daily_flags["sns_shown_today"]:
            return

        notifications = []

        # --- カテゴリ1: フレーバー（常時ランダム） ---
        if random.random() < 0.25:
            notifications.append("flavor")

        # --- カテゴリ2: カナ匂わせ（カナ出会い済み＋信頼20以上） ---
        if (kana_flags["met"]
            and kana["trust"] >= 20
            and random.random() < 0.20):
            notifications.append("kana_hint")

        # --- カテゴリ3: 美咲の意味深（美咲依存40以上） ---
        if (misaki["dependence"] >= 40
            and random.random() < 0.20):
            notifications.append("misaki_mood")

        # --- カテゴリ4: 目撃系（SNSリスク3以上） ---
        if (kana_flags.get("sns_risk", 0) >= 3
            and not flags.get("midgame_sighting_done", False)
            and game_date["day"] >= 16
            and random.random() < 0.25):
            notifications.append("sighting")

        # --- カテゴリ5: ニュース系（低確率フレーバー） ---
        if random.random() < 0.10:
            notifications.append("news")

        # 最大2件まで表示
        if notifications:
            selected = notifications[:SNS_MAX_PER_DAY]
            for notif_type in selected:
                _pending_events.append(("sns_show_" + notif_type, None))
            daily_flags["sns_shown_today"] = True


label sns_show_flavor:
    python:
        import random
        posts = [
            ("同級生・健太", "『本日付で主任に昇進しました！』"),
            ("同級生・由美", "『マイホーム購入 35年ローン頑張ります...』"),
            ("同級生・大輔", "『転職成功！試用期間中で緊張する』"),
            ("バイト仲間・拓也", "『バイトだるい〜 でも気楽でいいか』"),
            ("高校同級生・真理", "『結婚しました！！！』"),
            ("知り合い・翔太", "『起業して半年、やっと黒字化』"),
        ]
        poster, content = random.choice(posts)

    "SNSに通知。"
    "[poster]の投稿:"
    "[content]"
    himo "へー...まあ俺は俺だし"

    return


label sns_show_kana_hint:
    python:
        import random
        depend = kana["dependence"]
        if depend >= 40:
            posts = [
                "カナがストーリーを更新した。\n「今日も会えた...幸せ」",
                "カナがストーリーを更新した。\n「最近毎日楽しい。誰のおかげかな」",
                "カナが意味深な匂わせ投稿をしている。\nハートマークだらけの写真。",
            ]
        else:
            posts = [
                "カナがストーリーを更新した。\n「最近いい感じの人がいるかも」",
                "カナがカフェの写真を投稿。\n「ここ最近のお気に入り」",
            ]
        post = random.choice(posts)

    "[post]"
    himo "...これ、誰でも見れるんだよな"
    himo "大丈夫かな"

    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 1

    return


label sns_show_misaki_mood:
    python:
        import random
        depend = misaki["dependence"]
        if depend >= 60:
            posts = [
                "美咲のLINEステータスが変わっている。\n「...会いたいな」",
                "美咲のステータス。\n「早く帰りたい」",
            ]
        else:
            posts = [
                "美咲のLINEステータスが変わっている。\n「疲れた...」",
                "美咲のステータス。\n「残業つらい」",
            ]
        post = random.choice(posts)

    "[post]"

    if misaki["dependence"] >= 60:
        himo "...重いな"
    else:
        himo "大変そうだな"

    return


label sns_show_sighting:
    python:
        import random
        posts = [
            "知らないアカウントの投稿が目に入った。\n「駅前でいちゃついてるカップル見た笑」",
            "美咲の同僚っぽいアカウント。\n「あれ？美咲ちゃんの彼氏？見たことない人と歩いてた」",
            "カナの友達のストーリー。\n「カナの彼氏？大学の近くで見かけた気がする」",
        ]
        post = random.choice(posts)

    "[post]"

    himo "..."
    himo "（やばい...見られてた？）"

    # 修羅場イベント⑥のフラグを立てる
    $ flags["midgame_sighting_done"] = True

    return


label sns_show_news:
    python:
        import random
        posts = [
            ("ニュースアプリ", "『若者の恋愛離れが深刻化 交際経験なし4割超』"),
            ("ニュースアプリ", "『同棲カップルの家計管理術 共同口座のススメ』"),
            ("ニュースアプリ", "『マッチングアプリ利用者 過去最高を更新』"),
            ("ニュースアプリ", "『二股交際で損害賠償 200万円の判決』"),
        ]
        source, content = random.choice(posts)

    "[source]の通知:"
    "[content]"

    himo "...ふーん"

    return
