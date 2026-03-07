# midgame_events.rpy
# 中盤イベント — ルーティンを崩す揺さぶり＋修羅場

init python:
    def check_midgame_events():
        """main_loopの各ターン開始時に呼び出す"""
        day = game_date["day"]
        time = game_date["time"]

        # --- 中盤前半（9〜15日） ---

        # イベント①: 美咲「最近忙しいの？」
        if (day >= 9 and day <= 15
            and not flags.get("midgame_busymisaki_done", False)
            and kana_flags["met"]
            and misaki["last_contact"] >= 3
            and time == "morning"):
            _pending_events.append(("midgame_misaki_busy", None))
            return True

        # イベント④: カナからの急な呼び出し
        if (day >= 10 and day <= 20
            and kana_flags["met"]
            and kana["dependence"] >= 20
            and time == "afternoon"
            and not kana["met_today"]):
            import random
            if random.random() < 0.20:
                _pending_events.append(("midgame_kana_urgent", None))
                return True

        # --- 中盤後半（16〜23日） ---

        # イベント⑤: ダブルブッキング危機
        if (day >= 16 and day <= 25
            and not flags.get("midgame_doublebooking_done", False)
            and kana_flags["met"]
            and misaki["stage"] >= STAGE_FRIEND
            and kana["trust"] >= 25
            and time == "afternoon"
            and not daily_flags["double_booking_checked"]):
            import random
            if random.random() < 0.30:
                _pending_events.append(("midgame_double_booking", None))
                return True

        # イベント⑥: 目撃情報 → 修羅場
        if (flags.get("midgame_sighting_done", False)
            and not flags.get("midgame_sighting_confronted", False)
            and time == "night"):
            import random
            if random.random() < 0.40:
                _pending_events.append(("midgame_sighting_confrontation", None))
                return True

        # イベント⑦: カナの突撃訪問
        if (day >= 18
            and not flags.get("midgame_kana_raid_done", False)
            and kana_flags["met"]
            and kana["dependence"] >= 40
            and time == "night"
            and not kana["met_today"]):
            import random
            if random.random() < 0.20:
                _pending_events.append(("midgame_kana_raid", None))
                return True

        # イベント⑧: 美咲の直球質問 ver.2
        if (day >= 18
            and not flags.get("midgame_misaki_direct_done", False)
            and suspicion["misaki"] >= SUSPICION_SHURABA_THRESHOLD
            and misaki["trust"] >= 50
            and time == "night"):
            _pending_events.append(("midgame_misaki_direct", None))
            return True

        return False


# === イベント①: 美咲「最近忙しいの？」 ===

label midgame_misaki_busy:
    scene bg_placeholder

    "朝、スマホを見ると美咲からLINEが来ていた。"
    misaki_c "おはよう。最近連絡ないけど、忙しいの？"

    "...3日以上連絡してなかった。"

    menu:
        "すぐ返信する":
            himo "ごめん、ちょっとバタバタしてて"
            misaki_c "...そうなんだ。元気ならいいんだけど"
            "少し間があった。"
            misaki_c "最近、全然連絡くれないなって思って"
            $ change_trust(-5)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)
            $ reset_contact()

        "後で返そう（スルー）":
            "後で返せばいいか。"
            himo "まあいっか"
            $ change_trust(-10)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
            $ himo_aptitude["easy_choices"] += 1

    $ flags["midgame_busymisaki_done"] = True
    return


# === イベント③: パチンコの誘惑 ===
# （afternoon_streetから呼び出される）

