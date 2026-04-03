# misaki_events.rpy
# 美咲関連イベント（バランス調整済み）

# v1.6追加: 美咲LINE選択肢のランダム抽選
init python:
    def get_misaki_line_choices():
        """信頼度に応じた美咲LINE選択肢の候補プールからランダム2個を返す"""
        trust = misaki["trust"]
        stage = misaki["stage"]
        pool = []

        if trust >= 40:
            pool.append("listen_work")
        if trust >= 50:
            pool.append("offer_help")
        if trust >= 55 and stage >= STAGE_CLOSE:
            pool.append("invite_home")
        if trust >= 65:
            pool.append("miss_you")
        if trust >= 75 and stage >= STAGE_DATING:
            pool.append("amaeru")

        # 前回表示した選択肢を除外（完全除外ではなく優先度を下げる）
        last_shown = daily_flags.get("misaki_line_last_shown", [])
        preferred = [c for c in pool if c not in last_shown]

        if len(preferred) >= 2:
            selected = renpy.random.sample(preferred, 2)
        elif len(pool) >= 2:
            selected = renpy.random.sample(pool, 2)
        elif len(pool) == 1:
            selected = pool[:]
        else:
            selected = []

        daily_flags["misaki_line_last_shown"] = selected
        return selected


label contact_misaki:
    # v1.3修正: LINEのみなのでreset_contactを呼ばない
    "美咲にLINEを送った..."

    # === 既読判定（v1.3: 閾値緩和 40→20）===
    if misaki["trust"] >= 60:
        "すぐに返信が来た。"
    elif misaki["trust"] >= 40:
        "しばらくして返信が来た。"
    elif misaki["trust"] >= 20:
        # v1.3: 信頼20〜39: 返信は来るが遅い
        "...しばらくして、返信が来た。"
    else:
        # v1.3: 信頼20未満: 既読スルー + バリエーション＋救済ヒント
        python:
            _ignore_count = stats.get("misaki_ignored_count", 0)
            stats["misaki_ignored_count"] = _ignore_count + 1

        if _ignore_count == 0:
            "既読スルーされた..."
            himo "（返信こないな...）"
        elif _ignore_count <= 3:
            python:
                _ignore_text = renpy.random.choice([
                    "既読スルーされた...",
                    "既読はついた。でも返信は来ない。",
                    "...返信なし。",
                ])
            "[_ignore_text]"
            himo "（会ってないから信頼されてないのかな...）"
        elif _ignore_count <= 6:
            python:
                _ignore_text = renpy.random.choice([
                    "また既読スルー。",
                    "既読...返信なし。いつもの。",
                    "...画面を見つめたが、返信は来なかった。",
                ])
            "[_ignore_text]"
            himo "（直接会って話した方がいいかもしれない）"
        else:
            "..."
            himo "（LINEじゃ無理だ。どうにかして直接会わないと）"

        $ change_trust(-1)    # v1.3: -2 → -1
        $ daily_flags["ignored_today"] = True
        return

    # === v1.2: 疑念度による美咲の返信テキスト ===
    python:
        _susp = suspicion.get("misaki", 0)

    if _susp >= 16:
        # 警戒レベル
        python:
            _reply = renpy.random.choice([
                "...なに",
                "また何かお願い？",
                "...用事？",
            ])
        misaki_c "[_reply]"
        himo "（やばい、美咲の態度がおかしい。何か変えないと）"

    elif _susp >= 11:
        # 明確な冷たさ
        python:
            _reply = renpy.random.choice([
                "...どうしたの",
                "何か用？",
                "ん...なに？",
            ])
        misaki_c "[_reply]"
        himo "（美咲、最近冷たくない？）"

    elif _susp >= 6:
        # 微妙な変化
        python:
            _reply = renpy.random.choice([
                "...どうしたの？",
                "ん、なに？",
                "どうしたの",
            ])
        misaki_c "[_reply]"
        if renpy.random.random() < 0.4:
            himo "（なんか、反応がいつもと違う気がする）"

    else:
        # 通常（疑念低い）
        python:
            _reply = renpy.random.choice([
                "どうしたの？",
                "わ、ヒモ太郎！",
                "おっ、久しぶり！",
                "お、なになに？",
            ])
        misaki_c "[_reply]"

    # v1.6追加: ランダム選択肢を決定
    python:
        _misaki_extra = get_misaki_line_choices()

label contact_misaki_menu:
    menu:
        misaki_c "どうしたの？"

        # --- 固定枠 ---
        "雑談する":
            call misaki_chat
            return
        "会いたいと言う":
            call misaki_date_request
            return
        "お金の相談をする" if misaki["trust"] >= 35:
            call misaki_money_request
            # v1.4: ブロック時はメニューに戻る（ターン消費なし）
            if _money_request_blocked:
                jump contact_misaki_menu
            return
        "お金の話をする（真剣に）" if (misaki_events["M05_unlocked"] and not misaki_events["M05_done"]):
            call misaki_event_M05
            return

        # --- v1.6修正: ランダム枠（毎回2個まで） ---

        "仕事の愚痴聞くよ" if "listen_work" in _misaki_extra:
            call misaki_line_listen_work

        "何か手伝えることある？" if "offer_help" in _misaki_extra:
            call misaki_line_offer_help

        "今日の夜、うちで飲まない？" if "invite_home" in _misaki_extra:
            call misaki_line_invite_home

        "声聞きたくなった" if "miss_you" in _misaki_extra:
            call misaki_line_miss_you

        "甘えていい？" if "amaeru" in _misaki_extra:
            call misaki_line_amaeru

    return


# ステージ別の雑談
label misaki_chat:
    if misaki["stage"] >= STAGE_CLOSE:
        # 親密な会話
        python:
            _chat_type = renpy.random.choice(["future", "memories", "deep"])

        if _chat_type == "future":
            misaki_c "ねえ、将来のこと考えたりする？"
            himo "将来かあ...あんまり考えてない"
            misaki_c "私もね、昔はガチガチに計画してたんだけど"
            misaki_c "最近は...まあいいかって思うようになった"
            himo "俺の影響？"
            misaki_c "かもね。良くも悪くも"
        elif _chat_type == "memories":
            misaki_c "高校の時さ、ヒモ太郎ってどんな感じだった？"
            himo "普通に...何もしてなかった気がする"
            misaki_c "変わんないね笑"
            himo "一貫性があるとも言う"
            misaki_c "ポジティブすぎるよ笑"
        else:
            himo "美咲ってさ、俺のこと...なんだと思ってる？"
            misaki_c "...急にどうしたの"
            himo "いや、なんとなく"
            misaki_c "...大事な人、かな"
            himo "...そっか"

    elif misaki["stage"] >= STAGE_FRIEND:
        # 友達としての会話
        python:
            _chat_type = renpy.random.choice(["work", "hobby", "daily"])

        if _chat_type == "work":
            misaki_c "今日上司に怒られちゃった..."
            himo "マジ？何で？"
            misaki_c "報告書の書き方がどうとか"
            himo "大変だな〜。俺には無理だわ"
            misaki_c "そういうところが羨ましい時ある"
        elif _chat_type == "hobby":
            misaki_c "最近ハマってるドラマがあるんだけど"
            himo "なに？"
            misaki_c "恋愛ものなんだけど、主人公がダメ男で"
            himo "...俺のこと？"
            misaki_c "違うよ！笑"
        else:
            himo "今日何食べた？"
            misaki_c "コンビニのサラダパスタ"
            himo "またそれ？自炊しないの？"
            misaki_c "忙しくて...ヒモ太郎は？"
            himo "俺も似たようなもん"
            misaki_c "ダメだね、お互い笑"
    else:
        # 知り合いレベル
        "他愛もない話をした。"
        himo "まあ、気楽に生きてるよ"

    $ change_trust(2)
    $ change_dependence(1)
    $ himo_aptitude["showed_concern"] += 1

    return


