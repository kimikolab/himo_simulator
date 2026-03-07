# ヒモ男シミュレーター Phase 4 ステップ1 差分修正指示書

**前提**: Phase 3 v1.1が実装済みであること  
**参照**: phase4_step1_design.md（設計書）  
最終更新日: 2026年3月7日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | 変数追加 | 疑念度・デート関連フラグ・嘘パズル用変数 | variables.rpy / constants.rpy |
| 2 | 新規システム | SNS受動通知システム | systems/sns_system.rpy |
| 3 | 新規システム | 嘘パズル＋タイマー | systems/lie_puzzle.rpy |
| 4 | 新規システム | 証拠隠滅QTE（基本形） | systems/evidence_qte.rpy |
| 5 | 新規イベント | 中盤前半イベント（①〜④） | events/midgame_events.rpy |
| 6 | 新規イベント | 中盤後半イベント（⑤〜⑨） | events/midgame_events.rpy |
| 7 | 機能追加 | 美咲デート場所選択 | events/date_misaki_places.rpy |
| 8 | 機能追加 | カナデート場所選択 | events/date_kana_places.rpy |
| 9 | 機能追加 | デート中の探り・地雷・ハプニング | events/date_incidents.rpy |
| 10 | 既存修正 | SNSを見る選択肢の削除＋受動通知の組み込み | script.rpy / daily_events.rpy |
| 11 | 既存修正 | 所持金バレリスクの組み込み | misaki_events.rpy |
| 12 | 既存修正 | デート処理を場所選択経由に変更 | misaki_events.rpy / kana_events.rpy |

---

## 修正1: 変数・定数の追加

### ファイル: `data/variables.rpy`

既存の変数に以下を追加。

```python
# === Phase 4 追加変数 ===

# 疑念度（キャラ別）
default suspicion = {
    "misaki": 0,
    "kana": 0
}

# デート関連フラグ（daily_flagsに追加）
# 既存の daily_flags に以下のキーを追加
# "date_location": None,
# "date_with": None,
# "sns_shown_today": False,
# "double_booking_checked": False,
```

既存の `daily_flags` を以下に差し替え。

```python
default daily_flags = {
    "asked_money_today": False,
    "ignored_today": False,
    "ignored_kana_today": False,
    "ate_today": False,
    "date_location": None,
    "date_with": None,
    "sns_shown_today": False,
    "double_booking_checked": False,
    "misaki_wants_tonight": False,
    "kana_wants_tonight": False
}
```

既存の `flags` に以下のキーを追加。

```python
# flags に追加するキー
# "midgame_busymisaki_done": False,     # イベント①完了
# "midgame_pachinko_triggered": False,  # イベント③当日発生済
# "midgame_doublebooking_done": False,  # イベント⑤完了（1回のみ強制、以降はランダム）
# "midgame_sighting_done": False,       # イベント⑥完了
# "midgame_kana_raid_done": False,      # イベント⑦完了
# "midgame_misaki_direct_done": False,  # イベント⑧完了
# "kana_friend_info_obtained": False,   # カナの大学付近デートで情報入手済
```

嘘パズル用の変数。

```python
# 嘘パズル
default lie_puzzle = {
    "active": False,
    "bare_gauge": 0,
    "previous_answers": [],
    "time_limit": 5.0,
    "result": None
}
```

### ファイル: `data/constants.rpy`

```python
# === Phase 4 追加定数 ===

# 疑念度の閾値
define SUSPICION_PROBE_THRESHOLD = 1     # 探り発生の最低疑念度
define SUSPICION_SHURABA_THRESHOLD = 3   # 修羅場イベント⑧発生の疑念度
define SUSPICION_MAX = 100

# 所持金バレリスク閾値
define MONEY_SUSPICION_THRESHOLD = 30000

# 嘘パズル設定
define LIE_TIME_LV0 = 5.0
define LIE_TIME_LV1 = 7.0
define LIE_TIME_LV2 = 10.0

# バレ度上昇量
define BARE_CONTRADICTION = 35    # 矛盾回答
define BARE_SILENCE = 40          # 時間切れ
define BARE_WEAK = 10             # 弱い回答
define BARE_PERFECT = 3           # 完璧でも微増
define BARE_MAX = 100             # これでバレ確定

# QTE設定
define QTE_TIME_LIMIT = 12.0

# SNS通知の最大表示数/日
define SNS_MAX_PER_DAY = 2
```

---

## 修正2: SNS受動通知システム

### 新規ファイル: `systems/sns_system.rpy`

