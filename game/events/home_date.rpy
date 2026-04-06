# home_date.rpy
# Phase 4 Step 3 v2.0: 自宅デート3ラウンド会話システム
# ヒモ太郎の部屋にキャラを招く自宅デート専用

# ========================================
# エントリーポイント
# ========================================

label home_date(target):
    # 訪問カウント加算
    if target == "misaki":
        $ misaki_himo_room_visit_count += 1
    else:
        $ kana_himo_room_visit_count += 1

    # 自宅デートムード初期化
    $ _home_mood = 0
    $ flags["sake_bonus_active"] = False
    # 交渉用の場所フラグを先に設定（酒ルート交渉で参照される）
    $ daily_flags["date_location"] = "himo_room"

    # パターン判定
    if target == "misaki":
        call home_date_pattern_misaki
    else:
        call home_date_pattern_kana

    # 冷戦突��した場合は泊まり判定をスキップ
    if target == "misaki" and cold_war.get("misaki_active", False):
        return
    if target == "kana" and cold_war.get("kana_active", False):
        return

    # 泊まり判定（ムード依存）
    call home_date_stay_check(target)

    # v1.9: 自宅デート処理済みフラグ（後続の泊まりフローの二重実行を防止）
    $ flags["home_date_completed"] = True

    return


# ========================================
# パターン判定: 美咲
# ========================================

label home_date_pattern_misaki:
    python:
        if suspicion["misaki"] >= 15 or flags.get("cold_war_recently_resolved_misaki", False):
            _pattern = "D"
        elif misaki_himo_room_visit_count >= 5 and misaki["trust"] >= 80:
            _pattern = "C"
        elif misaki_himo_room_visit_count >= 3:
            _pattern = "B"
        else:
            _pattern = "A"

    $ log_action("HOME_DATE_MISAKI", "pattern=" + _pattern + " visit=" + str(misaki_himo_room_visit_count) + " trust=" + str(misaki["trust"]) + " suspicion=" + str(suspicion["misaki"]))

    if _pattern == "A":
        call misaki_home_A
    elif _pattern == "B":
        call misaki_home_B
    elif _pattern == "C":
        call misaki_home_C
    else:
        call misaki_home_D

    return


# ========================================
# パターン判定: カナ
# ========================================

label home_date_pattern_kana:
    python:
        _trigger_D = False
        if kana["dependence"] >= 70 or suspicion["kana"] >= 15:
            if renpy.random.random() < 0.5:
                _trigger_D = True

        if _trigger_D:
            _pattern = "D"
        elif kana_himo_room_visit_count >= 5 and kana["trust"] >= 80:
            _pattern = "C"
        elif kana_himo_room_visit_count >= 3:
            _pattern = "B"
        else:
            _pattern = "A"

    $ log_action("HOME_DATE_KANA", "pattern=" + _pattern + " visit=" + str(kana_himo_room_visit_count) + " trust=" + str(kana["trust"]) + " dep=" + str(kana["dependence"]))

    if _pattern == "A":
        call kana_home_A
    elif _pattern == "B":
        call kana_home_B
    elif _pattern == "C":
        call kana_home_C
    else:
        call kana_home_D

    return


# ========================================
# 食材分岐: 美咲
# ========================================

label misaki_home_food_check:
    if inventory["groceries"] == 2:
        misaki_c "...これ、私のために買ってたの？"
        himo "まあ、一応"
        misaki_c "...じゃあ一緒に作ろうか"
        $ change_trust(5)
        $ daily_flags["groceries_used_dinner"] = True
        $ daily_flags["ate_today"] = True
        $ _home_mood += 2
    elif inventory["groceries"] == 1:
        misaki_c "あ、ちゃんと買ってあるんだ"
        himo "たまにはな"
        misaki_c "...じゃあ私作るね"
        $ change_trust(3)
        $ daily_flags["groceries_used_dinner"] = True
        $ daily_flags["ate_today"] = True
        $ _home_mood += 1
    else:
        misaki_c "冷蔵庫、空だと思って買ってきたよ"
        "美咲がバッグからコンビニの袋を出した。"
        misaki_c "一人暮らし長いから、こういうの慣れてる"
        $ daily_flags["ate_today"] = True
    return


# ========================================
# 食材分岐: カナ
# ========================================

label kana_home_food_check:
    if inventory["groceries"] == 2:
        "カナが冷蔵庫を開けた。"
        kana_c "お！卵ある！...なにこれ、ベーコンまで"
        kana_c "ヒモ太郎が料理するの？"
        himo "たまにはな"
        kana_c "嘘でしょ笑。じゃあ私が作る！"
        $ change_trust_kana(5)
        $ daily_flags["groceries_used_dinner"] = True
        $ daily_flags["ate_today"] = True
        $ _home_mood += 2
    elif inventory["groceries"] == 1:
        "カナが冷蔵庫を開けた。"
        kana_c "あ、卵あるじゃん。目玉焼き作るね"
        $ change_trust_kana(3)
        $ daily_flags["groceries_used_dinner"] = True
        $ daily_flags["ate_today"] = True
        $ _home_mood += 1
    else:
        "カナが冷蔵庫を開けた。"
        kana_c "は？何もないじゃん"
        himo "..."
        kana_c "カップ麺は？"
        himo "それもない"
        kana_c "終わってる笑。出前取ろ"
        if can_afford(1000):
            $ change_money(-1000)
            $ daily_flags["ate_today"] = True
        else:
            kana_c "...お金もないの？"
            himo "...すまん"
            kana_c "しょうがないな〜。私が出す"
            $ daily_flags["ate_today"] = True
            $ change_trust_kana(-2)
    return


# ========================================
# 美咲パターンA「初めての部屋」（訪問1〜2回目）
# ========================================

