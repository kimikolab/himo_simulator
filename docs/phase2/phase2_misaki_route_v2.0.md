# ヒモ男シミュレーター Steamデモ Phase 2 実装指示書 v2.0

**対象**: ロードマップ Phase 2（Week 4〜6）  
**前提**: Phase 1（7日間プロトタイプ v2.6）が完成済みであること  
**ゴール**: 美咲との関係が「生き物のように動く」30日間

最終更新日: 2026年2月19日

---

## v1.0 からの変更点

v1.0（30日拡張・美咲5イベント）に以下を追加。

| 追加内容 | 目的 |
|---|---|
| バランス調整（信頼/依存の成長速度・収支） | パラメータカンストと金余りの解消 |
| 美咲イニシアチブシステム | 美咲が能動的に動く仕組み |
| 依存度マイルストーンイベント | 依存度を「重さ」として体感させる |
| 今日のムードシステム | お金交渉に不確実性と読み合いを生む |

**設計の核心**  
現状の美咲は「リソースを持ったNPC」になっている。  
美咲が変化し、プレイヤーに働きかけることで、30日間に自然とドラマが生まれる状態を目指す。

---

## ディレクトリ変更点

```
himo-simulator/
└── game/
    ├── data/
    │   ├── constants.rpy       ← 変更（定数・減衰値調整）
    │   └── variables.rpy       ← 変更（新変数追加）
    │
    ├── systems/
    │   ├── time_system.rpy     ← 変更（曜日・月次・ムード更新）
    │   └── parameter_system.rpy ← 変更（収穫逓減・ムード補正）
    │
    └── events/
        ├── misaki_events.rpy   ← 大幅追加（M-02〜M-05・マイルストーン）
        ├── daily_events.rpy    ← 変更（ランダム出費・SNS効果追加）
        ├── endings.rpy         ← 変更（30日エンディング）
        └── script.rpy          ← 変更（main_loop・status_bar）
```

---

## 1. data/constants.rpy

```python
# constants.rpy

define TIMES_OF_DAY  = ["morning", "afternoon", "night"]
define WEEKDAYS      = ["日", "月", "火", "水", "木", "金", "土"]

# ゲーム期間・固定費
define GAME_DAYS     = 30
define MONTHLY_RENT  = 50000
define PHONE_BILL    = 3000

# パラメータ減衰（v2.0調整）
define STAMINA_DECAY_PER_TURN     = 5    # v1.0: 3 → 5（食事の重要性UP）
define CLEANLINESS_DECAY_PER_TURN = 4    # v1.0: 7 → 4（シャワーで維持可能に）
define HUNGER_PENALTY_PER_DAY     = 15   # 食事しなかった日の翌朝ペナルティ

# ステージ定数
define STAGE_ACQUAINTANCE = 1
define STAGE_FRIEND       = 2
define STAGE_CLOSE        = 3
define STAGE_DATING       = 4

# イベント発生タイミング
define DOUBT_EVENT_DAY  = 12
define M02_EARLIEST_DAY = 5
define M03_EARLIEST_DAY = 14
define M05_EARLIEST_DAY = 20

# 依存度マイルストーン（美咲イニシアチブ）
define DEPEND_MILD   = 40   # 軽い干渉開始
define DEPEND_MEDIUM = 60   # 約束の強制
define DEPEND_HEAVY  = 80   # 行動制限
```

---

## 2. data/variables.rpy（差分のみ）

```python
# variables.rpy（Phase 2追加分）

# 曜日追加
default game_date = {
    "day": 1,
    "time": "morning",
    "weekday": 1    # 0=日, 1=月, ..., 6=土
}

# 美咲イベント進行フラグ
default misaki_events = {
    "M01_done": False,
    "M02_done": False,
    "M02_unlocked": False,
    "M03_done": False,
    "M03_unlocked": False,
    "M04_done": False,    # スタブのみ（Phase 3で実装）
    "M05_done": False,
    "M05_unlocked": False,
}

# 場所フラグ
default location_flags = {
    "misaki_room_unlocked": False,
    "staying_at_misaki": False,
}

# daily_flags（追加分）
default daily_flags = {
    "asked_money_today": False,
    "ignored_today": False,
    "date_planned_tonight": False,
    "ate_today": False,         # 食事システム
}

# 月次管理
default monthly = {
    "rent_paid": False,
    "total_months": 1,
}

# 美咲イニシアチブ：ムードシステム
default misaki_mood = {
    "work_stress": 0,       # 0〜100
    "today_mood": "normal", # "good" / "normal" / "tired" / "stressed"
}

# 美咲イニシアチブ：依存度管理
default misaki_streak    = 0      # 連続で会った日数
default weekend_promised = False  # 週末の約束フラグ
```

