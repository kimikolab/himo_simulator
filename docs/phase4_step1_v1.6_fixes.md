# ヒモ男シミュレーター Phase 4 ステップ1 修正指示書 v1.6

**前提**: Phase 4 ステップ1 v1.5が実装済みであること  
最終更新日: 2026年3月15日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | UX改善 | 美咲への連絡選択肢が多すぎる → ランダム2〜3個に | misaki_events.rpy |
| 2 | 機能追加 | 「うちで飲まない？」→ ヒモ太郎の部屋に美咲が来るイベント | misaki_events.rpy / date_misaki_places.rpy |
| 3 | バランス | カナの部屋が安定しすぎ → 不在日を追加 | kana_events.rpy |
| 4 | バランス | 所持金バレリスクが厳しすぎて家賃に届かない | constants.rpy / misaki_events.rpy |

---

## 修正1: 美咲への連絡選択肢をランダム化

### 問題

信頼度が上がるにつれ選択肢が増え、75以上で8個近くになる。多すぎて読むだけで面倒。

### 修正方針

固定枠（雑談・会いたい・お金の相談）＋ランダム枠（2個）の構成にする。ランダム枠は信頼度に応じた候補プールから毎回抽選。同じ選択肢ばかり出ないように前回表示分を除外。

### ファイル: `events/misaki_events.rpy`

```python
init python:
    def get_misaki_line_choices():
        """信頼度に応じた美咲LINE選択肢の候補プールからランダム2個を返す"""
        import random
        trust = misaki["trust"]
        stage = misaki["stage"]
        pool = []

        if trust >= 40:
            pool.append("listen_work")
        if trust >= 50:
            pool.append("offer_help")
        if trust >= 55 and stage >= STAGE_CLOSE:
            pool.append("invite_home")
        if trust >= 65:
            pool.append("miss_you")
        if trust >= 75 and stage >= STAGE_DATING:
            pool.append("amaeru")

        # 前回表示した選択肢を除外（完全除外ではなく優先度を下げる）
        last_shown = daily_flags.get("misaki_line_last_shown", [])
        preferred = [c for c in pool if c not in last_shown]

        if len(preferred) >= 2:
            selected = random.sample(preferred, 2)
        elif len(pool) >= 2:
            selected = random.sample(pool, 2)
        elif len(pool) == 1:
            selected = pool[:]
        else:
            selected = []

        daily_flags["misaki_line_last_shown"] = selected
        return selected


label contact_misaki:
    $ misaki["last_contact"] = 0

    "美咲にLINEを送った..."

    if misaki["trust"] >= 60:
        "すぐに返信が来た。"
    elif misaki["trust"] >= 40:
        "しばらくして返信が来た。"
    else:
        "既読スルーされた..."
        $ change_trust(-2)
        $ daily_flags["ignored_today"] = True
        $ daily_flags["misaki_lined_only"] = True
        return

    $ daily_flags["misaki_lined_only"] = True

    # ランダム選択肢を決定
    python:
        _misaki_extra = get_misaki_line_choices()

    menu:
        misaki_c "どうしたの？"

        # --- 固定枠 ---
        "雑談する":
            call misaki_chat
            return

        "会いたいと言う":
            call misaki_date_request
            return

        "お金の相談をする" if misaki["trust"] >= 35:
            call misaki_money_request
            return

        # --- ランダム枠 ---
        "仕事の愚痴聞くよ" if "listen_work" in _misaki_extra:
            call misaki_line_listen_work

        "何か手伝えることある？" if "offer_help" in _misaki_extra:
            call misaki_line_offer_help

        "今日の夜、うちで飲まない？" if "invite_home" in _misaki_extra:
            call misaki_line_invite_home

        "声聞きたくなった" if "miss_you" in _misaki_extra:
            call misaki_line_miss_you

        "甘えていい？" if "amaeru" in _misaki_extra:
            call misaki_line_amaeru

    return
```

### daily_flags に追加

```python
"misaki_line_last_shown": [],
```

`advance_day()` のリセット対象に追加:

```python
daily_flags["misaki_line_last_shown"] = []
```

### 結果

固定3個＋ランダム2個 = 最大5個。毎回違う組み合わせが出るから飽きにくい。信頼度が低い段階ではランダム枠が0〜1個なので自然にシンプル。

---

## 修正2: ヒモ太郎の部屋に美咲が来るイベント

### 問題

