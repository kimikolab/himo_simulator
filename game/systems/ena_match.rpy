# ena_match.rpy
# Phase 4 Step 3: 簡易えなマッチ（5段階選択肢ベースミニゲーム）

init python:
    # === 段階1: ムード作り選択肢プール ===
    ena_mood_choices = {
        "gentle_approach": {
            "text": "自然に距離を詰める",
            "misaki": {"acquaintance": 1, "friend": 2, "close": 2, "dating": 1},
            "kana":  {"acquaintance": 1, "friend": 1, "close": 1, "dating": 1},
        },
        "sweet_words": {
            "text": "甘い言葉をかける",
            "misaki": {"acquaintance": 0, "friend": 1, "close": 1, "dating": 2},
            "kana":  {"acquaintance": 1, "friend": 2, "close": 2, "dating": 2},
        },
        "touch_hair": {
            "text": "髪に触れる",
            "misaki": {"acquaintance": 0, "friend": 1, "close": 2, "dating": 2},
            "kana":  {"acquaintance": 0, "friend": 1, "close": 1, "dating": 1},
        },
        "eye_contact": {
            "text": "じっと目を見つめる",
            "misaki": {"acquaintance": 1, "friend": 1, "close": 2, "dating": 1},
            "kana":  {"acquaintance": 0, "friend": 0, "close": 1, "dating": 1},
        },
        "make_laugh": {
            "text": "ふざけて笑わせる",
            "misaki": {"acquaintance": 1, "friend": 1, "close": 0, "dating": 0},
            "kana":  {"acquaintance": 2, "friend": 2, "close": 1, "dating": 1},
        },
        "sit_quietly": {
            "text": "黙って隣にいる",
            "misaki": {"acquaintance": 1, "friend": 2, "close": 2, "dating": 2},
            "kana":  {"acquaintance": 0, "friend": 0, "close": 0, "dating": 1},
        },
        "hold_hand": {
            "text": "手を握る",
            "misaki": {"acquaintance": 0, "friend": 1, "close": 1, "dating": 2},
            "kana":  {"acquaintance": 1, "friend": 1, "close": 2, "dating": 1},
        },
        "hug_behind": {
            "text": "後ろから抱きしめる",
            "misaki": {"acquaintance": -1, "friend": 0, "close": 1, "dating": 2},
            "kana":  {"acquaintance": 0, "friend": 1, "close": 2, "dating": 2},
        },
    }

    # === 段階2: サインプール ===
    ena_misaki_signs = [
        {
            "sign_text": "美咲が目を逸らした。",
            "best": "共感", "good": "静か", "miss": "積極",
        },
        {
            "sign_text": "美咲の肩がこわばっている。",
            "best": "触れる", "good": "共感", "miss": "言葉",
        },
        {
            "sign_text": "美咲が小さくため息をついた。",
            "best": "労う", "good": "静か", "miss": "積極",
        },
        {
            "sign_text": "美咲がじっとこちらを見ている。",
            "best": "言葉", "good": "触れる", "miss": "静か",
        },
        {
            "sign_text": "美咲が少し笑った。",
            "best": "自然", "good": "言葉", "miss": "触れる",
        },
    ]

    ena_kana_signs = [
        {
            "sign_text": "カナがスマホを置いた。",
            "best": "積極", "good": "言葉", "miss": "静か",
        },
        {
            "sign_text": "カナが甘えた声を出した。",
            "best": "受け止める", "good": "褒める", "miss": "流す",
        },
        {
            "sign_text": "カナがわざとらしく距離を取った。",
            "best": "追いかける", "good": "言葉", "miss": "待つ",
        },
        {
            "sign_text": "カナが黙ってくっついてきた。",
            "best": "受け入れる", "good": "褒める", "miss": "積極",
        },
        {
            "sign_text": "カナが「ねえ」と呼んだ。",
            "best": "応える", "good": "触れる", "miss": "流す",
        },
    ]

    # === 段階2: 反応テキストプール ===
    ena_response_pool = {
        "共感":       ["「大丈夫？」", "「無理しないで」", "「話聞くよ」"],
        "積極":       ["「こっち向いて」", "「もっと近くに」", "「離さないよ」"],
        "静か":       ["「...」（黙って寄り添う）", "「...」（肩に触れる）"],
        "触れる":     ["（髪を撫でる）", "（手を重ねる）", "（肩を抱く）"],
        "言葉":       ["「綺麗だよ」", "「今日楽しかった」", "「一緒にいると落ち着く」"],
        "労う":       ["「お疲れ様」", "「頑張ってるの知ってるよ」"],
        "自然":       ["「なに笑ってんの」", "（つられて笑う）"],
        "受け止める": ["「おいで」", "「どうした？」"],
        "褒める":     ["「可愛いな」", "「好きだわ」"],
        "追いかける": ["「逃がさないよ」", "（手を引く）"],
        "受け入れる": ["（そのまま受け入れる）", "「あったかいな」"],
        "応える":     ["「ん？」（目を合わせる）", "「なに？」（優しく）"],
        "流す":       ["「そろそろ寝るか」", "「明日早いんだよな」"],
        "待つ":       ["「...」（動かない）"],
    }

    # === 段階5: アフターケア選択肢プール ===
    ena_aftercare_choices = {
        "whisper_love": {
            "text": "「好きだよ」と囁く",
            "misaki_link": True, "kana_link": False,
            "misaki_trust": 3, "kana_trust": 2,
        },
        "say_thanks": {
            "text": "「ありがとう」と伝える",
            "misaki_link": False, "kana_link": False,
            "misaki_trust": 2, "kana_trust": 1,
        },
        "stroke_hair": {
            "text": "（髪を撫でる）",
            "misaki_link": True, "kana_link": False,
            "misaki_trust": 3, "kana_trust": 2,
        },
        "praise": {
            "text": "「最高だった」",
            "misaki_link": False, "kana_link": True,
            "misaki_trust": 1, "kana_trust": 3,
        },
        "want_again": {
            "text": "「また会いたい」と言う",
            "misaki_link": False, "kana_link": True,
            "misaki_trust": 2, "kana_trust": 3,
        },
        "arm_pillow": {
            "text": "そのまま腕枕する",
            "misaki_link": True, "kana_link": False,
            "misaki_trust": 3, "kana_trust": 0,
        },
        "ask_breakfast": {
            "text": "「明日何食べたい？」",
            "misaki_link": False, "kana_link": False,
            "misaki_trust": 2, "kana_trust": 2,
        },
    }

    def get_stage_key(target):
        """ターゲットの現在ステージをキー文字列に変換"""
        if target == "misaki":
            _st = misaki["stage"]
        else:
            _st = kana["stage"]
        return {1: "acquaintance", 2: "friend", 3: "close", 4: "dating"}.get(_st, "acquaintance")