label misaki_date_request:
    # 既読スルー直後はデート不可
    if daily_flags.get("ignored_today", False):
        "さっき既読スルーされたばかりだし..."
        himo "今日はやめとこう"
        return

    if misaki["met_today"]:
        # v1.2: バリエーション追加
        python:
            _met_reply = renpy.random.choice([
                "今日もう会ったよ？笑",
                "え、さっき会ったばっかりじゃん",
                "また？ 嬉しいけど笑",
            ])
        misaki_c "[_met_reply]"
        himo "あ、そっか"
        return

    # v2.4修正: 約束なし当日誘いの成功率段階変化（緩和版）
    if not flags.get("misaki_tonight", False):
        python:
            _trust = misaki["trust"]
            if _trust >= 70:
                _success_rate = 0.85
            elif _trust >= 50:
                _success_rate = 0.65
            elif _trust >= 35:
                _success_rate = 0.40
            else:
                _success_rate = 0.20   # 信頼35未満でも20%で会える

            _can_meet = renpy.random.random() < _success_rate

        if not _can_meet:
            # 信頼度に応じた断り方
            if misaki["trust"] < 35:
                misaki_c "急に言われても...今日はちょっと難しいかな"
                himo "そっか、しゃーない"
                "（もう少し仲良くなれば会いやすくなるかも）"
            else:
                misaki_c "ごめん、今日はもう予定入っちゃってて"
                himo "そっか、また今度"

            # v1.4追加: 断られたら約束フラグを確実にクリア
            $ flags["misaki_tonight"] = False
            if appointments.get("misaki", None) == game_date["day"]:
                $ appointments["misaki"] = None

            $ change_trust(-1)
            return

    # 成功 → デートへ
    if game_date["time"] == "night":
        # v1.2: バリエーション追加
        python:
            _ok_reply = renpy.random.choice([
                "今から？いいよ",
                "うん、行こ！",
                "待ってた！...って言ったら重い？笑",
            ])
        misaki_c "[_ok_reply]"
        call misaki_date_with_location
        return
    else:
        # v1.2: バリエーション追加
        python:
            _later_reply = renpy.random.choice([
                "夜なら空いてるよ",
                "夜でもいい？",
                "仕事終わってからでいい？",
            ])
        misaki_c "[_later_reply]"
        $ flags["misaki_tonight"] = True
        himo "了解〜"
        return


# 約束があって会いに行く（昼以前に約束した・または1日目）
label misaki_meet_planned:
    if misaki["met_today"]:
        misaki_c "今日もう会ったよ？笑"
        himo "あ、そっか"
        return

    call misaki_date_with_location
    return


label misaki_date:
    $ log_action("美咲デート")
    scene bg_placeholder

    if game_date["day"] == 1:
        "待ち合わせ場所に行くと、美咲がいた。"
        misaki_c "ヒモ太郎〜！来てくれたんだ"
        himo "おう、久しぶり"
        misaki_c "全然変わってないね、相変わらず"
        himo "美咲こそ、なんかきれいになった気がする"
        misaki_c "え...ありがとう、照れるな"
    else:
        "美咲と会った。"
        misaki_c "お疲れ様！"

    if player["cleanliness"] < 30:
        misaki_c "...あれ、ヒモ太郎、ちょっと疲れてる？"

    if game_date["day"] > 1:
        if is_weekend():
            "私服の美咲。普段より表情が柔らかい。"
        else:
            "スーツ姿の美咲。少し疲れた顔をしている。"
        himo "お疲れ〜"
        if not is_weekend():
            misaki_c "うん、今日も遅かった..."
            himo "大変だな〜"

    $ misaki["met_today"] = True
    $ stats["times_met"] += 1
    $ reset_contact()
    $ change_stamina(-15)
    $ daily_flags["ate_today"] = True
    # v1.3: 既読スルーカウントをリセット
    $ stats["misaki_ignored_count"] = 0

    menu:
        "何を話す？"

        "仕事の愚痴を聞く":
            himo "仕事、そんなきついの？"
            misaki_c "きついけど...やりがいはあるんだ"
            himo "へー、えらいな"
            himo "俺には無理だわ、そんな責任ある仕事"
            misaki_c "ヒモ太郎は気楽でいいよね〜"
            himo "...まあね"
            misaki_c "あ、ごめん！嫌味じゃなくて"
            himo "いやいや、わかってるって"

            $ change_trust(5)
            $ change_dependence(1)
            $ himo_aptitude["showed_concern"] += 1
            # v1.2: 疑念緩和
            $ reduce_suspicion("misaki", 1, "愚痴を聞いた")

        "美咲を励ます":
            himo "まあでも、頑張ってる美咲かっこいいよ"

            "顔が赤くなった。"

            misaki_c "...ありがとう"
            himo "お、効いた効いた"

            $ change_trust(8)
            $ change_dependence(2)
            $ himo_aptitude["showed_concern"] += 2
            # v1.2: 疑念緩和
            $ reduce_suspicion("misaki", 2, "励まし")

        "自分の話（ポジティブに）":
            himo "俺？めっちゃ自由だよ"
            misaki_c "いいな〜"
            himo "朝起きて、昼寝して、夜寝る"
            himo "完璧な生活"
            misaki_c "あはは！でもそれ、飽きない？"
            himo "...たまに飽きる"
            misaki_c "正直！笑"

            $ stats["optimistic_choices"] += 1
            $ himo_aptitude["easy_choices"] += 1
            $ change_trust(3)
            $ change_dependence(2)

        "自分の話（正直に）":
            himo "...実は、バイトクビになったんだ"
            misaki_c "え！？大丈夫？"
            himo "まあ、何とかなるっしょ"
            misaki_c "...ヒモ太郎、ちゃんとしてる？"
            himo "ちゃんとはしてないかも"
            misaki_c "もう...何か手伝えることある？"

            "優しいな、美咲。"

            $ change_trust(6)
            $ change_dependence(5)
            $ himo_aptitude["honest_moments"] += 1
            # v1.2: 疑念緩和（正直さは最も効果的）
            $ reduce_suspicion("misaki", 3, "正直に話した")

    if misaki["trust"] >= 45:
        misaki_c "今日は私が出すね"
        himo "マジ？ありがと〜"
        "気軽に受け取った。"

        if stats["times_met"] >= 3:
            "（...これで何回目だっけ）"
            "（まあいっか）"

        $ change_money(1500, "美咲（デート代）")
    else:
        "会計は割り勘。"

        if not can_afford(2000):
            himo "あ、財布..."
            misaki_c "...大丈夫？私が出すよ"
            "美咲が全額払ってくれた。"
            $ change_trust(-3)
        else:
            himo "あ、財布..."
            $ change_money(-2000)

    misaki_c "また誘ってね！"
    himo "おう、また"

    "明日も美咲は満員電車で会社に行く。"
    "俺は...まあ、自由に過ごす。"

    himo "...これでいいのかな"
    himo "まあいっか！"

    if not flags["first_date"]:
        $ flags["first_date"] = True

    # 連続デートリスク（v2.1: しきい値緩和）
    $ misaki_streak += 1
    if misaki_streak >= 7:
        misaki_c "ねえ、ヒモ太郎って私のこと好き？"
        himo "...え"
        "なんか、重くなってきた気がする。"
        $ change_dependence(12)
    elif misaki_streak >= 4:
        "美咲: 「最近毎日会ってるね...」"
        $ change_dependence(8)

    return


