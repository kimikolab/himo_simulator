# lie_puzzle.rpy
# 嘘パズル＋タイマー — 修羅場で制限時間内に矛盾しない言い訳を選ぶ

init python:
    def get_lie_time_limit():
        """嘘スキルに応じた制限時間を返す"""
        lie_skill = himo_aptitude.get("lie_skill", 0)
        if lie_skill >= 15:
            return LIE_TIME_LV2
        elif lie_skill >= 5:
            return LIE_TIME_LV1
        else:
            return LIE_TIME_LV0

    def get_lie_skill_level():
        lie_skill = himo_aptitude.get("lie_skill", 0)
        if lie_skill >= 15:
            return 2
        elif lie_skill >= 5:
            return 1
        else:
            return 0

    def check_contradiction(new_answer, previous_answers):
        """前の回答と矛盾するか判定"""
        contradictions = {
            ("sleeping", "was_awake"): True,
            ("sleeping", "went_out"): True,
            ("at_home", "went_out"): True,
            ("working", "no_job"): True,
            ("with_friend", "alone"): True,
        }
        for prev in previous_answers:
            if (prev, new_answer) in contradictions or (new_answer, prev) in contradictions:
                return True
        return False

    def resolve_lie_puzzle(bare_gauge):
        """バレ度に基づいて結果を返す"""
        if bare_gauge >= BARE_MAX:
            return "busted"        # 完全にバレた
        elif bare_gauge >= 60:
            return "suspicious"    # 強い疑念（v1.2: 70→60）
        elif bare_gauge >= 30:
            return "uneasy"        # 不穏な空気（v1.2: 40→30）
        else:
            return "safe"          # 乗り切った


# 嘘パズルのタイマー付き選択肢用screen
screen lie_puzzle_choice(choices, time_limit):
    # バレ度ゲージ
    frame:
        xalign 0.5
        yalign 0.05
        padding (20, 10)
        background "#00000088"

        hbox:
            spacing 10
            text "バレ度: " size 22 color "#ffffff"
            bar:
                value lie_puzzle["bare_gauge"]
                range BARE_MAX
                xsize 300
                ysize 20
                left_bar "#ff4444"
                right_bar "#333333"

    # タイマー表示
    timer time_limit action [SetVariable("lie_puzzle_timeout", True), Return("timeout")]

    frame:
        xalign 0.5
        yalign 0.15
        padding (15, 8)
        background "#00000088"

        bar:
            value AnimatedValue(0, time_limit, time_limit, 0)
            xsize 400
            ysize 8
            left_bar "#ffaa00"
            right_bar "#333333"

    # 選択肢
    vbox:
        xalign 0.5
        yalign 0.75
        spacing 12

        for choice in choices:
            textbutton choice["text"]:
                action Return(choice["key"])
                text_size 22
                xminimum 500
                xalign 0.5