「今日の夜、うちで飲まない？」で `misaki_tonight` が立つ → 夜に `misaki_date_with_location` が呼ばれる → ファミレス〜美咲の部屋の場所選択メニューが出る。「うちに来い」と誘ったのに場所選択は矛盾。

### 修正方針

`misaki_line_invite_home` 成功時に専用フラグを立て、夜のデート処理でそのフラグがある場合はヒモ太郎の部屋専用のイベントを実行する。

### ファイル: `events/misaki_events.rpy`

```python
label misaki_line_invite_home:
    himo "今日の夜さ、うちで飲まない？"

    python:
        import random
        base_rate = 0.50
        if misaki["trust"] >= 65:
            base_rate += 0.20
        if is_weekend():
            base_rate += 0.15
        invite_success = random.random() < base_rate

    if invite_success:
        misaki_c "え、いいの？...行く"
        $ flags["misaki_tonight"] = True
        # v1.6追加: ヒモ太郎の部屋に来る専用フラグ
        $ flags["misaki_visit_himo_room"] = True
        $ change_trust(3)
        $ change_dependence(5)
        "（今夜、美咲がうちに来ることになった）"
        if player["cleanliness"] < 40:
            himo "（やばい、部屋汚い...片付けないと）"
            # 清潔感チェックへの伏線
    else:
        misaki_c "ごめん、今日はちょっと..."
        misaki_c "また今度ね"
        $ change_trust(1)

    return
```

### ファイル: `script.rpy`

夜の約束処理に専用分岐を追加。

```python
    # 2. 美咲の約束のみある場合
    if flags.get("misaki_tonight") and not flags.get("kana_tonight"):
        # v1.6追加: ヒモ太郎の部屋に美咲が来る場合
        if flags.get("misaki_visit_himo_room", False):
            "今夜は美咲がうちに来る。"
            $ flags["misaki_tonight"] = False
            $ flags["misaki_visit_himo_room"] = False
            call misaki_visit_himo_room
            return

        "今夜は美咲と約束がある。"
        $ flags["misaki_tonight"] = False
        call misaki_date_with_location
        return
```

### ファイル: `events/date_misaki_places.rpy`

ヒモ太郎の部屋に美咲が来る専用イベントを追加。

```python
label misaki_visit_himo_room:
    scene bg_placeholder

    "チャイムが鳴った。"
    misaki_c "お邪魔します..."

    # 清潔感チェック
    if player["cleanliness"] >= 60:
        misaki_c "あ、結構きれいにしてるんだね"
        himo "まあな"
        $ change_trust(3)
    elif player["cleanliness"] >= 35:
        misaki_c "...男の人の部屋って感じ"
        himo "悪いな、散らかってて"
        misaki_c "ううん、大丈夫"
    else:
        misaki_c "...ヒモ太郎、ちょっとこれは..."
        himo "ごめん..."
        $ change_trust(-5)
        "美咲が少し引いている。"

    "コンビニで買った缶ビールとつまみを並べた。"

    misaki_c "なんか、こういうの新鮮だね"
    himo "いつも美咲の部屋ばっかだし"
    misaki_c "...うん"

    "いつもと違う距離感。"
    "美咲がリラックスしている気がする。"

    # 会話メニュー
    menu:
        "何を話す？"

        "仕事の話を聞く":
            misaki_c "聞いてくれる？実はさ..."
            "美咲が仕事の愚痴をこぼし始めた。"
            "ヒモ太郎の部屋だから、いつもより素が出ている。"
            misaki_c "こんな話、他の人にはできないんだ"
            $ change_trust(5)
            $ change_dependence(4)
            $ himo_aptitude["showed_concern"] += 1

        "テレビ見ながらだらだら":
            "適当にテレビをつけて、並んで座った。"
            misaki_c "...これ、何の番組？"
            himo "知らん"
            misaki_c "あはは"
            "何もしない時間が、不思議と心地よかった。"
            $ change_trust(3)
            $ change_dependence(3)

        "美咲の本音を聞く":
            himo "なあ、美咲"
            misaki_c "ん？"
            himo "俺んち来て、どう？"
            misaki_c "...狭いけど、落ち着く"
            misaki_c "ヒモ太郎の匂いがするから、かな"
            himo "......"
            "なんだか気恥ずかしい。"
            $ change_trust(6)
            $ change_dependence(6)

    # 食事判定
    $ daily_flags["ate_today"] = True
    $ change_stamina(10)

    # 泊まり判定
    "夜も更けてきた。"

    if misaki["dependence"] >= 50:
        misaki_c "...帰りたくないな"
        menu:
            "泊まってく？":
                misaki_c "...いいの？"
                "美咲が泊まることになった。"
                $ location_flags["staying_at_misaki"] = False  # 美咲の部屋ではない
                # 泊まり恩恵
                $ change_stamina(30)
                $ change_cleanliness(15)  # 翌朝シャワー
                $ change_trust(5)
                $ change_dependence(8)
                $ daily_flags["ate_today"] = True  # 翌朝の朝食込み
                # 翌朝イベントフラグ
                $ flags["misaki_stayed_at_himo"] = True
                $ flags["morning_consumed"] = True

            "送ってくよ":
                misaki_c "...ありがとう"
                $ change_trust(2)
                $ change_dependence(-2)
    else:
        misaki_c "そろそろ帰るね"
        himo "気をつけてな"
        misaki_c "うん、ありがとう。楽しかった"
        $ change_trust(3)

    # 共通処理
    $ misaki["met_today"] = True
    $ stats["times_met"] += 1
    $ daily_flags["date_with"] = "misaki"
    $ daily_flags["date_location"] = "himo_room"
    $ reset_contact()

    # 探り・ハプニング
    call check_date_incidents("misaki")

    return
```