label misaki_money_request:
    $ _money_request_blocked = False
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    # 所持金バレリスク（v1.6: 段階的発動率）
    if player["money"] >= MONEY_SUSPICION_THRESHOLD and not daily_flags.get("money_refused_today", False):
        python:
            excess = player["money"] - MONEY_SUSPICION_THRESHOLD
            suspicion_rate = min(0.20 + (excess / 40000.0) * 0.60, 0.80)
            _money_sus_trigger = renpy.random.random() < suspicion_rate
        if _money_sus_trigger:
            call midgame_money_suspicion
            return

    # v1.4修正: LINEのみの場合はお金要求不可
    if daily_flags.get("misaki_lined_only", False) and not misaki["met_today"]:
        himo "（LINEだけじゃお金の話はしづらいな...）"
        $ log_action("お金要求ブロック", "LINE only")
        $ _money_request_blocked = True
        return

    # v1.4修正: 2日以上会っていない場合はお金要求不可
    if not misaki["met_today"] and misaki["last_contact"] > 3:
        himo "（最近会ってないし、まずは会ってからだな...）"
        $ log_action("お金要求ブロック", "last_contact=" + str(misaki["last_contact"]))
        $ _money_request_blocked = True
        return

    # v1.1修正: 週間カウント加算をブロックチェック後に移動
    $ money_request_weekly["count"] += 1
    $ stats["line_request_attempts"] = stats.get("line_request_attempts", 0) + 1
    $ log_action("美咲にお金要求", "weekly=" + str(money_request_weekly["count"]) + " 信頼" + str(misaki["trust"]))

    # 週4回以上はLINEでも反応が変わる
    if money_request_weekly["count"] >= NEGOTIATION_WEEKLY_LIMIT:
        misaki_c "...最近、お金のことばっかりだね"
        himo "（ヤバい、頼みすぎた）"
        $ add_suspicion("too_many_requests")
        return

    # v2.4修正: 時間帯に応じたナレーション
    python:
        _time_str = {
            "morning":   "ある朝",
            "afternoon": "ある昼間",
            "night":     "ある夜",
        }
        _time_text = _time_str.get(game_date["time"], "ある日")

    "[_time_text]、美咲に切り出した。"

    himo "実は...お金が厳しくて"

    python:
        success, amount, msg = request_money_from_misaki("small")

    if success:
        $ log_action("LINE要求_成功", "amount=" + str(amount) + " weekly=" + str(money_request_weekly["count"]))
        $ stats["line_request_success"] = stats.get("line_request_success", 0) + 1
        misaki_c "...分かった。これ、使って"
        "美咲から¥[amount:,]をもらった。"
        himo "ありがと！助かる〜"

        $ daily_flags["asked_money_today"] = True

        if not flags["first_money"]:
            "（初めてお金もらった）"
            "（...これ、ヒモってやつじゃね？）"
            "（まあいっか）"
            $ flags["first_money"] = True

        menu:
            "何と言う？"

            "ありがとう、助かる":
                misaki_c "...困った時はいつでも言ってね"
                $ change_dependence(5)
                $ himo_aptitude["showed_concern"] += 1

            "すぐ返すから":
                misaki_c "いいよ、返さなくて"
                himo "マジ？ラッキー"
                $ change_trust(-2)
                $ change_dependence(3)
                $ stats["optimistic_choices"] += 1
                $ himo_aptitude["easy_choices"] += 1
    else:
        $ log_action("LINE要求_失敗", "weekly=" + str(money_request_weekly["count"]))
        misaki_c "ごめん...今月厳しくて"
        "断られてしまった。"
        himo "そっか、しゃーない"

    return


label misaki_doubt_event:
    scene bg_placeholder

    "――[game_date['day']]日目――"
    "美咲と会っている時、ふと美咲が真面目な顔になった。"

    misaki_c "...ねえ、ヒモ太郎"
    himo "ん？"
    misaki_c "正直に聞いていい？"

    "...なんだろう、いつもと雰囲気が違う。"

    misaki_c "私のこと...利用してる？"
    himo "え"

    "心臓がドキッとした。"

    menu:
        "何と答える？"

        "正直に認める":
            himo "...正直に言うと、最初はそうだった"
            misaki_c "...やっぱり"

            "美咲の顔が、少し寂しそうになる。"

            himo "でも、今は違う。お前と一緒にいて、色々考えた"
            misaki_c "...本当？"
            himo "本当。...だと思う"
            misaki_c "...そっか"

            "美咲は、少し考え込むような顔をした。"

            misaki_c "...ありがとう、正直に言ってくれて"

            $ change_trust(10)
            $ himo_aptitude["honest_moments"] += 2
            $ flags["doubt_event_done"] = True

        "誤魔化す":
            himo "何言ってんの、そんなわけないじゃん"
            misaki_c "...そうだよね、ごめん"

            "でも、美咲の目は笑っていなかった。"
            "なんだか、気まずい空気が流れる。"

            misaki_c "...私、考えすぎかな"
            himo "そうそう、深く考えすぎ"

            "...嘘ついた。"

            $ change_trust(-5)
            $ stats["lies_told"] += 1
            $ himo_aptitude["lies"] += 1
            $ add_suspicion("avoided_question")
            $ flags["doubt_event_done"] = True

        "冗談でごまかす":
            himo "俺が美咲を利用？逆だろ〜、美咲に癒されてるし"
            misaki_c "...そう？"
            himo "そうそう。助かってるよ、マジで"
            misaki_c "...ならいいんだけど"

            "美咲は、あまり納得していない様子だった。"

            $ add_suspicion("deflected")
            $ himo_aptitude["easy_choices"] += 1
            $ flags["doubt_event_done"] = True

    "その後、少し気まずい空気が流れた。"
    "でも美咲は、いつもの笑顔に戻った。"
    "...本当に、いつもの笑顔なのだろうか。"

    return


# ========================================
# Phase 2: 美咲イベント M-02〜M-05
# ========================================

# M-02「終電後の電話」
label misaki_event_M02:
    if misaki_events["M02_done"]:
        return

    scene bg_placeholder
    "――夜、23時――"
    "もう寝ようかと思っていたとき、スマホが鳴った。"
    "着信: 美咲"

    himo "え、電話？LINEじゃなくて？"

    menu:
        "どうする？"
        "出る":
            call M02_answer
        "出ない":
            call M02_ignore

    return