# ========================================
# エナチェック（泊まりイベントから呼び出し）
# ========================================

label ena_check(target):
    # テスト実行時: えなマッチUIをスキップし、成功扱いで処理
    if renpy.is_in_test():
        $ energy = max(0, energy - 1)
        $ stats["ena_match_count"] = stats.get("ena_match_count", 0) + 1
        $ stats["ena_match_success"] = stats.get("ena_match_success", 0) + 1
        return

    if energy <= 0:
        call ena_zero_branch(target)
        return
    else:
        call ena_match(target)
        return


# ========================================
# エナ0時の分岐
# ========================================

label ena_zero_branch(target):
    $ _ena_target = target
    "（...やばい、エナが足りない）"

    if _ena_target == "kana":
        kana_c "ねえ...今日、いいでしょ？"
    else:
        "美咲がこちらを見ている。"

    menu:
        "断る":
            if _ena_target == "kana":
                kana_c "...え？なんで？"
                "カナが不満そうな顔をした。"
                $ change_trust_kana(-5)
                $ add_suspicion_kana("refused_ena")
            else:
                himo "...ごめん、今日は疲れてて"
                misaki_c "...そうなんだ"
                $ change_trust(-5)
                $ add_suspicion("refused_ena")

            # エナタッチで終了
            "そのまま隣で眠った。"
            if _ena_target == "kana":
                $ change_dependence_kana(5)
            else:
                $ change_dependence(5)
            $ stats["ena_touch_count"] = stats.get("ena_touch_count", 0) + 1
            return

        "栄養ドリンクを飲む" if inventory.get("energy_drink", 0) > 0:
            "こっそりエナドリを飲んだ。"
            himo "（...効いてくれ）"
            $ inventory["energy_drink"] -= 1
            $ energy += 1
            $ stats["energy_drinks_used"] = stats.get("energy_drinks_used", 0) + 1
            call ena_match(_ena_target)
            return

        "嘘でごまかす":
            himo "（なんか理由つけて...）"
            call lie_puzzle_from_ena(_ena_target)
            return

    return