```python
# sns_system.rpy
# SNS受動通知システム — 行動枠を消費せず情報が流れる

init python:
    def check_sns_notification():
        """朝・昼の行動メニュー前に呼び出す"""
        import random

        if daily_flags["sns_shown_today"]:
            return

        notifications = []

        # --- カテゴリ1: フレーバー（常時ランダム） ---
        if random.random() < 0.25:
            notifications.append("flavor")

        # --- カテゴリ2: カナ匂わせ（カナ出会い済み＋信頼20以上） ---
        if (kana_flags["met"]
            and kana["trust"] >= 20
            and random.random() < 0.20):
            notifications.append("kana_hint")

        # --- カテゴリ3: 美咲の意味深（美咲依存40以上） ---
        if (misaki["dependence"] >= 40
            and random.random() < 0.20):
            notifications.append("misaki_mood")

        # --- カテゴリ4: 目撃系（SNSリスク3以上） ---
        if (kana_flags.get("sns_risk", 0) >= 3
            and not flags.get("midgame_sighting_done", False)
            and game_date["day"] >= 16
            and random.random() < 0.25):
            notifications.append("sighting")

        # --- カテゴリ5: ニュース系（低確率フレーバー） ---
        if random.random() < 0.10:
            notifications.append("news")

        # 最大2件まで表示
        if notifications:
            selected = notifications[:SNS_MAX_PER_DAY]
            for notif_type in selected:
                renpy.call("sns_show_" + notif_type)
            daily_flags["sns_shown_today"] = True


label sns_show_flavor:
    python:
        import random
        posts = [
            ("同級生・健太", "『本日付で主任に昇進しました！』"),
            ("同級生・由美", "『マイホーム購入 35年ローン頑張ります...』"),
            ("同級生・大輔", "『転職成功！試用期間中で緊張する』"),
            ("バイト仲間・拓也", "『バイトだるい〜 でも気楽でいいか』"),
            ("高校同級生・真理", "『結婚しました！！！』"),
            ("知り合い・翔太", "『起業して半年、やっと黒字化』"),
        ]
        poster, content = random.choice(posts)

    "SNSに通知。"
    "[poster]の投稿:"
    "[content]"
    himo "へー...まあ俺は俺だし"

    return


label sns_show_kana_hint:
    python:
        import random
        depend = kana["dependence"]
        if depend >= 40:
            posts = [
                "カナがストーリーを更新した。\n「今日も会えた...幸せ」",
                "カナがストーリーを更新した。\n「最近毎日楽しい。誰のおかげかな」",
                "カナが意味深な匂わせ投稿をしている。\nハートマークだらけの写真。",
            ]
        else:
            posts = [
                "カナがストーリーを更新した。\n「最近いい感じの人がいるかも」",
                "カナがカフェの写真を投稿。\n「ここ最近のお気に入り」",
            ]
        post = random.choice(posts)

    "[post]"
    himo "...これ、誰でも見れるんだよな"
    himo "大丈夫かな"

    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 1

    return


label sns_show_misaki_mood:
    python:
        import random
        depend = misaki["dependence"]
        if depend >= 60:
            posts = [
                "美咲のLINEステータスが変わっている。\n「...会いたいな」",
                "美咲のステータス。\n「早く帰りたい」",
            ]
        else:
            posts = [
                "美咲のLINEステータスが変わっている。\n「疲れた...」",
                "美咲のステータス。\n「残業つらい」",
            ]
        post = random.choice(posts)

    "[post]"

    if misaki["dependence"] >= 60:
        himo "...重いな"
    else:
        himo "大変そうだな"

    return


label sns_show_sighting:
    python:
        import random
        posts = [
            "知らないアカウントの投稿が目に入った。\n「駅前でいちゃついてるカップル見た笑」",
            "美咲の同僚っぽいアカウント。\n「あれ？美咲ちゃんの彼氏？見たことない人と歩いてた」",
            "カナの友達のストーリー。\n「カナの彼氏？大学の近くで見かけた気がする」",
        ]
        post = random.choice(posts)

    "[post]"

    himo "..."
    himo "（やばい...見られてた？）"

    # 修羅場イベント⑥のフラグを立てる
    $ flags["midgame_sighting_done"] = True

    return


label sns_show_news:
    python:
        import random
        posts = [
            ("ニュースアプリ", "『若者の恋愛離れが深刻化 交際経験なし4割超』"),
            ("ニュースアプリ", "『同棲カップルの家計管理術 共同口座のススメ』"),
            ("ニュースアプリ", "『マッチングアプリ利用者 過去最高を更新』"),
            ("ニュースアプリ", "『二股交際で損害賠償 200万円の判決』"),
        ]
        source, content = random.choice(posts)

    "[source]の通知:"
    "[content]"

    himo "...ふーん"

    return
```

---

## 修正3: 嘘パズル＋タイマーシステム

### 新規ファイル: `systems/lie_puzzle.rpy`

```python
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
        elif bare_gauge >= 70:
            return "suspicious"    # 強い疑念
        elif bare_gauge >= 40:
            return "uneasy"        # 不穏な空気
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

    if scenario == "last_night":
        call lie_puzzle_last_night(target)
    elif scenario == "other_woman":
        call lie_puzzle_other_woman(target)
    elif scenario == "double_booking":
        call lie_puzzle_double_booking(target)

    # 結果判定
    python:
        result = resolve_lie_puzzle(lie_puzzle["bare_gauge"])
        lie_puzzle["result"] = result
        lie_puzzle["active"] = False

    if result == "busted":
        "（完全にバレた...）"
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
            import random
            random.shuffle(choices)
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
                import random
                random.shuffle(choices2)
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
                import random
                random.shuffle(choices2)
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
            import random
            random.shuffle(choices)
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
        $ lie_puzzle["bare_gauge"] = 0  # 正直ルートはバレ判定不要
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
            import random
            random.shuffle(choices2)
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
            import random
            random.shuffle(choices)
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
```

---

## 修正4: 証拠隠滅QTE（基本形）

### 新規ファイル: `systems/evidence_qte.rpy`