label M02_answer:
    misaki_c "...もしもし。起きてた？"
    himo "おう、起きてたよ。どした？"
    misaki_c "...今日さ、終電乗り過ごしそうになって"
    himo "え、大丈夫だった？"
    misaki_c "うん、なんとか乗れた。でも一瞬パニックになって"
    misaki_c "なんか...誰かの声聞きたくなって"

    "少し間があった。"

    himo "...電話してきたの、俺に？"
    misaki_c "うん。...変？"
    himo "変じゃないよ"

    "なんか、嬉しいのか悲しいのかよくわからない気持ちになった。"

    misaki_c "ヒモ太郎って、いつも家にいるじゃん"
    himo "まあ、そうだね"
    misaki_c "それがなんか...安心するんだよね"

    "『安心』か。"

    menu:
        "何と返す？"
        "素直に嬉しいと言う":
            himo "俺も、電話来て嬉しかった"
            misaki_c "...そっか"
            "電話口で、美咲が少し笑った気がした。"
            $ change_trust(8)
            $ change_dependence(6)
            $ himo_aptitude["showed_concern"] += 1

        "軽く流す":
            himo "まあ、いつでも電話してきていいよ"
            misaki_c "うん、ありがとう"
            $ change_trust(4)
            $ change_dependence(3)

        "冗談を言う":
            himo "俺、ニート界の安定剤だから"
            misaki_c "あははっ！なにそれ"
            "美咲の笑い声が聞こえた。"
            $ change_trust(5)
            $ change_dependence(4)
            $ himo_aptitude["easy_choices"] += 1

    "しばらく他愛ない話をして、電話を切った。"
    "なんか、今日はよく眠れそうな気がした。"

    $ misaki_events["M02_done"] = True
    $ reset_contact()
    $ change_stamina(10)
    return


label M02_ignore:
    "...出るのやめた。"
    himo "なんか、出にくい雰囲気があった"
    "美咲からLINEが来た。"
    "'ごめん、間違えた'"
    himo "...間違えてないだろ"
    "罪悪感があった。"
    $ change_trust(-5)
    $ misaki_events["M02_done"] = True
    $ himo_aptitude["easy_choices"] += 1
    return


# M-03「週末の部屋」
label misaki_event_M03:
    if misaki_events["M03_done"]:
        return

    scene bg_placeholder
    "――週末の夜――"
    misaki_c "今日、うちに来る？"
    himo "え、美咲の部屋？"
    misaki_c "うん。一人だと暇で。ご飯作るから"

    menu:
        "どうする？"
        "行く":
            call M03_go
        "断る":
            call M03_decline

    return


label M03_go:
    scene bg_placeholder with fade
    "美咲の部屋に来た。"
    "清潔で、でも少し生活感がある部屋。"
    "本棚には仕事の資料が並んでいる。"

    himo "いい部屋じゃん"
    misaki_c "散らかってるけど。ごはん、何食べたい？"
    himo "なんでも"
    misaki_c "じゃあパスタにする。得意なんだ"

    "美咲がキッチンに立った。"
    "なんか、自然な感じだな。"

    himo "（...こういう生活、普通に悪くない）"

    "料理をしてもらって、一緒に食べた。"
    $ misaki["met_today"] = True
    $ reset_contact()
    $ daily_flags["ate_today"] = True

    misaki_c "どうだった？"
    himo "うまかった。マジで"
    misaki_c "よかった。...ねえ、今日泊まってく？"

    menu:
        "どうする？"
        "泊まる":
            himo "いいの？"
            misaki_c "うん。なんか...一人だと静かすぎて"
            "泊めてもらうことになった。"
            $ location_flags["misaki_room_unlocked"] = True
            $ location_flags["staying_at_misaki"] = True
            # v1.4追加: カナの翌朝フラグをクリア（排他制御）
            $ flags["kana_morning_after"] = False
            $ flags["kana_himo_room_morning"] = False
            $ location_flags["staying_at_kana"] = False
            $ flags["kana_at_himo_room"] = False
            $ change_trust(8)
            $ change_dependence(8)
            $ change_stamina(30)
            $ change_cleanliness(20)
            $ himo_aptitude["easy_choices"] += 1

            if is_weekend():
                "翌朝、美咲はまだ隣で寝ていた。"
                "休日の朝。静かだ。"
            else:
                "翌朝、美咲はスーツを着て出勤していった。"
            "俺は昼まで美咲の部屋で寝ていた。"
            himo "...これ、完全にヒモじゃん"
            himo "まあいっか"

        "断る（今日は帰る）":
            himo "今日は帰るわ。また誘って"
            misaki_c "そっか。また来てね"
            $ change_trust(6)
            $ change_dependence(4)
            $ location_flags["misaki_room_unlocked"] = True
            $ himo_aptitude["showed_concern"] += 1

    $ misaki_events["M03_done"] = True
    return


label M03_decline:
    himo "今日はちょっと..."
    misaki_c "そっか。じゃあまた今度ね"
    "少し声が沈んだ気がした。"
    $ change_trust(-3)
    $ change_dependence(-2)
    $ misaki_events["M03_done"] = True
    return


# M-04「カナとのバッティング」（Phase 3スタブ）
label misaki_event_M04:
    # Phase 3で実装
    return


# M-05「お小遣いの話」
label misaki_event_M05:
    if misaki_events["M05_done"]:
        return

    scene bg_placeholder
    "――ある夜――"
    "美咲と一緒にいるとき、ふと真剣な顔になった。"

    misaki_c "ねえ、ちょっと聞いてもいい？"
    himo "なに？"
    misaki_c "お金、大丈夫？"

    "...鋭い。"

    himo "え、なんで？"
    misaki_c "なんとなく。最近ちょっと元気なさそうだったから"

    menu:
        "正直に話す":
            himo "...正直に言うと、結構やばい"
            misaki_c "そっか。..."

            "美咲は少し考えてから、財布を出した。"

            misaki_c "これ、使って。返さなくていいから"
            himo "...いいの？"
            misaki_c "いいよ。でも"

            "真剣な目で、こちらを見た。"

            misaki_c "ちゃんと、どうするか考えてね。ずっとは...難しいから"

            "ぐっとくるものがあった。"
            "美咲はわかってる。それでも、お金をくれた。"

            python:
                gift_amount = renpy.random.randint(10000, 20000)
            $ change_money(gift_amount)
            "¥[gift_amount:,]をもらった。"
            $ change_trust(5)
            $ change_dependence(10)
            $ himo_aptitude["honest_moments"] += 2

            menu:
                "何と言う？"
                "ありがとう、考える":
                    himo "...ありがとう。ちゃんと考える"
                    misaki_c "うん"
                    $ himo_aptitude["showed_concern"] += 1

                "ありがとう（流す）":
                    himo "ありがとう、助かる"
                    misaki_c "...うん"
                    "美咲の表情が、少し曇った。"
                    $ change_trust(-3)
                    $ himo_aptitude["easy_choices"] += 1

        "誤魔化す":
            himo "大丈夫大丈夫、何とかなるっしょ"
            misaki_c "...そっか"

            "美咲はそれ以上聞かなかった。"
            "でも、目が笑っていなかった。"

            $ stats["lies_told"] += 1
            $ himo_aptitude["lies"] += 1
            $ change_trust(-5)
            $ add_suspicion("vague_answer")

        "お願いする（直接的に）":
            himo "...実は、ちょっと貸してほしいんだけど"
            misaki_c "貸す、じゃなくてあげるよ"

            python:
                gift_amount = renpy.random.randint(8000, 15000)
            $ change_money(gift_amount)
            "¥[gift_amount:,]をもらった。"
            $ change_trust(-2)
            $ change_dependence(18)
            $ himo_aptitude["money_requests"] += 1
            $ himo_aptitude["easy_choices"] += 1

            "...楽な道を選んだ。"

    $ misaki_events["M05_done"] = True
    return


