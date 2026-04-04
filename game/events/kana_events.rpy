# kana_events.rpy
# カナルート イベント（Phase 3）

init python:
    def is_kana_available():
        """カナが部屋にいるかどうか"""
        # 土日は基本いる（90%）
        if is_weekend():
            return renpy.random.random() < 0.90

        # 平日の時間帯別
        time = game_date["time"]
        if time == "morning":
            # 朝は講義で不在が多い（40%で在宅）
            return renpy.random.random() < 0.40
        elif time == "afternoon":
            # 昼は半々（55%で在宅）
            return renpy.random.random() < 0.55
        else:
            # 夜は大体いる（85%で在宅）
            return renpy.random.random() < 0.85


    def check_kana_initiative():
        # v1.4追加: ゲーム終了後はメッセージを送らない
        if flags.get("game_ended", False):
            return

        # Phase 4 Step 2.5: 冷戦中は自発連絡しない
        if cold_war.get("kana_active", False):
            return

        # v1.3追加: 一緒にいるときは送らない
        if (flags.get("kana_at_himo_room", False)
                or location_flags.get("staying_at_kana", False)
                or flags.get("kana_tonight", False)
                or kana.get("met_today", False)):
            return

        global kana

        # last_contactが2以上かつ当日未接触で発火
        if kana["last_contact"] < 2:
            return

        # 依存度が高いほど頻繁に来る
        # Phase 4 v1.3: 発火率を下方修正
        depend = kana["dependence"]
        if depend >= 60:
            fire_rate = 0.45    # 旧: 0.60
        elif depend >= 30:
            fire_rate = 0.30    # 旧: 0.40
        else:
            fire_rate = 0.15    # 旧: 0.25

        if renpy.random.random() < fire_rate:
            _pending_events.append(("kana_initiative_event", None))


# ========================================
# カナの自発的連絡
# ========================================

label kana_initiative_event:
    python:
        kana_msgs = [
            ("暇〜。ヒモ太郎も暇？", "casual"),
            ("今日会える？", "meetup"),
            ("なんかいいことあった？", "check"),
            ("ご飯行かない？", "food"),
        ]
        # 依存度が高いと「会いたい」系が増える
        if kana["dependence"] >= 50:
            kana_msgs += [
                ("会いたい", "needy"),
                ("今どこにいる？", "location"),
            ]
        kana_msg, kana_msg_type = renpy.random.choice(kana_msgs)

    "カナからLINEが来た。"
    kana_c "[kana_msg]"

    menu:
        "返信する":
            if kana_msg_type in ["meetup", "food", "needy"]:
                menu:
                    "今夜会おう":
                        $ flags["kana_tonight"] = True
                        $ daily_flags["kana_tonight_source"] = "kana"
                        # v1.3修正: LINEのみなのでlast_contactをリセットしない
                        $ change_trust_kana(1)    # v1.3: 2→1
                    "今日は無理":
                        himo "今日はちょっと"
                        kana_c "そっか〜"
                        $ change_trust_kana(-1)
                        $ kana["last_contact"] = 0
            else:
                himo "まあまあかな"
                kana_c "そっか〜"
                $ kana["last_contact"] = 0
                $ change_trust_kana(1)    # v1.3: 2→1

        "既読スルーする":
            "既読スルーした。"
            $ change_trust_kana(-2)

    return


# ========================================
# K-01: ナンパの成功
# ========================================

label k01_nanpa_success:
    $ log_action("カナ出会い K-01")
    scene bg_placeholder

    kana_c "え、なに？ナンパ？"
    himo "まあ...そんな感じです"
    kana_c "あはは、正直じゃん"

    "屈託のない笑顔だった。"
    "なんか、美咲とは全然違うタイプだな。"

    kana_c "カナ。桜井カナ。大学3年"
    himo "ヒモ太郎。25歳"
    kana_c "無職？笑"
    himo "...まあ"
    kana_c "いいじゃん、自由で"

    "連絡先を交換した。"

    $ kana["trust"] = 15
    $ kana["dependence"] = 0
    $ kana["stage"] = 1
    $ kana_flags["met"] = True
    $ kana_flags["k01_done"] = True

    "こうして、カナと知り合った。"
    "美咲とは全然違う空気。"
    himo "...なんか、新鮮だな"

    return


