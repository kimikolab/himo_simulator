# midgame_events.rpy
# 中盤イベント — ルーティンを崩す揺さぶり＋修羅場

init python:
    def check_midgame_events():
        """main_loopの各ターン開始時に呼び出す
        戻り値: False=なし, "notify"=ターン消費しない, True=ターン消費する"""
        day = game_date["day"]
        time = game_date["time"]

        # --- 中盤前半（9〜15日） ---

        # イベント①: 美咲「最近忙しいの？」（LINE系 → ターン消費しない）（v1.5: 冷戦ガード追加）
        if (day >= 9 and day <= 15
            and not flags.get("midgame_busymisaki_done", False)
            and kana_flags["met"]
            and misaki["last_contact"] >= 3
            and time == "morning"
            and not cold_war.get("misaki_active", False)):
            _pending_events.append(("midgame_misaki_busy", None))
            return "notify"

        # イベント④: カナからの急な呼び出し
        if (day >= 10 and day <= 20
            and kana_flags["met"]
            and kana["dependence"] >= 20
            and time == "afternoon"
            and not kana["met_today"]
            and not cold_war.get("kana_active", False)):
            if renpy.random.random() < 0.20:
                _pending_events.append(("midgame_kana_urgent", None))
                return True

        # --- 中盤後半（16〜23日） ---

        # イベント⑤: ダブルブッキング危機（LINE系 → ターン消費しない）（v1.5: 冷戦ガード追加）
        if (day >= 16 and day <= 25
            and not flags.get("midgame_doublebooking_done", False)
            and kana_flags["met"]
            and misaki["stage"] >= STAGE_FRIEND
            and kana["trust"] >= 25
            and time == "afternoon"
            and not daily_flags["double_booking_checked"]
            and not cold_war.get("misaki_active", False)):
            if renpy.random.random() < 0.30:
                _pending_events.append(("midgame_double_booking", None))
                return "notify"

        # イベント⑥: 目撃情報 → 修羅場（v1.5: 冷戦ガード追加）
        if (flags.get("midgame_sighting_done", False)
            and not flags.get("midgame_sighting_confronted", False)
            and time == "night"
            and not cold_war.get("misaki_active", False)):
            if renpy.random.random() < 0.40:
                _pending_events.append(("midgame_sighting_confrontation", None))
                return True

        # イベント⑦: カナの突撃訪問
        if (day >= 18
            and not flags.get("midgame_kana_raid_done", False)
            and kana_flags["met"]
            and kana["dependence"] >= 40
            and time == "night"
            and not kana["met_today"]
            and not cold_war.get("kana_active", False)):
            if renpy.random.random() < 0.20:
                _pending_events.append(("midgame_kana_raid", None))
                return True

        # === カナ版疑念イベント（Phase 4 Step 2）===
        if (kana_flags.get("met", False)
            and not flags.get("kana_doubt_event_done", False)
            and day >= 15
            and calculate_kana_exploitation() >= KANA_EXPLOITATION_THRESHOLD
            and not cold_war.get("kana_active", False)):
            _pending_events.append(("kana_doubt_event", None))
            return True

        # イベント⑧: 美咲の直球質問 ver.2
        if (day >= 18
            and not flags.get("midgame_misaki_direct_done", False)
            and suspicion["misaki"] >= SUSPICION_SHURABA_THRESHOLD
            and misaki["trust"] >= 50
            and time == "night"
            and not cold_war.get("misaki_active", False)):
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
            # v1.4修正: last_contactは1にする（0だと「今日会った」と同等になる）
            $ misaki["last_contact"] = 1
            $ daily_flags["misaki_lined_only"] = True

        "後で返そう（スルー）":
            "後で返せばいいか。"
            himo "まあいっか"
            $ change_trust(-10)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
            $ himo_aptitude["easy_choices"] += 1
            # Phase 4 v1.3: スルー時はlast_contactもリセットしない

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
                pachinko_result = renpy.random.choice(["big_win", "small_win", "lose", "big_lose"])

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
    # Phase 4 v1.2: パチンコに入ったら午後ターン消費
    $ flags["afternoon_consumed"] = True
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
            $ daily_flags["kana_tonight_source"] = "kana"

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
            $ daily_flags["kana_tonight_source"] = "kana"

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

    # Phase 4 v1.3: 正直ルート専用分岐
    if result == "honest":
        "長い沈黙が続いた。"
        misaki_c "...正直に言ってくれたのは、ありがたい"
        misaki_c "でも...どうすればいいか、分からない"
        "美咲は静かに下を向いていた。"
        # 信頼低下は lie_puzzle 内で処理済み

    elif result == "busted":
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
        # safe は「嘘で乗り切った」場合のみ
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
    # Phase 4 v1.2: asked_money_todayとは別にrefusedフラグを立てる
    $ daily_flags["money_refused_today"] = True
    return