label misaki_home_A:
    misaki_c "お邪魔します..."
    "キョロキョロ見回している。スーツ姿のまま。"
    misaki_c "...男の人の部屋って感じ"

    call misaki_home_food_check

    "コンビニで買った缶ビールとつまみを並べた。"

    # ラウンド1「部屋に入る」
    python:
        _pool_r1 = [
            ("座って座って", "trust", 2, 1, "まだぎこちない笑顔で座った。"),
            ("散らかっててごめん", "trust", 3, 1, "ううん、男の人の部屋って感じで...落ち着く"),
            ("飲み物何がいい？", "trust", 3, 1, "...こういうの、新鮮"),
            ("緊張してる？", "trust", 5, 2, "...ちょっとだけ"),
        ]
        renpy.random.shuffle(_pool_r1)
        _choices_r1 = _pool_r1[:3]
        _menu_r1 = [(c[0], i) for i, c in enumerate(_choices_r1)]

    $ _r1_pick = renpy.display_menu(_menu_r1)

    python:
        _r1 = _choices_r1[_r1_pick]
    himo "[_r1[0]]"
    misaki_c "[_r1[4]]"
    python:
        if _r1[1] == "trust":
            change_trust(_r1[2])
        elif _r1[1] == "dependence":
            change_dependence(_r1[2])
        _home_mood += _r1[3]

    # ラウンド2「少しほぐれる」
    "お酒が入って美咲の口数が増えてきた。"

    python:
        _pool_r2 = [
            ("いつもスーツなの？", "trust", 3, 1, "休日はジャージだよ。見せないけど"),
            ("俺の部屋、どう？", "dependence", 3, 1, "狭いけど、落ち着く"),
            ("お酒もう一杯", "none", 0, 1, "...ん、ありがと"),
            ("仕事のこと忘れていいよ", "both", 5, 2, "...うん。今日くらいは"),
            ("美咲の部屋と全然違うな", "trust", 2, 1, "そりゃそうでしょ笑"),
        ]
        renpy.random.shuffle(_pool_r2)
        _choices_r2 = _pool_r2[:3]
        _menu_r2 = [(c[0], i) for i, c in enumerate(_choices_r2)]

    $ _r2_pick = renpy.display_menu(_menu_r2)

    python:
        _r2 = _choices_r2[_r2_pick]
    himo "[_r2[0]]"
    misaki_c "[_r2[4]]"
    python:
        if _r2[1] == "trust":
            change_trust(_r2[2])
        elif _r2[1] == "dependence":
            change_dependence(_r2[2])
        elif _r2[1] == "both":
            change_trust(_r2[2])
            change_dependence(3)
        _home_mood += _r2[3]
        # お酒もう一杯 → 酒ルート
        if _r2[0] == "お酒もう一杯":
            flags["sake_bonus_active"] = True

    "美咲の表情が少しずつ柔らかくなっていく。"

    # ラウンド3「帰り際」
    python:
        _pool_r3 = [
            ("送ろうか？", "trust", 5, 1, "大丈夫...でもありがとう"),
            ("また来いよ", "trust", 5, 2, "...いいの？"),
            ("終電大丈夫？", "none", 0, 2, "えっと...もうないかも"),
            ("楽しかった", "trust", 3, 1, "...私も"),
        ]
        renpy.random.shuffle(_pool_r3)
        _choices_r3 = _pool_r3[:3]
        _menu_r3 = [(c[0], i) for i, c in enumerate(_choices_r3)]

    $ _r3_pick = renpy.display_menu(_menu_r3)

    python:
        _r3 = _choices_r3[_r3_pick]
    himo "[_r3[0]]"
    misaki_c "[_r3[4]]"
    python:
        if _r3[1] == "trust":
            change_trust(_r3[2])
        elif _r3[1] == "dependence":
            change_dependence(_r3[2])
        _home_mood += _r3[3]

    return


# ========================================
# 美咲パターンB「素の美咲」（訪問3回以上）
# ========================================

label misaki_home_B:
    misaki_c "今日は早く帰れたんだ"
    "私服。いつもの『頑張ってる美咲』の顔じゃない。"

    call misaki_home_food_check

    "缶ビールを開けた。"

    # ラウンド1「リラックスした到着」
    python:
        _pool_r1 = [
            ("今日は私服じゃん", "dependence", 3, 1, "だってヒモ太郎の部屋でしょ"),
            ("今日の美咲、なんか違う", "trust", 3, 1, "リラックスしてるだけ"),
            ("ただいま", "dependence", 5, 2, "...おかえり？笑"),
            ("何か食べる？", "trust", 2, 1, "...うん、お腹空いた"),
        ]
        renpy.random.shuffle(_pool_r1)
        _choices_r1 = _pool_r1[:3]
        _menu_r1 = [(c[0], i) for i, c in enumerate(_choices_r1)]

    $ _r1_pick = renpy.display_menu(_menu_r1)

    python:
        _r1 = _choices_r1[_r1_pick]
    himo "[_r1[0]]"
    misaki_c "[_r1[4]]"
    python:
        if _r1[1] == "trust":
            change_trust(_r1[2])
        elif _r1[1] == "dependence":
            change_dependence(_r1[2])
        _home_mood += _r1[3]

    # ラウンド2「仕事の鎧が剥がれる」
    "ふと、美咲が黙った。"
    misaki_c "...ねえ、聞いてもらっていい？"

    python:
        _pool_r2 = [
            ("上司の話、前も言ってたな", "trust", 8, 2, "...覚えてたの？"),
            ("辛かったら泣いていいよ", "both_strong", 10, 3, "泣かないよ..."),
            ("お酒注ぐ", "none", 0, 1, "...ありがと"),
            ("美咲は頑張りすぎ", "trust", 5, 1, "そうかな..."),
            ("マッサージする？", "dependence", 5, 2, "え、いいの...？"),
            ("俺にできることある？", "trust", 5, 1, "こうしてくれるだけで十分"),
        ]
        renpy.random.shuffle(_pool_r2)
        _choices_r2 = _pool_r2[:3]
        _menu_r2 = [(c[0], i) for i, c in enumerate(_choices_r2)]

    $ _r2_pick = renpy.display_menu(_menu_r2)

    python:
        _r2 = _choices_r2[_r2_pick]
    himo "[_r2[0]]"
    if _r2[1] == "both_strong":
        misaki_c "[_r2[4]]"
        "目が少し潤んでいる。"
    else:
        misaki_c "[_r2[4]]"
    python:
        if _r2[1] == "trust":
            change_trust(_r2[2])
        elif _r2[1] == "dependence":
            change_dependence(_r2[2])
        elif _r2[1] == "both_strong":
            change_trust(_r2[2])
            change_dependence(8)
        _home_mood += _r2[3]
        if _r2[0] == "お酒注ぐ":
            flags["sake_bonus_active"] = True

    # ラウンド3「二人だけの時間」
    "テレビも消えた。静かな夜。"

    python:
        _pool_r3 = [
            ("隣に座る", "none", 0, 2, ""),
            ("もう帰らないで", "dependence", 5, 3, "仕事が...でも"),
            ("美咲がいると落ち着く", "both", 5, 2, "...私も"),
            ("（黙って髪を撫でる）", "none", 0, 3, ""),
            ("将来どうしたい？", "stage_check", 0, 0, ""),
        ]
        renpy.random.shuffle(_pool_r3)
        _choices_r3 = _pool_r3[:3]
        _menu_r3 = [(c[0], i) for i, c in enumerate(_choices_r3)]

    $ _r3_pick = renpy.display_menu(_menu_r3)

    python:
        _r3 = _choices_r3[_r3_pick]

    if _r3[0] == "隣に座る":
        "そっと隣に座った。"
        "少しだけ、美咲が寄りかかってきた。"
        $ _home_mood += 2
    elif _r3[0] == "（黙って髪を撫でる）":
        "美咲の髪をそっと撫でた。"
        "美咲が目を閉じる。"
        $ _home_mood += 3
    elif _r3[0] == "将来どうしたい？":
        himo "将来どうしたい？"
        if misaki["stage"] >= 4:
            misaki_c "...考えたことなかった"
            misaki_c "でも...こうしてる時間が続けばいいなって"
            $ change_trust(5)
            $ _home_mood += 2
        else:
            misaki_c "...急にそういうこと聞く？"
            "空気が少し冷えた。"
            $ change_trust(-5)
    else:
        himo "[_r3[0]]"
        misaki_c "[_r3[4]]"
        python:
            if _r3[1] == "dependence":
                change_dependence(_r3[2])
            elif _r3[1] == "both":
                change_trust(_r3[2])
                change_dependence(5)
            _home_mood += _r3[3]

    return


