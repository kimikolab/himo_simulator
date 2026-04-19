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
            # v1.2追加
            ("知り合い・翔太", "『起業して半年、やっと黒字化』", "positive"),
            ("同級生・あかり", "『第一子誕生！育休中です』", "milestone"),
            ("先輩・大和", "『海外赴任決まりました』", "positive"),
            ("バイト仲間・ケンタ", "『やっと正社員なれた〜泣』", "neutral"),
        ]

        # v1.2: 前回表示した投稿者を除外して重複防止
        last_sns = flags.get("last_sns_poster", "")
        available = [p for p in sns_posts if p[0] != last_sns]
        if not available:
            available = sns_posts
        post = renpy.random.choice(available)
        poster, content, tone = post
        flags["last_sns_poster"] = poster

    "[poster]の投稿:"
    "[content]"

    # v1.5: SNS反応バリエーション
    if tone == "positive":
        python:
            _sns_reaction = renpy.random.choice([
                ("おー、すげえじゃん", "でも大変そうだな"),
                ("へー...頑張ってんな", "俺には関係ないけど"),
                ("マジか、同い年なのにな", "...まあ人は人だ"),
                ("すげえな", "俺とは別の世界の話だわ"),
            ])
        himo "[_sns_reaction[0]]"
        himo "[_sns_reaction[1]]"
        $ stats["optimistic_choices"] += 1

    elif tone == "neutral":
        python:
            _sns_reaction = renpy.random.choice([
                "ローンとか責任とか、色々背負うんだな",
                "へー...まあ俺は俺だし",
                "ふーん、みんな色々あるんだな",
                "...俺もなんかしないとな。まあ明日から",
                "ふーん。（スクロール）",
            ])
        himo "[_sns_reaction]"
        $ stats["optimistic_choices"] += 1
        $ himo_aptitude["avoided_work"] += 1

    elif tone == "relatable":
        python:
            _sns_reaction = renpy.random.choice([
                ("わかる〜", "...って、俺バイトないんだった"),
                ("それな", "気楽が一番だよな"),
                ("分かるわ〜", "俺もそんな感じ。いやもっとひどいか"),
            ])
        himo "[_sns_reaction[0]]"
        himo "[_sns_reaction[1]]"

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
    # v1.4追加: 翌朝フラグの状態をデバッグログ
    $ log_action("MORNING_FLAGS misaki_sunday=" + str(flags.get("misaki_sunday_morning", False)) + " kana_after=" + str(flags.get("kana_morning_after", False)) + " kana_himo=" + str(flags.get("kana_himo_room_morning", False)) + " misaki_himo=" + str(flags.get("misaki_stayed_at_himo", False)))

    # === v1.2修正: 再生するイベントを1つ決定 ===
    $ _morning_event = None

    if flags.get("kana_himo_room_morning", False):
        $ _morning_event = "kana_himo_room_morning_event"

    elif flags.get("kana_morning_after", False):
        $ _morning_event = "kana_morning_after_event"

    elif flags.get("misaki_stayed_at_himo", False):
        $ _morning_event = "misaki_morning_at_himo_room"

    elif flags.get("misaki_sunday_morning", False):
        $ _morning_event = "misaki_sunday_morning_icha"

    # === すべての翌朝フラグを無条件クリア ===
    $ flags["kana_himo_room_morning"] = False
    $ flags["kana_morning_after"] = False
    $ flags["kana_at_himo_room"] = False
    $ location_flags["staying_at_kana"] = False
    $ flags["misaki_stayed_at_himo"] = False
    $ flags["misaki_sunday_morning"] = False
    $ flags["misaki_visit_himo_room"] = False
    $ location_flags["staying_at_misaki"] = False

    # === 決定したイベントを再生 ===
    if _morning_event is not None:
        call expression _morning_event
        $ flags["morning_consumed"] = True
        return

    # Phase 4 v1.3: 前日の約束を破った場合
    if flags.get("misaki_tonight_broken", False):
        $ flags["misaki_tonight_broken"] = False
        "美咲からLINEが来ていた。"
        misaki_c "昨日、会えるって言ってたよね...？"
        himo "あ...ごめん"
        misaki_c "...いいけど"
        $ change_trust(-5)
        $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)

    # イベント2: 疲労MAX → 昼まで寝てしまう
    if player["stamina"] <= 10:
        call event_oversleep
        $ flags["morning_consumed"] = True
        return

    # イベント3: 美咲 or カナから朝の電話（依存度が高い場合）
    # v1.6: 泊まり翌朝イベントが発火した朝はスキップ（_morning_eventで消費済み）
    # v1.6: 冷戦中は催促電話を抑制
    python:
        phone_call_chance = False

        # 泊まり翌朝チェック（フラグはクリア済みだが _morning_event で判定可能）
        _had_overnight = _morning_event is not None

        if (not _had_overnight
                and misaki["dependence"] >= 70 and misaki["last_contact"] >= 2
                and not cold_war.get("misaki_active", False)):
            if renpy.random.random() < 0.30:
                phone_call_chance = "misaki"

        if (not _had_overnight
                and kana_flags["met"] and kana["dependence"] >= 50 and kana["last_contact"] >= 2
                and not cold_war.get("kana_active", False)):
            if renpy.random.random() < 0.25:
                phone_call_chance = "kana"

    if phone_call_chance == "misaki":
        call morning_phone_misaki
    elif phone_call_chance == "kana":
        call morning_phone_kana

    return