# === Phase 4 v1.3: 約束不履行イベント ===

label misaki_appointment_broken:
    "美咲からLINEが来ていた。"
    misaki_c "昨日、約束してたよね...？"

    menu:
        "ごめん、忘れてた":
            misaki_c "...そう"
            $ change_trust(-10)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 3, SUSPICION_MAX)

        "急用が入って（嘘）":
            call run_lie_puzzle("double_booking", "misaki")

    return


label kana_appointment_broken:
    "カナからLINEが来ていた。"
    kana_c "昨日なんで来なかったの？"

    menu:
        "ごめん":
            kana_c "もう...許さない"
            kana_c "...嘘。許す。でも次はないからね"
            $ change_trust_kana(-8)

        "体調悪くて（嘘）":
            call run_lie_puzzle("double_booking", "kana")

    return


# ========================================
# Phase 4 Step 2.5: 別の女の痕跡イベント
# ========================================

label evidence_trace_event(discoverer):
    scene bg_placeholder

    # v1.6: 2回目以降の痕跡イベント専用テキスト
    if flags.get("evidence_trace_count", 0) >= 1:
        if discoverer == "misaki":
            "美咲が部屋を見回している。"

            misaki_c "...また？"

            "美咲の声は静かだが、怒りを通り越している。"

            misaki_c "前にも言ったよね。もうやめてって"

            himo "..."

            "美咲は何も言わずにドアに向かった。"

            menu:
                "待って":
                    himo "待って、美咲"
                    misaki_c "...何？"
                    "振り返った美咲の目は、もう何も期待していなかった。"
                    misaki_c "もう、いいよ"

                "...ごめん":
                    himo "...ごめん"
                    "美咲は振り返らなかった。"

            $ change_trust(-20)
            $ suspicion["misaki"] = 0
            $ flags["misaki_tonight"] = False
            $ start_cold_war("misaki", 2)
            $ flags["evidence_trace_count"] = flags.get("evidence_trace_count", 0) + 1
            return

        elif discoverer == "kana":
            "カナが部屋を見回している。"

            kana_c "...またやったんだ"

            "カナの声は震えていた。"

            kana_c "もう信じないって決めたのに。また信じちゃったんだ、私"

            himo "..."

            kana_c "バカだよね、私"

            "カナが涙を拭いながらドアに向かった。"

            menu:
                "待って":
                    himo "カナ、待ってくれ"
                    kana_c "...なに。また嘘つくの？"
                    "カナの涙が止まらなかった。"

                "...ごめん":
                    himo "...ごめん"
                    "カナは黙って首を横に振った。"

            $ change_trust_kana(-20)
            $ suspicion["kana"] = 0
            $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 5
            $ flags["kana_tonight"] = False
            $ start_cold_war("kana", 2)
            $ flags["evidence_trace_count"] = flags.get("evidence_trace_count", 0) + 1
            return

        $ flags["evidence_trace_count"] = flags.get("evidence_trace_count", 0) + 1
        return

    # === 1回目の痕跡イベント（既存テキスト） ===
    if discoverer == "misaki":
        "美咲が部屋を見回している。"

        python:
            _evidence = renpy.random.choice([
                ("...ねえ、この髪の毛", "長い髪。美咲の髪色とは違う。"),
                ("...この化粧品、私のじゃないんだけど", "見覚えのないリップがテーブルに。"),
                ("...なんか、甘い匂いしない？", "確かに、カナの香水の残り香。"),
            ])
            _line, _desc = _evidence

        misaki_c "[_line]"
        "[_desc]"
        "美咲の目が鋭くなった。"
        misaki_c "...誰か来たの？ この部屋に"

        # v1.4修正: 選択肢で正直に認めるか嘘をつくか分岐
        menu:
            "嘘をつく":
                call run_lie_puzzle("evidence_trace", "misaki")

                # v1.4修正: lie_puzzleの結果で分岐（qte_failed_badlyは証拠QTE専用）
                python:
                    _lp_result = lie_puzzle.get("result", "safe")

                if _lp_result in ["busted", "suspicious"]:
                    misaki_c "...もういい"
                    misaki_c "帰る"
                    "美咲が黙って部屋を出ていった。"
                    $ change_trust(-15)
                    $ suspicion["misaki"] = suspicion.get("misaki", 0) + 10
                    $ flags["misaki_tonight"] = False
                    $ start_cold_war("misaki", 1)
                    $ flags["evidence_trace_count"] = flags.get("evidence_trace_count", 0) + 1
                    return
                else:
                    himo "友達が遊びに来ただけだって"
                    misaki_c "...ほんとに？"
                    himo "ほんとほんと"
                    misaki_c "...まあ、いいけど"
                    "美咲はまだ少し疑っている。"
                    $ suspicion["misaki"] = suspicion.get("misaki", 0) + 3

            "正直に認める":
                himo "...ごめん。正直に言う"
                himo "他に会ってる人がいる"

                "美咲の手が止まった。"

                misaki_c "..."
                misaki_c "...そう"

                "美咲の声は静かだった。怒りですらなかった。"

                misaki_c "なんとなく、分かってた"
                misaki_c "最近、連絡遅いし。会っても目が合わないし"

                himo "..."

                misaki_c "私、ずっと気づかないフリしてた"
                misaki_c "気づいたら...怖くて"

                "美咲の手が小さく震えている。"

                misaki_c "...ねえ、私じゃダメだったの？"

                himo "...そういうことじゃない"

                misaki_c "じゃあ、なんなの"

                "答えられなかった。"

                misaki_c "...今日は帰って"
                misaki_c "一人にして"

                $ change_trust(-15)
                $ suspicion["misaki"] = 0
                $ himo_aptitude["honest_moments"] += 2
                $ flags["misaki_tonight"] = False
                $ start_cold_war("misaki", 1)

                "美咲は最後まで泣かなかった。"
                "でもドアが閉まる瞬間、声が震えていた。"

                $ flags["evidence_trace_count"] = flags.get("evidence_trace_count", 0) + 1
                return

    elif discoverer == "kana":
        "カナが部屋を歩き回っている。"

        python:
            _evidence = renpy.random.choice([
                ("...ねえ、この髪留め誰の？", "テーブルの上に、見覚えのないヘアピン。"),
                ("...なんかこの部屋、女の匂いする", "カナの鼻は鋭い。"),
                ("...この紙袋、どこの店？", "美咲と行った店のショッパーが残っていた。"),
            ])
            _line, _desc = _evidence

        kana_c "[_line]"
        "[_desc]"
        "カナの目が座った。"
        kana_c "ヒモ太郎...誰か連れ込んだでしょ"

        menu:
            "嘘をつく":
                call run_lie_puzzle("evidence_trace", "kana")

                python:
                    _lp_result = lie_puzzle.get("result", "safe")

                if _lp_result in ["busted", "suspicious"]:
                    kana_c "...最低"
                    "カナが泣き出した。"
                    kana_c "もう帰る。二度と呼ばないで"
                    $ change_trust_kana(-20)
                    $ suspicion["kana"] = suspicion.get("kana", 0) + 10
                    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 5
                    $ flags["kana_tonight"] = False
                    $ start_cold_war("kana", 1)
                    $ flags["evidence_trace_count"] = flags.get("evidence_trace_count", 0) + 1
                    return
                else:
                    himo "妹が来ただけだって"
                    kana_c "...ヒモ太郎に妹いたっけ"
                    himo "いとこ。いとこの妹"
                    kana_c "...ふーん"
                    "カナは完全には信じていないが、追及をやめた。"
                    $ suspicion["kana"] = suspicion.get("kana", 0) + 5

            "正直に認める":
                himo "...ごめん。実は..."
                himo "他に会ってる人がいる"

                kana_c "..."

                "カナの表情が凍った。"

                kana_c "...やっぱり"
                kana_c "分かってたよ。なんとなく"

                "カナの目に涙が溜まった。"

                kana_c "この部屋、あの人の匂いがしたから"
                kana_c "でも...信じたかった"

                "カナが声を震わせた。"

                kana_c "前の彼氏と同じだ"
                kana_c "優しくしてくれて、でも裏では..."

                himo "..."

                "何も言えなかった。"

                kana_c "...でも"

                "カナが涙を拭いた。"

                kana_c "正直に言ってくれたのは...あの人と違う"
                kana_c "嘘つかれるよりマシ"

                "長い沈黙。"

                kana_c "...今日は帰って"
                kana_c "少し考えたいから"

                $ change_trust_kana(-15)
                $ suspicion["kana"] = 0
                $ himo_aptitude["honest_moments"] += 2
                $ flags["kana_tonight"] = False
                $ start_cold_war("kana", 1)

                "カナが静かにドアを閉めた。"
                "背中越しに、小さな嗚咽が聞こえた。"

                $ flags["evidence_trace_count"] = flags.get("evidence_trace_count", 0) + 1
                return

    # 嘘成功時もカウント（冷戦にはならないが発生回数は記録）
    $ flags["evidence_trace_count"] = flags.get("evidence_trace_count", 0) + 1
    return