```python
# evidence_qte.rpy
# 証拠隠滅QTE — 制限時間内にアイテムを処理する

init python:
    def create_evidence_items(scenario="kana_raid"):
        """シナリオに応じた証拠アイテムリストを生成"""
        if scenario == "kana_raid":
            items = [
                {"id": "phone", "name": "スマホ（LINE画面）", "risk": 40, "cleared": False},
                {"id": "hairpin", "name": "美咲の髪留め", "risk": 30, "cleared": False},
                {"id": "receipt", "name": "レシート", "risk": 20, "cleared": False},
            ]
            # 依存度が高いと証拠が増える
            if misaki["dependence"] >= 50:
                items.append(
                    {"id": "clothes", "name": "女物の上着", "risk": 50, "cleared": False}
                )
            return items
        return []

    def calculate_qte_result(items):
        """未処理アイテムのリスク合算"""
        total_risk = 0
        for item in items:
            if not item["cleared"]:
                total_risk += item["risk"]
        return total_risk


screen evidence_qte_screen(items, time_limit):
    timer time_limit action Return("timeout")

    # タイマーバー
    frame:
        xalign 0.5
        yalign 0.05
        padding (15, 8)
        background "#00000088"

        vbox:
            spacing 5
            text "証拠を隠せ！" size 28 color "#ff4444" xalign 0.5
            bar:
                value AnimatedValue(0, time_limit, time_limit, 0)
                xsize 400
                ysize 10
                left_bar "#ff4444"
                right_bar "#333333"
                xalign 0.5

    # アイテムボタン（散らばって配置）
    python:
        positions = [
            (0.2, 0.3), (0.7, 0.35),
            (0.4, 0.55), (0.6, 0.7),
            (0.25, 0.7),
        ]

    for i, item in enumerate(items):
        if not item["cleared"]:
            $ pos = positions[i] if i < len(positions) else (0.5, 0.5)
            textbutton item["name"]:
                xalign pos[0]
                yalign pos[1]
                action [SetDict(item, "cleared", True)]
                text_size 24
                text_color "#ffffff"
                background "#cc000088"
                padding (20, 15)


label run_evidence_qte(scenario="kana_raid"):
    python:
        qte_items = create_evidence_items(scenario)
        qte_time = QTE_TIME_LIMIT

    "（やばい！急いで隠さないと！）"

    call screen evidence_qte_screen(qte_items, qte_time)

    python:
        total_risk = calculate_qte_result(qte_items)
        cleared_count = sum(1 for item in qte_items if item["cleared"])
        total_count = len(qte_items)

    if cleared_count == total_count:
        "（全部隠した！セーフ！）"
        himo "ふう..."
    elif total_risk >= 50:
        "（隠しきれなかった...）"
        # 高リスク — 証拠発見、修羅場へ
        $ flags["qte_failed_badly"] = True
    else:
        "（大体隠せた...たぶん大丈夫）"
        $ suspicion["kana"] = min(suspicion["kana"] + 10, SUSPICION_MAX)

    return
```

---

## 修正5: 中盤前半イベント（①〜④）

### 新規ファイル: `events/midgame_events.rpy`