label midgame_pachinko_temptation:
    scene bg_placeholder

    "街を歩いていると、パチンコ屋の前を通りかかった。"
    "「新台入替！大盤振舞！」"

    himo "...ちょっと覗くだけ"

    menu:
        "入る":
            "気づいたら座っていた。"
            himo "まあちょっとだけ..."

            python:
                import random
                pachinko_result = random.choice(["big_win", "small_win", "lose", "big_lose"])

            if pachinko_result == "big_win":
                "大当たり！！！"
                himo "うおおお！！！"
                $ change_money(15000)
                $ stats["pachinko_profit"] = stats.get("pachinko_profit", 0) + 15000
                "¥15,000の勝ち。最高の気分。"
                himo "パチンコ最高！"
                $ himo_aptitude["easy_choices"] += 2

            elif pachinko_result == "small_win":
                "少し勝った。"
                $ change_money(3000)
                $ stats["pachinko_profit"] = stats.get("pachinko_profit", 0) + 3000
                himo "まあまあかな"
                $ himo_aptitude["easy_choices"] += 1

            elif pachinko_result == "lose":
                "負けた。"
                $ change_money(-5000)
                $ stats["pachinko_profit"] = stats.get("pachinko_profit", 0) - 5000
                himo "...まあこんなもんか"

            else:
                "大負け。"
                $ change_money(-10000)
                $ stats["pachinko_profit"] = stats.get("pachinko_profit", 0) - 10000
                himo "...やば"
                "財布の中身が一気に減った。"
                if player["money"] < MONTHLY_RENT:
                    "（家賃...大丈夫か？）"

            $ change_stamina(-15)
            $ himo_aptitude["easy_choices"] += 1

        "通り過ぎる":
            himo "...いや、やめとこ"
            "誘惑に打ち勝った。"

    $ flags["midgame_pachinko_triggered"] = True
    return


# === イベント④: カナからの急な呼び出し ===

label midgame_kana_urgent:
    "カナからLINEが来た。"
    kana_c "ねえ今すぐ来て！！"
    kana_c "友達にドタキャンされた...一人で暇"

    menu:
        "行く（昼＋夜がカナに消費される）":
            himo "しょうがないな、行くよ"
            kana_c "やった！！！"

            "カナと合流した。結局夜まで一緒にいた。"
            $ kana["met_today"] = True
            $ kana["last_contact"] = 0
            $ change_trust_kana(8)
            $ change_dependence_kana(5)
            $ change_stamina(-20)
            $ daily_flags["ate_today"] = True
            $ daily_flags["date_with"] = "kana"

            # 昼＋夜を消費
            $ flags["afternoon_consumed"] = True
            $ flags["kana_tonight"] = True

            "（美咲に連絡する暇がなかった...）"

        "断る":
            himo "ごめん、今日はちょっと..."
            kana_c "え〜...マジで？"
            kana_c "いっつも断るじゃん"

            $ change_trust_kana(-8)
            $ kana["last_contact"] = 0

    return


# === イベント⑤: ダブルブッキング危機 ===

label midgame_double_booking:
    "昼、立て続けにLINEが来た。"

    misaki_c "今夜会える？ちょっと話したいことがあって"
    "...続けてもう1件。"
    kana_c "今夜暇？会いたい！"

    himo "...やばい、被った"

    $ daily_flags["double_booking_checked"] = True
    $ daily_flags["misaki_wants_tonight"] = True
    $ daily_flags["kana_wants_tonight"] = True

    menu:
        "美咲を優先する":
            himo "（カナに断りの連絡を入れないと）"
            call run_lie_puzzle("double_booking", "kana")

            $ daily_flags["kana_wants_tonight"] = False
            $ flags["misaki_tonight"] = True

            python:
                result = lie_puzzle["result"]
            if result == "busted":
                kana_c "嘘でしょ？なんか怪しいんだけど"
            elif result == "suspicious":
                kana_c "...ふーん"
            else:
                kana_c "しょうがないな〜"

        "カナを優先する":
            himo "（美咲に断りの連絡を...）"
            call run_lie_puzzle("double_booking", "misaki")

            $ daily_flags["misaki_wants_tonight"] = False
            $ flags["kana_tonight"] = True

            python:
                result = lie_puzzle["result"]
            if result == "busted":
                misaki_c "...嘘ついてるでしょ"
            elif result == "suspicious":
                misaki_c "...そう"
            else:
                misaki_c "分かった、じゃあまた今度ね"

        "両方断る":
            himo "今日は両方やめとこう..."
            "美咲に断りのLINEを送った。"
            misaki_c "...そう"
            $ change_trust(-3)
            "カナにも。"
            kana_c "え〜つまんない"
            $ change_trust_kana(-3)

    $ flags["midgame_doublebooking_done"] = True
    return


# === イベント⑥: 目撃情報 → 対面修羅場 ===