# ========================================
# 美咲パターンC「ここが居場所」（訪問5回以上・信頼80以上）
# ========================================

label misaki_home_C:
    misaki_c "ただいま"
    "もう自分の家のように入ってくる。"

    call misaki_home_food_check

    # ラウンド1「帰ってきた感覚」
    python:
        _pool_r1 = [
            ("おかえり", "dependence", 3, 2, "...ふふ"),
            ("今日も残業？", "trust", 3, 1, "早く帰りたくて、手抜きした"),
            ("飯作っといた", "trust_big", 10, 3, "...え、ほんと？"),
            ("（何も言わず迎える）", "trust", 2, 1, ""),
        ]
        # 「飯作っといた」は食材ありの場合のみ
        if inventory["groceries"] == 0:
            _pool_r1 = [p for p in _pool_r1 if p[0] != "飯作っといた"]
        renpy.random.shuffle(_pool_r1)
        _choices_r1 = _pool_r1[:3]
        _menu_r1 = [(c[0], i) for i, c in enumerate(_choices_r1)]

    $ _r1_pick = renpy.display_menu(_menu_r1)

    python:
        _r1 = _choices_r1[_r1_pick]

    if _r1[0] == "（何も言わず迎える）":
        "何も言わずに迎えた。"
        "美咲がそのまま着替え始める。"
        $ change_trust(2)
        $ _home_mood += 1
    elif _r1[0] == "飯作っといた":
        himo "飯作っといた"
        misaki_c "...え、ほんと？"
        "美咲が驚いた顔をしている。"
        misaki_c "...ありがとう"
        $ change_trust(10)
        $ daily_flags["groceries_used_dinner"] = True
        $ daily_flags["ate_today"] = True
        $ _home_mood += 3
    else:
        himo "[_r1[0]]"
        misaki_c "[_r1[4]]"
        python:
            if _r1[1] == "trust":
                change_trust(_r1[2])
            elif _r1[1] == "dependence":
                change_dependence(_r1[2])
            _home_mood += _r1[3]

    # ラウンド2「無言の心地よさ」
    "隣に座ってテレビを見てる。会話が少ない。"
    "でも、それが心地いい。"

    python:
        _pool_r2 = [
            ("（コーヒー淹れる）", "trust", 3, 1, "ありがとう"),
            ("美咲って家だとメガネなんだな", "dependence", 5, 2, "見ないで"),
            ("週末どっか行く？", "dependence", 8, 2, "...ここでいい"),
            ("（美咲の肩にもたれる）", "none", 0, 2, ""),
            ("今日の晩ご飯どうだった？", "trust", 2, 1, "おいしかった。ちょっと塩辛いけど"),
        ]
        renpy.random.shuffle(_pool_r2)
        _choices_r2 = _pool_r2[:3]
        _menu_r2 = [(c[0], i) for i, c in enumerate(_choices_r2)]

    $ _r2_pick = renpy.display_menu(_menu_r2)

    python:
        _r2 = _choices_r2[_r2_pick]

    if _r2[0] == "（コーヒー淹れる）":
        "コーヒーを淹れて渡した。"
        misaki_c "ありがとう"
        "目を合わせずに、でも嬉しそうに受け取った。"
        $ change_trust(3)
        $ _home_mood += 1
    elif _r2[0] == "（美咲の肩にもたれる）":
        "そっと美咲の肩にもたれた。"
        "何も言わず受け入れてくれた。"
        $ _home_mood += 2
    elif _r2[0] == "美咲って家だとメガネなんだな":
        himo "美咲って家だとメガネなんだな"
        misaki_c "見ないで"
        "耳が赤い。"
        $ change_dependence(5)
        $ _home_mood += 2
    else:
        himo "[_r2[0]]"
        misaki_c "[_r2[4]]"
        python:
            if _r2[1] == "trust":
                change_trust(_r2[2])
            elif _r2[1] == "dependence":
                change_dependence(_r2[2])
            _home_mood += _r2[3]

    # ラウンド3「ふと溢れるもの」
    python:
        _pool_r3 = [
            ("なあ、美咲", "none", 0, 2, ""),
            ("ずっとこうしてたい", "both_deep", 5, 3, "仕事辞めたら、ね"),
            ("（手を重ねる）", "none", 0, 3, ""),
            ("美咲の寝顔見たい", "dependence", 5, 2, "見せない"),
            ("俺がいなくなったら？", "both_deep2", 8, 2, ""),
        ]
        renpy.random.shuffle(_pool_r3)
        _choices_r3 = _pool_r3[:3]
        _menu_r3 = [(c[0], i) for i, c in enumerate(_choices_r3)]

    $ _r3_pick = renpy.display_menu(_menu_r3)

    python:
        _r3 = _choices_r3[_r3_pick]

    if _r3[0] == "なあ、美咲":
        himo "なあ、美咲"
        misaki_c "ん？"
        "何か言おうとして、言わなかった。"
        "でも、それで十分だった。"
        $ _home_mood += 2
    elif _r3[0] == "ずっとこうしてたい":
        himo "ずっとこうしてたい"
        misaki_c "仕事辞めたら、ね"
        "冗談ぽく言ったけど、目は本気だった。"
        $ change_trust(5)
        $ change_dependence(10)
        $ _home_mood += 3
    elif _r3[0] == "（手を重ねる）":
        "そっと手を重ねた。"
        "握り返してくる。何も言わない。"
        $ _home_mood += 3
    elif _r3[0] == "美咲の寝顔見たい":
        himo "美咲の寝顔見たい"
        misaki_c "見せない"
        "赤くなってる。"
        $ change_dependence(5)
        $ _home_mood += 2
    elif _r3[0] == "俺がいなくなったら？":
        himo "俺がいなくなったら？"
        misaki_c "そういうこと言わないで"
        "声が震えていた。"
        $ change_trust(8)
        $ change_dependence(10)
        $ _home_mood += 2

    return


