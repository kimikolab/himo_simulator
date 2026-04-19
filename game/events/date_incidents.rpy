# date_incidents.rpy
# デート中に発生する探り・地雷・ハプニング

init python:
    def should_trigger_probe(target):
        """探りが発生するか判定"""
        # Phase 4 v1.1: 序盤（7日目以前）は探り発生しない
        if game_date["day"] <= 7:
            return False

        sus = suspicion.get(target, 0)
        location = daily_flags.get("date_location", None)

        base_rate = 0.10
        if sus >= 1:
            base_rate += 0.15
        if sus >= 3:
            base_rate += 0.15
        if location == "izakaya":
            base_rate += 0.15  # 居酒屋は探り率UP

        return renpy.random.random() < base_rate

    def should_trigger_landmine():
        """地雷が発生するか判定"""
        # Phase 4 v1.2: 序盤（9日目以前）は地雷発生しない
        if game_date["day"] <= 9:
            return False
        return renpy.random.random() < 0.15  # 15%の固定確率

    def should_trigger_happening(target):
        """ハプニングが発生するか判定"""
        if not kana_flags["met"]:
            return False
        return renpy.random.random() < 0.20


label check_date_incidents(target):
    # 探り
    python:
        probe = should_trigger_probe(target)
    if probe:
        call date_probe(target)

    # 地雷（探りと同時には発生しない）
    if not probe:
        python:
            landmine = should_trigger_landmine()
        if landmine:
            call date_landmine(target)

    # ハプニング
    python:
        happening = should_trigger_happening(target)
    if happening:
        call date_happening(target)

    return


# === 探り ===

label date_probe(target):
    python:
        if target == "misaki":
            probes = [
                ("last_night", "昨日の夜、何してたの？"),
                ("schedule", "来週の土曜、空いてる？"),
                ("lately", "最近、楽しそうだね"),
            ]
            if suspicion["misaki"] >= 2:
                probes.append(("phone_check", "ねえ、LINE見せて？"))
        else:
            probes = [
                ("last_night", "昨日の夜なにしてた？"),
                ("insta", "インスタにツーショット載せていい？"),
            ]
            if kana["dependence"] >= 40:
                probes.append(("phone_check", "スマホ見せて〜"))

        probe_key, probe_text = renpy.random.choice(probes)

    "ふと、相手が真面目な顔になった。"

    if target == "misaki":
        $ show_misaki("serious")
        misaki_c "[probe_text]"
    else:
        show kana serious
        kana_c "[probe_text]"

    # 探りの種類別対応
    if probe_key == "last_night":
        # Phase 4 v1.1: 前日にもう片方と接触した実績がなければ軽い探りに差し替え
        python:
            if target == "misaki":
                other_recent = kana.get("last_contact", 99) <= 1 if kana_flags["met"] else False
            else:
                other_recent = misaki.get("last_contact", 99) <= 1

        if not other_recent:
            if target == "misaki":
                misaki_c "最近、楽しそうだね"
            else:
                kana_c "最近なんか楽しそうじゃん"
            himo "そう？"
            $ suspicion[target] = min(suspicion[target] + 1, SUSPICION_MAX)
            return

        # 前日にもう片方とデートしてたら嘘パズル発動
        if daily_flags.get("date_with", None) is not None:
            call run_lie_puzzle("last_night", target)
        else:
            himo "家でゴロゴロしてた"
            if target == "misaki":
                misaki_c "...そう"
            else:
                kana_c "暇人じゃん笑"

    elif probe_key == "phone_check":
        menu:
            "見せる":
                "スマホを渡した。"
                # もう片方からの通知が来るリスク
                python:
                    notification_risk = renpy.random.random() < 0.30
                if notification_risk:
                    "その瞬間、LINE通知が鳴った。"
                    if target == "misaki":
                        "「カナ」という名前が画面に表示された。"
                        misaki_c "...カナって誰？"
                        call run_lie_puzzle("other_woman", "misaki")
                    else:
                        "「美咲」という名前が画面に表示された。"
                        show kana serious
                        kana_c "...美咲って誰？"
                        call run_lie_puzzle("other_woman", "kana")
                else:
                    "特に怪しいものはなかった。"
                    if target == "misaki":
                        $ show_misaki("shy")
                        misaki_c "...ごめん、疑って"
                        $ change_trust(3)
                    else:
                        show kana normal
                        kana_c "ふーん、つまんない笑"

            "断る":
                himo "プライバシーってもんがあるだろ"
                if target == "misaki":
                    misaki_c "...そうだよね"
                    $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
                else:
                    kana_c "なんで？やましいことあるの？"
                    $ suspicion["kana"] = min(suspicion["kana"] + 2, SUSPICION_MAX)

    elif probe_key == "schedule":
        menu:
            "空いてるよ":
                $ show_misaki("happy")
                misaki_c "じゃあ約束ね！"
                # Phase 4 v1.3: 具体的な日付を記録
                python:
                    _weekday_idx = game_date["weekday"]
                    _days_until_saturday = (6 - _weekday_idx) % 7
                    if _days_until_saturday == 0:
                        _days_until_saturday = 7  # 今日が土曜なら来週
                    appointments["misaki"] = game_date["day"] + _days_until_saturday
                "（来週の土曜に約束した）"
                "（カナとの予定と被らないよな...?）"

            "まだ分からない":
                misaki_c "...そう"
                $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)

    elif probe_key == "insta":
        menu:
            "いいよ":
                show kana happy
                kana_c "やった！"
                "ツーショットを撮られた。"
                $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 3
                "（...これ、美咲に見られたらアウトだな）"

            "今日はやめとこ":
                kana_c "え〜、なんで？"
                $ change_trust_kana(-3)
                $ suspicion["kana"] = min(suspicion["kana"] + 1, SUSPICION_MAX)

    elif probe_key == "lately":
        menu:
            "まあ、それなりに":
                misaki_c "...何かいいことあった？"
                himo "別に？いつも通りだよ"
                misaki_c "...ふーん"
                $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)

            "美咲に会えるからな":
                $ show_misaki("blush")
                misaki_c "...もう、急にそういうこと言う"
                $ change_trust(5)
                $ change_dependence(3)

    return