---

## 3. systems/time_system.rpy

```python
# time_system.rpy（Phase 2版）

init python:
    def advance_time():
        global game_date, player, misaki

        if game_date["time"] == "morning":
            game_date["time"] = "afternoon"
        elif game_date["time"] == "afternoon":
            game_date["time"] = "night"
        else:
            game_date["time"] = "morning"
            advance_day()

        player["stamina"]     = max(0, player["stamina"] - STAMINA_DECAY_PER_TURN)
        player["cleanliness"] = max(0, player["cleanliness"] - CLEANLINESS_DECAY_PER_TURN)
        misaki["last_contact"] += 1

        if player["stamina"] <= 15:
            renpy.call("event_low_stamina")


    def advance_day():
        global game_date, misaki, flags, daily_flags
        global location_flags, misaki_events, misaki_streak

        game_date["day"]     += 1
        game_date["weekday"]  = (game_date["weekday"] + 1) % 7
        misaki["met_today"]   = False

        # daily_flags リセット
        daily_flags["asked_money_today"]    = False
        daily_flags["ignored_today"]        = False
        daily_flags["date_planned_tonight"] = False

        # 食事ペナルティチェック（v2.0追加）
        if not daily_flags["ate_today"]:
            renpy.call("hunger_penalty")
        daily_flags["ate_today"] = False

        # 美咲宅宿泊リセット
        location_flags["staying_at_misaki"] = False

        # 連続会った日数リセット（会わなかった日）
        if not misaki["met_today"]:
            misaki_streak = max(0, misaki_streak - 1)

        # 美咲ムード更新（v2.0追加）
        update_misaki_mood()

        # 街アンロック
        if game_date["day"] == 4:
            flags["street_unlocked"] = True
            renpy.notify("街に出られるようになった")

        # 月次処理
        if game_date["day"] > 1 and (game_date["day"] - 1) % 30 == 0:
            renpy.call("monthly_billing")

        # 美咲からの自発的連絡（v2.0追加）
        check_misaki_initiative()

        # 美咲イベントアンロック
        check_misaki_event_unlock()

        # 疑念イベント
        if game_date["day"] == DOUBT_EVENT_DAY and not flags["doubt_event_done"]:
            renpy.call("misaki_doubt_event")

        # 週末の約束チェック（v2.0追加）
        if weekend_promised and is_weekend() and not misaki["met_today"]:
            renpy.call("misaki_broken_promise")


    def update_misaki_mood():
        import random
        global misaki_mood

        if not is_weekend():
            misaki_mood["work_stress"] = clamp(
                misaki_mood["work_stress"] + random.randint(5, 15), 0, 100
            )
        else:
            misaki_mood["work_stress"] = clamp(
                misaki_mood["work_stress"] - 30, 0, 100
            )

        stress = misaki_mood["work_stress"]
        if stress >= 70:
            misaki_mood["today_mood"] = "stressed"
        elif stress >= 40:
            misaki_mood["today_mood"] = "tired"
        elif stress <= 15 and is_weekend():
            misaki_mood["today_mood"] = "good"
        else:
            misaki_mood["today_mood"] = "normal"


    def check_misaki_initiative():
        import random
        global misaki

        # 3日以上連絡なし → 美咲からLINE
        if misaki["last_contact"] >= 3 and random.random() < 0.6:
            renpy.call("misaki_check_in")

        # ストレス状態のとき低確率で電話（信頼40以上）
        if (misaki["trust"] >= 40
                and misaki_mood["today_mood"] == "stressed"
                and random.random() < 0.2):
            renpy.call("misaki_stress_call")


    def check_misaki_event_unlock():
        global misaki_events, misaki, player

        if (not misaki_events["M02_unlocked"]
                and misaki["trust"] >= 30
                and game_date["day"] >= M02_EARLIEST_DAY):
            misaki_events["M02_unlocked"] = True

        if (not misaki_events["M03_unlocked"]
                and misaki["trust"] >= 50
                and game_date["day"] >= M03_EARLIEST_DAY):
            misaki_events["M03_unlocked"] = True

        if (not misaki_events["M05_unlocked"]
                and misaki["trust"] >= 60
                and game_date["day"] >= M05_EARLIEST_DAY
                and player["money"] < 20000):
            misaki_events["M05_unlocked"] = True


    def is_weekend():
        return game_date["weekday"] in (0, 6)

    def get_weekday_string():
        return WEEKDAYS[game_date["weekday"]]

    def get_time_string():
        time_jp = {"morning": "朝", "afternoon": "昼", "night": "夜"}
        return time_jp.get(game_date["time"], "???")


label hunger_penalty:
    "（そういえば昨日ろくに食べていない）"
    "（腹が減って体が重い）"
    $ change_stamina(-HUNGER_PENALTY_PER_DAY)
    return

label event_low_stamina:
    "（体が重い...）"
    "（疲れすぎてる。少し休まないと）"
    return

label monthly_billing:
    scene bg_placeholder with fade
    "――月が変わった――"
    "スマホに通知が来た。"
    "'家賃引き落とし: 50,000円'"
    "'通信費引き落とし: 3,000円'"

    python:
        total_bill  = MONTHLY_RENT + PHONE_BILL
        can_pay_now = player["money"] >= total_bill

    if can_pay_now:
        $ change_money(-total_bill)
        "合計[total_bill]円が引き落とされた。"
        himo "...払えた。ギリギリだけど"
    else:
        "残高不足で引き落とせなかった。"
        himo "やばい...どうすんだこれ"
        jump ending_bankruptcy_30days

    return
```