label lie_puzzle_from_ena(target):
    $ _lpe_target = target
    # 嘘パズルを呼び出し（体調悪いフリ）
    call run_lie_puzzle("last_night", _lpe_target)

    if lie_puzzle["result"] == "safe" or lie_puzzle["result"] == "uneasy":
        # 成功: エナタッチ扱いで信頼微減のみ
        "なんとか体調が悪いフリでごまかした。"
        if _lpe_target == "misaki":
            misaki_c "...大丈夫？ 無理しないでね"
            $ change_trust(-2)
        else:
            kana_c "...しょうがないなー"
            $ change_trust_kana(-2)
        "そのまま隣で眠った。"
        $ stats["ena_touch_count"] = stats.get("ena_touch_count", 0) + 1
    else:
        # 失敗: バレて信頼大幅ダウン
        if _lpe_target == "misaki":
            misaki_c "...嘘でしょ。分かるよ"
            $ change_trust(-10)
            $ add_suspicion("lie_ena")
        else:
            kana_c "嘘つかないで"
            $ change_trust_kana(-10)
            $ add_suspicion_kana("lie_ena")
        "気まずい空気のまま夜が過ぎた。"

    if _lpe_target == "kana":
        $ change_dependence_kana(5)
    else:
        $ change_dependence(5)

    return


# ========================================
# えなマッチ本体: 5段階
# ========================================

label ena_match(target):
    $ _em_target = target
    $ _ena_match_success = False
    $ _ena_link = False

    # 魅力ボーナスによるムード初期値
    python:
        _effective_charm = player["charm"] + energy_charm_bonus
        if _effective_charm >= 70:
            _mood = 2
        elif _effective_charm >= 55:
            _mood = 1
        else:
            _mood = 0

    $ log_action("ENA_MATCH_START", _em_target + " energy=" + str(energy) + " mood=" + str(_mood) + " charm=" + str(_effective_charm))

    # === 段階1: ムード作り ===
    call ena_stage1(_em_target)

    # === 段階2: 反応を読む ===
    call ena_stage2(_em_target)

    # === 段階3: 踏み込む/引く ===
    call ena_stage3(_em_target)

    # 引いた場合はena_stage3内でreturn済み
    if _result_returned:
        return

    # === 段階4: 結果判定 ===
    call ena_stage4(_em_target)

    # === 段階5: アフターケア ===
    if _ena_match_success:
        call ena_stage5(_em_target)

    return


# ========================================
# 段階1: ムード作り
# ========================================

label ena_stage1(target):
    $ _s1_target = target

    python:
        _pool = list(ena_mood_choices.keys())
        renpy.random.shuffle(_pool)
        _picked = _pool[:3]
        _stage_key = get_stage_key(_s1_target)

    "夜も更けてきた。"
    "二人きりの空間。"

    # 動的メニュー: renpy.display_menu で3つの選択肢を表示
    python:
        _menu_items = []
        for _pk in _picked:
            _choice = ena_mood_choices[_pk]
            _menu_items.append((_choice["text"], _pk))

    $ _s1_choice = renpy.display_menu(_menu_items)

    python:
        _s1_data = ena_mood_choices[_s1_choice]
        _s1_delta = _s1_data[_s1_target].get(_stage_key, 0)
        _mood += _s1_delta

        # 香水ボーナス
        if inventory.get("perfume_days", 0) > 0:
            _mood += 1

        log_action("ENA_STAGE1", "choice=" + _s1_choice + " mood_delta=" + str(_s1_delta) + " mood=" + str(_mood))

    # キャラ別反応テキスト
    if _s1_delta >= 2:
        if _s1_target == "misaki":
            "美咲が少し身を寄せてきた。"
        else:
            "カナが嬉しそうに笑った。"
    elif _s1_delta >= 1:
        if _s1_target == "misaki":
            "美咲は静かに受け入れた。"
        else:
            "カナが「ふーん」と言った。"
    else:
        if _s1_target == "misaki":
            "美咲が少し身を引いた。"
        else:
            "カナが微妙な顔をした。"

    return