翌朝イベント（泊まった場合）:

```python
# daily_events.rpy の check_forced_morning_event に追加

label check_forced_morning_event:
    # v1.6追加: 美咲がヒモ太郎の部屋に泊まった翌朝
    if flags.get("misaki_stayed_at_himo", False):
        $ flags["misaki_stayed_at_himo"] = False
        call misaki_morning_at_himo_room
        $ flags["morning_consumed"] = True
        return

    # （既存の強制朝イベント処理）
    # ...


label misaki_morning_at_himo_room:
    scene bg_placeholder

    "朝。隣に美咲がいる。"
    "いつもは美咲の部屋で目が覚めるのに、今日は逆だ。"

    misaki_c "...おはよう"
    himo "おう"

    "美咲がキッチンに立った。"
    misaki_c "何もないね...卵くらいない？"
    himo "コンビニ行くか"
    misaki_c "...もう"

    "結局、2人でコンビニに行って朝食を買った。"

    misaki_c "たまにはこういうのもいいね"
    himo "...そうだな"

    $ change_trust(3)
    $ change_dependence(3)
    $ daily_flags["ate_today"] = True
    $ misaki["met_today"] = True
    $ reset_contact()

    return
```

---

## 修正3: カナの部屋の不在日を追加

### 問題

カナの部屋に行けば常に食事・シャワー・体力回復が得られるため安定しすぎている。

### 修正方針

カナに「大学の講義」「友達との予定」がある日を設定。不在時はLINEで事前通知される（SNS受動通知として）。平日昼は50%程度で不在。

### ファイル: `events/kana_events.rpy`

`kana_visit` ラベルの先頭に不在チェックを追加。

```python
init python:
    def is_kana_available():
        """カナが部屋にいるかどうか"""
        import random

        # 土日は基本いる（90%）
        if is_weekend():
            return random.random() < 0.90

        # 平日の時間帯別
        time = game_date["time"]
        if time == "morning":
            # 朝は講義で不在が多い（40%で在宅）
            return random.random() < 0.40
        elif time == "afternoon":
            # 昼は半々（55%で在宅）
            return random.random() < 0.55
        else:
            # 夜は大体いる（85%で在宅）
            return random.random() < 0.85


label kana_visit:
    # v1.6追加: 不在チェック
    python:
        _kana_home = is_kana_available()

    if not _kana_home:
        "カナの部屋に行ったが、いなかった。"

        python:
            import random
            reasons = [
                "カナからLINEが来た。\nカナ「今日講義あるんだ〜ごめんね」",
                "カナからLINEが来た。\nカナ「友達と遊んでる！また明日ね」",
                "カナからLINEが来た。\nカナ「バイト入っちゃった〜」",
                "カナからLINEが来た。\nカナ「ちょっと出かけてる！夜なら空くかも」",
            ]
            _reason = random.choice(reasons)

        "[_reason]"
        himo "しゃーない"

        # 不在でもカナに会いに行った事実は記録
        $ kana["last_contact"] = 0
        return

    # カナが在宅 → 既存の訪問処理
    # ...（既存コード）
```