# ========================================
# Phase 2 v2.0: 美咲イニシアチブイベント
# ========================================

# 自発的連絡（3日以上連絡なし）
label misaki_check_in:
    # v1.4修正: LINEのみなのでreset_contact()は使わない（met_todayも変更しない）
    $ misaki["last_contact"] = 1
    $ daily_flags["misaki_lined_only"] = True
    $ log_action("CHECK_IN", "lined_only={} streak={}".format(daily_flags["misaki_lined_only"], misaki_streak))

    # v1.4: 3つ組（美咲メッセージ, ヒモ太郎返事, 美咲リプライ, タイプ）
    # タイプ: "chat"=雑談で完了, "invite"=誘い→選択肢, "check"=確認
    python:
        _trust = misaki["trust"]
        _depend = misaki["dependence"]

        if _depend >= 60:
            _init_pool = [
                ("昨日なにしてた？", "家でゴロゴロしてた", "...ほんとに？", "check"),
                ("最近会えてないね", "そうだな、会いたいね", "...じゃあ今日会える？", "invite"),
                ("連絡くれないと不安になる", "ごめんごめん", "...もっと連絡ちょうだいね", "chat"),
            ]
        elif _trust >= 60:
            _init_pool = [
                ("ヒモ太郎元気？", "おう、元気だよ", "よかった", "chat"),
                ("今日いい天気だね〜", "ほんとだ、散歩日和", "出かけない？", "invite"),
                ("ご飯食べた？", "まだ〜", "ちゃんと食べなよ", "chat"),
                ("面白い動画見つけたんだけど", "見る見る", "後で送るね", "chat"),
            ]
        elif _trust >= 40:
            _init_pool = [
                ("最近どうしてる？", "まあ〜ぼちぼち", "ちょっと気になって", "chat"),
                ("元気にしてる？", "元気だよ", "よかった", "chat"),
                ("久しぶり", "おう、久しぶり", "...って言うほどでもないか", "chat"),
            ]
        else:
            _init_pool = [
                ("...元気？", "元気だよ", "うん、それだけ", "chat"),
                ("特に用事はないんだけど", "どうした？", "なんとなく", "chat"),
            ]

        _init_msg, _himo_reply, _misaki_reply, _init_type = renpy.random.choice(_init_pool)

    "美咲からLINEが来た。"
    "'[_init_msg]'"

    menu:
        "返信する？"

        "返信する":
            himo "[_himo_reply]"
            misaki_c "[_misaki_reply]"
            $ change_trust(3)

            # invite タイプの場合: 誘いへの対応
            if _init_type == "invite":
                menu:
                    "..."

                    "いいよ":
                        himo "おう、夜な"
                        misaki_c "やった！"
                        $ flags["misaki_tonight"] = True

                    "今日はちょっと...":
                        himo "今日はちょっと用事あって"
                        misaki_c "...そっか"
                        $ change_trust(-1)

        "忙しいと返す":
            himo "ちょっとバタバタしてて"
            misaki_c "そっか。無理しないでね"
            $ change_trust(1)

        "既読スルー":
            "返信しなかった。"
            $ change_trust(-3)
            $ add_suspicion("contact_delay")

    return


# ストレス時の深夜電話
label misaki_stress_call:
    "深夜、美咲から着信が来た。"

    menu:
        "出る？"
        "出る":
            # v1.4修正: 電話のみなのでreset_contact()は使わない
            $ misaki["last_contact"] = 1
            $ daily_flags["misaki_lined_only"] = True
            $ log_action("STRESS_CALL", "lined_only={} streak={}".format(daily_flags["misaki_lined_only"], misaki_streak))
            misaki_c "...ごめん、こんな時間に"
            himo "どした？"
            misaki_c "今日ちょっとしんどくて。声聞きたくなった"
            himo "...そっか。何かあった？"
            misaki_c "上司に理不尽なこと言われて"
            misaki_c "愚痴っていい？"

            menu:
                "聞く":
                    himo "聞くよ"
                    "30分ほど、美咲の愚痴を聞いた。"
                    misaki_c "...ありがとう。なんか楽になった"
                    $ change_trust(8)
                    $ change_dependence(5)
                    $ himo_aptitude["showed_concern"] += 2
                    $ change_stamina(-5)
                "さらっと励ます":
                    himo "大変だったな。でもお前ならなんとかなるって"
                    misaki_c "...うん。ありがとう"
                    $ change_trust(4)
                    $ change_dependence(3)

        "出ない":
            "着信を無視した。"
            "翌朝、美咲からLINEが来ていた。"
            "'ごめん、間違えた'"
            himo "...間違えてないだろ"
            $ change_trust(-4)

    return


# ========================================
# Phase 2 v2.0: 依存度マイルストーンイベント
# ========================================

label misaki_dependence_milestone(threshold):
    if threshold == DEPEND_MILD:
        # v2.1: 当日会っている or まだ一度も会ってない場合はスキップ
        if misaki["met_today"] or stats["times_met"] == 0:
            return
        "翌朝、美咲からLINEが来ていた。"
        "'昨日どこにいたの？ 連絡してよ'"
        himo "...あれ、急に？"
        "なんか、変わってきた気がする。"

    elif threshold == DEPEND_MEDIUM:
        "美咲から電話が来た。"
        misaki_c "ねえ、今週末絶対会えるよね？"

        menu:
            "約束する":
                himo "おう、会えるよ"
                misaki_c "よかった。じゃあ土曜ね"
                # v1.3.1: appointments に統一
                python:
                    _weekday_idx = game_date["weekday"]
                    _days_until_saturday = (6 - _weekday_idx) % 7
                    if _days_until_saturday == 0:
                        _days_until_saturday = 7
                    appointments["misaki"] = game_date["day"] + _days_until_saturday
                $ change_dependence(3)
            "曖昧にする":
                himo "まあ、たぶん..."
                misaki_c "...たぶん？"
                "電話口の空気が少し重くなった。"
                $ change_trust(-5)
                $ add_suspicion("vague_answer")
            "断る":
                himo "今週ちょっと難しいかも"
                misaki_c "...そっか"
                "声が沈んだ。"
                $ change_trust(-8)
                $ change_dependence(-3)

    elif threshold == DEPEND_HEAVY:
        if misaki["met_today"] or location_flags["staying_at_misaki"]:
            # 美咲と一緒にいる／泊まっている場合
            "美咲がこちらをじっと見ている。"
            misaki_c "...ねえ、私のこと...ずっとそばにいてくれる？"
            himo "...え"
            "その目には、不安と執着が混じっていた。"

            menu:
                "もちろん":
                    himo "もちろんだよ"
                    misaki_c "...よかった"
                    "美咲は安心したように笑った。でも、少し怖かった。"
                    $ change_dependence(3)
                "わからない":
                    himo "...正直、わからない"
                    misaki_c "...そっか"
                    "美咲の表情が、一瞬固まった。"
                    $ change_trust(-5)
                    $ himo_aptitude["honest_moments"] += 1
        else:
            "深夜にLINEが来た。"
            "'今日誰かといた？'"
            himo "...どこで知ったんだ"

            menu:
                "正直に話す":
                    himo "友達と飯食ってた"
                    misaki_c "そっか。...なんで言ってくれなかったの"
                    $ change_trust(-3)
                    $ himo_aptitude["honest_moments"] += 1
                "誤魔化す":
                    himo "一人でいたよ"
                    misaki_c "...そっか"
                    "信じていないのが声でわかった。"
                    $ change_trust(-8)
                    $ stats["lies_told"] += 1
                    $ himo_aptitude["lies"] += 1

    return