---

## 4. systems/parameter_system.rpy（変更部分のみ）

### 収穫逓減ロジック（v2.0追加）

```python
def change_trust(amount):
    global misaki
    trust = misaki["trust"]

    if trust >= 70:
        amount = int(amount * 0.3)
    elif trust >= 50:
        amount = int(amount * 0.6)

    old_stage = misaki["stage"]
    misaki["trust"] = clamp(misaki["trust"] + amount, 0, 100)
    update_misaki_stage()

    if misaki["stage"] > old_stage:
        stage_names = {2: "友達", 3: "いい雰囲気", 4: "恋人"}
        if misaki["stage"] in stage_names:
            renpy.notify("美咲との関係が「" + stage_names[misaki["stage"]] + "」になった")


def change_dependence(amount):
    global misaki
    old    = misaki["dependence"]
    depend = old

    if depend >= 70:
        amount = int(amount * 0.4)
    elif depend >= 50:
        amount = int(amount * 0.7)

    misaki["dependence"] = clamp(misaki["dependence"] + amount, 0, 100)

    # マイルストーンを超えたら通知イベント
    for threshold in [DEPEND_MILD, DEPEND_MEDIUM, DEPEND_HEAVY]:
        if old < threshold <= misaki["dependence"]:
            renpy.call("misaki_dependence_milestone", threshold)
```

### ムード補正付き金銭要求（v2.0追加）

```python
def request_money_from_misaki(amount_type="small"):
    global stats, suspicion_count, himo_aptitude

    stats["times_asked_money"] += 1
    himo_aptitude["money_requests"] += 1

    required = {"small": 35, "medium": 55, "large": 75}
    if misaki["trust"] < required[amount_type]:
        return False, 0, "信頼度が足りない"

    import random
    mood_modifier = {
        "good":     1.2,
        "normal":   1.0,
        "tired":    0.7,
        "stressed": 0.3,
    }
    modifier = mood_modifier.get(misaki_mood["today_mood"], 1.0)

    if random.random() > modifier:
        mood_response = {
            "tired":    "ごめん、今日ちょっと余裕なくて",
            "stressed": "...今それどころじゃないんだけど",
        }
        msg = mood_response.get(misaki_mood["today_mood"], "今日は難しいかな")
        return False, 0, msg

    # 金額（v2.0下方修正）
    amounts = {
        "small":  (1500, 3000),
        "medium": (3000, 6000),
        "large":  (5000, 10000),
    }
    min_amt, max_amt = amounts[amount_type]
    amount = random.randint(min_amt, max_amt)

    change_trust(-3)
    change_dependence(8)
    change_money(amount, "美咲")

    if stats["times_asked_money"] >= 3:
        suspicion_count += 1
        if suspicion_count == 2:
            renpy.notify("美咲: 「...お金、大丈夫？」")

    return True, amount, "成功"
```