# v1.6追加: 美咲がヒモ太郎の部屋に泊まった翌朝
label misaki_morning_at_himo_room:
    scene bg_himo_room

    # テキストバリエーション: 泊まり回数で分岐
    python:
        _misaki_himo_stay = misaki_himo_room_visit_count

    show misaki pajama sleepy with dissolve

    if _misaki_himo_stay <= 1:
        # 1回目
        "朝。隣に美咲がいる。"
        "いつもは美咲の部屋で目が覚めるのに、今日は逆だ。"
        misaki_c "...おはよう"
        himo "おう"
        show misaki pajama smile
        "美咲がキッチンに立った。"
    elif _misaki_himo_stay <= 3:
        # 2〜3回目（プールからランダム）
        python:
            _misaki_wake_set = renpy.random.choice(["A", "B"])
        if _misaki_wake_set == "A":
            "朝。美咲がまだ寝ている。"
            "自分の部屋に美咲がいる。その光景に、慣れてきた。"
            show misaki pajama smile
            misaki_c "...ん、おはよう"
            "美咲がキッチンに立った。"
        else:
            "美咲の目覚ましが鳴った。"
            show misaki pajama surprised
            misaki_c "...うそ、ヒモ太郎の部屋だった"
            himo "おはよ"
            show misaki pajama smile
            misaki_c "...おはよう。会社行かなきゃ...あ、今日休みか"
            "美咲がほっとした顔をして、キッチンに立った。"
    else:
        # 4回以上（プールからランダム）
        python:
            _misaki_wake_set = renpy.random.choice(["A", "B"])
        if _misaki_wake_set == "A":
            "朝。もう驚かない。隣に美咲がいる。"
            show misaki pajama smile
            misaki_c "おはよう"
            himo "おう"
            "自然にキッチンに向かう美咲。もう自分の家みたいだ。"
        else:
            "美咲が先に起きて、窓を開けていた。"
            show misaki pajama smile
            misaki_c "...いい天気。"
            himo "おはよ"
            misaki_c "コーヒー淹れようか。インスタントだけど"
            himo "助かる"

    # Phase 4 Step 3: 食材による分岐
    # v1.9: 夕食で使った残りで朝食を作れるケース
    if daily_flags.get("groceries_used_dinner", False) and inventory.get("groceries", 0) > 0:
        if inventory["groceries"] == 2:
            misaki_c "昨日の残りでオムレツ作れそう"
        else:
            misaki_c "卵まだ残ってたね。目玉焼き作るね"
        $ change_trust(3)
        $ inventory["groceries"] = 0
        $ daily_flags["ate_today"] = True
    elif not daily_flags.get("groceries_used_dinner", False) and inventory.get("groceries", 0) == 2:
        show misaki pajama surprised
        misaki_c "...これ、私のために買ってたの？"
        himo "まあ、一応"
        show misaki pajama happy
        misaki_c "...ありがとう"
        $ change_trust(5)
        $ inventory["groceries"] = 0
        $ daily_flags["ate_today"] = True
    elif not daily_flags.get("groceries_used_dinner", False) and inventory.get("groceries", 0) == 1:
        misaki_c "ちゃんと買ってたんだ...えらいじゃん"
        $ change_trust(2)
        $ inventory["groceries"] = 0
        $ daily_flags["ate_today"] = True
    else:
        show misaki pajama sad
        misaki_c "何もないね...卵くらいない？"
        himo "コンビニ行くか"
        misaki_c "...もう"
        "結局、2人でコンビニに行って朝食を買った。"
        $ daily_flags["ate_today"] = True

    show misaki pajama happy
    misaki_c "たまにはこういうのもいいね"
    himo "...そうだな"

    $ change_trust(3)
    $ change_dependence(3)
    $ misaki["met_today"] = True
    $ reset_contact()

    return