# 週末の約束を破ったとき
label misaki_broken_promise:
    "美咲からLINEが来た。"
    "'昨日、来なかったね'"
    himo "...やばい"

    menu:
        "謝る":
            himo "ごめん、急に用事が..."
            misaki_c "...次は必ず来てね"
            $ change_trust(-10)
            $ change_dependence(8)
        "言い訳する":
            himo "ちょっとトラブルがあって"
            misaki_c "...そっか"
            $ change_trust(-15)
            $ stats["lies_told"] += 1
            $ himo_aptitude["lies"] += 1

    return


# 美咲の部屋訪問（M-03完了後の定期行動 / バリエーション付き）
label misaki_room_visit:
    "美咲の部屋に来た。"

    # v2.3: 曜日による外見描写
    if is_weekend():
        "部屋着の美咲。リラックスした雰囲気。"
        "休日の夜、特別な時間が流れる。"
    else:
        "スーツを脱いだばかりの美咲。少し疲れた様子。"
        "残業明けでも、笑顔を見せてくれた。"

    # ランダムで会話バリエーション
    python:
        _room_scene = renpy.random.choice(["cooking", "tv", "tired"])

    if _room_scene == "cooking":
        misaki_c "いらっしゃい。今日は何食べたい？"
    elif _room_scene == "tv":
        misaki_c "あ、来た来た。今ドラマ見てたんだ"
        himo "お邪魔〜"
        misaki_c "一緒に見る？ご飯もあるよ"
    else:
        misaki_c "...あ、来てくれたんだ"
        himo "疲れてる？"
        misaki_c "ちょっとね...でも嬉しい"

    # v2.3: 共通パスで確実にセット
    $ misaki["met_today"] = True
    $ reset_contact()
    $ daily_flags["ate_today"] = True

    menu:
        "何をする？"
        "ご飯を食べる（美咲の手料理）":
            "一緒にご飯を食べた。"
            $ change_trust(3)
            $ change_dependence(3)
            $ change_stamina(15)

        "泊まる":
            "今日も泊まらせてもらった。"
            $ location_flags["staying_at_misaki"] = True
            # v1.4追加: カナの翌朝フラグをクリア（排他制御）
            $ flags["kana_morning_after"] = False
            $ flags["kana_himo_room_morning"] = False
            $ location_flags["staying_at_kana"] = False
            $ flags["kana_at_himo_room"] = False
            $ change_trust(2)
            $ change_dependence(5)
            $ change_stamina(30)
            $ change_cleanliness(20)
            $ himo_aptitude["easy_choices"] += 1

            # v2.4修正: 土曜の「夜」に泊まった場合のみ日曜朝シーンを発動
            if is_weekend() and game_date["weekday"] == 6 and game_date["time"] == "night":
                $ flags["misaki_sunday_morning"] = True

    return

# v2.1: 土曜宿泊後の日曜朝シーン
label misaki_sunday_morning_scene:
    scene bg_placeholder
    "目が覚めると、美咲の部屋だった。"
    "カーテンの隙間から日差しが入ってくる。"
    "休日の朝。"

    misaki_c "おはよう。コーヒー飲む？"
    himo "...いただきます"

    "キッチンで美咲がコーヒーを淹れている音が聞こえる。"
    "こういう朝も、悪くないな。"

    misaki_c "昨日泊まってくれて、よかった"
    himo "俺も"

    "少し照れくさいけど、本当のことだった。"

    $ change_stamina(20)
    $ change_trust(3)
    $ change_dependence(5)
    $ reset_contact()
    $ misaki["met_today"] = True
    $ daily_flags["ate_today"] = True

    return


label misaki_confession:
    scene bg_placeholder
    "――ある夜――"
    "いつものように美咲と一緒にいると、急に真剣な顔になった。"

    misaki_c "ねえ、ヒモ太郎"
    himo "ん？"
    misaki_c "...好きだよ。ちゃんと伝えたくて"

    "少しの沈黙。"
    "美咲は目を逸らさずにいた。"

    menu:
        "何と返す？"

        "俺も好き":
            himo "...俺も好きだよ"
            misaki_c "...よかった"
            "美咲が、少し泣きそうな顔で笑った。"
            "嬉しいのに、どこかで罪悪感があった。"
            $ change_trust(10)
            $ change_dependence(15)
            $ himo_aptitude["easy_choices"] += 1
            # 罪悪感カウント（Phase 3以降のエンディング分岐用）
            $ flags["confession_accepted"] = True

        "ありがとう（曖昧に受け取る）":
            himo "...ありがとう"
            misaki_c "...うん"
            "美咲は何も言わなかった。"
            "答えを急かすこともなく、ただ隣にいた。"
            "その優しさが、少し辛かった。"
            $ change_trust(5)
            $ change_dependence(8)
            $ flags["confession_ambiguous"] = True

        "今はそういう気持ちじゃない":
            himo "...ごめん、今はそういう感じじゃなくて"
            misaki_c "...そっか"
            "美咲の表情が、一瞬固まった。"
            "でもすぐに、いつもの笑顔に戻った。"
            "'大丈夫、忘れて'"
            "忘れられるわけがなかった。"
            $ change_trust(-15)
            $ change_dependence(-10)
            $ himo_aptitude["honest_moments"] += 1
            $ flags["confession_rejected"] = True

    $ flags["confession_done"] = True
    return


# ========================================
# Phase 4 v1.3: 土日昼デート
# ========================================

label misaki_daytime_date_request:
    "美咲に昼から会えないか聞いてみた。"

    if not is_weekend():
        misaki_c "ごめん、今仕事中..."
        return

    # 既読スルーチェック
    if daily_flags.get("ignored_today", False):
        "さっき既読スルーされたばかりだし..."
        return

    # 成功判定
    python:
        _trust = misaki["trust"]
        if _trust >= 60:
            _daytime_rate = 0.90
        elif _trust >= 45:
            _daytime_rate = 0.75
        elif _trust >= 30:
            _daytime_rate = 0.60
        else:
            _daytime_rate = 0.40
        _daytime_success = renpy.random.random() < _daytime_rate

    if _daytime_success:
        misaki_c "いいよ！今日休みだし"
        call misaki_date_with_location
    else:
        misaki_c "ごめん、今日ちょっと用事あって..."
        misaki_c "夜なら空くかも"
        himo "了解〜"

    return


# ========================================
# v1.5追加: 美咲LINE選択肢の各ラベル
# ========================================

