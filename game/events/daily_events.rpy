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


# ========================================
# Phase 3 v1.1: 強制朝イベント
# ========================================

label check_forced_morning_event:

    # イベント1: 日曜朝・美咲宅でイチャイチャして昼になる
    if flags.get("misaki_sunday_morning", False):
        $ flags["misaki_sunday_morning"] = False
        call misaki_sunday_morning_icha
        $ flags["morning_consumed"] = True
        return

    # イベント2: 疲労MAX → 昼まで寝てしまう
    if player["stamina"] <= 10:
        call event_oversleep
        $ flags["morning_consumed"] = True
        return

    # イベント3: 美咲 or カナから朝の電話（依存度が高い場合）
    python:
        import random
        phone_call_chance = False

        if misaki["dependence"] >= 70 and misaki["last_contact"] >= 2:
            if random.random() < 0.30:
                phone_call_chance = "misaki"

        if kana_flags["met"] and kana["dependence"] >= 50 and kana["last_contact"] >= 2:
            if random.random() < 0.25:
                phone_call_chance = "kana"

    if phone_call_chance == "misaki":
        call morning_phone_misaki
    elif phone_call_chance == "kana":
        call morning_phone_kana

    return


label misaki_sunday_morning_icha:
    scene bg_placeholder

    "日曜の朝。美咲の部屋。"
    "カーテン越しに柔らかい光が差し込んでいた。"

    misaki_c "...おはよう"
    himo "おう、おはよ"

    "美咲がくっついてきた。"
    misaki_c "今日、どこか行く？"
    himo "どうしよっか"

    "結局、昼まで部屋でゆっくりした。"

    $ change_stamina(20)
    $ change_trust(5)
    $ change_dependence(8)
    $ reset_contact()
    $ daily_flags["ate_today"] = True

    "気づいたら昼になっていた。"
    "（朝の時間が消えた）"

    return


label event_oversleep:
    scene bg_placeholder

    "――朝――"
    "体が重い。"
    himo "（疲れすぎてる...）"
    himo "（ちょっとだけ...）"

    "気づいたら昼になっていた。"

    $ change_stamina(30)
    $ himo_aptitude["easy_choices"] += 1

    himo "やばい、昼じゃん"

    return


label morning_phone_misaki:
    scene bg_placeholder

    "朝から美咲の電話が鳴った。"

    himo "もしもし"
    misaki_c "おはよう。昨日、連絡なかったから"
    himo "あ、ごめん寝てた"
    misaki_c "...そうなんだ"

    "少し沈黙。"

    menu:
        "フォローする":
            himo "夜に連絡するから"
            misaki_c "...うん、待ってる"
            $ change_trust(3)
            $ flags["misaki_tonight"] = True
            # v1.3修正: 電話のみなのでreset_contactを呼ばない

        "適当にごまかす":
            himo "バタバタしててさ〜"
            misaki_c "...そっか"
            "美咲は何も言わなかった。"
            $ add_suspicion("vague_answer")
            # v1.3修正: 電話のみなのでreset_contactを呼ばない

    return


label morning_phone_kana:
    scene bg_placeholder

    "朝から着信。カナだ。"

    himo "もしもし"
    kana_c "おはよ〜！昨日連絡なかったじゃん"
    himo "悪い悪い"
    kana_c "今日どうする？暇？"

    menu:
        "今日会おう":
            himo "夜なら"
            kana_c "やった！じゃあ夜ね"
            $ flags["kana_tonight"] = True
            # v1.3修正: 電話のみなのでlast_contactをリセットしない
            $ change_trust_kana(3)

        "今日は無理":
            himo "今日はちょっと用事あって"
            kana_c "え〜、また？"
            $ change_trust_kana(-3)
            # v1.3修正: 電話のみなのでlast_contactをリセットしない

    return


# ========================================
# Phase 3 v1.1: 強制昼イベント
# ========================================

label check_forced_afternoon_event:
    python:
        import random

    # イベント1: ナンパ解禁トリガー（カナ未出会い・魅力35以上・5日目以降）
    if (not kana_flags["met"]
        and not flags.get("nanpa_unlocked", False)
        and player["charm"] >= 35
        and game_date["day"] >= 5):
        call event_nanpa_unlock
        return

    # イベント2: 町中でカナと偶然遭遇（カナ出会い済み・信頼50未満・ランダム）
    if (kana_flags["met"]
        and kana["trust"] < 50
        and not kana["met_today"]
        and random.random() < 0.15):
        call event_kana_encounter
        $ flags["afternoon_consumed"] = True
        return

    return


label event_nanpa_unlock:
    "街を歩いていると、前を歩く男が女の子に声をかけていた。"
    "...ナンパだ。"

    "女の子は笑顔で立ち止まった。"
    "連絡先を交換している。"

    himo "..."
    himo "（俺でも、できるかな）"

    $ flags["nanpa_unlocked"] = True

    "なんか、やってみたくなった。"
    "ナンパができるようになった。"

    # そのままナンパを試みるか選択
    menu:
        "試してみる":
            call nanpa_event

        "今日はやめとく":
            himo "まあ、今日はいいか"

    $ flags["afternoon_consumed"] = True
    return


