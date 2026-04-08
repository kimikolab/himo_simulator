# ena_match.rpy
# Phase 4 Step 3: ボルテージバトル（3本ゲージ・2フェーズ制）

init python:
    # === ボルテージバトル: コマンド効果テキスト ===
    ena_command_texts = {
        "stare":         "じっと見つめた。",
        "joke":          "ふざけて笑わせた。",
        "kiss":          "キスをした。",
        "wait":          "じっと様子を見た。",
        "normal":        "ペースを保った。",
        "rush":          "攻めの姿勢に出た。",
        "slow":          "ペースを落とした。",
        "return_out":    "一度体勢を戻した。",
    }

    # マッサージ系: ターゲット別テキストプール
    ena_massage_texts = {
        "massage_upper": {
            "misaki": [
                "上半身をゆっくり撫でた。美咲が小さく息を飲んだ。",
                "胸元に手を滑らせた。美咲が目を閉じた。",
                "優しく触れた。美咲の体が少し震えた。",
            ],
            "kana": [
                "上半身をゆっくり撫でた。カナが「...ん」と声を漏らした。",
                "胸元に手を伸ばした。カナが目を逸らした。",
                "触れた瞬間、カナの体がびくっとした。",
            ],
        },
        "massage_lower": {
            "misaki": [
                "下半身に手を伸ばした。美咲が声を抑えた。",
                "太ももから、ゆっくりと。美咲が唇を噛んだ。",
                "敏感な場所に触れた。美咲の呼吸が変わった。",
            ],
            "kana": [
                "下半身に手を滑らせた。カナが「...っ」と息を詰めた。",
                "太ももに触れた。カナが足を閉じかけて、やめた。",
                "敏感な場所に触れた。カナが枕に顔を埋めた。",
            ],
        },
    }

    # === ボルテージバトル: 相手の技プール（Phase A: 低信頼のみ） ===

    # 美咲の技（低信頼: 受け身・無自覚型）
    ena_misaki_skills = [
        {
            "name": "うるんだ瞳",
            "vol_self": 2,
            "texts": [
                "美咲が上目遣いでじっと見ている...",
                "美咲の瞳が潤んでいる。無意識なのが一番効く。",
                "ふと目が合った。美咲の目が揺れている。",
            ],
        },
        {
            "name": "沈黙",
            "vol_self": 2,
            "texts": [
                "美咲は何も言わない。ただ、じっと見つめている。",
                "美咲が黙っている。その沈黙が、逆に効く。",
                "何も言わない美咲。でも、手は離さなかった。",
            ],
        },
        {
            "name": "いい匂い",
            "vol_self": 1,
            "texts": [
                "ふわっと、美咲の髪からいい匂いがした。",
                "美咲が近づいた。シャンプーの匂い。",
                "美咲の首筋から、甘い香りがした。",
            ],
        },
    ]

    # カナの技（低信頼: 挑発的・攻撃的）
    ena_kana_skills = [
        {
            "name": "口撃",
            "vol_self": 3,
            "texts": [
                "カナの口撃！ヒモ太郎は声を殺した...！",
                "カナの口撃！...慣れた手つきだ。容赦ない。",
                "カナの口撃！「動かないで」...これはきつい。",
            ],
        },
        {
            "name": "まとわりつき",
            "vol_self": 2,
            "texts": [
                "カナが離れようとしない。",
                "カナが体を押し付けてきた。",
                "カナの体温が伝わってくる。離れない。",
            ],
        },
        {
            "name": "あまえる",
            "vol_self": 1,
            "texts": [
                "カナが甘えた声を出した。",
                "カナが腕にしがみついてきた。",
                "「ねえ...」カナが小さく呼んだ。",
            ],
        },
    ]


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
        call ena_battle(target)
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
            call ena_battle(_ena_target)
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
# ボルテージバトル本体（Phase A）
# ========================================