label misaki_sunday_morning_icha:
    scene bg_misaki_room

    "日曜の朝。美咲の部屋。"
    "カーテン越しに柔らかい光が差し込んでいた。"

    show misaki pajama sleepy with dissolve
    misaki_c "...おはよう"
    himo "おう、おはよ"

    "美咲がくっついてきた。"
    show misaki pajama happy
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
    scene bg_himo_room

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
    scene bg_himo_room

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
    scene bg_himo_room

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
            $ daily_flags["kana_tonight_source"] = "kana"
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

    # イベント1: ナンパ解禁トリガー（カナ未出会い・5日目以降。v1.8: 魅力条件を撤廃）
    if (not kana_flags["met"]
        and not flags.get("nanpa_unlocked", False)
        and game_date["day"] >= 5):
        call event_nanpa_unlock
        return

    # イベント2: 町中でカナと偶然遭遇（カナ出会い済み・信頼50未満・ランダム）
    if (kana_flags["met"]
        and kana["trust"] < 50
        and not kana["met_today"]
        and renpy.random.random() < 0.15):
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
    scene bg_street

    "街を歩いていると、見覚えのある顔が目に入った。"
    "カナだ。"

    show kana happy with dissolve
    kana_c "あ、ヒモ太郎！なにしてんの？"
    himo "散歩"
    kana_c "暇人じゃん。一緒にいていい？"

    "断る理由もないので、そのままカナと合流した。"

    $ kana["met_today"] = True
    $ reset_contact_kana()

    # カナの恩恵（食事）
    show kana smile
    kana_c "お腹減った。なんか食べよ"
    "近くのカフェに入った。"
    "カナがおごってくれた。"

    $ change_stamina(15)
    $ change_trust_kana(8)
    $ change_dependence_kana(4)
    $ daily_flags["ate_today"] = True

    hide kana
    "思わぬ形でカナと過ごすことになった。"
    "（昼の時間が消費された）"

    return


label afternoon_street:
    scene bg_street

    # Phase 4追加: パチンコの誘惑チェック
    if (player["money"] >= 15000
        and game_date["day"] >= 10
        and not flags.get("midgame_pachinko_triggered", False)):
        python:
            _pachinko_tempt = renpy.random.random() < 0.25
        if _pachinko_tempt:
            call midgame_pachinko_temptation

    # Phase 4 v1.2: パチンコに入ったら午後の残りをスキップ
    if flags.get("afternoon_consumed", False):
        $ flags["afternoon_consumed"] = False
        return

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
    scene bg_street

    "繁華街をぶらぶらしていた。"

    # v1.8: カナ未出会い時は65%固定（魅力依存を撤廃。カナとの出会いはストーリー必須イベント）
    # カナ出会い済み後のナンパ（将来拡張用）は魅力依存を残す
    python:
        if not kana_flags["met"]:
            success_rate = 0.65
        else:
            charm = player["charm"] + energy_charm_bonus
            if charm >= 70:
                success_rate = 0.60
            elif charm >= 50:
                success_rate = 0.40
            elif charm >= 35:
                success_rate = 0.25
            else:
                success_rate = 0.10

        nanpa_success = renpy.random.random() < success_rate

    if not nanpa_success:
        # v1.2: ナンパ失敗のセリフバリエーション
        python:
            _nanpa_fail_lines = [
                ("声をかけてみたが、うまくいかなかった。", "...まあ、そんなもんか"),
                ("笑顔で話しかけたが、無視された。", "...つれないな"),
                ("いい感じに話せたけど、連絡先は教えてもらえなかった。", "惜しかったな...多分"),
                ("声をかける前に相手が去っていった。", "タイミングって大事だな"),
                ("話しかけたら彼氏がいると言われた。", "そりゃそうだよな"),
            ]
            _fail_text, _fail_himo = renpy.random.choice(_nanpa_fail_lines)

        "[_fail_text]"
        himo "[_fail_himo]"
        $ change_stamina(-5)
        $ flags["afternoon_consumed"] = True   # v1.5修正: 失敗時も昼ターン消費
        return

    # 成功
    "前を歩く女の子に声をかけた。"
    himo "あの、ちょっといいですか"

    "振り返ったのは、明るそうな女の子だった。"

    $ flags["afternoon_consumed"] = True   # v1.5修正: 成功時も昼ターン消費
    jump k01_nanpa_success