# ========================================
# Phase 4 Step 2.5: 冷戦中の専用テキスト
# ========================================

label cold_war_contact(target):
    if target == "misaki":
        "美咲にLINEを送った..."

        if cold_war["misaki_level"] == 1:
            python:
                _cw_reply = renpy.random.choice([
                    "...用事？",
                    "...なに",
                    "今ちょっと話したくない",
                ])
            "しばらくして、短い返信が来た。"
            misaki_c "[_cw_reply]"
            himo "（まだ怒ってる...）"

            if cold_war.get("misaki_apology_available", False):
                himo "（...ちゃんと謝った方がいいかもしれない）"

        elif cold_war["misaki_level"] == 2:
            python:
                _cw_reply = renpy.random.choice([
                    "...",
                    "もう連絡しないで",
                    "考えさせて",
                ])
            "かなり経ってから、返信が来た。"
            misaki_c "[_cw_reply]"
            himo "（完全にやばい...）"

            if cold_war.get("misaki_apology_available", False):
                himo "（直接謝りに行かないとダメだ）"

    elif target == "kana":
        "カナにLINEを送った..."

        if cold_war["kana_level"] == 1:
            python:
                _cw_reply = renpy.random.choice([
                    "は？",
                    "なんの用",
                    "今無理",
                ])
            "しばらくして、返信が来た。"
            kana_c "[_cw_reply]"
            himo "（カナ、怒りの返信...）"

            if cold_war.get("kana_apology_available", False):
                himo "（直接会って謝らないと...）"

        elif cold_war["kana_level"] == 2:
            "既読スルーされた..."
            himo "（完全に無視されてる...）"

            if cold_war.get("kana_apology_available", False):
                himo "（家まで行くしかない...）"

    return