---

## 5. events/misaki_events.rpy（追加・変更）

### 美咲イニシアチブ：自発的連絡イベント（v2.0新規）

```python
label misaki_check_in:
    "美咲からLINEが来た。"
    "'最近どうしてる？'"
    $ reset_contact()

    menu:
        "返信する？"
        "元気だよと返す":
            himo "元気だよ〜、そっちは？"
            misaki_c "私も。...なんか急に気になって"
            $ change_trust(3)
        "忙しいと返す":
            himo "ちょっとバタバタしてて"
            misaki_c "そっか。無理しないでね"
            $ change_trust(1)
        "既読スルー":
            "返信しなかった。"
            $ change_trust(-3)
            $ add_suspicion("contact_delay")

    return


label misaki_stress_call:
    "深夜、美咲から着信が来た。"

    menu:
        "出る？"
        "出る":
            misaki_c "...ごめん、こんな時間に"
            himo "どした？"
            misaki_c "今日ちょっとしんどくて。声聞きたくなった"
            himo "...そっか。何かあった？"
            misaki_c "上司に理不尽なこと言われて"
            misaki_c "愚痴っていい？"

            menu:
                "聞く":
                    himo "聞くよ"
                    "30分ほど、美咲の愚痴を聞いた。"
                    misaki_c "...ありがとう。なんか楽になった"
                    $ change_trust(8)
                    $ change_dependence(5)
                    $ himo_aptitude["showed_concern"] += 2
                    $ change_stamina(-5)
                "さらっと励ます":
                    himo "大変だったな。でもお前ならなんとかなるって"
                    misaki_c "...うん。ありがとう"
                    $ change_trust(4)
                    $ change_dependence(3)

        "出ない":
            "着信を無視した。"
            "翌朝、美咲からLINEが来ていた。"
            "'ごめん、間違えた'"
            himo "...間違えてないだろ"
            $ change_trust(-4)

    return
```

### 依存度マイルストーンイベント（v2.0新規）

```python
label misaki_dependence_milestone(threshold):
    if threshold == DEPEND_MILD:
        "翌朝、美咲からLINEが来ていた。"
        "'昨日どこにいたの？ 連絡してよ'"
        himo "...あれ、急に？"
        "なんか、変わってきた気がする。"

    elif threshold == DEPEND_MEDIUM:
        "美咲から電話が来た。"
        misaki_c "ねえ、今週末絶対会えるよね？"

        menu:
            "約束する":
                himo "おう、会えるよ"
                misaki_c "よかった。じゃあ土曜ね"
                $ weekend_promised = True
                $ change_dependence(3)
            "曖昧にする":
                himo "まあ、たぶん..."
                misaki_c "...たぶん？"
                "電話口の空気が少し重くなった。"
                $ change_trust(-5)
                $ add_suspicion("vague_answer")
            "断る":
                himo "今週ちょっと難しいかも"
                misaki_c "...そっか"
                "声が沈んだ。"
                $ change_trust(-8)
                $ change_dependence(-3)

    elif threshold == DEPEND_HEAVY:
        "深夜にLINEが来た。"
        "'今日誰かといた？'"
        himo "...どこで知ったんだ"

        menu:
            "正直に話す":
                himo "友達と飯食ってた"
                misaki_c "そっか。...なんで言ってくれなかったの"
                $ change_trust(-3)
                $ himo_aptitude["honest_moments"] += 1
            "誤魔化す":
                himo "一人でいたよ"
                misaki_c "...そっか"
                "信じていないのが声でわかった。"
                $ change_trust(-8)
                $ stats["lies_told"] += 1
                $ himo_aptitude["lies"] += 1

    return


label misaki_broken_promise:
    "美咲からLINEが来た。"
    "'昨日、来なかったね'"
    himo "...やばい"

    menu:
        "謝る":
            himo "ごめん、急に用事が..."
            misaki_c "...次は必ず来てね"
            $ change_trust(-10)
            $ change_dependence(8)
        "言い訳する":
            himo "ちょっとトラブルがあって"
            misaki_c "...そっか"
            $ change_trust(-15)
            $ stats["lies_told"] += 1
            $ himo_aptitude["lies"] += 1

    $ weekend_promised = False
    return
```