# ========================================
# カナ宅訪問
# ========================================

label kana_visit:
    # === 冷戦チェック ===
    if cold_war.get("kana_active", False):
        himo "（カナの部屋には行けない。怒ってるし）"
        return

    # v1.6追加: 不在チェック
    python:
        _kana_home = is_kana_available()

    if not _kana_home:
        "カナの部屋に行ったが、いなかった。"

        python:
            _kana_absence_reasons = [
                "カナからLINEが来た。",
                "カナからLINEが来た。",
                "カナからLINEが来た。",
                "カナからLINEが来た。",
            ]
            _kana_absence_msgs = [
                "今日講義あるんだ〜ごめんね",
                "友達と遊んでる！また明日ね",
                "バイト入っちゃった〜",
                "ちょっと出かけてる！夜なら空くかも",
            ]
            _kana_abs_idx = renpy.random.randint(0, len(_kana_absence_msgs) - 1)

        "カナからLINEが来た。"
        kana_c "[_kana_absence_msgs[_kana_abs_idx]]"
        himo "しゃーない"

        # 不在でもカナに会いに行った事実は記録
        $ kana["last_contact"] = 0
        return

    # カナが在宅 → 既存の訪問処理
    scene bg_placeholder

    "カナの部屋に来た。"

    if game_date["time"] == "afternoon":
        "昼間から来られるのは、カナならでは。"

    # v1.5: 訪問回数に応じたセリフ
    python:
        _kana_visit_count = stats.get("kana_visit_count", 0)
        stats["kana_visit_count"] = _kana_visit_count + 1

    if _kana_visit_count == 0:
        kana_c "来た来た！暇だったんだよね〜"
    elif _kana_visit_count <= 3:
        python:
            _kv = renpy.random.choice([
                "来た来た！暇だったんだよね〜",
                "お、来た！待ってたよ",
                "いらっしゃ〜い",
            ])
        kana_c "[_kv]"
    elif _kana_visit_count <= 7:
        python:
            _kv = renpy.random.choice([
                "また来たの？笑 まあ入りなよ",
                "もう合鍵渡そうかな笑",
                "おかえり〜...って違うか",
            ])
        kana_c "[_kv]"
    else:
        python:
            _kv = renpy.random.choice([
                "もうここ半分ヒモ太郎の部屋じゃん",
                "おかえり。...もうおかえりでいいよね",
                "鍵、開けといたよ",
            ])
        kana_c "[_kv]"

    # --- 食事（独立チェック）---
    if not daily_flags["ate_today"]:
        kana_c "ごはん食べた？なんか作るよ"
        menu:
            "食べていく":
                "カナが料理を作ってくれた。"
                kana_c "たいしたもんじゃないけど"
                himo "いや、うまい"
                $ change_stamina(20)
                $ daily_flags["ate_today"] = True
                $ change_trust_kana(3)
                $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1
            "いい、気にしないで":
                himo "大丈夫"
                kana_c "遠慮しなくていいのに"

    # --- シャワー（独立チェック）---
    if player["cleanliness"] < 50:
        kana_c "シャワー使う？タオルあるよ"
        menu:
            "借りる":
                "シャワーを借りた。"
                $ change_cleanliness(30)
                $ change_trust_kana(2)
                $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1
            "いい":
                pass

    # --- 魅力増加（無条件）---
    if player["charm"] < KANA_CHARM_CAP:
        $ change_charm(1)

    # --- Phase 4 Step 3 v1.7: エナタッチ判定（Stage3以上で発生）---
    python:
        _ena_touch_trigger = False
        if kana["stage"] >= STAGE_CLOSE:
            if kana["dependence"] >= 40:
                _ena_touch_trigger = True
            elif renpy.random.random() < 0.5:
                _ena_touch_trigger = True

    if _ena_touch_trigger:
        call kana_daytime_touch

    $ kana["met_today"] = True
    $ reset_contact_kana()
    $ kana_dates_count += 1

    return


# ========================================
# Phase 4 Step 3 v1.7: カナの昼エナタッチ
# ========================================