# === Phase 4 Step 3: コンビニ ===
label convenience_store:
    scene bg_convenience_store
    "コンビニに入った。"

    python:
        _is_night = (game_date["time"] == "night")
        _bento_price = 700 if _is_night else 500
        bento_label = "弁当（¥" + str(_bento_price) + "）"

    label _conveni_menu:
    menu:
        "[bento_label]":
            if not can_afford(_bento_price):
                himo "...財布が足りない"
                jump _conveni_menu
            "コンビニ飯で腹を満たした。"
            $ change_money(-_bento_price)
            $ change_stamina(10 if not _is_night else 12)
            $ daily_flags["ate_today"] = True

        "栄養ドリンク（¥1,500）" if energy < energy_max:
            if daily_flags.get("used_energy_drink", False):
                himo "...2本目はさすがにやめとこう"
                jump _conveni_menu
            if not can_afford(1500):
                himo "...高い。今は無理だ"
                jump _conveni_menu
            "栄養ドリンクを手に取った。"
            $ change_money(-1500)
            $ energy += 1
            $ daily_flags["used_energy_drink"] = True
            $ stats["energy_drinks_used"] = stats.get("energy_drinks_used", 0) + 1
            himo "（...効いてくれ）"

        "制汗スプレー（¥300）":
            if not can_afford(300):
                himo "...300円すらない"
                jump _conveni_menu
            "制汗スプレーを買った。"
            $ change_money(-300)
            $ change_cleanliness(10)
            himo "これで少しはマシか"

        "食材（¥800）" if inventory["groceries"] == 0:
            if not can_afford(800):
                himo "...食材すら買えない"
                jump _conveni_menu
            "卵とパンとハムを買った。"
            "コンビニ食材だけど、何もないよりマシだ。"
            $ change_money(-800)
            $ inventory["groceries"] = 1
            $ inventory["groceries_day"] = game_date["day"]
            himo "（これで最低限は何か作れるな）"

        "何も買わずに出る":
            pass

    return