label event_kana_encounter:
    scene bg_placeholder

    "街を歩いていると、見覚えのある顔が目に入った。"
    "カナだ。"

    kana_c "あ、ヒモ太郎！なにしてんの？"
    himo "散歩"
    kana_c "暇人じゃん。一緒にいていい？"

    "断る理由もないので、そのままカナと合流した。"

    $ kana["met_today"] = True
    $ kana["last_contact"] = 0

    # カナの恩恵（食事）
    kana_c "お腹減った。なんか食べよ"
    "近くのカフェに入った。"
    "カナがおごってくれた。"

    $ change_stamina(15)
    $ change_trust_kana(8)
    $ change_dependence_kana(4)
    $ daily_flags["ate_today"] = True

    "思わぬ形でカナと過ごすことになった。"
    "（昼の時間が消費された）"

    return


label afternoon_street:
    scene bg_placeholder

    # v1.1追加: 昼の強制イベントチェック
    call check_forced_afternoon_event

    if flags.get("afternoon_consumed", False):
        $ flags["afternoon_consumed"] = False
        return

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
        "【街】何をする？"

        "買い物をする":
            call shopping_event

        "パチンコに行く":
            call pachinko_event

        "ナンパしてみる" if (flags["nanpa_unlocked"] and not kana_flags["met"]):
            call nanpa_event

        "求人情報を見る":
            call check_job_hint

        "自宅に戻る":
            himo "帰るか"

    return


# ========================================
# Phase 3: ナンパシステム
# ========================================

label nanpa_event:
    $ log_action("ナンパ")
    scene bg_placeholder

    "繁華街をぶらぶらしていた。"

    python:
        import random
        charm = player["charm"]
        if charm >= 70:
            success_rate = 0.60
        elif charm >= 50:
            success_rate = 0.40
        elif charm >= 35:
            success_rate = 0.25
        else:
            success_rate = 0.10

        nanpa_success = random.random() < success_rate

    if not nanpa_success:
        "声をかけてみたが、うまくいかなかった。"
        himo "...まあ、そんなもんか"
        $ change_stamina(-5)
        return

    # 成功
    "前を歩く女の子に声をかけた。"
    himo "あの、ちょっといいですか"

    "振り返ったのは、明るそうな女の子だった。"

    jump k01_nanpa_success


label shopping_event:
    scene bg_placeholder
    "街の店を見て回った。"

    menu:
        "何を買う？"

        "服を見る":
            if not can_afford(3000):
                himo "...欲しいけど、今は無理だな"
                return

            "服屋に入った。"
            himo "ちょっといい服買っとくか"
            $ change_money(-3000)
            $ change_charm(5)
            himo "おっ、いい感じ"

        "何も買わない":
            himo "まあ、今日はいいか"

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


# ========================================
# Phase 2 v2.2: パチンコシステム
# ========================================

label pachinko_event:
    $ log_action("パチンコ")
    scene bg_placeholder

    "繁華街のパチンコ店に入った。"
    "平日昼間でも、それなりに人がいる。"
    himo "まあ、ちょっとだけな"

    # 掛け金選択
    menu:
        "いくら賭ける？"

        "1,000円":
            $ pachinko_bet = 1000

        "3,000円":
            $ pachinko_bet = 3000

        "5,000円" if can_afford(5000):
            $ pachinko_bet = 5000

    # 所持金チェック
    if not can_afford(pachinko_bet):
        himo "...財布の中身が足りない"
        himo "やめとくか"
        return

    $ change_money(-pachinko_bet)

    "台に向かった。"

    # 長丁場判定（20%）
    python:
        is_long_session = renpy.random.random() < 0.20

    if is_long_session:
        "なんか、ハマってしまった。"
        himo "もうちょっとだけ..."
        himo "あ、もうちょっとだけ..."
        "気づいたら夕方になっていた。"

        # 夜のターンも消費
        $ advance_time()

        # 美咲との約束チェック
        if flags.get("misaki_tonight", False):
            "スマホを見ると、美咲からのLINEが溜まっていた。"
            "'今日会う約束だったよね？'"
            "'どこにいるの？'"
            himo "...やばい"
            $ change_trust(-8)
            $ change_dependence(5)
            $ add_suspicion("contact_delay")
            "長丁場のせいで、約束を破ってしまった。"
        else:
            "気づいたら夕方になっていたが、今日は特に約束もなかった。"
            himo "...まあいっか"
    else:
        "1〜2時間で切り上げた。"

    # 結果抽選
    python:
        roll = renpy.random.random()
        if roll < 0.20:
            pachinko_result = "win"
            multiplier = renpy.random.uniform(2.0, 5.0)
            pachinko_gain = int(pachinko_bet * multiplier)
        elif roll < 0.50:
            pachinko_result = "draw"
            pachinko_gain = pachinko_bet
        else:
            pachinko_result = "loss"
            pachinko_gain = 0

    if pachinko_result == "win":
        "大当たりが来た。"
        himo "よっしゃ！"
        "¥[pachinko_gain:,]を獲得した。"
        $ change_money(pachinko_gain)
        $ stats["pachinko_wins"] += 1
        $ stats["pachinko_profit"] += pachinko_gain - pachinko_bet
        $ himo_aptitude["easy_choices"] += 1

    elif pachinko_result == "draw":
        "なんとかプラマイゼロで終わった。"
        himo "まあ、負けなかっただけいいか"
        $ change_money(pachinko_gain)

    else:
        "全部飲まれた。"
        himo "...まあしゃーない"

        if player["money"] < 3000:
            "（残り少ない...）"
            "（明日の飯代、大丈夫かな）"
            himo "まあ何とかなるっしょ"

        $ stats["pachinko_losses"] += 1
        $ stats["pachinko_profit"] -= pachinko_bet
        $ himo_aptitude["easy_choices"] += 1

    # スタミナ消費
    $ change_stamina(-20)

    return