label kana_daytime_touch:
    python:
        _touch_texts = [
            ("ねえ、まだ帰らないでしょ？", "カナがくっついてきた。"),
            ("暇〜。ヒモ太郎も暇でしょ？", "カナが甘えてきた。"),
            ("ちょっとだけ...いいでしょ？", "カナが離れない。"),
        ]
        _tt = renpy.random.choice(_touch_texts)

    kana_c "[_tt[0]]"
    "[_tt[1]]"

    if energy <= 0:
        menu:
            "そろそろ帰るわ":
                kana_c "え〜...もうちょっといてよ"
                $ change_trust_kana(-2)
                himo "（不満そう...）"

            "嘘でごまかす":
                himo "ちょっと体調悪くて..."
                kana_c "大丈夫？無理しないでね"
                $ change_trust_kana(-1)
    else:
        menu:
            "もうちょっといる":
                "しばらくカナとイチャイチャした。"
                $ energy -= 1
                $ energy_full_days = 0
                $ energy_charm_bonus = 0
                $ change_dependence_kana(5)
                $ stats["ena_touch_count"] = stats.get("ena_touch_count", 0) + 1
                himo "（エナ使っちゃったな...）"

            "そろそろ帰るわ":
                kana_c "え〜、つまんない"
                $ change_trust_kana(-2)

    return


# ========================================
# カナへの連絡
# ========================================

label contact_kana:
    # === 冷戦チェック ===
    if cold_war.get("kana_active", False):
        call cold_war_contact("kana")
        return

    # v1.3修正: LINEのみなのでlast_contactをリセットしない

    "カナにLINEを送った..."

    # Phase 4 v1.1: 閾値を緩和（旧: 40/20 → 新: 25/10）
    if kana["trust"] >= 25:
        "すぐに返信が来た。"
    elif kana["trust"] >= 10:
        "しばらくして返信が来た。"
    else:
        # 信頼10未満でも50%の確率で返信あり
        python:
            kana_responds = renpy.random.random() < 0.50

        if kana_responds:
            "...しばらくして返信が来た。"
        else:
            "既読スルーされた..."
            $ change_trust_kana(-1)
            $ daily_flags["ignored_kana_today"] = True
            "（でも、LINEを送ったことは覚えてくれてるはず）"
            return

    menu:
        kana_c "なに？"

        "雑談する":
            kana_c "暇〜。ヒモ太郎も暇？"
            himo "暇だよ"
            kana_c "じゃあ会おう"
            # v1.6修正: フラグだけ立てる（成功率チェックは夜に移動）
            $ flags["kana_tonight"] = True
            $ daily_flags["kana_tonight_source"] = "player"
            $ change_trust_kana(2)

        "今日会いたいと言う":
            call kana_date_request

        # Phase 4 v1.2: 新メニュー3つ
        "写真送って" if kana["trust"] >= 20:
            himo "なんか写真送ってよ"
            kana_c "え〜、なに？自撮り？"
            himo "なんでもいいよ"
            kana_c "しょうがないな〜"
            "カナが自撮りを送ってきた。"
            kana_c "はい、特別だよ？"
            $ change_charm(2)
            $ change_trust_kana(2)

        "なんか食べたい" if kana["trust"] >= 30:
            himo "腹減った〜。なんか食べたい"
            kana_c "え、私に言う？笑"
            kana_c "しょうがないな、作ってあげるから来なよ"
            "カナの部屋で食事をご馳走になった。"
            $ change_stamina(15)
            $ daily_flags["ate_today"] = True
            $ change_trust_kana(3)
            $ kana["met_today"] = True
            $ reset_contact_kana()

        "甘える" if kana["trust"] >= 40 and kana["dependence"] >= 20:
            himo "カナ〜、会いたい〜"
            kana_c "...なにそれ、キモい"
            kana_c "...でも嬉しい"
            $ change_trust_kana(5)
            $ change_dependence_kana(5)
            $ flags["kana_tonight"] = True
            $ daily_flags["kana_tonight_source"] = "player"

    return


# ========================================
# カナデート誘い・デート
# ========================================