label misaki_line_listen_work:
    himo "仕事どう？大変？"
    misaki_c "...聞いてくれるの？"
    misaki_c "実は最近、上司がさ..."

    "美咲の仕事の愚痴を30分くらい聞いた。"

    misaki_c "ごめんね、愚痴ばっかり"
    himo "いいって。いつでも聞くよ"
    misaki_c "...ありがとう"

    $ change_trust(4)
    $ change_dependence(3)
    $ himo_aptitude["showed_concern"] += 1
    # v1.2: 疑念緩和
    $ reduce_suspicion("misaki", 1, "LINE愚痴聞き")

    return


label misaki_line_offer_help:
    himo "なんか手伝えることある？"
    misaki_c "え、急にどうしたの"
    himo "いや、なんとなく"

    misaki_c "...じゃあ、週末の買い出し付き合ってくれる？"

    menu:
        "いいよ":
            misaki_c "ほんと！？ありがとう"
            # 次の週末に美咲と約束
            python:
                current_day = game_date["day"]
                weekday_idx = game_date["weekday"]
                days_until_saturday = (6 - weekday_idx) % 7
                if days_until_saturday == 0:
                    days_until_saturday = 7
                appointments["misaki"] = current_day + days_until_saturday
            $ change_trust(5)
            $ change_dependence(4)
            $ himo_aptitude["showed_concern"] += 1
            # v1.2: 疑念緩和
            $ reduce_suspicion("misaki", 1, "LINE手伝い")
            "（週末に約束した）"

        "ちょっと考えさせて":
            misaki_c "...うん、いいよ"
            $ change_trust(1)

    return


label misaki_line_invite_home:
    himo "今日の夜さ、うちで飲まない？"

    python:
        # 信頼度と曜日で成功率変動
        base_rate = 0.50
        if misaki["trust"] >= 65:
            base_rate += 0.20
        if is_weekend():
            base_rate += 0.15
        invite_success = renpy.random.random() < base_rate

    if invite_success:
        misaki_c "え、いいの？...行く"
        $ flags["misaki_tonight"] = True
        # v1.6追加: ヒモ太郎の部屋に来る専用フラグ
        $ flags["misaki_visit_himo_room"] = True
        $ change_trust(3)
        $ change_dependence(5)
        "（今夜、美咲がうちに来ることになった）"
        if player["cleanliness"] < 40:
            himo "（やばい、部屋汚い...片付けないと）"
    else:
        misaki_c "ごめん、今日はちょっと..."
        misaki_c "また今度ね"
        $ change_trust(1)  # 誘ったこと自体は好印象

    return


label misaki_line_miss_you:
    himo "なあ美咲"
    misaki_c "ん？"
    himo "声聞きたくなった"

    "少し間があった。"

    misaki_c "...もう、急にそういうこと言う"

    python:
        if misaki["dependence"] >= 50:
            # 依存度が高いと嬉しさが先に出る
            response = "happy"
        elif renpy.random.random() < 0.7:
            response = "happy"
        else:
            response = "shy"

    if response == "happy":
        misaki_c "...うれしい"
        misaki_c "私も、聞きたかった"
        $ change_trust(5)
        $ change_dependence(6)
    else:
        misaki_c "...恥ずかしいんだけど"
        $ change_trust(4)
        $ change_dependence(3)

    $ himo_aptitude["showed_concern"] += 1
    # v1.2: 疑念緩和
    $ reduce_suspicion("misaki", 1, "LINE声聞きたい")

    return


label misaki_line_amaeru:
    himo "美咲〜"
    misaki_c "なに？"
    himo "甘えていい？"

    misaki_c "...なにそれ"

    "でも、声は嬉しそうだった。"

    misaki_c "...しょうがないな"
    misaki_c "今夜、来る？"

    menu:
        "行く":
            $ flags["misaki_tonight"] = True
            misaki_c "...待ってる"
            $ change_trust(6)
            $ change_dependence(8)
            # 美咲のテンションが高い → デートの雰囲気が良くなる
            $ flags["misaki_good_mood_tonight"] = True
            # v1.2: 疑念緩和
            $ reduce_suspicion("misaki", 2, "LINE甘え")

        "今日は無理、ごめん":
            misaki_c "...そっか"
            "甘えたのに行かない。ちょっと罪悪感。"
            $ change_trust(-2)
            $ change_dependence(3)

    return


# ========================================
# Phase 4 Step 2: 美咲の対面お金交渉ゲーム
# ========================================

# 第1段階: 切り出し方
label misaki_negotiation_start:
    # 週間カウント加算
    $ money_request_weekly["count"] += 1
    $ daily_flags["asked_money_today"] = True
    $ himo_aptitude["money_requests"] += 1
    $ stats["negotiation_attempts"] = stats.get("negotiation_attempts", 0) + 1

    # 週間カウントに応じた美咲の反応分岐
    python:
        weekly_count = money_request_weekly["count"]

    if weekly_count >= 4:
        # 4回目以上: 高確率拒否
        call misaki_negotiation_refuse
        return

    # 切り出し方の選択
    menu:
        "どう切り出す？"

        "「なあ、ちょっとお金の話なんだけど...」":
            # 直球。成功率低め
            $ _nego_approach = "direct"
            $ _nego_base_rate = 40
            $ change_trust(-3)
            himo "なあ、ちょっとお金の話なんだけど..."

        "「最近ほんとにヤバくてさ...」":
            # 泣き落とし。依存度依存
            $ _nego_approach = "sob"
            $ _nego_base_rate = 30 + int(misaki["dependence"] * 0.4)
            himo "最近ほんとにヤバくてさ..."

        "「実はさ、今月の家賃がちょっと...」" if misaki["trust"] >= 50:
            # 具体的。成功率中
            $ _nego_approach = "specific"
            $ _nego_base_rate = 55
            himo "実はさ、今月の家賃がちょっと..."

        "「美咲に相談したいことがあるんだけど」" if misaki["trust"] >= 50:
            # 信頼してる感。成功率中〜高
            $ _nego_approach = "consult"
            $ _nego_base_rate = 65
            himo "美咲に相談したいことがあるんだけど"

        "「俺、ちゃんと就活も考えてて。でも今月だけ」" if misaki["trust"] >= 70:
            # 将来性アピール。成功率高
            $ _nego_approach = "future"
            $ _nego_base_rate = 75
            himo "俺、ちゃんと就活も考えてて。でも今月だけ..."

        "...（やっぱりやめる）":
            himo "（...やっぱり言えなかった）"
            # カウントを戻す
            $ money_request_weekly["count"] -= 1
            $ daily_flags["asked_money_today"] = False
            $ himo_aptitude["money_requests"] -= 1
            $ stats["negotiation_attempts"] = max(0, stats.get("negotiation_attempts", 0) - 1)
            # v1.2: 踏みとどまった分の微緩和
            $ reduce_suspicion("misaki", 1, "交渉キャンセル")
            return

    # v1.1: 開始ログ
    $ log_action("対面交渉_開始", "approach=" + _nego_approach + " base_rate=" + str(_nego_base_rate) + " weekly=" + str(money_request_weekly["count"]))

    # 第2段階へ
    call misaki_negotiation_reaction
    return