# === 地雷 ===

label date_landmine(target):
    python:
        if target == "misaki":
            mines = [
                "quit_job",     # 仕事辞めれば？
                "support_me",   # 養ってよ
            ]
        else:
            mines = [
                "followers",    # フォロワー数気にしすぎ
                "other_guys",   # 他の男と遊んでんの？
            ]
        mine_key = renpy.random.choice(mines)

    # 地雷選択肢を通常会話に紛れ込ませる
    if mine_key == "quit_job":
        "美咲が仕事の愚痴を言い始めた。"
        $ show_misaki("sad")
        misaki_c "今日も残業で...もう疲れた"

        menu:
            "大変だな、お疲れ":
                misaki_c "ありがとう..."
                $ change_trust(3)
                $ himo_aptitude["showed_concern"] += 1

            "仕事辞めちゃえば？":
                misaki_c "..."
                $ show_misaki("angry")
                "美咲の表情が固まった。"
                misaki_c "...そんな簡単に言わないで"
                misaki_c "仕事は私のアイデンティティなの"
                $ change_trust(-15)
                "（地雷だった...）"

            "俺がいるから大丈夫だって":
                $ show_misaki("smile")
                misaki_c "...ふふ、何の役にも立たないくせに"
                himo "ひどい！"
                misaki_c "冗談。...でもありがとう"
                $ change_trust(5)
                $ change_dependence(5)

    elif mine_key == "support_me":
        himo "なあ美咲"

        menu:
            "いつもありがとう":
                misaki_c "急にどうしたの？"
                himo "いや、なんとなく"
                misaki_c "...ふふ、どういたしまして"
                $ change_trust(5)

            "俺のこと養ってよ":
                if misaki["stage"] <= STAGE_FRIEND:
                    $ show_misaki("neutral")
                    misaki_c "はは、冗談きついね"
                    $ change_trust(-2)
                else:
                    misaki_c "..."
                    $ show_misaki("serious")
                    misaki_c "それ、冗談？"
                    himo "あ、いや..."
                    misaki_c "...冗談だよね"
                    "空気が冷えた。"
                    $ change_trust(-10)

    elif mine_key == "followers":
        "カナがスマホを見ながら話してる。"
        kana_c "あ〜、フォロワー減ったかも"

        menu:
            "気にしすぎじゃない？":
                if kana["dependence"] >= 40:
                    show kana smile
                    kana_c "...うん、そうかも"
                    kana_c "ヒモ太郎がいるからいいか"
                    $ change_trust_kana(5)
                else:
                    show kana angry
                    kana_c "は？分かんないくせに"
                    $ change_trust_kana(-10)
                    "（地雷だった...）"

            "すごいじゃん、それだけいるの":
                kana_c "でしょ〜？"
                $ change_trust_kana(3)

            "俺がフォローしとくよ":
                kana_c "あはは！いらない！"
                $ change_trust_kana(5)

    elif mine_key == "other_guys":
        kana_c "昨日友達と遊んでたんだ〜"

        menu:
            "楽しかった？":
                kana_c "うん！"
                $ change_trust_kana(2)

            "男もいたの？":
                show kana angry
                kana_c "...は？"
                kana_c "何？嫉妬？"

                if flags.get("kana_friend_info_obtained", False):
                    # 情報を持ってるプレイヤーは地雷だと分かる
                    "（カナは前の彼氏に浮気されてる...この話題はヤバい）"

                $ change_trust_kana(-10)
                $ change_dependence_kana(5)
                "（怒らせてしまった）"

    return