label kana_date_request:
    # === 冷戦チェック ===
    if cold_war.get("kana_active", False):
        kana_c "...今無理"
        himo "（怒ってる...当たり前か）"
        return

    if daily_flags.get("ignored_kana_today", False):
        himo "今日はやめとこう"
        return

    if kana["met_today"]:
        kana_c "今日もう会ったじゃん"
        return

    python:
        trust = kana["trust"]
        # カナは美咲より会いやすい（暇な大学生）
        if trust >= 50:
            success_rate = 0.90
        elif trust >= 35:
            success_rate = 0.75
        elif trust >= 20:
            success_rate = 0.65
        elif trust >= 15:
            success_rate = 0.50
        else:
            success_rate = 0.30

        can_meet = renpy.random.random() < success_rate

    if not can_meet:
        kana_c "今日はちょっと〜、バイトあるんだよね"
        himo "そっか"
        return

    if game_date["time"] == "night":
        call kana_date_with_location
    else:
        kana_c "夜なら大丈夫だよ"
        $ flags["kana_tonight"] = True
        $ daily_flags["kana_tonight_source"] = "player"
        himo "了解"

    return


label kana_date:
    $ kana_dates_count += 1
    $ log_action("カナデート", "累計" + str(kana_dates_count) + "回")
    scene bg_placeholder

    "カナと会った。"
    kana_c "ヒモ太郎〜！"

    "いつも元気だな。"

    $ kana["met_today"] = True
    $ reset_contact_kana()
    $ change_stamina(-10)

    # 魅力値微増（上限70）
    if player["charm"] < KANA_CHARM_CAP:
        $ change_charm(1)

    menu:
        "何を話す？"

        "カナの話を聞く":
            kana_c "最近さ、TikTokにハマってて〜"
            himo "へー"
            kana_c "フォロワー増えてきた！"
            himo "すごいじゃん"
            "あんまりよくわからないけど、楽しそうだった。"
            $ change_trust_kana(5)
            $ change_dependence_kana(3)

        "一緒にいるだけ":
            "特に何も話さなかった。"
            "でも、それでいい空気だった。"
            $ change_trust_kana(3)
            $ change_dependence_kana(2)

        "自分の話をする":
            himo "最近暇でさ〜"
            kana_c "いいじゃん、一緒に暇しよ"
            "カナはこういうのを責めない。"
            $ change_trust_kana(4)
            $ change_dependence_kana(3)
            $ himo_aptitude["easy_choices"] += 1

    # 食事（ate_todayが未設定なら）
    if not daily_flags["ate_today"]:
        kana_c "ごはん、どっか行く？"
        himo "いいな"
        "カナが安い定食屋に連れて行ってくれた。"
        "割り勘だったが、安かった。"
        $ change_money(-600)
        $ change_stamina(15)
        $ daily_flags["ate_today"] = True

    return


# ========================================
# K-02: インスタのストーリー
# ========================================

label k02_insta_story:
    scene bg_placeholder

    "スマホを見ていると、カナのインスタのストーリーが上がっていた。"
    "今いる場所の写真。"
    "...繁華街だ。美咲と会うことが多いエリア。"

    himo "（あ、これまずいかも）"
    himo "（美咲に見られたら...）"

    "カナはインスタのフォロワーが5万人いる。"
    "誰でも見られる。"

    menu:
        "どうする？"

        "気にしない":
            himo "まあ、バレないだろ"
            $ kana_flags["sns_risk"] += 5
            $ himo_aptitude["easy_choices"] += 1

        "カナに非公開にしてもらうよう頼む":
            himo "（でも、なんて言えば...）"
            himo "（怪しまれるか）"
            "結局、何も言えなかった。"
            $ kana_flags["sns_risk"] += 3

        "自分のアカウントを非公開にする":
            himo "とりあえず、俺のアカウントを非公開にしておくか"
            "応急処置程度だが、気休めにはなる。"
            $ kana_flags["sns_risk"] += 1

    "SNS経由でバレるリスクが、じわじわ高まっている気がした。"

    $ kana_flags["k02_done"] = True
    return


# ========================================
# K-03: お金ない自慢
# ========================================