### contact_misaki にムードヒント追加（v2.0変更）

```python
label contact_misaki:
    $ reset_contact()
    "美咲にLINEを送った..."

    python:
        mood = misaki_mood["today_mood"]

    if mood == "stressed":
        "2時間後、やっと返信が来た。"
        misaki_c "ごめん、バタバタしてて"
    elif mood == "tired":
        "しばらくして返信が来た。"
        misaki_c "お疲れ。今日しんどくて..."
    elif mood == "good":
        "すぐに返信が来た。"
        misaki_c "わ、ヒモ太郎！"
    else:
        if misaki["trust"] >= 25:
            "しばらくして返信が来た。"
        else:
            "既読スルーされた..."
            $ change_trust(-2)
            $ daily_flags["ignored_today"] = True
            return
        misaki_c "どうしたの？"

    menu:
        misaki_c "どうしたの？"

        "雑談する":
            call misaki_chat
            return
        "会いたいと言う":
            call misaki_date_request
            return
        "お金の相談をする" if misaki["trust"] >= 35:
            call misaki_money_request
            return
        "お金の話をする（真剣に）" if (misaki_events["M05_unlocked"]
                                       and not misaki_events["M05_done"]):
            call misaki_event_M05
            return
```

### misaki_date に連続デートリスク追加（v2.0変更）

```python
# misaki_date ラベルの末尾に追加

    $ misaki_streak += 1
    if misaki_streak >= 5:
        misaki_c "ねえ、ヒモ太郎って私のこと好き？"
        himo "...え"
        "なんか、重くなってきた気がする。"
        $ change_dependence(12)
    elif misaki_streak >= 3:
        "美咲: 「最近毎日会ってるね...」"
        $ change_dependence(8)
```

### M-02〜M-05（v1.0から数値のみ修正）

v1.0（`phase2_misaki_route_v1.0.md` セクション4）の実装コードをそのまま使用。  
以下の数値だけ差し替えること。

| 箇所 | v1.0 | v2.0 |
|---|---|---|
| M-02「素直に嬉しい」信頼 | +12 | +8 |
| M-02「素直に嬉しい」依存 | +10 | +6 |
| M-03「泊まる」信頼 | +15 | +8 |
| M-03「泊まる」依存 | +15 | +8 |
| M-05「正直」一時金 | 20,000〜30,000 | 10,000〜20,000 |
| M-05「お願い」一時金 | 15,000〜25,000 | 8,000〜15,000 |

---

## 6. events/daily_events.rpy（変更部分のみ）

### フリマ・バイトの削除（v2.0）

`street_flea_market` と `street_day_job` のラベルを削除。  
`afternoon_street` の選択肢からも除去する。  
`check_job_hint`（求人情報を見る）は残す。

### SNSに効果追加（v2.0）

```python
label check_sns:
    # ...既存の投稿表示コード...

    if tone in ("milestone", "scary"):
        $ change_stamina(-3)
    elif tone == "relatable":
        $ change_charm(1)

    python:
        import random
        if misaki["stage"] >= STAGE_CLOSE and random.random() < 0.15:
            renpy.call("sns_misaki_post")

    return


label sns_misaki_post:
    "美咲の投稿が流れてきた。"
    python:
        import random
        posts = [
            "'最近なんか充実してる気がする'",
            "'仕事疲れたけど、帰ったら連絡しよう'",
            "'たまには息抜きも大事だよね'",
        ]
        post = random.choice(posts)
    "[post]"
    himo "（...俺のことかな）"
    himo "（まあ、そんなわけないか）"
    return
```