```python
# midgame_events.rpy
# 中盤イベント — ルーティンを崩す揺さぶり＋修羅場

init python:
    def check_midgame_events():
        """main_loopの各ターン開始時に呼び出す"""
        day = game_date["day"]
        time = game_date["time"]

        # --- 中盤前半（9〜15日） ---

        # イベント①: 美咲「最近忙しいの？」
        if (day >= 9 and day <= 15
            and not flags.get("midgame_busymisaki_done", False)
            and kana_flags["met"]
            and misaki["last_contact"] >= 3
            and time == "morning"):
            renpy.call("midgame_misaki_busy")
            return True

        # イベント④: カナからの急な呼び出し
        if (day >= 10 and day <= 20
            and kana_flags["met"]
            and kana["dependence"] >= 20
            and time == "afternoon"
            and not kana["met_today"]):
            import random
            if random.random() < 0.20:
                renpy.call("midgame_kana_urgent")
                return True

        # --- 中盤後半（16〜23日） ---

        # イベント⑤: ダブルブッキング危機
        if (day >= 16 and day <= 25
            and not flags.get("midgame_doublebooking_done", False)
            and kana_flags["met"]
            and misaki["stage"] >= STAGE_FRIEND
            and kana["trust"] >= 25
            and time == "afternoon"
            and not daily_flags["double_booking_checked"]):
            import random
            if random.random() < 0.30:
                renpy.call("midgame_double_booking")
                return True

        # イベント⑥: 目撃情報 → 修羅場
        if (flags.get("midgame_sighting_done", False)
            and not flags.get("midgame_sighting_confronted", False)
            and time == "night"):
            import random
            if random.random() < 0.40:
                renpy.call("midgame_sighting_confrontation")
                return True

        # イベント⑧: 美咲の直球質問 ver.2
        if (day >= 18
            and not flags.get("midgame_misaki_direct_done", False)
            and suspicion["misaki"] >= SUSPICION_SHURABA_THRESHOLD
            and misaki["trust"] >= 50
            and time == "night"):
            renpy.call("midgame_misaki_direct")
            return True

        return False


# === イベント①: 美咲「最近忙しいの？」 ===

label midgame_misaki_busy:
    scene bg_placeholder

    "朝、スマホを見ると美咲からLINEが来ていた。"
    misaki_c "おはよう。最近連絡ないけど、忙しいの？"

    "...3日以上連絡してなかった。"

    menu:
        "すぐ返信する":
            himo "ごめん、ちょっとバタバタしてて"
            misaki_c "...そうなんだ。元気ならいいんだけど"
            "少し間があった。"
            misaki_c "最近、全然連絡くれないなって思って"
            $ change_trust(-5)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)
            $ reset_contact()

        "後で返そう（スルー）":
            "後で返せばいいか。"
            himo "まあいっか"
            $ change_trust(-10)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
            $ himo_aptitude["easy_choices"] += 1

    $ flags["midgame_busymisaki_done"] = True
    return


# === イベント③: パチンコの誘惑 ===
# （afternoon_streetから呼び出される）

label midgame_pachinko_temptation:
    scene bg_placeholder

    "街を歩いていると、パチンコ屋の前を通りかかった。"
    "「新台入替！大盤振舞！」"

    himo "...ちょっと覗くだけ"

    menu:
        "入る":
            "気づいたら座っていた。"
            himo "まあちょっとだけ..."

            python:
                import random
                pachinko_result = random.choice(["big_win", "small_win", "lose", "big_lose"])

            if pachinko_result == "big_win":
                "大当たり！！！"
                himo "うおおお！！！"
                $ change_money(15000)
                $ stats["pachinko_total"] = stats.get("pachinko_total", 0) + 15000
                "¥15,000の勝ち。最高の気分。"
                himo "パチンコ最高！"
                $ himo_aptitude["easy_choices"] += 2

            elif pachinko_result == "small_win":
                "少し勝った。"
                $ change_money(3000)
                $ stats["pachinko_total"] = stats.get("pachinko_total", 0) + 3000
                himo "まあまあかな"
                $ himo_aptitude["easy_choices"] += 1

            elif pachinko_result == "lose":
                "負けた。"
                $ change_money(-5000)
                $ stats["pachinko_total"] = stats.get("pachinko_total", 0) - 5000
                himo "...まあこんなもんか"

            else:
                "大負け。"
                $ change_money(-10000)
                $ stats["pachinko_total"] = stats.get("pachinko_total", 0) - 10000
                himo "...やば"
                "財布の中身が一気に減った。"
                if player["money"] < WEEKLY_RENT:
                    "（家賃...大丈夫か？）"

            $ change_stamina(-15)
            $ himo_aptitude["easy_choices"] += 1

        "通り過ぎる":
            himo "...いや、やめとこ"
            "誘惑に打ち勝った。"

    $ flags["midgame_pachinko_triggered"] = True
    return


# === イベント④: カナからの急な呼び出し ===

label midgame_kana_urgent:
    "カナからLINEが来た。"
    kana_c "ねえ今すぐ来て！！"
    kana_c "友達にドタキャンされた...一人で暇"

    menu:
        "行く（昼＋夜がカナに消費される）":
            himo "しょうがないな、行くよ"
            kana_c "やった！！！"

            "カナと合流した。結局夜まで一緒にいた。"
            $ kana["met_today"] = True
            $ kana["last_contact"] = 0
            $ change_trust_kana(8)
            $ change_dependence_kana(5)
            $ change_stamina(-20)
            $ daily_flags["ate_today"] = True
            $ daily_flags["date_with"] = "kana"

            # 昼＋夜を消費
            $ flags["afternoon_consumed"] = True
            $ flags["kana_tonight"] = True

            "（美咲に連絡する暇がなかった...）"

        "断る":
            himo "ごめん、今日はちょっと..."
            kana_c "え〜...マジで？"
            kana_c "いっつも断るじゃん"

            $ change_trust_kana(-8)
            $ kana["last_contact"] = 0

    return
```

---

## 修正6: 中盤後半イベント（⑤〜⑨）

`midgame_events.rpy` に続けて追加。