# ========================================
# Phase 4 Step 2.5: 謝罪イベント
# ========================================

label apology_event(target):
    scene bg_placeholder
    $ stats["apology_" + target + "_count"] = stats.get("apology_" + target + "_count", 0) + 1

    if target == "misaki":
        "美咲のマンションの前に来た。"
        "インターホンを押した。"

        # 出てくる確率（冷戦レベルで変化）
        python:
            if cold_war["misaki_level"] == 1:
                _door_chance = 0.60
            else:
                _door_chance = 0.35

            _door_opens = renpy.random.random() < _door_chance

        if not _door_opens:
            "..."
            "反応がない。"
            himo "（いないのか、出たくないのか...）"
            "今日はダメだった。"
            return

        "ドアが開いた。"
        misaki_c "...なに"

        "美咲の目は冷たい。"

        call expression "apology_conversation" pass ("misaki")

    elif target == "kana":
        "カナのアパートの前に来た。"
        "ドアをノックした。"

        python:
            if cold_war["kana_level"] == 1:
                _door_chance = 0.55
            else:
                _door_chance = 0.30

            _door_opens = renpy.random.random() < _door_chance

        if not _door_opens:
            "..."
            "出てこない。"
            "中にいるのは分かってるのに。"
            himo "（...今日は無理か）"
            return

        "ドアが少しだけ開いた。"
        kana_c "...何しに来たの"

        "カナの目が赤い。泣いていたのかもしれない。"

        call expression "apology_conversation" pass ("kana")

    return


label apology_conversation(target):
    # Ren'Pyのmenu内callではラベルパラメータのローカル変数を渡せないため
    # ストア変数に退避してサブラベルで参照する
    $ _apology_target = target
    menu:
        "どう謝る？"

        "正直に謝る":
            call apology_honest

        "プレゼントを持っていく" if can_afford(5000):
            call apology_gift

        "ごまかす":
            call apology_dodge

    # v1.6: menu終了後に次ラベルへフォールスルーしないようreturnを追加
    return