### ランダム出費イベント（v2.0追加）

```python
label random_expense_event:
    python:
        import random
        events = [
            ("スマホの画面が割れた", 5000, "repair"),
            ("急に体調が悪くなった", 1500, "medicine"),
            ("友人から結婚祝いを求められた", 3000, "gift"),
            ("コインランドリーに行く羽目になった", 800, "laundry"),
            ("財布を落としかけてヒヤッとした", 0, "scare"),
        ]
        ev_name, ev_cost, ev_type = random.choice(events)

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
```

`advance_day()` 内に追記（20%の確率）:

```python
    import random
    if random.random() < 0.20:
        renpy.call("random_expense_event")
```

---

## 7. script.rpy（変更部分のみ）

### status_bar

```python
screen status_bar():
    frame:
        xalign 0.5
        yalign 0.02
        padding (15, 8)

        hbox:
            spacing 30
            text "[game_date[day]]日目([get_weekday_string()])"  size 24
            text get_time_string()                                size 24
            text "所持金: ¥[player[money]:,]"                   size 24 color "#FFD700"
            text "信頼: [misaki[trust]]"                         size 22 color "#87CEEB"
            text "依存: [misaki[dependence]]"                    size 22 color "#FF69B4"

            if player["stamina"] < 30:
                text "[[疲労]" size 20 color "#ff6b6b"
            if player["cleanliness"] < 20:
                text "[[不潔]" size 20 color "#4ecdc4"
```

### start / main_loop

```python
label start:
    call intro_scene
    $ misaki_events["M01_done"] = True
    if not flags["tutorial_done"]:
        call tutorial
        $ flags["tutorial_done"] = True
    jump main_loop


label main_loop:
    if game_date["day"] > GAME_DAYS:
        call ending_30days
        return

    scene bg_placeholder
    show screen status_bar

    if game_date["time"] == "morning":
        call morning_actions
    elif game_date["time"] == "afternoon":
        call afternoon_actions
    else:
        call night_actions

    hide screen status_bar
    $ advance_time()
    jump main_loop
```

### night_actions（美咲関連選択肢）

```python
label night_actions:
    menu:
        "【[game_date[day]]日目([get_weekday_string()])・夜】何をする？"

        "美咲と電話する" if (misaki_events["M02_unlocked"]
                            and not misaki_events["M02_done"]
                            and not daily_flags["date_planned_tonight"]):
            call misaki_event_M02

        "美咲の部屋に行く" if (is_weekend()
                              and misaki_events["M03_unlocked"]
                              and not misaki_events["M03_done"]):
            call misaki_event_M03

        "美咲の部屋に行く（週末）" if (is_weekend()
                                    and misaki_events["M03_done"]
                                    and location_flags["misaki_room_unlocked"]
                                    and not misaki["met_today"]):
            call misaki_room_visit

        "美咲の部屋に行く" if (misaki["stage"] >= STAGE_CLOSE
                              and misaki_events["M03_done"]
                              and not is_weekend()
                              and not misaki["met_today"]):
            call misaki_room_visit

        "美咲を誘う" if (not misaki["met_today"]
                        and not daily_flags["date_planned_tonight"]):
            call misaki_date_request

        "美咲に連絡する":
            call contact_misaki

        "コンビニ飯（700円）":
            if not can_afford(700):
                himo "...財布の中身が足りない"
                jump night_actions
            "コンビニ弁当を買ってきた。"
            $ change_money(-700)
            $ change_stamina(12)
            $ daily_flags["ate_today"] = True

        "風呂入って寝る":
            $ change_cleanliness(50)
            $ change_stamina(50)

    return
```

---

## 8. events/endings.rpy（30日版）