```python
# === イベント⑤: ダブルブッキング危機 ===

label midgame_double_booking:
    "昼、立て続けにLINEが来た。"

    misaki_c "今夜会える？ちょっと話したいことがあって"
    "...続けてもう1件。"
    kana_c "今夜暇？会いたい！"

    himo "...やばい、被った"

    $ daily_flags["double_booking_checked"] = True
    $ daily_flags["misaki_wants_tonight"] = True
    $ daily_flags["kana_wants_tonight"] = True

    menu:
        "美咲を優先する":
            himo "（カナに断りの連絡を入れないと）"
            call run_lie_puzzle("double_booking", "kana")

            $ daily_flags["kana_wants_tonight"] = False
            $ flags["misaki_tonight"] = True

            python:
                result = lie_puzzle["result"]
            if result == "busted":
                kana_c "嘘でしょ？なんか怪しいんだけど"
            elif result == "suspicious":
                kana_c "...ふーん"
            else:
                kana_c "しょうがないな〜"

        "カナを優先する":
            himo "（美咲に断りの連絡を...）"
            call run_lie_puzzle("double_booking", "misaki")

            $ daily_flags["misaki_wants_tonight"] = False
            $ flags["kana_tonight"] = True

            python:
                result = lie_puzzle["result"]
            if result == "busted":
                misaki_c "...嘘ついてるでしょ"
            elif result == "suspicious":
                misaki_c "...そう"
            else:
                misaki_c "分かった、じゃあまた今度ね"

        "両方断る":
            himo "今日は両方やめとこう..."
            "美咲に断りのLINEを送った。"
            misaki_c "...そう"
            $ change_trust(-3)
            "カナにも。"
            kana_c "え〜つまんない"
            $ change_trust_kana(-3)

    $ flags["midgame_doublebooking_done"] = True
    return


# === イベント⑥: 目撃情報 → 対面修羅場 ===

label midgame_sighting_confrontation:
    scene bg_placeholder

    # 直近のデート相手で分岐
    if daily_flags.get("date_with", None) == "kana":
        # 美咲から追及される
        misaki_c "ねえ、聞いていい？"
        misaki_c "友達がさ、駅前で女の子と歩いてるの見たって"
        misaki_c "あれ、ヒモ太郎？"

        call run_lie_puzzle("other_woman", "misaki")

    else:
        # カナから追及される
        kana_c "ねえ、ちょっと聞きたいことあるんだけど"
        kana_c "友達がヒモ太郎っぽい人が女の人と歩いてるの見たって"
        kana_c "誰？"

        call run_lie_puzzle("other_woman", "kana")

    $ flags["midgame_sighting_confronted"] = True
    return


# === イベント⑦: カナの突撃訪問（証拠隠滅QTE） ===

label midgame_kana_raid:
    scene bg_placeholder

    "ヒモ太郎の部屋で寛いでいると――"
    "ドンドンドン！"
    kana_c "ヒモ太郎〜！いる？来ちゃった！"

    himo "！？"
    "（やばい、美咲の荷物がそのままだ！）"

    call run_evidence_qte("kana_raid")

    # QTE結果で分岐
    if flags.get("qte_failed_badly", False):
        "カナが部屋に入ってきた。"
        "そして――見つけた。"

        kana_c "...これ、誰の？"

        # 嘘パズルに連鎖
        call run_lie_puzzle("other_woman", "kana")

        $ flags["qte_failed_badly"] = False
    else:
        "カナが部屋に入ってきた。"
        kana_c "急に来ちゃった〜。暇だったから"
        himo "（セーフ...）"

        "でもカナは、少し部屋を見回していた。"
        kana_c "...なんか慌ててなかった？"
        himo "いや、別に？"
        kana_c "ふーん..."

        $ suspicion["kana"] = min(suspicion["kana"] + 5, SUSPICION_MAX)

    $ kana["met_today"] = True
    $ kana["last_contact"] = 0
    $ flags["midgame_kana_raid_done"] = True
    return


# === イベント⑧: 美咲の直球質問 ver.2 ===

label midgame_misaki_direct:
    scene bg_placeholder

    "美咲と2人きりの夜。"
    "いつもと違う空気。"

    misaki_c "...ヒモ太郎"
    himo "ん？"
    misaki_c "ちゃんと聞きたいことがある"

    "美咲の目が、真剣だった。"

    misaki_c "他に女の人、いるでしょ"
    misaki_c "最近LINE返すの遅いし、予定よく断るし"
    misaki_c "前は暇だ暇だって言ってたのに"

    call run_lie_puzzle("other_woman", "misaki")

    python:
        result = lie_puzzle["result"]

    if result == "busted":
        misaki_c "...もういい"
        misaki_c "分かってた。薄々"
        "美咲は静かに泣いていた。"
        $ change_trust(-25)
        $ change_dependence(-10)
    elif result == "suspicious":
        misaki_c "...信じたいけど"
        "美咲は何かを飲み込んだような顔をした。"
        $ change_trust(-10)
    elif result == "safe":
        misaki_c "...ごめん、疑って"
        himo "いいって。ちゃんと話してくれてありがとう"
        $ change_trust(5)
    # "uneasy"の場合は run_lie_puzzle 内で処理済み

    $ flags["midgame_misaki_direct_done"] = True
    return


# === イベント⑨: 所持金バレリスク ===
# （misaki_money_request から呼び出される。修正11で組み込み）

label midgame_money_suspicion:
    misaki_c "...ねえ、本当にお金ないの？"
    misaki_c "最近ちょっと余裕ありそうに見えるけど"

    himo "え？"

    menu:
        "誤魔化す":
            himo "いやいや、見た目だけだって"
            misaki_c "...そう？"
            $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)
            $ himo_aptitude["lies"] += 1

        "正直に言う":
            himo "...まあ、ちょっと余裕は出てきたかも"
            misaki_c "じゃあなんでお金頼むの？"
            himo "......"
            $ change_trust(-5)
            $ himo_aptitude["honest_moments"] += 1

    "今日のお金の要求は失敗した。"
    $ daily_flags["asked_money_today"] = True
    return
```

---

## 修正7: 美咲デート場所選択

### 新規ファイル: `events/date_misaki_places.rpy`