# ========================================
# 美咲パターンD「壊れかけの夜」（疑念15以上 or 冷戦解除直後）
# ========================================

label misaki_home_D:
    misaki_c "...入っていい？"
    "いつもの笑顔がない。"

    # 食材チェックはしない（空気的にそれどころじゃない）

    # ラウンド1「冷たい到着」
    python:
        _pool_r1 = [
            ("どうぞ", "none", 0, 0, ""),
            ("美咲、どうした？", "trust", 2, 0, "...別に"),
            ("来てくれて嬉しい", "trust", 1, 0, "..."),
            ("今日は何か違うな", "trust", 5, 1, "...分かるんだ"),
        ]
        renpy.random.shuffle(_pool_r1)
        _choices_r1 = _pool_r1[:3]
        _menu_r1 = [(c[0], i) for i, c in enumerate(_choices_r1)]

    $ _r1_pick = renpy.display_menu(_menu_r1)

    python:
        _r1 = _choices_r1[_r1_pick]

    if _r1[0] == "どうぞ":
        himo "どうぞ"
        "美咲が部屋を見回す。何かを確認するように。"
    elif _r1[4]:
        himo "[_r1[0]]"
        misaki_c "[_r1[4]]"
    else:
        himo "[_r1[0]]"
        "反応が薄い。"
    python:
        if _r1[1] == "trust":
            change_trust(_r1[2])
        _home_mood += _r1[3]

    # ラウンド2「問い詰め」
    "沈黙が続く。"
    "美咲が何か言いたそうにしている。"

    python:
        _pool_r2 = [
            ("最近忙しかった？", "suspicion_route", 0, 0, "ヒモ太郎こそ。連絡少ないよね"),
            ("なんか怒ってる？", "trust", 3, 1, "怒ってない。...怒ってないよ"),
            ("（お酒を出す）", "none", 0, 0, "...飲みたい気分じゃない"),
            ("正直に話してほしい", "confrontation", 0, 0, ""),
            ("（黙って見つめる）", "trust", 2, 1, "...何？"),
        ]
        renpy.random.shuffle(_pool_r2)
        _choices_r2 = _pool_r2[:3]
        _menu_r2 = [(c[0], i) for i, c in enumerate(_choices_r2)]

    $ _r2_pick = renpy.display_menu(_menu_r2)

    python:
        _r2 = _choices_r2[_r2_pick]
        _confrontation = False

    if _r2[0] == "正直に話してほしい":
        himo "正直に話してほしい"
        misaki_c "最近、楽しそうだよね。私といない時"
        misaki_c "何してるの？本当のことを教えて"
        $ _confrontation = True
        # 嘘をつくか正直に話すか
        menu:
            "正直に話す":
                himo "...ごめん、他にも会ってる人がいる"
                misaki_c "......"
                misaki_c "...知ってた"
                misaki_c "知ってたけど、聞きたくなかった"
                $ change_trust(10)
                $ _home_mood += 2
                $ himo_aptitude["honest_moments"] += 1
            "嘘をつく":
                $ himo_aptitude["lies"] += 1
                call lie_puzzle_other_woman("misaki")
                if lie_puzzle["result"] == "busted":
                    misaki_c "...嘘つかないでって言ったよね"
                    $ change_trust(-15)
                    $ start_cold_war("misaki", 1)
                    $ flags["cold_war_recently_resolved_misaki"] = False
                    return
                elif lie_puzzle["result"] == "suspicious":
                    misaki_c "...本当に？"
                    $ _home_mood += 1
                else:
                    $ _home_mood += 1
    elif _r2[0] == "最近忙しかった？":
        himo "[_r2[0]]"
        misaki_c "[_r2[4]]"
        "美咲の目が鋭い。"
    elif _r2[4]:
        himo "[_r2[0]]"
        misaki_c "[_r2[4]]"
    else:
        himo "[_r2[0]]"
    python:
        if _r2[1] == "trust":
            change_trust(_r2[2])
        _home_mood += _r2[3]

    # ラウンド3「決壊 or 和解」
    if _home_mood >= 3:
        # 和解ルート
        misaki_c "...ごめん。疑って"
        misaki_c "でも...怖かったの"
        misaki_c "ヒモ太郎がどっか行っちゃう気がして"
        "美咲が泣いている。"
        "ゲームの中で、美咲が泣くのはこれが初めてだ。"
        $ change_trust(10)
        $ suspicion["misaki"] = 0
        $ _home_mood += 3
    else:
        # 決壊ルート
        misaki_c "...もう分からない"
        misaki_c "ヒモ太郎のこと、信じたいのに"
        "美咲が立ち上がった。"
        misaki_c "...今日は帰る"
        $ change_trust(-10)
        # 泊まり不可・エナマッチ不可（_home_mood が低いため自動的に不可）

    # 冷戦解除直後フラグをリセット
    $ flags["cold_war_recently_resolved_misaki"] = False

    return