# === Phase 4 Step 3: 街のショップ（旧shopping_event差し替え） ===
label shopping_event:
    scene bg_placeholder
    "ショッピングモールに来た。"

    label _shopping_menu:
    menu:
        "服を見る（¥3,000）":
            if not can_afford(3000):
                himo "...欲しいけど、今は無理だな"
                jump _shopping_menu
            "ちょっといい服を買った。"
            $ change_money(-3000)
            $ change_charm(5)
            himo "おっ、いい感じ"

        "香水を見る（¥2,500）" if inventory.get("perfume_days", 0) <= 0:
            if not can_afford(2500):
                himo "...いい匂いだけど高い"
                jump _shopping_menu
            "香水を買った。"
            $ change_money(-2500)
            $ change_charm(3)
            $ inventory["perfume_days"] = 3
            himo "これでデートもバッチリだな"

        "花束を買う（¥1,500）" if not inventory.get("bouquet", False):
            if not can_afford(1500):
                himo "...花は贅沢か"
                jump _shopping_menu
            "花束を買った。"
            $ change_money(-1500)
            $ inventory["bouquet"] = True
            $ inventory["bouquet_day"] = game_date["day"]
            himo "（次のデートで渡そう）"

        "アクセサリーを買う（¥5,000）" if not inventory.get("accessory", False):
            if not can_afford(5000):
                himo "...5000円は痛い"
                jump _shopping_menu
            "アクセサリーを買った。"
            $ change_money(-5000)
            $ inventory["accessory"] = True
            himo "（喜んでくれるかな）"

        "推しグッズを買う（¥2,000）" if kana_flags["met"] and not inventory.get("kana_goods", False):
            if not can_afford(2000):
                himo "...今は無理だ"
                jump _shopping_menu
            "カナが好きそうなグッズを見つけた。"
            $ change_money(-2000)
            $ inventory["kana_goods"] = True
            himo "（カナ、喜ぶかな）"

        "ウィンドウショッピング":
            "ぶらぶら見て回った。"
            $ change_stamina(-5)
            himo "目の保養にはなったな"

        "何も買わずに帰る":
            pass

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
    "スーパーに来た。"
    "週末だから人が多い。"

    label _weekend_menu:
    menu:
        "食材セット（¥1,000）" if inventory.get("groceries", 0) == 0:
            if not can_afford(1000):
                himo "...食材すら買えないのか"
                jump _weekend_menu
            "卵とか野菜とか、基本的な食材を買った。"
            $ change_money(-1000)
            $ inventory["groceries"] = 1
            $ inventory["groceries_day"] = game_date["day"]
            himo "（これで朝ごはん作れるな）"

        "ちょっといい食材（¥2,000）" if inventory.get("groceries", 0) == 0:
            if not can_afford(2000):
                himo "...贅沢は敵だ"
                jump _weekend_menu
            "ベーコンとかチーズとか、ちょっといい食材を買った。"
            $ change_money(-2000)
            $ inventory["groceries"] = 2
            $ inventory["groceries_day"] = game_date["day"]
            himo "（ちょっと奮発したな）"

        "お菓子を買う":
            python:
                _price = renpy.random.randint(200, 500)
            if not can_afford(_price):
                himo "...お菓子すら"
                jump _weekend_menu
            "お菓子を買った。"
            $ change_money(-_price)
            $ change_stamina(5)
            himo "甘いもの食べたかったんだよな"

        "洗剤を買う（¥400）":
            if not can_afford(400):
                himo "...400円"
                jump _weekend_menu
            "洗剤を買った。"
            $ change_money(-400)
            $ daily_flags["used_detergent"] = True
            himo "ちゃんとしてる感あるな"

        "何も買わずに帰る":
            himo "見るだけにしとこう"

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
    scene bg_pachinko

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


# ========================================
# Phase 4 Step 2: カナ泊まり翌朝イベント
# ========================================

label kana_morning_after_event:
    scene bg_kana_room

    "カナの部屋で目が覚めた。"
    "隣でカナがまだ寝ている。"

    show kana pajama sleepy with dissolve
    kana_c "...んん"
    kana_c "おはよ..."

    $ daily_flags["ate_today"] = True
    $ change_stamina(15)

    # v1.7修正: 泊まり回数で翌朝テキストを3段階分岐
    python:
        _stay_count = stats.get("kana_stayed_over", 0)

    if _stay_count <= 2:
        # 1〜2回目: 初々しい
        show kana pajama smile
        "カナが朝ごはんを作ってくれた。"
        show kana pajama blush
        kana_c "...昨日、ありがとう"
        kana_c "また泊まりに来てね"
        himo "（泊まるたびに『期待』されてる気がする...）"
        himo "（まあ、今はいっか）"
    elif _stay_count <= 5:
        # 3〜5回目: 慣れてきた
        python:
            _km_idx = renpy.random.randint(0, 2)

        if _km_idx == 0:
            show kana pajama smile
            kana_c "朝ごはん、目玉焼きとウインナーでいい？"
            himo "最高"
            kana_c "簡単なやつしか作れないけど"
        elif _km_idx == 1:
            show kana pajama excited
            kana_c "ねー、起きてー"
            "カナがスマホで写真を撮ろうとしている。"
            himo "やめろ"
            show kana pajama pouty
            kana_c "寝顔撮りたかったのに〜"
        else:
            "カナは先に起きて、何かの動画を見ていた。"
            show kana pajama smile
            kana_c "あ、起きた。コーヒー淹れたよ"
            himo "...気が利くな"
        himo "（もう何回目だ、ここ泊まるの）"
        himo "（...慣れてきたな）"
    else:
        # 6回以上: 日常化
        python:
            _km_idx = renpy.random.randint(0, 2)

        if _km_idx == 0:
            "もはや何も言わずに朝食が出てくる。"
            show kana pajama normal
            kana_c "いつもの"
            himo "いつもって何だよ"
            kana_c "目玉焼きとウインナー"
        elif _km_idx == 1:
            "カナはまだ寝ている。"
            "冷蔵庫を開けたら、カナが書いた付箋が貼ってあった。"
            "「パン焼いて食べてね。バター冷蔵庫の奥」"
        else:
            "カナが半分寝ぼけながらくっついてきた。"
            show kana pajama sleepy
            kana_c "...あと5分"
            himo "俺のセリフだろそれ"

    "気づいたら昼になっていた。"
    "（朝の時間が消えた）"

    return