```python
label day7_ending:
    jump ending_30days

label ending_30days:
    scene bg_placeholder with fade
    "――30日目、夜――"

    python:
        can_pay       = player["money"] >= 0
        is_honest     = stats["lies_told"] <= 3
        is_dependent  = misaki["dependence"] >= 65
        met_often     = stats["times_met"] >= 10
        concern_shown = himo_aptitude["showed_concern"] >= 5

    if not can_pay:
        jump ending_bankruptcy_30days

    if is_honest and met_often and not is_dependent and concern_shown:
        jump ending_balance_30days
    elif is_dependent or not is_honest:
        jump ending_himou_30days
    else:
        jump ending_unstable_30days


label ending_balance_30days:
    scene bg_placeholder with fade
    "30日目。気がついたら、ひと月が経っていた。"
    misaki_c "ヒモ太郎、最近ちょっと変わったよね"
    himo "え、そうか？"
    misaki_c "なんか...ちゃんと向き合ってくれる感じがして"
    "自分でもよくわからないけど、何かが変わった気がした。"
    "【GOOD END】"
    "「少し、前に進めた気がした」"
    call show_himo_aptitude_result
    return

label ending_himou_30days:
    scene bg_placeholder with fade
    "30日目。振り返ると、美咲に頼りっぱなしのひと月だった。"
    misaki_c "ねえ、ヒモ太郎って...私がいないとダメだよね？"
    himo "...そうかもな"
    "美咲の顔には、愛情と、あと何か複雑な感情があった。"
    "【GRAY END】"
    "「楽な道は、終わらない」"
    call show_himo_aptitude_result
    return

label ending_unstable_30days:
    scene bg_placeholder with fade
    "30日目。なんとか生き延びた。"
    himo "まあ、何とかなったな"
    "でも、このままでいいのかという気持ちが消えない。"
    "【NORMAL END】"
    "「不安定な自由が、まだ続く」"
    call show_himo_aptitude_result
    return

label ending_bankruptcy_30days:
    scene bg_placeholder with fade
    "家賃が払えなかった。"
    himo "...終わった"
    "大家から退去通知が来た。"
    "【BAD END】"
    "「楽観も、ほどほどに」"
    call show_himo_aptitude_result
    return
```

---

## 9. 実装順序（推奨）

**Week 4: システム基盤**
1. `constants.rpy` 更新（GAME_DAYS=30・減衰値・依存マイルストーン定数）
2. `variables.rpy` 新変数追加（misaki_mood・weekend_promised等）
3. `time_system.rpy` 更新（曜日・月次・ムード更新・食事ペナルティ）
4. `parameter_system.rpy` 更新（収穫逓減・ムード補正）
5. `endings.rpy` 30日版に差し替え
6. 動作確認：30日ループ・月次請求・食事ペナルティが機能するか

**Week 5: イベント実装**
1. `misaki_check_in` / `misaki_stress_call`（美咲イニシアチブ）
2. `misaki_dependence_milestone` 3種 + `misaki_broken_promise`
3. M-02「終電後の電話」
4. M-03「週末の部屋」
5. M-05「お小遣いの話」
6. M-04スタブ配置
7. `contact_misaki` ムードヒント追加
8. SNS効果・ランダム出費追加

**Week 6: 整合チェック**
1. 美咲5イベント通しプレイ
2. パラメータバランス調整（下記チェックリスト）
3. 依存マイルストーンが自然なタイミングで発生するか確認

---

## 10. バランスチェックリスト（Week 6）

| チェック項目 | 目標値 |
|---|---|
| 30日時点の所持金 | 20,000〜40,000円 |
| 信頼度100到達タイミング | 22日目以降 |
| 依存度60到達タイミング | 15日目以降 |
| 依存マイルストーンの発生感 | 驚きはあるが理不尽ではない |
| GOOD END到達難易度 | 意識したプレイで到達できる |
| BAD END到達可能性 | 怠けプレイで普通に破産できる |
| ムードでお金の結果が変わるか | 体感できる |

---

## 11. Phase 3 移行チェック

- [ ] 30日ループが崩れずに回る
- [ ] 月次家賃が正常に引き落とされる
- [ ] M-02〜M-05が自然なタイミングで発生する
- [ ] 依存40/60/80のマイルストーンが発生する
- [ ] 美咲からの自発的連絡が発生する
- [ ] ムードによってお金の交渉結果が変わることを体感できる
- [ ] 3種のエンディングに到達できる
- [ ] 美咲だけで「ヒモとして生活している感」が出ている

---

*phase2_misaki_route_v2.0.md - 2026年2月19日作成*