# ========================================
# 段階2: 反応を読む
# ========================================

label ena_stage2(target):
    $ _s2_target = target

    python:
        if _s2_target == "misaki":
            _sign = renpy.random.choice(ena_misaki_signs)
        else:
            _sign = renpy.random.choice(ena_kana_signs)

        _best_cat = _sign["best"]
        _good_cat = _sign["good"]
        _miss_cat = _sign["miss"]

        # 各カテゴリから1つずつテキストをランダム抽出（計3択）
        _best_text = renpy.random.choice(ena_response_pool[_best_cat])
        _good_text = renpy.random.choice(ena_response_pool[_good_cat])
        _miss_text = renpy.random.choice(ena_response_pool[_miss_cat])

        # メニュー構築（シャッフルして正解位置をランダム化）
        _s2_items = [
            (_best_text, "best"),
            (_good_text, "good"),
            (_miss_text, "miss"),
        ]
        renpy.random.shuffle(_s2_items)

    "[_sign['sign_text']]"

    $ _s2_choice = renpy.display_menu(_s2_items)

    python:
        if _s2_choice == "best":
            _s2_delta = 2
        elif _s2_choice == "good":
            _s2_delta = 1
        else:
            _s2_delta = 0
        _mood += _s2_delta

        log_action("ENA_STAGE2", "sign=" + _sign["sign_text"][:10] + " choice=" + _s2_choice + " mood_delta=" + str(_s2_delta) + " mood=" + str(_mood))

    # キャラ反応
    if _s2_delta >= 2:
        if _s2_target == "misaki":
            "美咲の表情がやわらいだ。"
        else:
            "カナが満足そうに笑った。"
    elif _s2_delta >= 1:
        if _s2_target == "misaki":
            "美咲が小さく頷いた。"
        else:
            "カナが「まあね」と言った。"
    else:
        if _s2_target == "misaki":
            "美咲は何も言わなかった。"
        else:
            "カナが「...ふーん」と呟いた。"

    return


# ========================================
# 段階3: 踏み込む/引く
# ========================================

label ena_stage3(target):
    $ _s3_target = target
    $ _result_returned = False

    # ムードに応じた雰囲気テキスト
    if _mood >= 4:
        "空気が変わった。"
        if _s3_target == "misaki":
            "美咲が目を閉じている。"
        else:
            "カナが離れようとしない。"
    elif _mood >= 2:
        "静かな時間が流れている。"
        if _s3_target == "misaki":
            "美咲は穏やかな表情をしている。"
        else:
            "カナがこちらを見ている。"
    else:
        "なんとなく、ぎこちない空気。"
        if _s3_target == "misaki":
            "美咲はどこか落ち着かない様子。"
        else:
            "カナが少し退屈そうだ。"

    menu:
        "このまま...":
            # 踏み込む → エナ-1確定
            $ energy -= 1
            $ energy_full_days = 0
            $ energy_charm_bonus = 0
            $ log_action("ENA_STAGE3", "decision=push")

        "今日はこのくらいで":
            # 引く → エナタッチで終了
            $ log_action("ENA_STAGE3", "decision=pull")
            "そのまま隣で眠った。"
            if _s3_target == "misaki":
                misaki_c "...おやすみ"
                $ change_dependence(5)
            else:
                kana_c "え、寝るの？...まあいいけど"
                $ change_dependence_kana(5)
                $ daily_flags["kana_mood_resolved"] = False
            $ stats["ena_touch_count"] = stats.get("ena_touch_count", 0) + 1
            $ _result_returned = True
            return

    return


# ========================================
# 段階4: 結果判定
# ========================================