# ========================================
# カナパターンA「探り合い」（訪問1〜2回目）
# ========================================

label kana_home_A:
    kana_c "お邪魔しまーす"
    "カナが部屋をキョロキョロ見回している。"
    kana_c "へー...男の人の部屋って感じ"

    call kana_home_food_check

    # ラウンド1「初めての空間」
    python:
        _pool_r1 = [
            ("飲み物出す", "trust", 3, 1, "お、気が利くじゃん"),
            ("部屋狭いけど", "dependence", 3, 1, "いいじゃん、距離近い方が"),
            ("適当に座って", "trust", 1, 0, "ソファないの？"),
            ("散らかっててごめん", "trust", 2, 1, "別にいいよ、慣れてるし"),
        ]
        renpy.random.shuffle(_pool_r1)
        _choices_r1 = _pool_r1[:3]
        _menu_r1 = [(c[0], i) for i, c in enumerate(_choices_r1)]

    $ _r1_pick = renpy.display_menu(_menu_r1)

    python:
        _r1 = _choices_r1[_r1_pick]
    himo "[_r1[0]]"
    if _r1[0] == "適当に座って":
        "カナが床にぺたんと座った。"
        kana_c "[_r1[4]]"
    else:
        kana_c "[_r1[4]]"
    python:
        if _r1[1] == "trust":
            change_trust_kana(_r1[2])
        elif _r1[1] == "dependence":
            change_dependence_kana(_r1[2])
        _home_mood += _r1[3]

    # ラウンド2「ちょっと慣れてきた」
    "カナがスマホを見ながらリラックスし始めた。"

    python:
        _pool_r2 = [
            ("何見てんの？", "trust", 2, 1, "え、インスタ。見る？"),
            ("音楽かける？", "trust", 3, 1, "あ、いいね！私選んでいい？"),
            ("腹減った？", "trust", 1, 0, "もう食べたじゃん笑"),
            ("大学どう？", "trust", 5, 1, "んー、まあぼちぼち。課題やばいけど"),
        ]
        renpy.random.shuffle(_pool_r2)
        _choices_r2 = _pool_r2[:3]
        _menu_r2 = [(c[0], i) for i, c in enumerate(_choices_r2)]

    $ _r2_pick = renpy.display_menu(_menu_r2)

    python:
        _r2 = _choices_r2[_r2_pick]
    himo "[_r2[0]]"
    kana_c "[_r2[4]]"
    python:
        if _r2[1] == "trust":
            change_trust_kana(_r2[2])
        _home_mood += _r2[3]

    # ラウンド3「帰り際の空気」
    python:
        _pool_r3 = [
            ("もう遅いけど", "none", 0, 1, "...送ってくれる？"),
            ("また来いよ", "trust", 5, 2, "...いいの？"),
            ("楽しかった", "both", 5, 1, "うん。...また来たい"),
            ("終電大丈夫？", "none", 0, 2, "えっと...もうないかも"),
        ]
        renpy.random.shuffle(_pool_r3)
        _choices_r3 = _pool_r3[:3]
        _menu_r3 = [(c[0], i) for i, c in enumerate(_choices_r3)]

    $ _r3_pick = renpy.display_menu(_menu_r3)

    python:
        _r3 = _choices_r3[_r3_pick]
    himo "[_r3[0]]"
    kana_c "[_r3[4]]"
    python:
        if _r3[1] == "trust":
            change_trust_kana(_r3[2])
        elif _r3[1] == "both":
            change_trust_kana(_r3[2])
            change_dependence_kana(3)
        _home_mood += _r3[3]

    "カナが嬉しそうに手を振った。"

    return


# ========================================
# カナパターンB「カオスな夜」（訪問3回以上）
# ========================================