```python
# date_misaki_places.rpy
# 美咲デート — 場所選択で展開が変わる

label misaki_date_with_location:
    scene bg_placeholder

    "美咲と会うことになった。"

    menu:
        "どこに行く？"

        "ファミレス（安い・安全）":
            $ daily_flags["date_location"] = "famires"
            call misaki_date_famires

        "居酒屋（本音が出やすい）":
            $ daily_flags["date_location"] = "izakaya"
            call misaki_date_izakaya

        "美咲の部屋（親密・依存UP）" if misaki["stage"] >= STAGE_CLOSE:
            $ daily_flags["date_location"] = "misaki_room"
            call misaki_date_room

        "ちょっといい店（自腹・信頼大幅UP）" if can_afford(3000):
            $ daily_flags["date_location"] = "fancy"
            call misaki_date_fancy

    # デート後の共通処理
    $ misaki["met_today"] = True
    $ stats["times_met"] += 1
    $ daily_flags["date_with"] = "misaki"
    $ reset_contact()

    # 探り・地雷・ハプニングの判定
    call check_date_incidents("misaki")

    return


label misaki_date_famires:
    "ファミレスに入った。"
    misaki_c "ここ落ち着くよね"
    himo "安いしな"

    $ change_trust(3)
    $ change_dependence(2)
    $ change_stamina(-10)
    $ change_money(0)  # 美咲奢り

    return


label misaki_date_izakaya:
    "居酒屋に入った。"
    misaki_c "たまにはこういうのもいいね"

    "お酒が入って、美咲の口数が増える。"

    $ change_trust(5)
    $ change_dependence(5)
    $ change_stamina(-15)
    $ change_money(0)  # 美咲奢り

    # 居酒屋は探り発生率UP
    $ suspicion["misaki"] = suspicion["misaki"]  # 探り発生率は check_date_incidents で処理

    return


label misaki_date_room:
    "美咲の部屋に行った。"
    misaki_c "散らかっててごめんね"
    himo "いいっていいって"

    "2人きりの空間。"

    $ change_trust(5)
    $ change_dependence(8)
    $ change_stamina(-10)
    $ change_cleanliness(15)  # シャワー借りれる

    # 翌日の日曜朝イベントフラグ（既存）
    python:
        weekday_index = (game_date["day"] - 1) % 7
        if weekday_index == 5:  # 土曜の夜
            flags["misaki_sunday_morning"] = True

    return


label misaki_date_fancy:
    "少しいい店に入った。"
    "自分から奢りを申し出た。"
    misaki_c "え、いいの？"
    himo "たまにはな"

    misaki_c "...ありがとう"
    "美咲が嬉しそうに笑った。"

    $ change_money(-3000)
    $ change_trust(10)
    $ change_dependence(3)
    $ change_stamina(-10)

    return
```

---

## 修正8: カナデート場所選択

### 新規ファイル: `events/date_kana_places.rpy`

```python
# date_kana_places.rpy
# カナデート — 場所選択で展開が変わる

label kana_date_with_location:
    scene bg_placeholder

    "カナと会うことになった。"

    menu:
        "どこに行く？"

        "カフェ（奢り・SNSリスクあり）":
            $ daily_flags["date_location"] = "cafe"
            call kana_date_cafe

        "カラオケ（¥500・SNSリスクなし）" if can_afford(500):
            $ daily_flags["date_location"] = "karaoke"
            call kana_date_karaoke

        "カナの大学付近（情報収集・奢り）":
            $ daily_flags["date_location"] = "campus"
            call kana_date_campus

        "ヒモ太郎の部屋（コスト0・清潔感依存）":
            $ daily_flags["date_location"] = "himo_room"
            call kana_date_himo_room

    # デート後の共通処理
    $ kana["met_today"] = True
    $ kana["last_contact"] = 0
    $ daily_flags["date_with"] = "kana"
    $ daily_flags["ate_today"] = True  # カナとのデートは食事込み

    # 探り・地雷・ハプニングの判定
    call check_date_incidents("kana")

    return


label kana_date_cafe:
    "カフェに入った。"
    kana_c "ここインスタ映えする〜"

    "カナがスマホを取り出して写真を撮り始めた。"

    $ change_trust_kana(5)
    $ change_dependence_kana(3)
    $ change_stamina(-10)
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 2

    return


label kana_date_karaoke:
    "カラオケに行った。"
    kana_c "何歌う？"
    himo "適当に"

    "盛り上がった。カナの歌が意外と上手い。"

    $ change_money(-500)
    $ change_trust_kana(8)
    $ change_dependence_kana(5)
    $ change_stamina(-15)
    # SNSリスクなし

    return


label kana_date_campus:
    "カナの大学の近くで会った。"
    kana_c "この辺よく来るんだ〜"

    "カナの友達とすれ違った。"
    kana_c "あ、まりちゃん！紹介するね、ヒモ太郎！"

    "...紹介された。"

    $ change_trust_kana(8)
    $ change_dependence_kana(4)
    $ change_stamina(-10)
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 1

    # 情報収集イベント
    if not flags.get("kana_friend_info_obtained", False):
        "友達と少し話す機会があった。"
        "友達「カナってさ、前の彼氏に浮気されてから男性不信なんだよね」"
        "友達「だからヒモ太郎のこと大事にしてあげてね」"
        himo "（...なるほど）"
        $ flags["kana_friend_info_obtained"] = True
        "カナの過去を知った。今後の会話で地雷を避けやすくなるかもしれない。"

    return


label kana_date_himo_room:
    "ヒモ太郎の部屋で会うことにした。"

    if player["cleanliness"] >= 50:
        kana_c "意外と綺麗にしてるじゃん"
        $ change_trust_kana(5)
    elif player["cleanliness"] >= 30:
        kana_c "...まあ、男の人の部屋ってこんなもんか"
        $ change_trust_kana(3)
    else:
        kana_c "...汚い"
        $ change_trust_kana(-3)

    $ change_dependence_kana(6)
    $ change_stamina(-5)
    # SNSリスクなし、コストなし

    # 親密スキル経験値（将来のエナマッチ用）
    $ himo_aptitude["intimacy_exp"] = himo_aptitude.get("intimacy_exp", 0) + 1

    return
```

---

## 修正9: デート中の探り・地雷・ハプニング

### 新規ファイル: `events/date_incidents.rpy`