label ena_stage4(target):
    $ _s4_target = target

    python:
        _success_rate = min(100, 40 + _mood * 15)
        _roll = renpy.random.randint(1, 100)
        _ena_match_success = (_roll <= _success_rate)

        log_action("ENA_STAGE4", "rate=" + str(_success_rate) + " roll=" + str(_roll) + " result=" + ("success" if _ena_match_success else "fail"))

    $ stats["ena_match_count"] = stats.get("ena_match_count", 0) + 1

    if _ena_match_success:
        # 成功
        python:
            if _s4_target == "misaki":
                _success_texts = [
                    "美咲が小さく「...うん」と頷いた。",
                    "美咲が目を閉じた。",
                    "...ありがとう、と聞こえた気がした。",
                ]
            else:
                _success_texts = [
                    "カナが「...えへへ」と笑った。",
                    "カナが腕を離さなかった。",
                    "...もう帰さないから、と囁かれた。",
                ]
            _st = renpy.random.choice(_success_texts)

        "[_st]"
        "一緒に過ごした。"

        if _s4_target == "misaki":
            $ change_dependence(15)
        else:
            $ change_dependence_kana(15)

        $ stats["ena_match_success"] = stats.get("ena_match_success", 0) + 1

    else:
        # 失敗（エナは既に消費済み）
        python:
            if _s4_target == "misaki":
                _fail_texts = [
                    "...ごめん、今日はちょっと",
                    "...疲れてるの？ 私もかな",
                ]
            else:
                _fail_texts = [
                    "なんか今日違くない？",
                    "...テンション合わない",
                ]
            _ft = renpy.random.choice(_fail_texts)

        if _s4_target == "misaki":
            misaki_c "[_ft]"
            $ change_dependence(5)
            $ change_trust(-3)
        else:
            kana_c "[_ft]"
            $ change_dependence_kana(5)
            $ change_trust_kana(-3)

        himo "...ごめん"
        "（エナを使ったのに...）"
        $ stats["ena_match_failed"] = stats.get("ena_match_failed", 0) + 1

    return


# ========================================
# 段階5: アフターケア（成功後のみ）
# ========================================

label ena_stage5(target):
    $ _s5_target = target

    python:
        _ac_pool = list(ena_aftercare_choices.keys())
        renpy.random.shuffle(_ac_pool)
        _ac_picked = _ac_pool[:3]

        _ac_menu = []
        for _ack in _ac_picked:
            _ac_menu.append((ena_aftercare_choices[_ack]["text"], _ack))

    $ _s5_choice = renpy.display_menu(_ac_menu)

    python:
        _ac_data = ena_aftercare_choices[_s5_choice]

        # 連続使用減衰チェック
        _ac_history = ena_aftercare_history.get(_s5_target, [])
        _ac_repeated = _s5_choice in _ac_history[-2:] if len(_ac_history) >= 2 else _s5_choice in _ac_history

        # 信頼効果
        _ac_trust = _ac_data[_s5_target + "_trust"]
        if _ac_repeated:
            _ac_trust = max(0, _ac_trust // 2)

        # エナリンク判定
        _ac_link_key = _s5_target + "_link"
        _ena_link = False
        if _ac_data.get(_ac_link_key, False) and _mood >= 4 and not _ac_repeated:
            _ena_link = True

        # 信頼適用
        if _s5_target == "misaki":
            change_trust(_ac_trust)
        else:
            change_trust_kana(_ac_trust)

        # 履歴更新
        _ac_history.append(_s5_choice)
        if len(_ac_history) > 3:
            _ac_history = _ac_history[-3:]
        ena_aftercare_history[_s5_target] = _ac_history

        log_action("ENA_STAGE5", "choice=" + _s5_choice + " link=" + str(_ena_link) + " repeated=" + str(_ac_repeated))

    # 反応テキスト
    if _ac_repeated:
        if _s5_target == "misaki":
            misaki_c "...前も言ってたね"
        else:
            kana_c "それ前も言った"
    else:
        if _s5_target == "misaki":
            "美咲が安心したように微笑んだ。"
        else:
            "カナが満足そうにくっついてきた。"

    # エナリンク成立（v1.7: フィードバック強化）
    if _ena_link:
        $ ena_link_active[_s5_target] = 3
        $ stats["ena_link_count"] = stats.get("ena_link_count", 0) + 1
        $ log_action("ENA_LINK_ACTIVE", _s5_target + " days=3")
        $ renpy.notify("エナリンク成立！（3日間バフ）")
        if _s5_target == "misaki":
            "美咲が安心したように目を閉じた。"
            "（しばらく、この関係は安定しそうだ）"
        else:
            "カナが満足そうに腕を絡めてきた。"
            "（しばらく、カナの機嫌は良さそうだ）"

    return