label kana_home_B:
    kana_c "おじゃましまーす！...って勝手に入るけど"
    "勝手に冷蔵庫を開けている。"

    call kana_home_food_check

    # ラウンド1「突入」
    python:
        _pool_r1 = [
            ("勝手に開けるな", "trust", 2, 1, "えー、いいじゃん"),
            ("何か作ろうか", "trust_food", 5, 1, "マジ？やった！"),
            ("お菓子ならある", "trust", 3, 1, "神！"),
            ("何でもいいから食べよ", "none", 0, 1, "カップ麺で乾杯！"),
        ]
        # 食材なしなら「何か作ろうか」の反応変更
        if inventory["groceries"] == 0:
            _pool_r1[1] = ("何か作ろうか", "trust", 1, 1, "何もないじゃん笑")
        renpy.random.shuffle(_pool_r1)
        _choices_r1 = _pool_r1[:3]
        _menu_r1 = [(c[0], i) for i, c in enumerate(_choices_r1)]

    $ _r1_pick = renpy.display_menu(_menu_r1)

    python:
        _r1 = _choices_r1[_r1_pick]
    himo "[_r1[0]]"
    kana_c "[_r1[4]]"
    python:
        if _r1[1] == "trust" or _r1[1] == "trust_food":
            change_trust_kana(_r1[2])
        _home_mood += _r1[3]

    # ラウンド2「暴走」
    "カナのテンションが上がっている。"

    python:
        _pool_r2 = [
            ("インスタ撮るな", "none", 0, 1, "1枚だけ！"),
            ("一緒にゲームする", "trust", 5, 2, "え、負けないし！"),
            ("カナの持ち物チェック", "trust", 3, 1, "え、何で？...いいけど"),
            ("動画一緒に見る", "both", 3, 1, "これ見て見て！爆笑"),
            ("部屋探索させる", "trust", 2, 1, "漫画いっぱいある！借りていい？"),
            ("踊ってみせて", "trust", 3, 2, "え〜...いいよ、見てて！"),
        ]
        renpy.random.shuffle(_pool_r2)
        _choices_r2 = _pool_r2[:3]
        _menu_r2 = [(c[0], i) for i, c in enumerate(_choices_r2)]

    $ _r2_pick = renpy.display_menu(_menu_r2)

    python:
        _r2 = _choices_r2[_r2_pick]
    himo "[_r2[0]]"
    kana_c "[_r2[4]]"
    python:
        if _r2[1] == "trust":
            change_trust_kana(_r2[2])
        elif _r2[1] == "both":
            change_trust_kana(_r2[2])
            change_dependence_kana(2)
        _home_mood += _r2[3]

    # ラウンド3「静けさ」
    "ふとカナが黙った。テンションの後に来る静寂。"

    python:
        _pool_r3 = [
            ("どうした？", "trust_branch", 3, 1, "なんでもない"),
            ("疲れた？", "dependence", 5, 1, "ちょっとだけ"),
            ("楽しかった", "trust", 5, 2, "...うん、楽しかった"),
            ("カナって実は人見知りだろ", "trust", 8, 3, "！...バレた？"),
            ("（黙って隣にいる）", "dependence", 8, 2, ""),
        ]
        renpy.random.shuffle(_pool_r3)
        _choices_r3 = _pool_r3[:3]
        _menu_r3 = [(c[0], i) for i, c in enumerate(_choices_r3)]

    $ _r3_pick = renpy.display_menu(_menu_r3)

    python:
        _r3 = _choices_r3[_r3_pick]

    if _r3[0] == "どうした？":
        himo "どうした？"
        kana_c "なんでもない"
        menu:
            "そうか":
                $ change_trust_kana(3)
                $ _home_mood += 1
            "嘘つけ":
                kana_c "...なんか、楽しい時間って終わるの早いなって"
                $ change_trust_kana(8)
                $ _home_mood += 2
    elif _r3[0] == "（黙って隣にいる）":
        "何も言わず、隣に座り続けた。"
        "カナが肩にもたれてきた。"
        $ change_dependence_kana(8)
        $ _home_mood += 2
    else:
        himo "[_r3[0]]"
        kana_c "[_r3[4]]"
        python:
            if _r3[1] == "trust":
                change_trust_kana(_r3[2])
            elif _r3[1] == "dependence":
                change_dependence_kana(_r3[2])
            _home_mood += _r3[3]

    return


# ========================================
# カナパターンC「二人の日常」（訪問5回以上・信頼80以上）
# ========================================

label kana_home_C:
    kana_c "ただいま〜...って違うか"
    "もう自分の家のように振る舞っている。"

    call kana_home_food_check

    # ラウンド1「ただいま」
    python:
        _pool_r1 = [
            ("おかえり", "dependence", 3, 1, "...へへ"),
            ("飯どうする", "trust", 3, 1, "今日は私が作る！"),
            ("今日何してた？", "trust", 2, 1, "バイトー。めっちゃ疲れた"),
            ("荷物増えてない？", "dependence", 5, 2, "歯ブラシ置いていい？"),
        ]
        renpy.random.shuffle(_pool_r1)
        _choices_r1 = _pool_r1[:3]
        _menu_r1 = [(c[0], i) for i, c in enumerate(_choices_r1)]

    $ _r1_pick = renpy.display_menu(_menu_r1)

    python:
        _r1 = _choices_r1[_r1_pick]
    himo "[_r1[0]]"
    kana_c "[_r1[4]]"
    python:
        if _r1[1] == "trust":
            change_trust_kana(_r1[2])
        elif _r1[1] == "dependence":
            change_dependence_kana(_r1[2])
        _home_mood += _r1[3]

    # ラウンド2「日常のルーティン」
    "並んでスマホいじったり、テレビ見たり。"

    python:
        _pool_r2 = [
            ("一緒にダラダラ", "both", 3, 1, ""),
            ("カナの将来の話", "trust_deep", 0, 0, ""),
            ("写真見返す", "trust", 5, 2, "あー、これ懐かしい！"),
            ("カナのバイトの話", "trust", 3, 1, "店長がさ〜マジうざくて"),
            ("何かやりたいこととかある？", "trust", 8, 2, "うーん...カフェやりたいかも"),
        ]
        renpy.random.shuffle(_pool_r2)
        _choices_r2 = _pool_r2[:3]
        _menu_r2 = [(c[0], i) for i, c in enumerate(_choices_r2)]

    $ _r2_pick = renpy.display_menu(_menu_r2)

    python:
        _r2 = _choices_r2[_r2_pick]

    if _r2[0] == "一緒にダラダラ":
        "何もしない。でも、それが心地いい。"
        $ change_trust_kana(3)
        $ change_dependence_kana(3)
        $ _home_mood += 1
    elif _r2[0] == "カナの将来の話":
        himo "卒業したらどうすんの？"
        if kana["trust"] >= 70:
            kana_c "んー...まだ分かんない"
            kana_c "でも、こうやって誰かと一緒にいられたらいいなって"
            $ change_trust_kana(8)
            $ _home_mood += 2
        else:
            kana_c "え、急に重くない？"
            "空気が少し変わった。"
            $ change_trust_kana(-3)
    else:
        himo "[_r2[0]]"
        kana_c "[_r2[4]]"
        python:
            if _r2[1] == "trust":
                change_trust_kana(_r2[2])
            _home_mood += _r2[3]

    # ラウンド3「ふとした瞬間」
    python:
        _pool_r3 = [
            ("ずっとこうしてたいな", "dependence", 10, 3, "...うん"),
            ("カナがいないと静かだな", "both", 5, 2, "寂しいの？"),
            ("俺、カナに甘えすぎてるかな", "trust_dep", 0, 0, ""),
            ("（何も言わず手を握る）", "none", 0, 3, ""),
        ]
        renpy.random.shuffle(_pool_r3)
        _choices_r3 = _pool_r3[:3]
        _menu_r3 = [(c[0], i) for i, c in enumerate(_choices_r3)]

    $ _r3_pick = renpy.display_menu(_menu_r3)

    python:
        _r3 = _choices_r3[_r3_pick]

    if _r3[0] == "ずっとこうしてたいな":
        himo "ずっとこうしてたいな"
        kana_c "...うん"
        $ change_dependence_kana(10)
        $ _home_mood += 3
    elif _r3[0] == "カナがいないと静かだな":
        himo "カナがいないと静かだな"
        kana_c "寂しいの？"
        himo "...まあな"
        kana_c "じゃあ毎日来てあげよっか"
        $ change_trust_kana(5)
        $ change_dependence_kana(5)
        $ _home_mood += 2
    elif _r3[0] == "俺、カナに甘えすぎてるかな":
        himo "俺、カナに甘えすぎてるかな"
        if kana["trust"] >= 80:
            kana_c "いいよ、甘えて"
            kana_c "私もヒモ太郎に甘えてるし"
            $ change_trust_kana(5)
            $ change_dependence_kana(5)
            $ _home_mood += 3
        else:
            kana_c "...ちょっとだけね"
            $ change_trust_kana(2)
            $ _home_mood += 1
    elif _r3[0] == "（何も言わず手を握る）":
        "何も言わず手を握った。"
        "握り返してくる。"
        $ _home_mood += 3

    return