```python
# date_incidents.rpy
# デート中に発生する探り・地雷・ハプニング

init python:
    def should_trigger_probe(target):
        """探りが発生するか判定"""
        import random
        sus = suspicion.get(target, 0)
        location = daily_flags.get("date_location", None)

        base_rate = 0.10
        if sus >= 1:
            base_rate += 0.15
        if sus >= 3:
            base_rate += 0.15
        if location == "izakaya":
            base_rate += 0.15  # 居酒屋は探り率UP

        return random.random() < base_rate

    def should_trigger_landmine():
        """地雷が発生するか判定"""
        import random
        return random.random() < 0.15  # 15%の固定確率

    def should_trigger_happening(target):
        """ハプニングが発生するか判定"""
        import random
        if not kana_flags["met"]:
            return False
        return random.random() < 0.20


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
        import random

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

        probe_key, probe_text = random.choice(probes)

    "ふと、[target]が真面目な顔になった。"

    if target == "misaki":
        misaki_c "[probe_text]"
    else:
        kana_c "[probe_text]"

    # 探りの種類別対応
    if probe_key == "last_night":
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
                    import random
                    notification_risk = random.random() < 0.30
                if notification_risk:
                    "その瞬間、LINE通知が鳴った。"
                    if target == "misaki":
                        "「カナ」という名前が画面に表示された。"
                        misaki_c "...カナって誰？"
                        call run_lie_puzzle("other_woman", "misaki")
                    else:
                        "「美咲」という名前が画面に表示された。"
                        kana_c "...美咲って誰？"
                        call run_lie_puzzle("other_woman", "kana")
                else:
                    "特に怪しいものはなかった。"
                    if target == "misaki":
                        misaki_c "...ごめん、疑って"
                        $ change_trust(3)
                    else:
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
                misaki_c "じゃあ約束ね！"
                $ flags["misaki_saturday_promise"] = True
                "（カナとの予定と被らないよな...?）"

            "まだ分からない":
                misaki_c "...そう"
                $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)

    elif probe_key == "insta":
        menu:
            "いいよ":
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
                misaki_c "...もう、急にそういうこと言う"
                $ change_trust(5)
                $ change_dependence(3)

    return


# === 地雷 ===

label date_landmine(target):
    python:
        import random

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
        mine_key = random.choice(mines)

    # 地雷選択肢を通常会話に紛れ込ませる
    if mine_key == "quit_job":
        "美咲が仕事の愚痴を言い始めた。"
        misaki_c "今日も残業で...もう疲れた"

        menu:
            "大変だな、お疲れ":
                misaki_c "ありがとう..."
                $ change_trust(3)
                $ himo_aptitude["showed_concern"] += 1

            "仕事辞めちゃえば？":
                misaki_c "..."
                "美咲の表情が固まった。"
                misaki_c "...そんな簡単に言わないで"
                misaki_c "仕事は私のアイデンティティなの"
                $ change_trust(-15)
                "（地雷だった...）"

            "俺がいるから大丈夫だって":
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
                    misaki_c "はは、冗談きついね"
                    $ change_trust(-2)
                else:
                    misaki_c "..."
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
                    kana_c "...うん、そうかも"
                    kana_c "ヒモ太郎がいるからいいか"
                    $ change_trust_kana(5)
                else:
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
        import random

        happenings = ["line_notification", "acquaintance"]

        if target == "kana":
            happenings.append("insta_shot")
        if target == "misaki":
            happenings.append("receipt")

        happening_key = random.choice(happenings)

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
                    import random
                    name_visible = random.random() < 0.40
                if name_visible:
                    if target == "misaki":
                        misaki_c "...カナって誰？"
                        call run_lie_puzzle("other_woman", "misaki")
                    else:
                        kana_c "...美咲って誰？"
                        call run_lie_puzzle("other_woman", "kana")
                else:
                    "名前は見えなかったようだ。"

    elif happening_key == "acquaintance":
        "デート中、向こうから見覚えのある顔が歩いてきた。"
        if target == "misaki":
            "美咲の同僚だ。"
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
            kana_c "あ〜！まりちゃ〜ん！"
            "嬉しそうに紹介してくる。"
            kana_c "彼氏！"
            himo "（彼氏...?）"
            $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 2

    elif happening_key == "insta_shot":
        "突然、カナがスマホを向けてきた。"
        kana_c "はい撮るよ〜！"

        menu:
            "撮らせる":
                "パシャ。"
                kana_c "いい写真〜！載せよ！"
                $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 3
                "（...証拠が増えた）"

            "顔を隠す":
                himo "やめろ〜"
                kana_c "え〜、なんで〜！"
                $ change_trust_kana(-2)
                $ suspicion["kana"] = min(suspicion["kana"] + 1, SUSPICION_MAX)

    elif happening_key == "receipt":
        "ポケットからレシートが落ちた。"
        "美咲が拾った。"
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
```

---

## 修正10: 既存ファイルの修正（SNS受動通知の組み込み）

### ファイル: `script.rpy`

`morning_actions` と `afternoon_actions` の先頭にSNS受動通知と中盤イベントチェックを追加。