### SNS受動通知との連携（任意）

カナの予定をSNS受動通知で事前に知らせることも可能。ただし確実ではない（通知が出ない日もある）。

```python
# sns_system.rpy に追加候補

# カナの予定通知（朝に出ることがある）
if (kana_flags["met"]
    and not is_weekend()
    and game_date["time"] == "morning"
    and random.random() < 0.30):
    notifications.append("kana_schedule")


label sns_show_kana_schedule:
    python:
        import random
        posts = [
            "カナがストーリーを更新した。\n「今日は1限からだるい〜」",
            "カナがストーリーを更新した。\n「友達とランチ！」",
            "カナがストーリーを更新した。\n「今日バイト頑張る」",
        ]
        post = random.choice(posts)

    "[post]"
    himo "（今日はカナの部屋に行っても いないかもな）"

    return
```

---

## 修正4: 所持金バレリスクの最終調整

### 問題

ログを見ると、5日目・9日目・10日目・12日目・13日目・20日目で「お金要求ブロック LINE only」が頻発。しかしこれはLINE onlyガード（修正3系）であって所持金バレリスクではない。

ただし、後半（所持金¥30,000〜¥45,000の時期）に所持金バレリスクが60%で発動すると、家賃¥53,000に届くのが厳しい。パチンコ大勝ち（+¥9,089）でようやく¥53,462で突破している。

### 修正方針

所持金バレリスクの発動率を段階的にする。閾値に近いほど発動しにくく、大幅に超えているほど発動しやすい。

### ファイル: `events/misaki_events.rpy`

```python
    # 所持金バレリスク（v1.6: 段階的発動率）
    if player["money"] >= MONEY_SUSPICION_THRESHOLD:
        python:
            excess = player["money"] - MONEY_SUSPICION_THRESHOLD
            # 超過額に応じて発動率が上がる
            # ¥40,000ちょうど → 20%
            # ¥45,000（5000超過） → 35%
            # ¥50,000（10000超過） → 50%
            # ¥60,000（20000超過） → 70%
            suspicion_rate = min(0.20 + (excess / 40000.0) * 0.60, 0.80)
            money_suspicious = renpy.random.random() < suspicion_rate
        if money_suspicious:
            call midgame_money_suspicion
            return
```

### ファイル: `data/constants.rpy`

閾値は¥40,000のまま維持。

```python
define MONEY_SUSPICION_THRESHOLD = 40000
```

### 効果

| 所持金 | 超過額 | 発動率 |
|---|---|---|
| ¥40,000 | ¥0 | 20% |
| ¥43,000 | ¥3,000 | 25% |
| ¥45,000 | ¥5,000 | 28% |
| ¥50,000 | ¥10,000 | 35% |
| ¥53,000 | ¥13,000 | 40% |
| ¥60,000 | ¥20,000 | 50% |

¥53,000（家賃ライン）付近では40%程度。10回中6回は通るから、計画的に貯めれば家賃に届く。ただし¥60,000以上貯め込むと半分の確率で疑われる。

---

## テスト確認項目

### 選択肢ランダム化
- [ ] 美咲への連絡で固定3個＋ランダム2個の合計5個以下が表示される
- [ ] 信頼40未満ではランダム枠が空（固定3個のみ）
- [ ] 毎日違う組み合わせが出る（前日と完全一致しにくい）

### ヒモ太郎の部屋イベント
- [ ] 「うちで飲まない？」成功→夜に場所選択メニューが出ない
- [ ] ヒモ太郎の部屋専用の会話メニューが表示される
- [ ] 清潔感による美咲の反応が変わる
- [ ] 依存50以上で泊まり選択肢が出る
- [ ] 泊まった翌朝に専用の朝イベントが発生する

### カナの不在
- [ ] 平日昼にカナの部屋に行くと40〜55%で不在
- [ ] 不在時にLINEで理由が表示される
- [ ] 土日はほぼ在宅（90%）
- [ ] 夜はほぼ在宅（85%）

### 所持金バレリスク
- [ ] ¥40,000で発動率20%程度
- [ ] ¥53,000付近で発動率40%程度
- [ ] 家賃ライン到達が「運ゲー」ではなく「計画的に可能」

---

*phase4_step1_v1.6_fixes.md - 2026年3月15日作成*