# ========================================
# カナパターンD「不安な夜」（依存70以上 or 疑念高い、50%で発火）
# ========================================

label kana_home_D:
    "カナが来た瞬間からくっついてくる。"
    kana_c "...会いたかった"

    # 食材チェックはしない（空気的にそれどころじゃない）

    # ラウンド1「甘え」
    python:
        _pool_r1 = [
            ("どうした？", "dependence", 5, 1, "別に...会いたかっただけ"),
            ("今日元気ないな", "trust", 5, 1, "...分かる？"),
            ("飯食った？", "trust", 3, 1, "食べてない..."),
            ("（受け入れる）", "dependence", 8, 2, ""),
        ]
        renpy.random.shuffle(_pool_r1)
        _choices_r1 = _pool_r1[:3]
        _menu_r1 = [(c[0], i) for i, c in enumerate(_choices_r1)]

    $ _r1_pick = renpy.display_menu(_menu_r1)

    python:
        _r1 = _choices_r1[_r1_pick]

    if _r1[0] == "（受け入れる）":
        "何も言わず受け入れた。"
        "カナがしばらく離れない。"
        $ change_dependence_kana(8)
        $ _home_mood += 2
    elif _r1[0] == "飯食った？":
        himo "飯食った？"
        kana_c "食べてない..."
        himo "...何か作るか"
        kana_c "...うん"
        $ change_trust_kana(3)
        $ daily_flags["ate_today"] = True
        $ _home_mood += 1
    else:
        himo "[_r1[0]]"
        kana_c "[_r1[4]]"
        python:
            if _r1[1] == "trust":
                change_trust_kana(_r1[2])
            elif _r1[1] == "dependence":
                change_dependence_kana(_r1[2])
            _home_mood += _r1[3]

    # ラウンド2「重い」
    "カナが不安を口にし始める。"

    python:
        _pool_r2 = [
            ("他に女いないよね？", "confrontation", 0, 0, ""),
            ("私のことどう思ってる？", "feeling", 0, 0, ""),
            ("LINEの返信遅くない？", "excuse", 0, 0, ""),
            ("前の彼氏の話", "trust", 10, 1, ""),
            ("（スマホを置いて向き合う）", "trust", 5, 2, "...ありがとう"),
        ]
        renpy.random.shuffle(_pool_r2)
        _choices_r2 = _pool_r2[:3]
        _menu_r2 = [(c[0], i) for i, c in enumerate(_choices_r2)]

    $ _r2_pick = renpy.display_menu(_menu_r2)

    python:
        _r2 = _choices_r2[_r2_pick]

    if _r2[0] == "他に女いないよね？":
        kana_c "ねえ、他に女いないよね？"
        menu:
            "いないよ":
                $ himo_aptitude["lies"] += 1
                call lie_puzzle_other_woman("kana")
                if lie_puzzle["result"] == "busted":
                    kana_c "...嘘ばっかり"
                    $ change_trust_kana(-15)
                    $ start_cold_war("kana", 1)
                    $ flags["cold_war_recently_resolved_kana"] = False
                    return
                elif lie_puzzle["result"] == "suspicious":
                    kana_c "...ほんとに？"
                    $ _home_mood += 1
                else:
                    kana_c "...うん、信じる"
                    $ _home_mood += 1
            "正直に話す":
                himo "...実は、他にも会ってる人がいる"
                kana_c "......"
                kana_c "...やっぱり"
                kana_c "分かってた。分かってたけど"
                $ change_trust_kana(8)
                $ _home_mood += 2
                $ himo_aptitude["honest_moments"] += 1
    elif _r2[0] == "私のことどう思ってる？":
        kana_c "ねえ、私のことどう思ってる？"
        menu:
            "大切に思ってる":
                kana_c "...本当？"
                himo "本当だよ"
                $ change_trust_kana(8)
                $ change_dependence_kana(5)
                $ _home_mood += 2
            "好きだよ":
                kana_c "...ずるい。そういうこと言うの"
                $ change_dependence_kana(10)
                $ _home_mood += 2
            "分からない":
                kana_c "...そっか"
                "カナが少し離れた。"
                $ change_trust_kana(-5)
    elif _r2[0] == "LINEの返信遅くない？":
        kana_c "最近LINEの返信遅くない？"
        menu:
            "ごめん、忙しかった":
                kana_c "...うん、分かってるけど"
                $ _home_mood += 1
            "そうかな？":
                kana_c "そうだよ。前は3分で返してくれたのに"
                $ change_trust_kana(-2)
    elif _r2[0] == "前の彼氏の話":
        himo "前の彼氏って、どんなやつだった？"
        kana_c "...聞くの？"
        himo "うん"
        kana_c "...普通の人だった。優しくて、ちゃんとしてて"
        kana_c "でも、つまんなかった"
        kana_c "ヒモ太郎は...ダメなのに、目が離せない"
        $ change_trust_kana(10)
        $ _home_mood += 1
    elif _r2[0] == "（スマホを置いて向き合う）":
        "スマホを置いて、カナに向き合った。"
        kana_c "...ありがとう"
        $ change_trust_kana(5)
        $ _home_mood += 2

    # ラウンド3「爆発 or 安心」
    if _home_mood >= 3:
        # 安心ルート
        kana_c "...ごめんね、重かったよね"
        kana_c "でも聞いてくれて嬉しかった"
        "カナが少し笑った。"
        $ change_dependence_kana(5)
        $ suspicion["kana"] = 0
        $ _home_mood += 2
    else:
        # 爆発ルート
        kana_c "...やっぱり信じられない"
        kana_c "もういい。帰る"
        "カナが荷物をまとめて立ち上がった。"
        $ change_trust_kana(-15)
        # 冷戦リスク（信頼が低ければ冷戦突入）
        if kana["trust"] < 30:
            $ start_cold_war("kana", 1)

    # 冷戦解除直後フラグをリセット
    $ flags["cold_war_recently_resolved_kana"] = False

    return