label apology_honest:
    if _apology_target == "misaki":
        himo "...ごめん。俺が悪かった"
        misaki_c "..."
        himo "言い訳はしない。本当にごめん"

        "長い沈黙。"

        if cold_war["misaki_level"] == 1:
            misaki_c "...分かった"
            misaki_c "でも、次はないから"
            "美咲は許してくれた。"
            "でも、目の奥にまだ不信感が残っている。"
            $ end_cold_war("misaki")
            $ change_trust(-3)
            $ himo_aptitude["honest_moments"] += 2

        else:
            # レベル2: 一度では許されない。もう1回来る必要がある
            misaki_c "...正直に言ってくれたのは分かる"
            misaki_c "でも、すぐには無理"
            misaki_c "...少し時間ちょうだい"
            "完全には許されなかった。でも、少し和らいだ。"
            $ cold_war["misaki_level"] = 1
            $ cold_war["misaki_days_left"] = 2
            $ himo_aptitude["honest_moments"] += 1

    elif _apology_target == "kana":
        himo "カナ、ごめん。俺が最低だった"
        kana_c "..."
        kana_c "...分かってるよ、そんなの"

        "カナの声が震えている。"

        if cold_war["kana_level"] == 1:
            kana_c "...ヒモ太郎のバカ"
            "カナが泣きながら怒っている。"
            kana_c "もう絶対しないって言って"
            himo "しない。約束する"
            kana_c "...信じるから"
            $ end_cold_war("kana")
            $ change_trust_kana(-3)
            $ himo_aptitude["honest_moments"] += 2

        else:
            kana_c "...約束しても、また破るんでしょ"
            kana_c "前の彼氏もそうだった"
            "カナの過去の傷が開いている。"
            himo "俺は違う"
            kana_c "...それも前の彼氏と同じこと言ってる"
            "完全には許されなかった。"
            $ cold_war["kana_level"] = 1
            $ cold_war["kana_days_left"] = 2
            $ himo_aptitude["honest_moments"] += 1

    return


label apology_gift:
    $ change_money(-5000)

    if _apology_target == "misaki":
        himo "これ...好きだって言ってたやつ"
        misaki_c "..."
        misaki_c "...物で解決しようとしてる？"
        himo "違う。ごめんって気持ちを形にしたかっただけ"

        "美咲がプレゼントを受け取った。"

        if cold_war["misaki_level"] == 1:
            misaki_c "...ありがと。でも、もうしないでね"
            $ end_cold_war("misaki")
            $ change_trust(-1)

        else:
            misaki_c "...気持ちは分かった。でも、まだ許せない"
            $ cold_war["misaki_level"] = 1
            $ cold_war["misaki_days_left"] = 1

    elif _apology_target == "kana":
        himo "カナ、これ"
        kana_c "...なに"
        "プレゼントを渡した。"

        if cold_war["kana_level"] == 1:
            kana_c "...買収？"
            himo "違う"
            kana_c "..."
            kana_c "...かわいい"
            "カナが少し笑った。"
            $ end_cold_war("kana")
            $ change_trust_kana(-1)

        else:
            kana_c "...物もらっても、嬉しくない"
            kana_c "嘘。ちょっと嬉しい。でもまだ怒ってる"
            $ cold_war["kana_level"] = 1
            $ cold_war["kana_days_left"] = 1

    return


label apology_dodge:
    # ごまかし → 嘘パズル
    if _apology_target == "misaki":
        himo "いや、あれは本当に友達で..."
        misaki_c "...まだそれ言うの？"

        call run_lie_puzzle("apology_dodge", "misaki")

        if lie_puzzle.get("result", "safe") in ["busted", "suspicious"]:
            misaki_c "...帰って"
            "ドアが閉まった。"
            $ cold_war["misaki_days_left"] += 2
            $ suspicion["misaki"] = suspicion.get("misaki", 0) + 3
            $ himo_aptitude["lies"] += 1
        else:
            misaki_c "...もういい。信じるから"
            "半ば呆れたように言った。"
            $ end_cold_war("misaki")
            $ change_trust(-5)
            $ suspicion["misaki"] = suspicion.get("misaki", 0) + 2
            $ himo_aptitude["lies"] += 1

    elif _apology_target == "kana":
        himo "あれはマジでいとこで..."
        kana_c "ヒモ太郎にいとこいないって前に言ってたじゃん"
        himo "（やば、覚えてたのか）"

        call run_lie_puzzle("apology_dodge", "kana")

        if lie_puzzle.get("result", "safe") in ["busted", "suspicious"]:
            kana_c "もう嘘つかないで"
            "ドアが閉まった。"
            $ cold_war["kana_days_left"] += 2
            $ suspicion["kana"] = suspicion.get("kana", 0) + 3
            $ himo_aptitude["lies"] += 1
        else:
            kana_c "...もう信じないけど、今回だけ"
            $ end_cold_war("kana")
            $ change_trust_kana(-8)
            $ suspicion["kana"] = suspicion.get("kana", 0) + 3
            $ himo_aptitude["lies"] += 1

    return