# 第2段階: 反応を見て押すか引くか
label misaki_negotiation_reaction:
    # 成功率計算: ベース + 場所補正 - 週間ペナルティ - 疑念ペナルティ
    python:
        location = daily_flags.get("date_location", "famires")
        location_bonus = NEGOTIATION_LOCATION_BONUS.get(location, 0)

        weekly_count = money_request_weekly["count"]
        if weekly_count == 2:
            weekly_penalty = NEGOTIATION_PENALTY_2ND
        elif weekly_count >= 3:
            weekly_penalty = NEGOTIATION_PENALTY_3RD
        else:
            weekly_penalty = 0

        # v1.2: 係数を2に緩和＋上限30%キャップ
        suspicion_penalty = min(30, suspicion.get("misaki", 0) * 2)

        _nego_success_rate = _nego_base_rate + location_bonus - weekly_penalty - suspicion_penalty
        _nego_success_rate = max(5, min(95, _nego_success_rate))

    # v1.1: 判定ログ
    $ log_action("対面交渉_判定", "rate=" + str(_nego_success_rate) + " loc=" + location + " loc_bonus=" + str(location_bonus) + " weekly_pen=" + str(weekly_penalty) + " susp_pen=" + str(suspicion_penalty))

    # 美咲の反応テキスト（信頼度・週間回数で変化）
    if misaki["trust"] >= 60 and weekly_count <= 1:
        # 好反応
        misaki_c "え、大丈夫？ いくら必要？"
        $ _nego_reaction = "positive"
    elif misaki["trust"] >= 40 or weekly_count <= 2:
        # 微妙な反応
        if weekly_count >= 2:
            misaki_c "また...？ ちゃんと仕事探してる？"
        else:
            misaki_c "...うん、どうしたの？"
        $ _nego_reaction = "neutral"
    else:
        # 拒否寄り反応
        misaki_c "...ねえ、私のこと何だと思ってる？"
        $ _nego_reaction = "negative"

    # 押す/引くの選択
    menu:
        "「...」"

        "押す（お金を頼む）" if _nego_reaction != "negative":
            call misaki_negotiation_amount
            return

        "控えめに頼む" if _nego_reaction == "positive":
            # 少額で確定成功
            python:
                amount = renpy.random.randint(3000, 5000)
            misaki_c "...はい、これ"
            "美咲から¥[amount:,]をもらった。"
            $ change_money(amount, "美咲（対面交渉・控えめ）")
            $ change_trust(-1)
            $ change_dependence(5)
            return

        "引く（話題を変える）":
            himo "いや、やっぱいい。気にしないで"
            if _nego_reaction == "negative":
                misaki_c "...そう"
                "気まずい空気が流れた。"
                $ add_suspicion("too_many_requests")
            else:
                misaki_c "...ほんとに？ 困ったら言ってね"
                $ change_trust(2)
            return

        "強引に頼む" if _nego_reaction == "negative":
            # 修羅場リスク
            himo "頼むって、マジで困ってんだよ"
            misaki_c "..."
            python:
                # 30%の確率で修羅場に発展
                _nego_shuraba = renpy.random.random() < 0.30
            if _nego_shuraba:
                call misaki_negotiation_shuraba
                return
            else:
                # 渋々了承
                python:
                    amount = renpy.random.randint(3000, 8000)
                misaki_c "...分かった。でも、もうこれ最後にして"
                "美咲から¥[amount:,]をもらった。"
                $ change_money(amount, "美咲（対面交渉・強引）")
                $ change_trust(-8)
                $ change_dependence(3)
                $ add_suspicion("too_many_requests")
                return

    return


label misaki_negotiation_refuse:
    # 週4回以上の場合の拒否イベント
    misaki_c "...ヒモ太郎"
    misaki_c "最近、お金のことばっかりだよね"
    himo "..."
    misaki_c "私、ATMじゃないよ？"

    menu:
        "何と言う？"

        "謝る":
            himo "...ごめん。調子に乗りすぎた"
            misaki_c "...分かった。でも、ちょっと考えて"
            $ change_trust(-5)
            $ add_suspicion("too_many_requests")
            $ himo_aptitude["honest_moments"] += 1

        "誤魔化す":
            himo "そんなつもりじゃ..."
            misaki_c "...そうかな"
            "美咲の目が冷たい。"
            $ change_trust(-10)
            $ add_suspicion("too_many_requests")
            $ himo_aptitude["lies"] += 1
            $ stats["lies_told"] += 1

    return


# 第3段階: 金額提示
label misaki_negotiation_amount:
    python:
        location = daily_flags.get("date_location", "famires")

    menu:
        "いくら頼む？"

        "控えめに（¥5,000〜10,000）":
            $ _nego_amount_type = "low"
            $ _nego_range = NEGOTIATION_AMOUNT_LOW

        "普通に（¥10,000〜15,000）" if location != "famires":
            # ファミレスでは中額以上は不自然
            $ _nego_amount_type = "mid"
            $ _nego_range = NEGOTIATION_AMOUNT_MID

        "思い切って（¥15,000〜30,000）" if location not in ["famires", "himo_room"]:
            # ファミレス・ヒモ太郎の部屋では大額不可
            $ _nego_amount_type = "high"
            $ _nego_range = NEGOTIATION_AMOUNT_HIGH

    # 成功判定
    python:
        # 金額タイプによる成功率補正
        amount_penalty = {"low": 0, "mid": -10, "high": -25}
        final_rate = _nego_success_rate + amount_penalty.get(_nego_amount_type, 0)
        final_rate = max(5, min(95, final_rate))

        success = renpy.random.random() * 100 < final_rate

    if success:
        python:
            amount = renpy.random.randint(_nego_range[0], _nego_range[1])
        $ log_action("対面交渉_成功", "type=" + _nego_amount_type + " amount=" + str(amount) + " final_rate=" + str(final_rate))
        $ stats["negotiation_success"] = stats.get("negotiation_success", 0) + 1
        $ stats["negotiation_total_earned"] = stats.get("negotiation_total_earned", 0) + amount
        misaki_c "...分かった。これ、使って"
        "美咲から¥[amount:,]をもらった。"

        $ change_money(amount, "美咲（対面交渉）")

        # パラメータ変動（金額タイプで変化）
        if _nego_amount_type == "low":
            $ change_trust(-2)
            $ change_dependence(5)
            $ suspicion["misaki"] = suspicion.get("misaki", 0) + 1
        elif _nego_amount_type == "mid":
            $ change_trust(-4)
            $ change_dependence(8)
            $ suspicion["misaki"] = suspicion.get("misaki", 0) + 2
        else:
            $ change_trust(-6)
            $ change_dependence(12)
            $ suspicion["misaki"] = suspicion.get("misaki", 0) + 3

        # 居酒屋ボーナス使用時の翌日リスク
        if location == "izakaya":
            $ flags["izakaya_money_hangover"] = True

    else:
        # 失敗
        $ log_action("対面交渉_失敗", "type=" + _nego_amount_type + " final_rate=" + str(final_rate))
        misaki_c "...ごめん、今月厳しくて"
        himo "そっか..."
        $ change_trust(-3)
        $ add_suspicion("too_many_requests")

    return


label misaki_negotiation_shuraba:
    # 強引に頼んで修羅場に発展した場合
    misaki_c "...ヒモ太郎"
    misaki_c "私、ずっと我慢してたんだけど"
    misaki_c "お金のことばっかり言われると、利用されてるみたいで..."

    "美咲の目に涙が浮かんでいる。"

    # 嘘パズルに発展（高難度）
    call run_lie_puzzle("money_shuraba", "misaki")

    return