# ========================================
# 泊まり判定
# ========================================

label home_date_stay_check(target):
    # パターンDの決壊ルート等で既にreturnされている場合はここに来ない
    # （ムードが低いため自動的に泊まり不可になる）

    $ _hd_target = target

    # エナマッチへのムードボーナスを計算してストア変数に保存
    python:
        if _home_mood >= 6:
            home_date_mood_bonus = 2
        elif _home_mood >= 3:
            home_date_mood_bonus = 1
        else:
            home_date_mood_bonus = 0

    if _home_mood >= 6:
        # 相手から泊まり提案（自然な流れ）
        if _hd_target == "misaki":
            misaki_c "...帰りたくないな"
        else:
            kana_c "今日泊まっていい？...っていうか泊まるけど"

        # 泊まり確定
        if _hd_target == "misaki":
            "美咲が泊まることになった。"
            $ change_stamina(30)
            $ change_cleanliness(15)
            $ change_trust(5)
            $ change_dependence(8)
            $ flags["misaki_stayed_at_himo"] = True
            $ flags["misaki_stayed_himo_this_week"] = True
            $ flags["morning_consumed"] = True
            $ flags["kana_morning_after"] = False
            $ flags["kana_himo_room_morning"] = False
            $ flags["kana_at_himo_room"] = False
            $ location_flags["staying_at_kana"] = False
            if cold_war.get("kana_active", False):
                $ escalate_cold_war("kana")
                himo "（...カナが知ったら、もう二度と会ってくれないだろうな）"
        else:
            "カナが泊まることになった。"
            $ change_stamina(20)
            $ change_trust_kana(5)
            $ change_dependence_kana(8)
            $ flags["kana_at_himo_room"] = True
            $ flags["kana_himo_room_morning"] = True
            $ flags["kana_stayed_himo_this_week"] = True
            $ stats["kana_stayed_himo_room"] = stats.get("kana_stayed_himo_room", 0) + 1
            if cold_war.get("misaki_active", False):
                $ escalate_cold_war("misaki")
                himo "（...美咲にバレたらやばいな）"

        # エナマッチ
        call ena_check(_hd_target)

    elif _home_mood >= 3:
        # プレイヤーから提案が必要
        menu:
            "泊まってく？":
                if _hd_target == "misaki":
                    misaki_c "...いいの？"
                    "美咲が泊まることになった。"
                    $ change_stamina(30)
                    $ change_cleanliness(15)
                    $ change_trust(5)
                    $ change_dependence(8)
                    $ flags["misaki_stayed_at_himo"] = True
                    $ flags["misaki_stayed_himo_this_week"] = True
                    $ flags["morning_consumed"] = True
                    $ flags["kana_morning_after"] = False
                    $ flags["kana_himo_room_morning"] = False
                    $ flags["kana_at_himo_room"] = False
                    $ location_flags["staying_at_kana"] = False
                    if cold_war.get("kana_active", False):
                        $ escalate_cold_war("kana")
                else:
                    kana_c "いいの？やった！"
                    "カナが泊まることになった。"
                    $ change_stamina(20)
                    $ change_trust_kana(5)
                    $ change_dependence_kana(8)
                    $ flags["kana_at_himo_room"] = True
                    $ flags["kana_himo_room_morning"] = True
                    $ flags["kana_stayed_himo_this_week"] = True
                    $ stats["kana_stayed_himo_room"] = stats.get("kana_stayed_himo_room", 0) + 1
                    if cold_war.get("misaki_active", False):
                        $ escalate_cold_war("misaki")
                call ena_check(_hd_target)

            "今日は送るよ":
                if _hd_target == "misaki":
                    misaki_c "...うん、ありがとう"
                    $ change_dependence(3)
                else:
                    kana_c "え〜..."
                    $ change_dependence_kana(3)

    else:
        # ムード不足で泊まり不可
        if _hd_target == "misaki":
            misaki_c "...今日は帰るね"
            $ change_trust(-2)
        else:
            kana_c "...なんか今日微妙。帰る"
            $ change_trust_kana(-3)

    # 酒ルートのお金交渉（美咲のみ・泊まり判定の後）
    if _hd_target == "misaki" and flags.get("sake_bonus_active", False):
        menu:
            "（酔ってる今なら...お金の話ができるかも）":
                call misaki_negotiation_start
                $ flags["izakaya_money_hangover"] = True

            "（やめとこう）":
                pass

    $ flags["sake_bonus_active"] = False

    return
