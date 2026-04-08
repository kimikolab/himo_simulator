# ena_match.rpy
# Phase 4 Step 3: 簡易えなマッチ（5段階選択肢ベースミニゲーム）

init python:
    # === 段階1: ムード作り選択肢プール ===
    ena_mood_choices = {
        "gentle_approach": {
            "text": "自然に距離を詰める",
            "icon": "\u2663",
            "misaki": {"acquaintance": 1, "friend": 2, "close": 2, "dating": 1},
            "kana":  {"acquaintance": 1, "friend": 1, "close": 1, "dating": 1},
        },
        "sweet_words": {
            "text": "甘い言葉をかける",
            "icon": "\u2665",
            "misaki": {"acquaintance": 0, "friend": 1, "close": 1, "dating": 2},
            "kana":  {"acquaintance": 1, "friend": 2, "close": 2, "dating": 2},
        },
        "touch_hair": {
            "text": "髪に触れる",
            "icon": "\u2663",
            "misaki": {"acquaintance": 0, "friend": 1, "close": 2, "dating": 2},
            "kana":  {"acquaintance": 0, "friend": 1, "close": 1, "dating": 1},
        },
        "eye_contact": {
            "text": "じっと目を見つめる",
            "icon": "\u2665",
            "misaki": {"acquaintance": 1, "friend": 1, "close": 2, "dating": 1},
            "kana":  {"acquaintance": 0, "friend": 0, "close": 1, "dating": 1},
        },
        "make_laugh": {
            "text": "ふざけて笑わせる",
            "icon": "\u2660",
            "misaki": {"acquaintance": 1, "friend": 1, "close": 0, "dating": 0},
            "kana":  {"acquaintance": 2, "friend": 2, "close": 1, "dating": 1},
        },
        "sit_quietly": {
            "text": "黙って隣にいる",
            "icon": "\u2666",
            "misaki": {"acquaintance": 1, "friend": 2, "close": 2, "dating": 2},
            "kana":  {"acquaintance": 0, "friend": 0, "close": 0, "dating": 1},
        },
        "hold_hand": {
            "text": "手を握る",
            "icon": "\u2663",
            "misaki": {"acquaintance": 0, "friend": 1, "close": 1, "dating": 2},
            "kana":  {"acquaintance": 1, "friend": 1, "close": 2, "dating": 1},
        },
        "hug_behind": {
            "text": "後ろから抱きしめる",
            "icon": "\u2665",
            "misaki": {"acquaintance": -1, "friend": 0, "close": 1, "dating": 2},
            "kana":  {"acquaintance": 0, "friend": 1, "close": 2, "dating": 2},
        },
        # v1.1追加コマンド
        "shoulder_massage": {
            "text": "肩を揉んであげる",
            "icon": "\u2663",
            "misaki": {"acquaintance": 0, "friend": 1, "close": 2, "dating": 2},
            "kana":  {"acquaintance": 0, "friend": 0, "close": 1, "dating": 1},
        },
        "cook_something": {
            "text": "なにか作ってあげる",
            "icon": "\u2666",
            "misaki": {"acquaintance": 0, "friend": 1, "close": 2, "dating": 2},
            "kana":  {"acquaintance": 1, "friend": 1, "close": 1, "dating": 1},
            "requires": "inventory_groceries",
        },
        "show_meme": {
            "text": "面白い動画を見せる",
            "icon": "\u2660",
            "misaki": {"acquaintance": 1, "friend": 1, "close": 0, "dating": 0},
            "kana":  {"acquaintance": 2, "friend": 2, "close": 1, "dating": 0},
        },
        "whisper_ear": {
            "text": "耳元で囁く",
            "icon": "\u2665",
            "misaki": {"acquaintance": -1, "friend": 0, "close": 1, "dating": 2},
            "kana":  {"acquaintance": 0, "friend": 1, "close": 2, "dating": 2},
        },
    }

    # === 段階1: 地雷コマンドプール（16日目以降に混入） ===
    ena_trap_choices = {
        "check_phone": {
            "text": "スマホを確認する",
            "icon": "\u2666",
            "misaki": {"acquaintance": -2, "friend": -2, "close": -2, "dating": -2},
            "kana":  {"acquaintance": -1, "friend": -2, "close": -2, "dating": -2},
            "is_trap": True,
        },
        "talk_about_ex": {
            "text": "昔の話をする",
            "icon": "\u2660",
            "misaki": {"acquaintance": -1, "friend": -1, "close": -2, "dating": -2},
            "kana":  {"acquaintance": 0, "friend": -1, "close": -2, "dating": -2},
            "is_trap": True,
        },
        "yawn_loudly": {
            "text": "大きくあくびする",
            "icon": "\u2663",
            "misaki": {"acquaintance": -1, "friend": -1, "close": -1, "dating": -1},
            "kana":  {"acquaintance": -1, "friend": -1, "close": -2, "dating": -2},
            "is_trap": True,
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
        # v1.1追加
        {
            "sign_text": "美咲がため息をついた。",
            "best": "共感", "good": "自然", "miss": "積極",
        },
        {
            "sign_text": "美咲がこちらの服の袖を掴んだ。",
            "best": "静か", "good": "触れる", "miss": "言葉",
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
        # v1.1追加
        {
            "sign_text": "カナが自撮りを撮ろうとしている。",
            "best": "受け止める", "good": "褒める", "miss": "流す",
        },
        {
            "sign_text": "カナが急に黙った。",
            "best": "応える", "good": "待つ", "miss": "積極",
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
            "text": "「好きだよ」と囁く", "type": "words",
            "misaki_link": True, "kana_link": False,
            "misaki_trust": 3, "kana_trust": 2,
        },
        "say_thanks": {
            "text": "「ありがとう」と伝える", "type": "words",
            "misaki_link": False, "kana_link": False,
            "misaki_trust": 2, "kana_trust": 1,
        },
        "stroke_hair": {
            "text": "（髪を撫でる）", "type": "action",
            "misaki_link": True, "kana_link": False,
            "misaki_trust": 3, "kana_trust": 2,
        },
        "praise": {
            "text": "「最高だった」", "type": "words",
            "misaki_link": False, "kana_link": True,
            "misaki_trust": 1, "kana_trust": 3,
        },
        "want_again": {
            "text": "「また会いたい」と言う", "type": "words",
            "misaki_link": False, "kana_link": True,
            "misaki_trust": 2, "kana_trust": 3,
        },
        "arm_pillow": {
            "text": "そのまま腕枕する", "type": "action",
            "misaki_link": True, "kana_link": False,
            "misaki_trust": 3, "kana_trust": 0,
        },
        "ask_breakfast": {
            "text": "「明日何食べたい？」", "type": "words",
            "misaki_link": False, "kana_link": False,
            "misaki_trust": 2, "kana_trust": 2,
        },
    }

    # === Part 3: 状態依存テキストプール ===

    # 段階4: 成功テキスト（信頼度帯別）
    ena_success_texts = {
        "misaki": {
            "low_trust": [
                "美咲が小さく頷いた。",
                "美咲はなにも言わなかったが、抵抗もしなかった。",
                "「...いいよ」と、かすかに聞こえた。",
            ],
            "mid_trust": [
                "美咲が目を閉じた。受け入れるように。",
                "「...うん」。短い返事だった。",
                "美咲の手が、こちらの手を握り返した。",
            ],
            "high_trust": [
                "美咲が微笑んだ。安心したような顔だった。",
                "「...ありがとう」。なぜか、そう言った。",
                "美咲が自分から距離を詰めてきた。",
            ],
        },
        "kana": {
            "low_trust": [
                "カナは少し驚いた顔をしたが、離れなかった。",
                "「...ふーん、やるじゃん」",
                "カナがスマホを置いた。それが答えだった。",
            ],
            "mid_trust": [
                "カナが「えへへ」と笑った。",
                "「...待ってた」と小さく言われた。",
                "カナが腕に絡みついてきた。",
            ],
            "high_trust": [
                "カナが「好き」と言った。真っ直ぐな目で。",
                "カナが離れようとしない。離さないように。",
                "「...もう帰さないから」",
            ],
        },
    }

    # 段階4: 失敗テキスト（ムード帯別）
    ena_fail_texts = {
        "misaki": {
            "low_mood": [
                "美咲がそっと体を離した。",
                "「...ごめん、今日はちょっと」",
                "空気がぎこちなくなった。",
            ],
            "mid_mood": [
                "いい感じだったのに、なぜか噛み合わなかった。",
                "美咲「...疲れてるの？」",
                "タイミングが悪かったらしい。",
            ],
        },
        "kana": {
            "low_mood": [
                "カナが「は？」と言った。冷たい声だった。",
                "急すぎたらしい。カナがスマホを手に取った。",
                "「...空気読めないんだね」",
            ],
            "mid_mood": [
                "カナ「なんか違う」",
                "惜しかった気がする。カナが寝返りを打った。",
                "「...今日はいいや」",
            ],
        },
    }

    def _get_partner_state_text(target, stage, mood):
        """コマンドバトルUI用: 相手の状態テキストを返す"""
        if target == "misaki":
            if mood >= 4:
                return "美咲が目を閉じている。\n受け入れるような空気。"
            elif mood >= 2:
                return "美咲は穏やかな表情を\nしている。"
            else:
                return "美咲はどこか落ち着かない\n様子だ。"
        else:
            if mood >= 4:
                return "カナが離れようとしない。\n期待している目。"
            elif mood >= 2:
                return "カナがこちらを見ている。\n悪くない雰囲気。"
            else:
                return "カナが少し退屈そうだ。"

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

        # v2.0: 自宅デートからの流入ボーナス
        _mood += home_date_mood_bonus
        home_date_mood_bonus = 0

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

    # === 不測事態判定（段階4成功後） ===
    if _ena_match_success:
        python:
            _extra_round = False

            if _em_target == "kana":
                _depend = kana["dependence"]
            else:
                _depend = misaki["dependence"]

            if _depend >= 50:
                _day_bonus = max(0, (game_date["day"] - 15)) * 0.01
                _extra_rate = 0.10 + (_depend - 50) * 0.005 + _day_bonus
                if renpy.random.random() < _extra_rate:
                    _extra_round = True

            log_action("ENA_EXTRA_ROUND", _em_target + " rate=" + str(_extra_rate if _depend >= 50 else 0) + " triggered=" + str(_extra_round))

        if _extra_round:
            call ena_extra_round(_em_target)

    # === 段階5: アフターケア ===
    if _ena_match_success:
        call ena_stage5(_em_target)

    $ log_action("ENA_DIFFICULTY", "day=" + str(game_date["day"]) + " trap_rate=" + str(0.20 + max(0, game_date["day"] - 16) * 0.02 if game_date["day"] >= 16 else 0) + " extra_bonus=" + str(max(0, (game_date["day"] - 15)) * 0.01))

    return


# ========================================
# 段階1: ムード作り
# ========================================

label ena_stage1(target):
    $ _s1_target = target

    python:
        # 条件付きコマンドをフィルタリングしてプール構築
        _pool = []
        for key, data in ena_mood_choices.items():
            req = data.get("requires", None)
            if req == "inventory_groceries" and inventory.get("groceries", 0) <= 0:
                continue
            _pool.append(key)
        renpy.random.shuffle(_pool)
        _picked = _pool[:3]
        _stage_key = get_stage_key(_s1_target)

        # 地雷混入判定（16日目以降）
        _trap_key_used = None
        if game_date["day"] >= 16:
            _trap_rate = 0.20 + (game_date["day"] - 16) * 0.02
            if renpy.random.random() < _trap_rate:
                _trap_key_used = renpy.random.choice(list(ena_trap_choices.keys()))
                _replace_idx = renpy.random.randint(0, 2)
                _picked[_replace_idx] = _trap_key_used

        # コマンドUIデータ構築
        _commands = []
        for key in _picked:
            if key in ena_mood_choices:
                _cmd_data = ena_mood_choices[key]
            else:
                _cmd_data = ena_trap_choices[key]
            _commands.append({
                "key": key,
                "text": _cmd_data["text"],
                "icon": _cmd_data.get("icon", "\u2666"),
            })

        _state_text = _get_partner_state_text(_s1_target, "stage1", _mood)

    "夜も更けてきた。"
    "二人きりの空間。"

    $ log_action("ENA_UI", "stage=1 commands=" + ",".join(_picked) + " trap=" + str(_trap_key_used if _trap_key_used else "none"))

    # コマンドバトルUI表示
    window hide
    $ _s1_choice = renpy.call_screen("ena_command_menu", commands=_commands, mood_current=_mood, mood_max=6, state_text=_state_text, can_retreat=False)

    python:
        # 通常コマンドか地雷コマンドかでデータソースを切り替え
        if _s1_choice in ena_mood_choices:
            _s1_data = ena_mood_choices[_s1_choice]
        else:
            _s1_data = ena_trap_choices[_s1_choice]
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

        # コピーして操作（元データを壊さないため）
        _sign_data = dict(_sign)

        # 20日目以降、15%の確率でbest/goodが入れ替わる（ミスリード）
        _mislead = False
        if game_date["day"] >= 20 and renpy.random.random() < 0.15:
            _temp = _sign_data["best"]
            _sign_data["best"] = _sign_data["good"]
            _sign_data["good"] = _temp
            _mislead = True

        _best_cat = _sign_data["best"]
        _good_cat = _sign_data["good"]
        _miss_cat = _sign_data["miss"]

        # 各カテゴリから1つずつテキストをランダム抽出（計3択）
        _best_text = renpy.random.choice(ena_response_pool[_best_cat])
        _good_text = renpy.random.choice(ena_response_pool[_good_cat])
        _miss_text = renpy.random.choice(ena_response_pool[_miss_cat])

        # コマンドUI用データ構築
        _s2_commands = [
            {"key": "best", "text": _best_text, "icon": "\u2665"},
            {"key": "good", "text": _good_text, "icon": "\u2666"},
            {"key": "miss", "text": _miss_text, "icon": "\u2660"},
        ]
        renpy.random.shuffle(_s2_commands)

        _state_text = _sign_data["sign_text"]

    $ log_action("ENA_UI", "stage=2 sign=" + _sign_data["sign_text"][:10] + " mislead=" + str(_mislead))

    # コマンドバトルUI表示（サインテキストを状態テキストとして表示）
    window hide
    $ _s2_choice = renpy.call_screen("ena_command_menu", commands=_s2_commands, mood_current=_mood, mood_max=6, state_text=_state_text, can_retreat=False)

    python:
        if _s2_choice == "best":
            _s2_delta = 2
        elif _s2_choice == "good":
            _s2_delta = 1
        else:
            _s2_delta = 0
        _mood += _s2_delta

        log_action("ENA_STAGE2", "sign=" + _sign_data["sign_text"][:10] + " choice=" + _s2_choice + " mood_delta=" + str(_s2_delta) + " mood=" + str(_mood) + " mislead=" + str(_mislead))

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

    python:
        _state_text = _get_partner_state_text(_s3_target, "stage3", _mood)

        # 段階3: 踏み込む/引くの2択をコマンドUI化
        _s3_commands = [
            {"key": "push", "text": "このまま...", "icon": "\u2665"},
        ]

    $ log_action("ENA_UI", "stage=3 mood=" + str(_mood))

    # コマンドバトルUI表示（撤退コマンドあり）
    window hide
    $ _s3_choice = renpy.call_screen("ena_command_menu", commands=_s3_commands, mood_current=_mood, mood_max=6, state_text=_state_text, can_retreat=True)

    if _s3_choice == "push":
        # 踏み込む → エナ-1確定
        $ energy -= 1
        $ energy_full_days = 0
        $ energy_charm_bonus = 0
        $ log_action("ENA_STAGE3", "decision=push")
    else:
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
        # 成功: 信頼度帯別テキスト
        python:
            if _s4_target == "misaki":
                _trust = misaki["trust"]
            else:
                _trust = kana["trust"]

            if _trust >= 80:
                _trust_tier = "high_trust"
            elif _trust >= 50:
                _trust_tier = "mid_trust"
            else:
                _trust_tier = "low_trust"

            _st = renpy.random.choice(ena_success_texts[_s4_target][_trust_tier])

        "[_st]"
        "一緒に過ごした。"

        if _s4_target == "misaki":
            $ change_dependence(15)
        else:
            $ change_dependence_kana(15)

        $ stats["ena_match_success"] = stats.get("ena_match_success", 0) + 1

    else:
        # 失敗: ムード帯別テキスト（エナは既に消費済み）
        python:
            _mood_tier = "mid_mood" if _mood >= 2 else "low_mood"
            _ft = renpy.random.choice(ena_fail_texts[_s4_target][_mood_tier])

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

        # コマンドUI用データ構築
        _ac_commands = []
        for _ack in _ac_picked:
            _ac_data_tmp = ena_aftercare_choices[_ack]
            _ac_icon = "\u2665" if _ac_data_tmp.get("type", "words") == "words" else "\u2663"
            _ac_commands.append({
                "key": _ack,
                "text": _ac_data_tmp["text"],
                "icon": _ac_icon,
            })

        _state_text = _get_partner_state_text(_s5_target, "stage5", _mood)

    $ log_action("ENA_UI", "stage=5 commands=" + ",".join(_ac_picked))

    # コマンドバトルUI表示
    window hide
    $ _s5_choice = renpy.call_screen("ena_command_menu", commands=_ac_commands, mood_current=_mood, mood_max=6, state_text=_state_text, can_retreat=False)

    python:
        _ac_data = ena_aftercare_choices[_s5_choice]

        # 連続使用減衰チェック
        _ac_history = ena_aftercare_history.get(_s5_target, [])
        _ac_repeated = _s5_choice in _ac_history[-2:] if len(_ac_history) >= 2 else _s5_choice in _ac_history

        # 信頼効果
        # v1.9: 行動系/言葉系でrepeated時の効果を分ける
        _ac_type = _ac_data.get("type", "words")
        _ac_trust = _ac_data[_s5_target + "_trust"]
        if _ac_repeated and _ac_type == "words":
            _ac_trust = max(0, _ac_trust // 2)
        # 行動系のrepeatedは信頼効果据え置き（行動の繰り返しは「習慣」として自然）

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
        if _ac_type == "action":
            # v1.9: 行動系のrepeatedは別テキスト
            if _s5_target == "misaki":
                "美咲が嬉しそうに受け入れた。"
            else:
                "カナが慣れた様子で受け入れた。"
        else:
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


# ========================================
# 不測事態: もう1ラウンド（依存度50以上で確率発生）
# ========================================

label ena_extra_round(target):
    $ _er_target = target

    if _er_target == "kana":
        kana_c "...ねえ、もう1回"
        "カナの目が離してくれない。"
    else:
        "美咲がまだこちらを見ている。"
        misaki_c "...もう少し、一緒にいたい"

    # エナが残っているかチェック
    if energy >= 1:
        menu:
            "応える":
                $ energy -= 1
                $ energy_full_days = 0
                "もう一度、一緒に過ごした。"

                if _er_target == "kana":
                    $ change_dependence_kana(10)
                    $ change_trust_kana(5)
                    kana_c "...えへへ"
                else:
                    $ change_dependence(10)
                    $ change_trust(5)
                    misaki_c "...ありがとう"

                $ log_action("ENA_EXTRA_ROUND", _er_target + " accepted=True energy=" + str(energy))

            "今日はもう無理":
                himo "（...体力の限界だ）"
                himo "ごめん、もう限界"

                if _er_target == "kana":
                    kana_c "...ちぇ"
                    $ change_trust_kana(-2)
                else:
                    misaki_c "...そうだよね、ごめん"

                $ log_action("ENA_EXTRA_ROUND", _er_target + " accepted=False")

    else:
        # エナ0 → 断るしかない
        himo "（...エナがない）"
        himo "ごめん、もう限界"

        if _er_target == "kana":
            kana_c "...使えないな"
            $ change_trust_kana(-3)
            $ add_suspicion_kana("weak_performance")
        else:
            misaki_c "...大丈夫？疲れてる？"
            $ change_trust(-2)

        $ log_action("ENA_EXTRA_ROUND", _er_target + " forced_decline energy=0")

    return