# 汎用嘘パズル呼び出しラベル
label run_lie_puzzle(scenario="generic", target="misaki"):
    $ lie_puzzle["active"] = True
    $ lie_puzzle["bare_gauge"] = 0
    $ lie_puzzle["previous_answers"] = []
    $ lie_puzzle_timeout = False

    # テスト実行時: パズルUIをスキップし、安全クリアとして処理
    if renpy.is_in_test():
        $ lie_puzzle["result"] = "safe"
        $ lie_puzzle["active"] = False
        return

    if scenario == "last_night":
        call lie_puzzle_last_night(target)
    elif scenario == "other_woman":
        call lie_puzzle_other_woman(target)
    elif scenario == "double_booking":
        call lie_puzzle_double_booking(target)
    elif scenario == "evidence_trace" or scenario == "apology_dodge":
        # Phase 4 Step 2.5: 痕跡イベント・謝罪ごまかしは other_woman と同じパズルを使用
        # 難易度はターゲットで変化
        call lie_puzzle_other_woman(target)

    # 結果判定
    python:
        # Phase 4 v1.3: 正直ルートで直接設定された場合はスキップ
        if lie_puzzle.get("result", None) != "honest":
            result = resolve_lie_puzzle(lie_puzzle["bare_gauge"])
            lie_puzzle["result"] = result
        else:
            result = "honest"
        lie_puzzle["active"] = False
        # Phase 4 v1.1: 統計カウント
        stats["lie_puzzles_faced"] = stats.get("lie_puzzles_faced", 0) + 1

    # Phase 4 v1.3: 正直ルートは専用処理（lie_puzzle内で既に処理済み）
    if result == "honest":
        return

    if result == "busted":
        "（完全にバレた...）"
        $ stats["lie_puzzles_busted"] = stats.get("lie_puzzles_busted", 0) + 1
        if target == "misaki":
            $ change_trust(-20)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 30, SUSPICION_MAX)
        else:
            $ change_trust_kana(-20)
            $ suspicion["kana"] = min(suspicion["kana"] + 30, SUSPICION_MAX)
    elif result == "suspicious":
        "（...怪しまれてる）"
        if target == "misaki":
            $ change_trust(-10)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 15, SUSPICION_MAX)
        else:
            $ change_trust_kana(-10)
            $ suspicion["kana"] = min(suspicion["kana"] + 15, SUSPICION_MAX)
    elif result == "uneasy":
        "（なんとか誤魔化せた...かな）"
        if target == "misaki":
            $ suspicion["misaki"] = min(suspicion["misaki"] + 5, SUSPICION_MAX)
        else:
            $ suspicion["kana"] = min(suspicion["kana"] + 5, SUSPICION_MAX)
    else:
        "（...乗り切った）"
        # 嘘スキル経験値
        $ himo_aptitude["lie_skill"] = himo_aptitude.get("lie_skill", 0) + 1

    $ himo_aptitude["lies"] += 1
    $ stats["lies_told"] += 1

    return


# --- 嘘パズルシナリオ: 昨日の夜 ---

label lie_puzzle_last_night(target="misaki"):
    python:
        skill_lv = get_lie_skill_level()
        time_limit = get_lie_time_limit()

    if target == "misaki":
        misaki_c "昨日の夜、何してたの？LINE返ってこなかったけど"
    else:
        kana_c "昨日の夜なにしてたの？既読つかなかったんだけど"

    # --- 第1段階 ---
    python:
        choices = [
            {"key": "sleeping", "text": "寝てた", "quality": "good"},
            {"key": "was_awake", "text": "起きてたけど気づかなかった", "quality": "ok"},
        ]
        if skill_lv == 0:
            choices += [
                {"key": "dog_walk", "text": "犬の散歩してた", "quality": "terrible"},
                {"key": "space", "text": "宇宙のことを考えてた", "quality": "terrible"},
            ]
            renpy.random.shuffle(choices)
        elif skill_lv == 1:
            choices += [
                {"key": "friend", "text": "友達と飲んでた", "quality": "ok"},
            ]
        else:
            choices += [
                {"key": "friend", "text": "友達と飲んでた", "quality": "ok"},
                {"key": "battery", "text": "充電切れてて気づかなかった", "quality": "good"},
            ]

    call screen lie_puzzle_choice(choices, time_limit)
    $ answer1 = _return

    if answer1 == "timeout":
        "ヒモ太郎「え...あ...」"
        $ lie_puzzle["bare_gauge"] += BARE_SILENCE
        return

    python:
        lie_puzzle["previous_answers"].append(answer1)
        if answer1 in ["dog_walk", "space"]:
            lie_puzzle["bare_gauge"] += BARE_CONTRADICTION
        elif answer1 in ["sleeping", "battery"]:
            lie_puzzle["bare_gauge"] += BARE_PERFECT
        else:
            lie_puzzle["bare_gauge"] += BARE_WEAK

    # --- 第2段階（追及） ---
    if answer1 == "sleeping":
        if target == "misaki":
            misaki_c "寝てた？22時に既読ついてたけど？"
        else:
            kana_c "寝てた？でもインスタのストーリー見てたよね？"

        python:
            choices2 = [
                {"key": "fell_asleep_after", "text": "既読つけてからすぐ寝ちゃった", "quality": "good"},
                {"key": "dont_remember", "text": "覚えてない", "quality": "ok"},
            ]
            if skill_lv == 0:
                choices2 += [
                    {"key": "went_out", "text": "友達と飲んでた", "quality": "contradiction"},
                    {"key": "lent_phone", "text": "スマホ誰かに貸してた", "quality": "terrible"},
                ]
                renpy.random.shuffle(choices2)
            elif skill_lv >= 1:
                choices2 += [
                    {"key": "half_asleep", "text": "半分寝ぼけてて覚えてない", "quality": "good"},
                ]

        call screen lie_puzzle_choice(choices2, time_limit)
        $ answer2 = _return

        if answer2 == "timeout":
            "ヒモ太郎「...」"
            $ lie_puzzle["bare_gauge"] += BARE_SILENCE
            return

        python:
            if answer2 == "went_out":
                # 「寝てた」と矛盾
                lie_puzzle["bare_gauge"] += BARE_CONTRADICTION
            elif answer2 == "lent_phone":
                lie_puzzle["bare_gauge"] += BARE_CONTRADICTION
            elif answer2 in ["fell_asleep_after", "half_asleep"]:
                lie_puzzle["bare_gauge"] += BARE_PERFECT
            else:
                lie_puzzle["bare_gauge"] += BARE_WEAK

    elif answer1 == "friend":
        if target == "misaki":
            misaki_c "誰と？"
        else:
            kana_c "え、誰と？"

        python:
            choices2 = [
                {"key": "old_friend", "text": "地元の友達", "quality": "ok"},
                {"key": "vague", "text": "いろんな人", "quality": "weak"},
            ]
            if skill_lv == 0:
                choices2 += [
                    {"key": "alone", "text": "一人で", "quality": "contradiction"},
                ]
                renpy.random.shuffle(choices2)
            elif skill_lv >= 1:
                choices2 += [
                    {"key": "specific", "text": "高校の時の健太ってやつ", "quality": "good"},
                ]

        call screen lie_puzzle_choice(choices2, time_limit)
        $ answer2 = _return

        if answer2 == "timeout":
            "ヒモ太郎「えーっと...」"
            $ lie_puzzle["bare_gauge"] += BARE_SILENCE
            return

        python:
            if answer2 == "alone":
                lie_puzzle["bare_gauge"] += BARE_CONTRADICTION
            elif answer2 == "specific":
                lie_puzzle["bare_gauge"] += BARE_PERFECT
            elif answer2 == "old_friend":
                lie_puzzle["bare_gauge"] += BARE_WEAK
            else:
                lie_puzzle["bare_gauge"] += BARE_WEAK + 5

    return