label k03_money_talk:
    scene bg_placeholder

    "カナと話していると、突然こんなことを言い出した。"

    kana_c "ねえ、今月マジで金ないんだけど"
    himo "え"
    kana_c "仕送り使い果たしてさ〜、バイトも先月サボりすぎて"
    kana_c "笑えるよね"

    "笑えない。"
    himo "（美咲と真逆だな）"

    menu:
        "大変だな（同情する）":
            himo "それは大変だな"
            kana_c "でしょ〜。ヒモ太郎も金ないんだっけ？"
            himo "俺も大概だよ"
            kana_c "じゃあ二人で貧乏同盟だ！"
            "なんか、妙な連帯感が生まれた。"
            $ change_trust_kana(8)
            $ change_dependence_kana(5)

        "少し渡す（1000円）" if can_afford(1000):
            himo "ちょっとだけど"
            kana_c "え、いいの？！"
            himo "まあ、俺も余裕ないけど"
            kana_c "ありがと〜！好きだわヒモ太郎"
            $ change_money(-1000)
            $ change_trust_kana(15)
            $ change_dependence_kana(10)

        "俺も金ない（正直に言う）":
            himo "俺も同じ状況だよ"
            kana_c "え、マジで？！"
            kana_c "じゃあどうやって生きてんの？"
            himo "...なんとかなってる"
            kana_c "謎すぎる。でもなんかウケる"
            $ change_trust_kana(10)
            $ himo_aptitude["honest_moments"] += 1

    "カナとお金の話をした。"
    "美咲とのお金の話とは、全然違う空気だった。"

    $ kana_flags["k03_done"] = True
    return


# ========================================
# v1.3追加: カナ「推しの人」到達イベント（ルート別演出）
# ========================================

label kana_oshi_event(route):
    scene bg_placeholder

    if route == "A":
        "何度も会ううちに、カナとの時間が当たり前になってきた。"
        kana_c "ヒモ太郎って、なんか特別だよね"
        himo "そうか？"
        kana_c "うん。推しって感じ"
        himo "推し..."
        "なんか変な感じだけど、悪くない。"

    elif route == "B":
        "カナのインスタのストーリーに、俺の後ろ姿が映っていた。"
        "'今日も会ってる人'"
        "コメントが100件以上ついていた。"
        kana_c "フォロワーに紹介しちゃった。ヒモ太郎のこと、推しって言っといたから"
        himo "え"
        kana_c "ダメだった？"
        himo "...まあ、いいけど"

        # ルートB: 美咲へのバレリスクが上昇
        $ kana_flags["sns_risk"] += 10
        $ add_suspicion("sns_exposure")
        $ renpy.notify("SNSでの露出が増えた。美咲にバレるリスクが高まっている。")
        $ log_notify("SNSでの露出が増えた。美咲にバレるリスクが高まっている。")

    elif route == "C":
        "気づけば、カナのことをよく考えるようになっていた。"
        kana_c "なんか、最近ヒモ太郎のこと推しって思ってる"
        himo "は？"
        kana_c "褒めてるんだけど"
        himo "...そうか"

    return


# ========================================
# K-05: 「俺のこと好き？」
# ========================================

label k05_do_you_like_me:
    scene bg_placeholder

    "カナとの時間が増えてきた頃。"
    "ふと、カナが真顔になった。"

    kana_c "ねえ、ヒモ太郎"
    kana_c "私のこと、好き？"

    himo "..."

    "急にどうしたんだ。"
    "カナはいつもの軽い感じじゃなかった。"

    menu:
        "好きだよ":
            himo "好きだよ"
            kana_c "...ほんと？"
            himo "ほんと"
            kana_c "へへ、よかった"
            "なんか、あっさりしてるけど、それがカナらしかった。"
            $ change_trust_kana(10)
            $ change_dependence_kana(15)
            $ flags["k05_accepted"] = True

        "まあ、嫌いじゃない":
            himo "嫌いじゃないよ"
            kana_c "なにそれ笑"
            kana_c "まあいいか"
            "カナは深く追及しなかった。"
            $ change_trust_kana(5)
            $ change_dependence_kana(8)
            $ flags["k05_ambiguous"] = True

        "正直に言えない":
            himo "...難しい質問だな"
            kana_c "なにそれ、ウケる"
            kana_c "まあ、逃げてるってことは嫌いじゃないってことにしとく"
            $ change_trust_kana(3)
            $ change_dependence_kana(5)

    $ kana_flags["k05_done"] = True

    # v1.5修正: ゲーム終了処理を削除。K-05後の余韻テキストを追加
    "カナとの関係は、新しい段階に入った。"
    "でも、まだ月末まで日がある。"
    himo "（...どうなるんだろ、この先）"

    return