# === ハプニング ===

label date_happening(target):
    python:
        happenings = ["line_notification"]

        # 自宅デートでは外で人に会う系のハプニングを除外
        _current_location = daily_flags.get("date_location", "")
        if _current_location not in ("himo_room", "room", "misaki_room"):
            happenings.append("acquaintance")

        if target == "kana":
            happenings.append("insta_shot")
        if target == "misaki":
            happenings.append("receipt")

        happening_key = renpy.random.choice(happenings)

    if happening_key == "line_notification":
        "デートの最中、スマホが鳴った。"
        if target == "misaki":
            "カナからのLINE通知。"
        else:
            "美咲からのLINE通知。"

        menu:
            "そっと無視する":
                "通知をスワイプして消した。"
                if target == "misaki":
                    misaki_c "LINE？見なくていいの？"
                else:
                    kana_c "LINE来てんじゃん？見なくていいの？"
                himo "後で見る"

            "トイレに行って返信する":
                himo "ちょっとトイレ"
                "急いで返信した。"
                $ change_stamina(-3)

            "相手の前で普通に見る":
                "通知を確認した。"
                python:
                    name_visible = renpy.random.random() < 0.40
                if name_visible:
                    if target == "misaki":
                        $ show_misaki("serious")
                        misaki_c "...カナって誰？"
                        call run_lie_puzzle("other_woman", "misaki")
                        # Phase 4 v1.2: 嘘パズル後のリアクション
                        if lie_puzzle["result"] == "safe":
                            misaki_c "...ごめん、変なこと聞いて"
                        elif lie_puzzle["result"] == "uneasy":
                            "美咲は何か言いたそうだったが、黙った。"
                    else:
                        kana_c "...美咲って誰？"
                        call run_lie_puzzle("other_woman", "kana")
                        # Phase 4 v1.2: 嘘パズル後のリアクション
                        if lie_puzzle["result"] == "safe":
                            kana_c "ふーん、まあいいけど"
                        elif lie_puzzle["result"] == "uneasy":
                            "カナは少し不機嫌そうだった。"
                else:
                    "名前は見えなかったようだ。"

    elif happening_key == "acquaintance":
        "デート中、向こうから見覚えのある顔が歩いてきた。"
        if target == "misaki":
            "美咲の同僚だ。"
            $ show_misaki("surprised")
            misaki_c "あ、田中さん"

            menu:
                "普通に挨拶する":
                    "田中さんに軽く挨拶された。"
                    "（美咲の彼氏として認識された...かもしれない）"
                    $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)

                "トイレに逃げる":
                    himo "あ、ちょっとトイレ"
                    misaki_c "え？今？"
                    "逃げた。"
                    $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)
        else:
            "カナの友達だ。"
            show kana excited
            kana_c "あ〜！まりちゃ〜ん！"
            "嬉しそうに紹介してくる。"
            kana_c "彼氏！"
            himo "（彼氏...?）"
            $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 2

    elif happening_key == "insta_shot":
        "突然、カナがスマホを向けてきた。"
        show kana happy
        kana_c "はい撮るよ〜！"

        menu:
            "撮らせる":
                "パシャ。"
                kana_c "いい写真〜！載せよ！"
                $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 3
                "（...証拠が増えた）"

            "顔を隠す":
                himo "やめろ〜"
                show kana pouty
                kana_c "え〜、なんで〜！"
                $ change_trust_kana(-2)
                $ suspicion["kana"] = min(suspicion["kana"] + 1, SUSPICION_MAX)

    elif happening_key == "receipt":
        "ポケットからレシートが落ちた。"
        "美咲が拾った。"
        $ show_misaki("serious")
        misaki_c "これ...カフェのレシート？"
        misaki_c "2人分のコーヒーって書いてあるけど"

        menu:
            "友達と行った":
                misaki_c "...ふーん"
                $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)

            "一人で2杯飲んだ":
                misaki_c "...嘘でしょ？"
                $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
                $ himo_aptitude["lies"] += 1

    return