# --- 嘘パズルシナリオ: 他に女がいるでしょ ---

label lie_puzzle_other_woman(target="misaki"):
    python:
        skill_lv = get_lie_skill_level()
        time_limit = get_lie_time_limit()

    if target == "misaki":
        misaki_c "...ねえ、正直に答えて"
        misaki_c "他に女の人、いるでしょ"
    else:
        kana_c "ねえ、他に会ってる女いる？"

    # --- 第1段階 ---
    python:
        choices = [
            {"key": "deny", "text": "いないよ", "quality": "ok"},
            {"key": "honest", "text": "...正直に言うと", "quality": "special"},
        ]
        if skill_lv == 0:
            choices += [
                {"key": "panic", "text": "な、なんで？", "quality": "terrible"},
                {"key": "reverse", "text": "お前こそ他にいるんじゃないの？", "quality": "terrible"},
            ]
            renpy.random.shuffle(choices)
        elif skill_lv >= 1:
            choices += [
                {"key": "deflect", "text": "なんでそう思うの？", "quality": "good"},
            ]
        if skill_lv >= 2:
            choices += [
                {"key": "charm", "text": "お前以外に誰がいるんだよ", "quality": "good"},
            ]

    call screen lie_puzzle_choice(choices, time_limit)
    $ answer1 = _return

    if answer1 == "timeout":
        "ヒモ太郎「...」"
        "沈黙が全てを物語っていた。"
        $ lie_puzzle["bare_gauge"] += BARE_SILENCE + 20
        return

    if answer1 == "honest":
        # 正直ルート — 嘘パズル中断、別の分岐へ
        "ヒモ太郎「...正直に言うと、他にも会ってる人がいる」"
        if target == "misaki":
            misaki_c "...やっぱり"
            "長い沈黙。"
            misaki_c "...分かってた。薄々"
            $ change_trust(-15)
            $ himo_aptitude["honest_moments"] += 2
            # 正直に言ったので疑念はリセット寄り
            $ suspicion["misaki"] = max(suspicion["misaki"] - 10, 0)
        else:
            kana_c "...は？マジで？"
            $ change_trust_kana(-15)
            $ himo_aptitude["honest_moments"] += 2
            $ suspicion["kana"] = max(suspicion["kana"] - 10, 0)
        # Phase 4 v1.3: 正直ルート専用の結果コードを設定
        $ lie_puzzle["bare_gauge"] = 0
        $ lie_puzzle["result"] = "honest"
        return

    python:
        if answer1 in ["panic", "reverse"]:
            lie_puzzle["bare_gauge"] += BARE_CONTRADICTION
        elif answer1 in ["deflect", "charm"]:
            lie_puzzle["bare_gauge"] += BARE_PERFECT
        else:
            lie_puzzle["bare_gauge"] += BARE_WEAK

    # --- 第2段階（証拠提示） ---
    if target == "misaki":
        misaki_c "...最近LINE返すの遅いし、予定よく断るし"
        misaki_c "前は暇だ暇だって言ってたのに"
    else:
        kana_c "最近忙しそうだし、夜連絡つかない時あるし"

    python:
        choices2 = [
            {"key": "job_hunting", "text": "就活始めたんだよ", "quality": "good"},
            {"key": "tired", "text": "最近疲れてて...", "quality": "ok"},
        ]
        if skill_lv == 0:
            choices2 += [
                {"key": "nothing", "text": "別に何もないって", "quality": "weak"},
            ]
            renpy.random.shuffle(choices2)
        elif skill_lv >= 1:
            choices2 += [
                {"key": "worry", "text": "心配してくれてるの？ありがとう", "quality": "good"},
            ]

    call screen lie_puzzle_choice(choices2, time_limit)
    $ answer2 = _return

    if answer2 == "timeout":
        "ヒモ太郎「...」"
        $ lie_puzzle["bare_gauge"] += BARE_SILENCE
        return

    python:
        if answer2 == "nothing":
            lie_puzzle["bare_gauge"] += BARE_WEAK + 10
        elif answer2 in ["job_hunting", "worry"]:
            lie_puzzle["bare_gauge"] += BARE_PERFECT
        else:
            lie_puzzle["bare_gauge"] += BARE_WEAK

    return