# ========================================
# 体験版エンドシーン
# ========================================

label demo_end_scene:
    scene bg_placeholder

    "しばらくして、カナがまた口を開いた。"

    kana_c "...ねえ、ほんとに私だけ？"

    himo "......"

    "なんて答えればいい。"

    kana_c "まあいいけど。"
    kana_c "あ、そういえばさ"
    kana_c "麗子さんって人、ヒモ太郎のこと知ってるって言ってたよ？"

    himo "麗子？誰だそれ"

    kana_c "私も知らない。なんか大人っぽい感じの人。"
    kana_c "ヒモ太郎のこと、「面白い」って言ってたって聞いたけど"

    himo "...誰だよ"

    "心当たりが、ない。"
    "ないはずなのに、なぜか嫌な予感がした。"

    scene bg_placeholder with fade

    "暗転。"

    centered "「俺のヒモ生活は、まだ始まったばかりだった」"

    pause 2.0

    centered "{size=40}体験版 END{/size}"
    centered "製品版へ続く"

    pause 1.0

    $ log_action("体験版END")
    $ export_debug_log()
    $ flags["game_ended"] = True
    $ _ending_type = "demo"

    return


# ========================================
# Phase 4 Step 2: カナの泊まりイベント
# ========================================

label kana_stay_offer:
    # === 冷戦チェック ===
    if cold_war.get("kana_active", False):
        return

    # カナデート後に呼ばれる。条件: 夜のデート＋信頼30以上
    if game_date["time"] != "night" or kana["trust"] < 30:
        return

    # === v1.1: ヒモ太郎の部屋デートの場合は別ルート ===
    if daily_flags.get("date_location", "") == "himo_room":
        call kana_stay_at_himo_room
        return

    # === v1.4追加: カナの部屋以外からの導線テキスト ===
    python:
        _date_loc = daily_flags.get("date_location", "")

    if _date_loc in ["cafe", "karaoke", "campus"]:
        # v1.2修正: 訪問歴で導線テキストを分岐
        python:
            _kana_visit_count = stats.get("kana_visit_count", 0)

        if _kana_visit_count == 0:
            "夜も遅くなってきた。"
            kana_c "ねー、うちこの近くなんだけど..."
            "カナの部屋に寄ることになった。"
        else:
            python:
                _transition = renpy.random.choice([
                    ("夜も遅くなってきた。", "カナの部屋に行こっか"),
                    ("終電の時間が近い。", "うち寄ってく？"),
                    ("夜も更けてきた。", "帰るの面倒じゃない？ うち来れば？"),
                ])
                _t1, _t2 = _transition
            "[_t1]"
            kana_c "[_t2]"

    # === 以下、カナの部屋での泊まり（既存）===
    # 依存度で誘い方が変わる
    if kana["dependence"] >= 50:
        kana_c "今日泊まってくよね？"
        # 依存高: 半強制的
    elif kana["dependence"] >= 30:
        kana_c "泊まってく？"
    else:
        kana_c "もし良かったら...泊まってく？"

    menu:
        "泊まる":
            call kana_stay_event
            return

        "帰る":
            call kana_stay_decline
            return