# ========================================
# Phase 4 Step 2 v1.1: カナがヒモ太郎の部屋に泊まった翌朝
# ========================================

label kana_himo_room_morning_event:
    scene bg_himo_room

    # テキストバリエーション: 泊まり回数で3段階分岐
    python:
        _kana_stay = stats.get("kana_stayed_himo_room", 0)

    show kana pajama sleepy with dissolve

    if _kana_stay <= 2:
        # 1〜2回目: 新鮮
        "自分の部屋で目が覚めた。"
        "隣でカナが寝ている。"
        kana_c "...んん...おはよ"
        show kana pajama smile
        "カナがキッチンに立った。"
    elif _kana_stay <= 5:
        # 3〜5回目: 慣れてきた（プールからランダム）
        python:
            _kana_wake_set = renpy.random.choice(["A", "B", "C"])
        if _kana_wake_set == "A":
            "目が覚めると、隣にカナがいた。"
            "いつもの寝息に、慣れてきた。"
            show kana pajama smile
            kana_c "...おはよ"
            "カナが先にキッチンに立っていた。"
        elif _kana_wake_set == "B":
            "カナの寝息で目が覚めた。"
            "毛布を半分取られていた。"
            kana_c "...あと5分"
            himo "（俺のセリフだろそれ）"
            show kana pajama smile
            "結局カナが起きて、キッチンに向かった。"
        else:
            "朝、カナがベッドから落ちかけていた。"
            show kana pajama smile
            kana_c "ぅぁ...起きた？おはよ"
            himo "...先に起きてたのか"
            show kana pajama excited
            kana_c "うん...ヒモ太郎の寝顔撮ろうとしてた"
            himo "やめろ"
    else:
        # 6回以上: 日常化（プールからランダム）
        python:
            _kana_wake_set = renpy.random.choice(["A", "B", "C"])
        if _kana_wake_set == "A":
            "いつの間にか、カナが隣にいるのが普通になった。"
            show kana pajama smile
            kana_c "おはよ〜"
            himo "おう"
            "何も言わなくても、朝が始まる。"
        elif _kana_wake_set == "B":
            "カナはもう起きていた。"
            "コーヒーの匂いがする。"
            show kana pajama normal
            kana_c "おはよ、いつもの。"
            himo "...いつの間にうちにコーヒー常備してたんだ"
        else:
            "カナが布団の中からくっついてきた。"
            kana_c "...寒い"
            himo "エアコンつけろ"
            show kana pajama happy
            kana_c "ヒモ太郎の方があったかい"

    # 3回目以降のバリエーションでキッチン描写がないパターン向け
    if _kana_stay > 2:
        "カナがキッチンに立った。"

    # Phase 4 Step 3: 食材による分岐
    # v1.9: 夕食で使った残りで朝食を作れるケース
    if daily_flags.get("groceries_used_dinner", False) and inventory.get("groceries", 0) > 0:
        show kana pajama happy
        if inventory["groceries"] == 2:
            kana_c "昨日のベーコンまだあるじゃん！朝ごはん作る！"
        else:
            kana_c "卵あるから目玉焼きね〜"
        $ change_trust_kana(3)
        $ inventory["groceries"] = 0
        $ daily_flags["ate_today"] = True
        $ change_stamina(12)
    elif not daily_flags.get("groceries_used_dinner", False) and inventory.get("groceries", 0) == 2:
        show kana pajama excited
        kana_c "え、ベーコンある！パンケーキ作れる！"
        himo "（買っといてよかった）"
        $ change_trust_kana(5)
        $ inventory["groceries"] = 0
        $ daily_flags["ate_today"] = True
        $ change_stamina(15)
    elif not daily_flags.get("groceries_used_dinner", False) and inventory.get("groceries", 0) == 1:
        show kana pajama smile
        kana_c "あ、卵あるじゃん。目玉焼き作るね"
        himo "（ちゃんと用意しといた甲斐があったな）"
        $ change_trust_kana(2)
        $ inventory["groceries"] = 0
        $ daily_flags["ate_today"] = True
        $ change_stamina(12)
    else:
        show kana pajama sad
        kana_c "冷蔵庫...何もないじゃん"
        himo "...すまん"
        show kana pajama smile
        kana_c "しょうがないな〜。コンビニ行ってくるね"
        "カナがコンビニで朝ごはんを買ってきてくれた。"
        $ daily_flags["ate_today"] = True
        $ change_stamina(10)
        $ change_trust_kana(2)

    # v1.7: 泊まり回数で翌朝テキストを分岐
    python:
        _stay_count = stats.get("kana_stayed_over", 0)

    if _stay_count <= 2:
        show kana pajama normal
        kana_c "ヒモ太郎の部屋、もうちょっと片付けなよ"
        himo "...はい"
        himo "（泊まるたびに『期待』されてる気がする...）"
        himo "（まあ、今はいっか）"
    elif _stay_count <= 5:
        python:
            _kh_idx = renpy.random.randint(0, 2)

        if _kh_idx == 0:
            show kana pajama serious
            kana_c "ヒモ太郎の部屋、前より散らかってない？"
            himo "...気のせいだろ"
        elif _kh_idx == 1:
            show kana pajama pouty
            kana_c "次来るまでに掃除しといてよね？"
            himo "善処します"
        else:
            show kana pajama smile
            kana_c "ここに置きっぱなしのヘアゴム、回収するね"
            himo "（生活感出てきたな...）"
        himo "（もう何回目だ、ここ泊まるの）"
        himo "（...慣れてきたな）"
    else:
        python:
            _kh_idx = renpy.random.randint(0, 2)

        if _kh_idx == 0:
            show kana pajama happy
            kana_c "おはよ。...もうここ半分私の部屋だね"
            himo "勝手に住み着くなよ"
        elif _kh_idx == 1:
            "カナはまだ寝ている。枕を抱きしめたまま動かない。"
            himo "（...起こすのもなんだし、放置するか）"
        else:
            show kana pajama normal
            kana_c "歯ブラシ、私の分も買っといて"
            himo "...マジで住む気か"

    "気づいたら昼になっていた。"
    "（朝の時間が消えた）"

    return


