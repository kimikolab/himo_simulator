# misaki_events.rpy
# 美咲関連イベント（バランス調整済み）

label contact_misaki:
    # v1.3修正: LINEのみなのでreset_contactを呼ばない
    "美咲にLINEを送った..."

    python:
        mood = misaki_mood["today_mood"]

    if mood == "stressed":
        "2時間後、やっと返信が来た。"
        misaki_c "ごめん、バタバタしてて"
    elif mood == "tired":
        "しばらくして返信が来た。"
        misaki_c "お疲れ。今日しんどくて..."
    elif mood == "good":
        "すぐに返信が来た。"
        misaki_c "わ、ヒモ太郎！"
    else:
        if misaki["trust"] >= 25:
            "しばらくして返信が来た。"
        else:
            "既読スルーされた..."
            $ change_trust(-2)
            $ daily_flags["ignored_today"] = True
            return
        misaki_c "どうしたの？"

    # v1.4: お金要求ブロック時にメニューに戻れるようラベル化
label contact_misaki_menu:
    menu:
        misaki_c "どうしたの？"

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
        misaki_c "今日もう会ったよ？笑"
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

            $ change_trust(-1)
            return

    # 成功 → デートへ
    if game_date["time"] == "night":
        call misaki_date
        return
    else:
        misaki_c "夜なら空いてるよ"
        $ flags["misaki_tonight"] = True
        himo "了解〜"
        return


# 約束があって会いに行く（昼以前に約束した・または1日目）
label misaki_meet_planned:
    if misaki["met_today"]:
        misaki_c "今日もう会ったよ？笑"
        himo "あ、そっか"
        return

    call misaki_date
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

        "美咲を励ます":
            himo "まあでも、頑張ってる美咲かっこいいよ"

            "顔が赤くなった。"

            misaki_c "...ありがとう"
            himo "お、効いた効いた"

            $ change_trust(8)
            $ change_dependence(2)
            $ himo_aptitude["showed_concern"] += 2

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

    # v2.1: 週末に会った記録
    if is_weekend():
        $ flags["met_misaki_this_weekend"] = True

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
    $ log_action("美咲にお金要求", "信頼" + str(misaki["trust"]))
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    # v1.2追加: 最近会っていない場合
    # v1.4修正: ブロック時はターンを消費しない（呼び出し元でメニューに戻す）
    if misaki["last_contact"] > 1:
        himo "（最近会ってもいないし、さすがにお金の話はしにくいな）"
        $ _money_request_blocked = True
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
    "美咲からLINEが来た。"
    "'最近どうしてる？'"
    $ reset_contact()

    menu:
        "返信する？"
        "元気だよと返す":
            himo "元気だよ〜、そっちは？"
            misaki_c "私も。...なんか急に気になって"
            $ change_trust(3)
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
            $ reset_contact()
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
                $ weekend_promised = True
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

    $ weekend_promised = False
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
            $ change_trust(2)
            $ change_dependence(5)
            $ change_stamina(30)
            $ change_cleanliness(20)
            $ himo_aptitude["easy_choices"] += 1

            # v2.4修正: 土曜の「夜」に泊まった場合のみ日曜朝シーンを発動
            if is_weekend() and game_date["weekday"] == 6 and game_date["time"] == "night":
                $ flags["misaki_sunday_morning"] = True

    # v2.1: 週末に会った記録
    if is_weekend():
        $ flags["met_misaki_this_weekend"] = True

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