label kana_stay_event:
    "カナの部屋に泊まることにした。"

    $ stats["kana_stayed_over"] = stats.get("kana_stayed_over", 0) + 1
    $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1

    # 恩恵
    $ change_stamina(KANA_STAY_STAMINA)
    $ change_cleanliness(KANA_STAY_CLEANLINESS)
    $ change_trust_kana(KANA_STAY_TRUST)
    $ change_dependence_kana(KANA_STAY_DEPENDENCE)
    $ daily_flags["ate_today"] = True

    # 泊まりフラグ（翌朝消費用）— location_flags を使う（既存定義と統一）
    $ location_flags["staying_at_kana"] = True
    # v1.4追加: 美咲の翌朝フラグをクリア（排他制御）
    $ flags["misaki_sunday_morning"] = False
    $ location_flags["staying_at_misaki"] = False

    # === Phase 4 Step 3: えなマッチ ===
    call ena_check("kana")

    kana_c "...えへへ"
    "カナが幸せそうに笑った。"

    # v1.2修正: 泊まり回数で匂わせテキストを分岐
    python:
        _stay_count = stats.get("kana_stayed_over", 0)

    if _stay_count <= 1:
        himo "（...なんか、こういうのもいいな）"
    elif _stay_count <= 3:
        kana_c "...また泊まりに来てね"
        himo "（カナといると、なんか楽だな）"
    else:
        kana_c "...昨日、ありがとう"
        kana_c "また泊まりに来てね"
        himo "（泊まるたびに『期待』されてる気がする...）"
        himo "（まあ、今はいっか）"

    # 翌朝の演出用フラグ
    $ flags["kana_morning_after"] = True

    return


label kana_stay_decline:
    # 帰る場合。依存度で反応が変わる
    if kana["dependence"] >= 60:
        kana_c "...なんで？"
        "カナの声が少し震えている。"
        $ change_trust_kana(-5)
        $ suspicion["kana"] = suspicion.get("kana", 0) + 2

        # ご機嫌取りQTE発動（依存60以上で断った場合）
        if not daily_flags.get("kana_mood_resolved", False):
            call gokiragen_qte_start
    elif kana["dependence"] >= 30:
        kana_c "え〜、帰るの？"
        $ change_trust_kana(-3)
    else:
        kana_c "そっか〜"
        $ change_trust_kana(-1)

    return


# ========================================
# Phase 4 Step 2: カナ版疑念イベント
# ========================================

label kana_doubt_event:
    scene bg_placeholder

    "カナと過ごしている時、急にカナが黙り込んだ。"

    kana_c "...ねえ"
    himo "ん？"

    kana_c "私のこと、都合のいい女だと思ってない？"

    himo "え？"

    kana_c "ご飯も作ったし、泊めてあげたし"
    kana_c "でもヒモ太郎は...私のこと大事にしてくれてる？"

    "カナの目が潤んでいる。"

    kana_c "前の彼氏もそうだった"
    kana_c "優しいフリして、利用してただけ"

    kana_c "ヒモ太郎は...違うよね？"

    menu:
        "何と答える？"

        "正直に認める":
            himo "...正直に言うと、甘えすぎてた"
            kana_c "...最低"

            "カナが泣き出した。"

            himo "でも、お前のこと嫌いじゃない。それは本当"
            kana_c "...嘘"
            himo "嘘じゃない"

            "長い沈黙。"

            kana_c "...正直に言ってくれたから、許す"
            kana_c "でも次やったら、もう知らないから"

            $ change_trust_kana(-15)
            $ suspicion["kana"] = 0     # 疑念リセット
            $ himo_aptitude["honest_moments"] += 2
            $ flags["kana_doubt_event_done"] = True

        "ご機嫌取りQTE（3段階・高難度）":
            call gokiragen_qte_doubt
            $ flags["kana_doubt_event_done"] = True

        "逆ギレする":
            himo "はあ？ 俺が何したってんだよ"
            kana_c "..."

            "カナが黙った。目に涙が溜まっている。"

            kana_c "...最低"

            "カナがスマホを取り出した。"

            $ change_trust_kana(-25)
            $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 10
            $ flags["kana_doubt_event_done"] = True

            himo "（やばい、SNSに書かれるかも...）"

    return


# ========================================
# Phase 4 Step 2 v1.1: カナがヒモ太郎の部屋に泊まる
# ========================================

label kana_stay_at_himo_room:
    # カナがヒモ太郎の部屋に泊まりたがる
    "夜も更けてきた。"

    if kana["dependence"] >= 50:
        kana_c "ねえ、今日泊まっていい？ ...っていうか泊まるけど"
    elif kana["dependence"] >= 30:
        kana_c "今日泊まっていい？"
    else:
        kana_c "...帰るの遅くなっちゃったし、泊まっていい？"

    menu:
        "いいよ":
            call kana_stay_at_himo_room_event
            return

        "今日は帰ってくれ":
            call kana_stay_at_himo_decline
            return