# ========================================
# Phase 4 Step 3: プレゼントシステム
# ========================================

label give_present(target):
    $ _gp_target = target
    menu:
        "花束を渡す" if inventory.get("bouquet", False):
            call give_bouquet(_gp_target)
        "アクセサリーを渡す" if inventory.get("accessory", False):
            call give_accessory(_gp_target)
        "推しグッズを渡す" if inventory.get("kana_goods", False) and _gp_target == "kana":
            call give_kana_goods
        "やっぱりやめる":
            pass
    return


label give_bouquet(target):
    $ _gb_target = target
    $ inventory["bouquet"] = False
    $ stats["presents_given"] = stats.get("presents_given", 0) + 1

    if _gb_target == "misaki":
        himo "これ"
        show misaki surprised
        misaki_c "...花？ 私に？"
        show misaki happy
        misaki_c "...ありがとう"
        if cold_war.get("misaki_active", False):
            $ change_trust(8)
            "（冷戦中に花...効果は大きかったかもしれない）"
        else:
            $ change_trust(5)
    else:
        himo "はい、これ"
        show kana surprised
        kana_c "え！花！？ インスタ載せていい！？"
        show kana excited
        $ change_trust_kana(5)

    return


label give_accessory(target):
    $ _ga_target = target
    $ inventory["accessory"] = False
    $ stats["presents_given"] = stats.get("presents_given", 0) + 1

    if _ga_target == "misaki":
        himo "これ、美咲に"
        show misaki surprised
        misaki_c "え...私に？"
        "美咲が目を丸くした。"
        show misaki happy
        misaki_c "...ありがとう。大事にする"
        $ change_trust(10)
        $ change_dependence(5)
    else:
        himo "これ、カナに"
        show kana surprised
        kana_c "やばい！かわいい！！"
        show kana excited
        kana_c "インスタ載せていい！？"
        $ change_trust_kana(10)
        $ change_dependence_kana(5)

    return


label give_kana_goods:
    $ inventory["kana_goods"] = False
    $ stats["presents_given"] = stats.get("presents_given", 0) + 1

    show kana shock
    kana_c "え！これ限定の！どこで見つけたの！？"
    show kana excited
    kana_c "ヒモ太郎、センスいいかも..."
    $ change_trust_kana(8)
    $ flags["kana_gokiragen_skip"] = True

    return