label ena_battle(target):
    # === 初期化 ===
    $ _mood = 0
    $ _vol_self = 0
    $ _vol_partner = 0
    $ _phase = "outfight"
    $ _spark_count = 0
    $ _released = False
    $ _turn = 0

    # 自宅デートからの流入ボーナス（ムード初期値）
    python:
        _effective_charm = player["charm"] + energy_charm_bonus
        if _effective_charm >= 70:
            _mood += 2
        elif _effective_charm >= 55:
            _mood += 1

        _mood += home_date_mood_bonus
        home_date_mood_bonus = 0

    # 相手の技プール構築（Phase A: 低信頼のみ）
    python:
        if target == "misaki":
            _skill_pool = list(ena_misaki_skills)
            _partner_name = "美咲"
        else:
            _skill_pool = list(ena_kana_skills)
            _partner_name = "カナ"

    $ log_action("ENA_BATTLE_START", target + " energy=" + str(energy) + " mood_init=" + str(_mood))

    # 導入テキスト
    "夜も更けてきた。二人きりの空間。"

    $ stats["ena_match_count"] = stats.get("ena_match_count", 0) + 1

    # === バトルループ ===
    label .battle_loop:
        $ _turn += 1

        # コマンドリスト構築
        python:
            _commands = []
            if _phase == "outfight":
                # アウトファイトコマンド
                _cmd_pool = [
                    {"key": "stare", "text": "見つめる", "icon": "\u2665"},
                    {"key": "joke", "text": "おふざけ", "icon": "\u2660"},
                    {"key": "massage_upper", "text": "マッサージ(上半身)", "icon": "\u2663"},
                    {"key": "wait", "text": "ようすみ", "icon": "\u2666"},
                ]
                # Stage3以上で解放
                _stage = misaki["stage"] if target == "misaki" else kana["stage"]
                if _stage >= STAGE_CLOSE:
                    _cmd_pool.append({"key": "kiss", "text": "キス", "icon": "\u2665"})
                    _cmd_pool.append({"key": "massage_lower", "text": "マッサージ(下半身)", "icon": "\u2663"})
                _commands = _cmd_pool
            else:
                # インファイトコマンド
                _commands = [
                    {"key": "normal", "text": "ノーマル", "icon": "\u2666"},
                    {"key": "rush", "text": "ラッシュ", "icon": "\u2665"},
                    {"key": "slow", "text": "スロー", "icon": "\u2666"},
                    {"key": "return_out", "text": "アウトファイトに戻る", "icon": "\u2660"},
                ]

            # 自分ボルテージの色計算（max=15）
            if _vol_self <= 9:
                _vol_self_color = "#66bbff"
            elif _vol_self <= 12:
                _vol_self_color = "#ffcc00"
            else:
                _vol_self_color = "#ff3333"

            # 状態テキスト
            if _phase == "outfight":
                if _mood >= 4:
                    _state_text = _partner_name + "の表情が変わっている..."
                elif _mood >= 2:
                    _state_text = _partner_name + "がリラックスしている。"
                else:
                    _state_text = _partner_name + "はまだ緊張している。"
            else:
                if _vol_partner >= 7:
                    _state_text = _partner_name + "の息が荒くなっている...！"
                elif _vol_partner >= 4:
                    _state_text = _partner_name + "が声を抑えている。"
                else:
                    _state_text = _partner_name + "はまだ余裕がありそうだ。"

        # スクリーン呼び出し
        window hide
        $ _result = renpy.call_screen("ena_battle_ui",
            commands=_commands,
            mood=_mood, mood_max=6,
            vol_self=_vol_self, vol_self_max=15,
            vol_partner=_vol_partner, vol_partner_max=10,
            state_text=_state_text,
            phase=_phase,
            can_infight=(_phase == "outfight" and _mood >= 4),
            can_retreat=(_phase == "outfight"),
            partner_name=_partner_name
        )

        # === 特殊コマンド処理 ===
        if _result == "retreat":
            "そのまま隣で眠った。"
            # エナタメ扱い（エナ消費なし）
            if target == "misaki":
                $ change_dependence(5)
            else:
                $ change_dependence_kana(5)
            $ stats["ena_touch_count"] = stats.get("ena_touch_count", 0) + 1
            $ log_action("ENA_BATTLE_RETREAT", target)
            return

        if _result == "start_infight":
            $ _phase = "infight"
            "――空気が変わった。"
            "もう戻れない領域に踏み込んだ。"
            # エナ消費はリリース時のみ（方法A）
            $ log_action("ENA_INFIGHT_START", target + " energy=" + str(energy))
            jump .battle_loop

        # === コマンド効果適用 ===
        python:
            _cmd_effects = {
                "stare":         {"mood": 1, "vp": 0, "vs": 0},
                "joke":          {"mood": 1, "vp": 0, "vs": 0},
                "kiss":          {"mood": 2, "vp": 1, "vs": 1},
                "massage_upper": {"mood": 1, "vp": 2, "vs": 1},
                "massage_lower": {"mood": 1, "vp": 3, "vs": 2},
                "wait":          {"mood": 0, "vp": 0, "vs": -1},
                "normal":        {"mood": 0, "vp": 2, "vs": 1},
                "rush":          {"mood": 0, "vp": 3, "vs": 3},
                "slow":          {"mood": 0, "vp": 1, "vs": -1},
                "return_out":    {"mood": 0, "vp": -1, "vs": -2},
            }
            _eff = _cmd_effects[_result]
            _mood = min(6, _mood + _eff["mood"])
            _vol_partner = max(0, _vol_partner + _eff["vp"])
            _vol_self = max(0, _vol_self + _eff["vs"])

            if _result == "return_out":
                _phase = "outfight"

        # コマンドテキスト表示（マッサージ系はターゲット別プールから選択）
        python:
            if _result in ena_massage_texts:
                _cmd_text = renpy.random.choice(ena_massage_texts[_result][target])
            else:
                _cmd_text = ena_command_texts.get(_result, "...")
        "[_cmd_text]"

        # === 相手のカウンター技 ===
        python:
            _skill = renpy.random.choice(_skill_pool)
            _vol_self = min(15, _vol_self + _skill["vol_self"])
            _skill_text = renpy.random.choice(_skill["texts"])
            _skill_name = _skill["name"]

        "[_skill_text]"

        $ log_action("ENA_TURN", str(_turn) + " phase=" + _phase + " cmd=" + _result + " mood=" + str(_mood) + " vol_self=" + str(_vol_self) + " vol_partner=" + str(_vol_partner) + " counter=" + _skill_name)

        # === ゲージ上限チェック（スパーク→リリースの順で判定） ===

        # スパークチェック（先に判定することで同時到達時にシンクロ可能）
        if _vol_partner >= 10:
            "――スパーク！"
            "[_partner_name]のボルテージがオーバーフローに達した！"
            $ _spark_count += 1
            $ log_action("ENA_SPARK", target + " count=" + str(_spark_count))

        # リリースチェック
        if _vol_self >= 15:
            $ _released = True
            # フェーズ問わずエナ消費
            if energy > 0:
                $ energy -= 1
                $ energy_full_days = 0
                $ energy_charm_bonus = 0
            "――リリース！"
            "ヒモ太郎は耐えきれなかった...！"
            $ log_action("ENA_RELEASE", "vol_self=" + str(_vol_self) + " energy=" + str(energy))
            jump .battle_end

        # スパークのみ（リリースなし）→ Phase Aではスパーク1回で終了判定へ
        if _spark_count >= 1:
            jump .battle_end

        jump .battle_loop

    # === 結果判定 ===
    label .battle_end:
        python:
            if _released and _spark_count >= 1:
                _battle_result = "synchro"
            elif _released and _spark_count == 0:
                _battle_result = "too_early"
            elif not _released and _spark_count >= 1:
                _battle_result = "too_late"
            else:
                _battle_result = "dud"

        $ log_action("ENA_RESULT", _battle_result + " sparks=" + str(_spark_count) + " turns=" + str(_turn))

        # 結果テキスト
        if _battle_result == "synchro":
            if target == "misaki":
                "美咲が小さく震えた...同時だった。"
            else:
                "カナが声を上げた...同じ瞬間だった。"
            $ stats["ena_match_success"] = stats.get("ena_match_success", 0) + 1
        elif _battle_result == "too_early":
            if target == "misaki":
                misaki_c "...疲れてる？"
                "心配そうに聞いてくる。"
            else:
                kana_c "...え？もう？"
                "冷たい目。"
            $ stats["ena_match_failed"] = stats.get("ena_match_failed", 0) + 1
        elif _battle_result == "too_late":
            if target == "misaki":
                misaki_c "...私ばっかりだった！"
                "不安そうな顔。"
            else:
                kana_c "...何？終わらないの？"
                "退屈そう。"
            $ stats["ena_match_failed"] = stats.get("ena_match_failed", 0) + 1
        else:
            "気まずい沈黙が流れた。"
            $ stats["ena_match_failed"] = stats.get("ena_match_failed", 0) + 1

        # パラメータ効果
        python:
            _effects = {
                "synchro":   {"dep": 15, "trust": 5},
                "too_early": {"dep": 5, "trust": -3},
                "too_late":  {"dep": 10, "trust": -2},
                "dud":       {"dep": 3, "trust": -5},
            }
            _e = _effects[_battle_result]
            if target == "misaki":
                change_dependence(_e["dep"])
                change_trust(_e["trust"])
            else:
                change_dependence_kana(_e["dep"])
                change_trust_kana(_e["trust"])

        # エナリンク判定（シンクロ かつ ムード6）
        if _battle_result == "synchro" and _mood >= 6:
            $ ena_link_active[target] = 3
            $ stats["ena_link_count"] = stats.get("ena_link_count", 0) + 1
            $ log_action("ENA_LINK_ACTIVE", target + " days=3")
            $ renpy.notify("エナリンク成立！（3日間バフ）")
            if target == "misaki":
                "美咲が安心したように目を閉じた。"
                "（しばらく、この関係は安定しそうだ）"
            else:
                "カナが満足そうに腕を絡めてきた。"
                "（しばらく、カナの機嫌は良さそうだ）"

        return
