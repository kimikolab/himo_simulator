# sns_system.rpy
# SNS受動通知システム — 行動枠を消費せず情報が流れる

init python:
    def check_sns_notification():
        """朝・昼の行動メニュー前に呼び出す"""
        if daily_flags["sns_shown_today"]:
            return

        notifications = []

        # --- カテゴリ1: フレーバー（常時ランダム） ---
        if renpy.random.random() < 0.25:
            notifications.append("flavor")

        # --- カテゴリ2: カナ匂わせ（カナ出会い済み＋信頼20以上） ---
        if (kana_flags["met"]
            and kana["trust"] >= 20
            and renpy.random.random() < 0.20):
            notifications.append("kana_hint")

        # --- カテゴリ3: 美咲の意味深（美咲依存40以上） ---
        if (misaki["dependence"] >= 40
            and renpy.random.random() < 0.20):
            notifications.append("misaki_mood")

        # --- カテゴリ4: 目撃系（SNSリスク3以上） ---
        if (kana_flags.get("sns_risk", 0) >= 3
            and not flags.get("midgame_sighting_done", False)
            and game_date["day"] >= 16
            and renpy.random.random() < 0.25):
            notifications.append("sighting")

        # --- カテゴリ5: ニュース系（低確率フレーバー） ---
        if renpy.random.random() < 0.10:
            notifications.append("news")

        # 最大2件まで表示
        if notifications:
            selected = notifications[:SNS_MAX_PER_DAY]
            for notif_type in selected:
                _pending_events.append(("sns_show_" + notif_type, None))
            daily_flags["sns_shown_today"] = True


label sns_show_flavor:
    python:
        # 投稿をカテゴリ付きで管理（poster, content, tone）
        posts = [
            ("同級生・健太", "『本日付で主任に昇進しました！』", "positive"),
            ("同級生・由美", "『マイホーム購入 35年ローン頑張ります...』", "neutral"),
            ("同級生・大輔", "『転職成功！試用期間中で緊張する』", "neutral"),
            ("バイト仲間・拓也", "『バイトだるい〜 でも気楽でいいか』", "relatable"),
            ("高校同級生・真理", "『結婚しました！！！』", "marriage"),
            ("知り合い・翔太", "『起業して半年、やっと黒字化』", "positive"),
        ]
        poster, content, _tone = renpy.random.choice(posts)

        # カテゴリ別反応プール
        _reaction_pools = {
            "positive": [
                "へー...まあ俺は俺だし",
                "ふーん、頑張ってんな...まあ俺には関係ないけど",
                "すごいな...俺もなんとかなるだろ。まあ明日から",
                "まあ、みんな大変そうだな。がんばれがんばれ",
            ],
            "neutral": [
                "さーね。まあ人それぞれだろ",
                "ローンとか責任とか、色々背負うんだな。俺は無理",
                "みんな頑張ってんな。俺は俺のペースで",
                "大変そう。でもちょっと羨まし...いやさすがに無理",
            ],
            "relatable": [
                "わかる...って、俺もいつもなんだった",
                "だよな、気楽が一番...たぶん",
                "同じような生活してるやつがいると安心する...のかこれで",
            ],
            "marriage": [
                "へー、結婚か。おめでと...って思うべきなのかな",
                "結婚か。俺には想像がつかない世界だ",
                "みんなどんどん先に行くな...まあいっか",
            ],
        }
        _reaction = renpy.random.choice(_reaction_pools.get(_tone, _reaction_pools["positive"]))

    "SNSに通知。"
    "[poster]の投稿:"
    "[content]"
    himo "[_reaction]"

    return


label sns_show_kana_hint:
    python:
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
        post = renpy.random.choice(posts)

    "[post]"
    himo "...これ、誰でも見れるんだよな"
    himo "大丈夫かな"

    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 1

    return


label sns_show_misaki_mood:
    python:
        # v1.5: 冷戦レベル別ステータス分岐
        _cw_level = cold_war.get("misaki_level", 0) if cold_war.get("misaki_active", False) else 0
        if _cw_level >= 2:
            posts = [
                "美咲のLINEステータスが変わっている。\n「...」",
                "美咲のステータス。\n「もういいかな」",
                "美咲のLINEステータスが変わっている。\n「信じるって難しい」",
            ]
        elif _cw_level == 1:
            posts = [
                "美咲のLINEステータスが変わっている。\n「...」",
                "美咲のステータス。\n「考え中」",
                "美咲のLINEステータスが変わっている。\n「一人の時間も大事」",
            ]
        elif misaki["dependence"] >= 60:
            posts = [
                "美咲のLINEステータスが変わっている。\n「...会いたいな」",
                "美咲のステータス。\n「早く帰りたい」",
            ]
        else:
            posts = [
                "美咲のLINEステータスが変わっている。\n「疲れた...」",
                "美咲のステータス。\n「残業つらい」",
            ]
        post = renpy.random.choice(posts)

    "[post]"

    if cold_war.get("misaki_active", False):
        if cold_war.get("misaki_level", 0) >= 2:
            himo "...怒ってるな、完全に"
        else:
            himo "...気まずいな"
    elif misaki["dependence"] >= 60:
        himo "...重いな"
    else:
        himo "大変そうだな"

    return


label sns_show_sighting:
    python:
        posts = [
            "知らないアカウントの投稿が目に入った。\n「駅前でいちゃついてるカップル見た笑」",
            "美咲の同僚っぽいアカウント。\n「あれ？美咲ちゃんの彼氏？見たことない人と歩いてた」",
            "カナの友達のストーリー。\n「カナの彼氏？大学の近くで見かけた気がする」",
        ]
        post = renpy.random.choice(posts)

    "[post]"

    himo "..."
    himo "（やばい...見られてた？）"

    # 修羅場イベント⑥のフラグを立てる
    $ flags["midgame_sighting_done"] = True

    return


label sns_show_news:
    python:
        posts = [
            ("ニュースアプリ", "『若者の恋愛離れが深刻化 交際経験なし4割超』"),
            ("ニュースアプリ", "『同棲カップルの家計管理術 共同口座のススメ』"),
            ("ニュースアプリ", "『マッチングアプリ利用者 過去最高を更新』"),
            ("ニュースアプリ", "『二股交際で損害賠償 200万円の判決』"),
            # v1.3追加
            ("ニュースアプリ", "『副業で月10万稼ぐ方法 会社員の3割が挑戦』"),
            ("ニュースアプリ", "『家賃滞納で即退去？ 法的にはどうなの』"),
            ("ニュースアプリ", "『フリーターから正社員へ 転職成功の秘訣』"),
            ("ニュースアプリ", "『一人暮らしの食費 月3万円以下で抑える方法』"),
            ("ニュースアプリ", "『SNSで浮気発覚 証拠になるケースとは』"),
        ]

        # v1.3: 前回表示したニュースを除外して重複防止
        last_news = flags.get("last_news_item", "")
        available_news = [p for p in posts if p[1] != last_news]
        if not available_news:
            available_news = posts
        source, content = renpy.random.choice(available_news)
        flags["last_news_item"] = content

    "[source]の通知:"
    "[content]"

    himo "...ふーん"

    return