# --- 嘘パズルシナリオ: ダブルブッキング時の断り ---

label lie_puzzle_double_booking(target="misaki"):
    python:
        skill_lv = get_lie_skill_level()
        time_limit = get_lie_time_limit()

    if target == "misaki":
        misaki_c "今夜会えない？"
    else:
        kana_c "今夜暇？会いたい"

    himo "あー、今日はちょっと..."

    if target == "misaki":
        misaki_c "えっ、なんで？"
    else:
        kana_c "え〜、なんで？"

    python:
        choices = [
            {"key": "tired", "text": "体調悪くて", "quality": "ok"},
            {"key": "errand", "text": "用事があって", "quality": "weak"},
        ]
        if skill_lv == 0:
            choices += [
                {"key": "work", "text": "バイトの面接", "quality": "terrible"},
                {"key": "vague", "text": "えーっと...なんか色々", "quality": "terrible"},
            ]
            renpy.random.shuffle(choices)
        elif skill_lv >= 1:
            choices += [
                {"key": "friend", "text": "友達に呼ばれてて", "quality": "good"},
            ]
        if skill_lv >= 2:
            choices += [
                {"key": "tomorrow", "text": "明日なら空いてる。明日がいい", "quality": "good"},
            ]

    call screen lie_puzzle_choice(choices, time_limit)
    $ answer1 = _return

    if answer1 == "timeout":
        "ヒモ太郎「...あ、えっと」"
        $ lie_puzzle["bare_gauge"] += BARE_SILENCE
    else:
        python:
            if answer1 in ["work", "vague"]:
                lie_puzzle["bare_gauge"] += BARE_CONTRADICTION
            elif answer1 in ["friend", "tomorrow"]:
                lie_puzzle["bare_gauge"] += BARE_PERFECT
            elif answer1 == "tired":
                lie_puzzle["bare_gauge"] += BARE_WEAK
            else:
                lie_puzzle["bare_gauge"] += BARE_WEAK + 5

    return