label kana_stay_at_himo_room_event:
    # === Phase 4 Step 2.5: 痕跡チェック ===
    if flags.get("misaki_stayed_himo_this_week", False) and not flags.get("evidence_trace_done_this_week", False):
        call evidence_trace_event("kana")
        $ flags["evidence_trace_done_this_week"] = True
        if cold_war.get("kana_active", False):
            # 嘘パズル失敗→冷戦突入→帰った
            return

        # === v1.3追加: 嘘パズル成功でも空気は変わっている ===
        "..."
        "気まずい沈黙が流れた。"
        kana_c "..."

        menu:
            "「...泊まってく？」":
                himo "...泊まってけよ。こんな時間だし"
                kana_c "...うん"
                "カナは小さくうなずいた。"
                "さっきまでの空気とは違う。"
                # フラグ設定は通常通り行うが、泊まりテキストは短縮
                $ stats["kana_stayed_over"] = stats.get("kana_stayed_over", 0) + 1
                $ stats["kana_stayed_himo_room"] = stats.get("kana_stayed_himo_room", 0) + 1
                $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1
                $ flags["kana_stayed_himo_this_week"] = True
                $ change_stamina(20)
                $ change_trust_kana(1)
                $ change_dependence_kana(KANA_STAY_DEPENDENCE + 3)
                $ flags["kana_at_himo_room"] = True
                $ flags["kana_himo_room_morning"] = True
                # 排他制御
                $ flags["misaki_sunday_morning"] = False
                $ location_flags["staying_at_misaki"] = False
                "..."
                "その夜は、あまり話さなかった。"
                return

            "「...帰るか？」":
                himo "...送ろうか"
                kana_c "...いい。一人で帰れる"
                "カナが静かに出ていった。"
                $ change_trust_kana(-3)
                return

    # === 以下、痕跡チェックなしの通常フロー ===
    himo "いいよ、泊まってけ"
    kana_c "やった！"

    "カナがヒモ太郎の部屋に泊まることになった。"
    "狭い部屋に二人。"

    $ stats["kana_stayed_over"] = stats.get("kana_stayed_over", 0) + 1
    $ stats["kana_stayed_himo_room"] = stats.get("kana_stayed_himo_room", 0) + 1
    $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1
    $ flags["kana_stayed_himo_this_week"] = True

    # 恩恵（カナの部屋より少ない。自分の部屋なので清潔感回復なし）
    $ change_stamina(20)
    $ change_trust_kana(KANA_STAY_TRUST)
    $ change_dependence_kana(KANA_STAY_DEPENDENCE + 3)   # ヒモ太郎の部屋＝距離が近い→依存UP多め

    # 泊まりフラグ
    $ flags["kana_at_himo_room"] = True
    # v1.4追加: 美咲の翌朝フラグをクリア（排他制御）
    $ flags["misaki_sunday_morning"] = False
    $ location_flags["staying_at_misaki"] = False

    # === 冷戦悪化チェック ===
    if cold_war.get("misaki_active", False):
        $ escalate_cold_war("misaki")
        himo "（...美咲にバレたら、もう終わりだな）"

    # === Phase 4 Step 3: えなマッチ ===
    call ena_check("kana")

    kana_c "...ヒモ太郎の部屋、狭いけど落ち着く"

    # 翌朝演出用フラグ
    $ flags["kana_himo_room_morning"] = True

    return


label kana_stay_at_himo_decline:
    himo "今日はちょっと..."

    if kana["dependence"] >= 60:
        kana_c "...なんで？ 嫌なの？"
        "カナの声が震えている。"
        $ change_trust_kana(-5)
        $ suspicion["kana"] = suspicion.get("kana", 0) + 2

        if not daily_flags.get("kana_mood_resolved", False):
            call gokiragen_qte_start
    elif kana["dependence"] >= 30:
        kana_c "え〜...分かった"
        $ change_trust_kana(-3)
    else:
        kana_c "そっか、じゃあ帰るね"
        $ change_trust_kana(-1)

    return