```python
label morning_actions:
    # Phase 4追加: SNS受動通知
    $ check_sns_notification()

    # Phase 4追加: 中盤イベントチェック
    python:
        midgame_fired = check_midgame_events()

    if midgame_fired:
        return

    # v1.1: 強制朝イベントのチェック
    call check_forced_morning_event

    if flags.get("morning_consumed", False):
        $ flags["morning_consumed"] = False
        return

    # 通常の朝メニュー
    # ※「SNSを見る」の選択肢を削除
    menu:
        "【[game_date[day]]日目・朝】何をする？"

        "シャワーを浴びる":
            # 既存処理

        "美咲に連絡する":
            call contact_misaki

        "カナに連絡する" if kana_flags["met"]:
            call contact_kana

        "二度寝する":
            # 既存処理

    return


label afternoon_actions:
    # Phase 4追加: SNS受動通知（朝に出なかった場合のみ）
    $ check_sns_notification()

    # Phase 4追加: 中盤イベントチェック
    python:
        midgame_fired = check_midgame_events()

    if midgame_fired:
        return

    # 既存処理（afternoon_consumed チェック等）
    ...
```

### ファイル: `events/daily_events.rpy`

`afternoon_street` にパチンコの誘惑を追加。

```python
label afternoon_street:
    scene bg_placeholder

    # Phase 4追加: パチンコの誘惑チェック
    if (player["money"] >= 15000
        and game_date["day"] >= 10
        and not flags.get("midgame_pachinko_triggered", False)):
        python:
            import random
            if random.random() < 0.25:
                renpy.call("midgame_pachinko_temptation")

    # v1.1: 昼の強制イベントチェック
    call check_forced_afternoon_event

    if flags.get("afternoon_consumed", False):
        $ flags["afternoon_consumed"] = False
        return

    # 街メニュー（SNSを見る は存在しない）
    menu:
        "【街】何をする？"

        "買い物をする":
            call shopping_event

        "ナンパしてみる" if flags.get("nanpa_unlocked", False) and not kana_flags["met"]:
            call nanpa_event

        "求人情報を見る":
            call check_job_hint

        "自宅に戻る":
            pass

    return
```

---

## 修正11: 所持金バレリスクの組み込み

### ファイル: `events/misaki_events.rpy`

`misaki_money_request` の先頭に所持金チェックを追加。

```python
label misaki_money_request:
    # 既存チェック: 1日1回制限
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    # Phase 4追加: 所持金バレリスク
    if player["money"] >= MONEY_SUSPICION_THRESHOLD:
        call midgame_money_suspicion
        return

    # 既存の処理...
    himo "実は...お金が厳しくて"
    # （以降は既存コードのまま）
```

---

## 修正12: デート処理を場所選択経由に変更

### ファイル: `events/misaki_events.rpy`

`misaki_date` ラベルの呼び出しを `misaki_date_with_location` に差し替え。

```python
# 既存の misaki_date を呼び出している箇所を全て
# misaki_date_with_location に変更

# 例: misaki_date_request 内
label misaki_date_request:
    # ...（既存のチェック処理）...

    if game_date["time"] == "night":
        misaki_c "今から？いいよ"
        call misaki_date_with_location    # ← 変更
        return
    # ...
```

### ファイル: `events/kana_events.rpy`

同様に、カナのデート処理を `kana_date_with_location` に差し替え。

```python
# 既存の kana_date を呼び出している箇所を全て
# kana_date_with_location に変更
```

---

## 新規ファイル一覧

| ファイル | 内容 |
|---|---|
| `systems/sns_system.rpy` | SNS受動通知 |
| `systems/lie_puzzle.rpy` | 嘘パズル＋タイマー |
| `systems/evidence_qte.rpy` | 証拠隠滅QTE |
| `events/midgame_events.rpy` | 中盤イベント①〜⑨ |
| `events/date_misaki_places.rpy` | 美咲デート場所別 |
| `events/date_kana_places.rpy` | カナデート場所別 |
| `events/date_incidents.rpy` | 探り・地雷・ハプニング |

---

## テスト確認項目

### SNS受動通知
- [ ] 朝・昼の行動メニュー前にSNS通知が表示される
- [ ] 行動枠を消費しない
- [ ] 1日最大2件まで
- [ ] カナ未出会い時にはカナ関連通知が出ない
- [ ] 朝のメニューから「SNSを見る」が消えている

### 嘘パズル
- [ ] タイマーが動作し、時間切れで最悪の結果になる
- [ ] 嘘スキルLv.0でしょうもない選択肢が混ざる
- [ ] バレ度ゲージが画面に表示される
- [ ] 矛盾回答でバレ度が大きく上がる
- [ ] 正直に認めるルートが機能する

### 中盤イベント
- [ ] 10〜25日目に各イベントが発生する
- [ ] イベント⑨: 所持金¥30,000超で美咲にお金要求→拒否される
- [ ] イベント⑤: ダブルブッキング時に嘘パズルが発動する
- [ ] パチンコで大負けした場合に家賃危機になりうる

### デートバリエーション
- [ ] 美咲・カナそれぞれ4つの場所から選べる
- [ ] 場所によってパラメータ変動が異なる
- [ ] 探り・地雷・ハプニングがランダムで発生する
- [ ] カナの大学付近で友達情報を入手できる
- [ ] 入手した情報が後の地雷回避に使える

### バランス
- [ ] 中盤のイベント頻度が適切か（多すぎず少なすぎず）
- [ ] 嘘パズル失敗でもリカバリー可能か
- [ ] 探り・地雷が毎回ではなく適度に発生するか

---

*phase4_step1_implementation.md - 2026年3月7日作成*