label midgame_sighting_confrontation:
    scene bg_placeholder

    # 直近のデート相手で分岐
    if daily_flags.get("date_with", None) == "kana":
        # 美咲から追及される
        misaki_c "ねえ、聞いていい？"
        misaki_c "友達がさ、駅前で女の子と歩いてるの見たって"
        misaki_c "あれ、ヒモ太郎？"

        call run_lie_puzzle("other_woman", "misaki")

    else:
        # カナから追及される
        kana_c "ねえ、ちょっと聞きたいことあるんだけど"
        kana_c "友達がヒモ太郎っぽい人が女の人と歩いてるの見たって"
        kana_c "誰？"

        call run_lie_puzzle("other_woman", "kana")

    $ flags["midgame_sighting_confronted"] = True
    return


# === イベント⑦: カナの突撃訪問（証拠隠滅QTE） ===

label midgame_kana_raid:
    scene bg_placeholder

    "ヒモ太郎の部屋で寛いでいると――"
    "ドンドンドン！"
    kana_c "ヒモ太郎〜！いる？来ちゃった！"

    himo "！？"
    "（やばい、美咲の荷物がそのままだ！）"

    call run_evidence_qte("kana_raid")

    # QTE結果で分岐
    if flags.get("qte_failed_badly", False):
        "カナが部屋に入ってきた。"
        "そして――見つけた。"

        kana_c "...これ、誰の？"

        # 嘘パズルに連鎖
        call run_lie_puzzle("other_woman", "kana")

        $ flags["qte_failed_badly"] = False
    else:
        "カナが部屋に入ってきた。"
        kana_c "急に来ちゃった〜。暇だったから"
        himo "（セーフ...）"

        "でもカナは、少し部屋を見回していた。"
        kana_c "...なんか慌ててなかった？"
        himo "いや、別に？"
        kana_c "ふーん..."

        $ suspicion["kana"] = min(suspicion["kana"] + 5, SUSPICION_MAX)

    $ kana["met_today"] = True
    $ kana["last_contact"] = 0
    $ flags["midgame_kana_raid_done"] = True
    return


# === イベント⑧: 美咲の直球質問 ver.2 ===

label midgame_misaki_direct:
    scene bg_placeholder

    "美咲と2人きりの夜。"
    "いつもと違う空気。"

    misaki_c "...ヒモ太郎"
    himo "ん？"
    misaki_c "ちゃんと聞きたいことがある"

    "美咲の目が、真剣だった。"

    misaki_c "他に女の人、いるでしょ"
    misaki_c "最近LINE返すの遅いし、予定よく断るし"
    misaki_c "前は暇だ暇だって言ってたのに"

    call run_lie_puzzle("other_woman", "misaki")

    python:
        result = lie_puzzle["result"]

    if result == "busted":
        misaki_c "...もういい"
        misaki_c "分かってた。薄々"
        "美咲は静かに泣いていた。"
        $ change_trust(-25)
        $ change_dependence(-10)
    elif result == "suspicious":
        misaki_c "...信じたいけど"
        "美咲は何かを飲み込んだような顔をした。"
        $ change_trust(-10)
    elif result == "safe":
        misaki_c "...ごめん、疑って"
        himo "いいって。ちゃんと話してくれてありがとう"
        $ change_trust(5)
    # "uneasy"の場合は run_lie_puzzle 内で処理済み

    $ flags["midgame_misaki_direct_done"] = True
    return


# === イベント⑨: 所持金バレリスク ===
# （misaki_money_request から呼び出される。修正11で組み込み）

label midgame_money_suspicion:
    misaki_c "...ねえ、本当にお金ないの？"
    misaki_c "最近ちょっと余裕ありそうに見えるけど"

    himo "え？"

    menu:
        "誤魔化す":
            himo "いやいや、見た目だけだって"
            misaki_c "...そう？"
            $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)
            $ himo_aptitude["lies"] += 1

        "正直に言う":
            himo "...まあ、ちょっと余裕は出てきたかも"
            misaki_c "じゃあなんでお金頼むの？"
            himo "......"
            $ change_trust(-5)
            $ himo_aptitude["honest_moments"] += 1

    "今日のお金の要求は失敗した。"
    $ daily_flags["asked_money_today"] = True
    return
