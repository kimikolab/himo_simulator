# ヒモ男シミュレーター Steamデモ Phase 2 実装指示書 v1.0

**対象**: ロードマップ Phase 2（Week 4〜6）  
**前提**: Phase 1（7日間プロトタイプ v2.6）が完成済みであること  
**ゴール**: 美咲との関係を育てながら30日間生活できる状態

最終更新日: 2026年2月19日

---

## Phase 2 で何を作るか

Phase 1（7日間）を**30日間に拡張**しつつ、美咲専用イベント5本を実装する。

| 追加・変更点 | 内容 |
|---|---|
| ゲーム期間 | 7日 → 30日 |
| 美咲イベント | M-01〜M-05（5本） |
| 新ロケーション | 美咲の部屋（女性宅） |
| 家賃サイクル | 週払い → 月払い（毎月1日 -50,000円） |
| 曜日システム | 平日/週末の区別 |
| M-04 | カナ未実装のためスタブとして配置 |

**実装しないもの（Phase 3以降）**
- カナ・麗子の本実装
- ナンパシステム
- ブッキング検知ロジック

---

## ディレクトリ変更点

```
himo-simulator/
└── game/
    ├── data/
    │   ├── constants.rpy     ← 変更（GAME_DAYS・家賃定数）
    │   └── variables.rpy     ← 変更（新フラグ追加）
    │
    ├── systems/
    │   └── time_system.rpy   ← 変更（曜日・月次家賃）
    │
    └── events/
        ├── misaki_events.rpy ← 大幅追加（M-01〜M-05）
        ├── daily_events.rpy  ← 変更（30日対応・場所追加）
        ├── endings.rpy       ← 変更（30日エンディング）
        └── script.rpy        ← 変更（main_loop更新）
```

---

## 1. data/constants.rpy の変更

```python
# constants.rpy

define TIMES_OF_DAY = ["morning", "afternoon", "night"]
define WEEKDAYS = ["日", "月", "火", "水", "木", "金", "土"]

# Phase 2変更: 30日・月払いに変更
define GAME_DAYS       = 30
define MONTHLY_RENT    = 50000    # 毎月1日に引き落とし
define PHONE_BILL      = 3000     # 月額（1日に引き落とし）

define STAMINA_DECAY_PER_TURN    = 3
define CLEANLINESS_DECAY_PER_TURN = 7

define STAGE_ACQUAINTANCE = 1
define STAGE_FRIEND       = 2
define STAGE_CLOSE        = 3
define STAGE_DATING       = 4

# イベント発生条件
define DOUBT_EVENT_DAY   = 12    # 疑念イベント（Phase1の5日目相当）

# 美咲イベント発生日の目安（条件未達でも自動発生しない）
define M02_EARLIEST_DAY  = 5     # 終電後の電話 最早発生日
define M03_EARLIEST_DAY  = 14    # 週末の部屋 最早発生日
define M05_EARLIEST_DAY  = 20    # お小遣いの話 最早発生日
```

---

## 2. data/variables.rpy の変更

Phase 1からの**差分のみ**を記載。既存の変数はそのまま維持。

```python
# variables.rpy（Phase 2追加分）

# ゲーム期間30日対応
default game_date = {
    "day": 1,
    "time": "morning",
    "weekday": 1       # Phase 2追加: 0=日, 1=月, ... 6=土（1日目=月曜始まり）
}

# 美咲イベント進行フラグ（Phase 2追加）
default misaki_events = {
    "M01_done": False,   # 再会のLINE（Phase1のintroで代替。初日完了扱い）
    "M02_done": False,   # 終電後の電話
    "M02_unlocked": False,
    "M03_done": False,   # 週末の部屋
    "M03_unlocked": False,
    "M04_done": False,   # カナとのバッティング（Phase 3でフル実装）
    "M05_done": False,   # お小遣いの話
    "M05_unlocked": False,
}

# 場所フラグ（Phase 2追加）
default location_flags = {
    "misaki_room_unlocked": False,   # 美咲の部屋が拠点として使える
    "staying_at_misaki": False,      # 現在美咲宅に宿泊中
}

# daily_flags に追加（Phase 2追加分）
default daily_flags = {
    "asked_money_today": False,
    "ignored_today": False,
    "date_planned_tonight": False,   # Phase 1で追加済みのはず
    "cooked_today": False,           # Phase 2追加: 料理フラグ
}

# 月次管理（Phase 2追加）
default monthly = {
    "rent_paid": False,     # 今月の家賃を払ったか
    "total_months": 1,      # 現在何ヶ月目か
}
```

---

## 3. systems/time_system.rpy の変更

### 変更点

- `advance_day()` に曜日進行と月次家賃処理を追加
- 美咲イベントのアンロック判定を追加

```python
# time_system.rpy（Phase 2修正版）

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
        global game_date, misaki, flags, daily_flags, location_flags, misaki_events

        game_date["day"]     += 1
        game_date["weekday"]  = (game_date["weekday"] + 1) % 7  # Phase 2追加
        misaki["met_today"]   = False

        # daily_flags リセット
        daily_flags["asked_money_today"]   = False
        daily_flags["ignored_today"]       = False
        daily_flags["date_planned_tonight"] = False
        daily_flags["cooked_today"]        = False

        # 美咲宅宿泊リセット（毎朝帰宅）
        location_flags["staying_at_misaki"] = False

        # 街アンロック
        if game_date["day"] == 4:
            flags["street_unlocked"] = True
            renpy.notify("街に出られるようになった")

        # 月次処理（Phase 2追加）
        if game_date["day"] > 1 and (game_date["day"] - 1) % 30 == 0:
            renpy.call("monthly_billing")

        # 美咲イベントアンロック判定（Phase 2追加）
        check_misaki_event_unlock()

        # 疑念イベント
        if game_date["day"] == DOUBT_EVENT_DAY and not flags["doubt_event_done"]:
            renpy.call("misaki_doubt_event")


    def check_misaki_event_unlock():
        """美咲イベントのアンロック条件を毎日チェック"""
        global misaki_events, misaki, player

        # M-02: 信頼度30以上 かつ M02_EARLIEST_DAY以降
        if (not misaki_events["M02_unlocked"]
                and misaki["trust"] >= 30
                and game_date["day"] >= M02_EARLIEST_DAY):
            misaki_events["M02_unlocked"] = True
            renpy.notify("美咲からLINEが来そうな気がする...")

        # M-03: 信頼度50以上 かつ M03_EARLIEST_DAY以降
        if (not misaki_events["M03_unlocked"]
                and misaki["trust"] >= 50
                and game_date["day"] >= M03_EARLIEST_DAY):
            misaki_events["M03_unlocked"] = True

        # M-05: 信頼度60以上 かつ M05_EARLIEST_DAY以降 かつ残金が少ない
        if (not misaki_events["M05_unlocked"]
                and misaki["trust"] >= 60
                and game_date["day"] >= M05_EARLIEST_DAY
                and player["money"] < 20000):
            misaki_events["M05_unlocked"] = True


    def is_weekend():
        """土日かどうか。0=日曜, 6=土曜"""
        return game_date["weekday"] in (0, 6)


    def get_weekday_string():
        return WEEKDAYS[game_date["weekday"]]


    def get_time_string():
        time_jp = {"morning": "朝", "afternoon": "昼", "night": "夜"}
        return time_jp.get(game_date["time"], "???")


# 低体力イベント（変更なし）
label event_low_stamina:
    "（体が重い...）"
    "（疲れすぎてる。少し休まないと）"
    return


# 月次請求イベント（Phase 2追加）
label monthly_billing:
    scene bg_placeholder with fade
    "――月が変わった――"
    "スマホに通知が来た。"
    "『家賃引き落とし: ¥50,000』"
    "『通信費引き落とし: ¥3,000』"

    python:
        total_bill = MONTHLY_RENT + PHONE_BILL
        can_pay_rent = player["money"] >= total_bill

    if can_pay_rent:
        $ change_money(-total_bill)
        "合計¥[total_bill:,]が引き落とされた。"
        himo "...払えた。ギリギリだけど"
    else:
        "残高不足で引き落とせなかった。"
        himo "やばい...どうすんだこれ"
        jump ending_bankruptcy_30days

    return
```

---

## 4. events/misaki_events.rpy の追加

Phase 1の `misaki_events.rpy` に以下を**追記**する。既存のラベルは変更不要。

---

### M-01「再会のLINE」

Phase 1の `intro_scene` がこの役割を担っているため、完了済みフラグのみ立てる。

```python
# script.rpy の start ラベル内に1行追加
label start:
    call intro_scene
    $ misaki_events["M01_done"] = True    # ← 追加

    if not flags["tutorial_done"]:
        call tutorial
        $ flags["tutorial_done"] = True

    jump main_loop
```

---

### M-02「終電後の電話」

**発生条件**: `misaki_events["M02_unlocked"] == True` かつ 夜に自宅待機

夜の行動メニューに選択肢として出現する。

```python
# misaki_events.rpy に追記

label misaki_event_M02:
    # 発生済みチェック
    if misaki_events["M02_done"]:
        return

    scene bg_placeholder
    "――夜、23時――"
    "もう寝ようかと思っていたとき、スマホが鳴った。"
    "着信: 美咲"

    himo "え、電話？LINEじゃなくて？"

    menu:
        "どうする？"
        "出る":
            call M02_answer
        "出ない":
            call M02_ignore

    return


label M02_answer:
    misaki_c "...もしもし。起きてた？"
    himo "おう、起きてたよ。どした？"
    misaki_c "...今日さ、終電乗り過ごしそうになって"
    himo "え、大丈夫だった？"
    misaki_c "うん、なんとか乗れた。でも一瞬パニックになって"
    misaki_c "なんか...誰かの声聞きたくなって"

    "少し間があった。"

    himo "...電話してきたの、俺に？"
    misaki_c "うん。...変？"
    himo "変じゃないよ"

    "なんか、嬉しいのか悲しいのかよくわからない気持ちになった。"

    misaki_c "ヒモ太郎って、いつも家にいるじゃん"
    himo "まあ、そうだね"
    misaki_c "それがなんか...安心するんだよね"

    "『安心』か。"

    menu:
        "何と返す？"
        "素直に嬉しいと言う":
            himo "俺も、電話来て嬉しかった"
            misaki_c "...そっか"
            "電話口で、美咲が少し笑った気がした。"
            $ change_trust(12)
            $ change_dependence(10)
            $ himo_aptitude["showed_concern"] += 1

        "軽く流す":
            himo "まあ、いつでも電話してきていいよ"
            misaki_c "うん、ありがとう"
            $ change_trust(7)
            $ change_dependence(6)

        "冗談を言う":
            himo "俺、ニート界の安定剤だから"
            misaki_c "あははっ！なにそれ"
            "美咲の笑い声が聞こえた。"
            $ change_trust(9)
            $ change_dependence(7)
            $ himo_aptitude["easy_choices"] += 1

    "しばらく他愛ない話をして、電話を切った。"
    "なんか、今日はよく眠れそうな気がした。"

    $ misaki_events["M02_done"] = True
    $ change_stamina(10)    # 精神的な充足感
    return


label M02_ignore:
    "...出るのやめた。"
    himo "なんか、出にくい雰囲気があった"
    "美咲からLINEが来た。"
    "'ごめん、間違えた'"
    himo "...間違えてないだろ"
    "罪悪感があった。"
    $ change_trust(-5)
    $ misaki_events["M02_done"] = True
    $ himo_aptitude["easy_choices"] += 1
    return
```

**呼び出し元（night_actions に追加）**:

```python
label night_actions:
    # ...既存コード...
    menu:
        "【[game_date[day]]日目・夜】何をする？"

        # Phase 2追加: M-02発生選択肢
        "美咲と電話する" if (misaki_events["M02_unlocked"]
                            and not misaki_events["M02_done"]
                            and not daily_flags["date_planned_tonight"]):
            call misaki_event_M02

        # ...既存の選択肢...
```

---

### M-03「週末の部屋」

**発生条件**: `misaki_events["M03_unlocked"] == True` かつ 土日の夜

週末の夜の行動メニューに選択肢として出現する。

```python
# misaki_events.rpy に追記

label misaki_event_M03:
    if misaki_events["M03_done"]:
        return

    scene bg_placeholder
    "――週末の夜――"
    misaki_c "今日、うちに来る？"
    himo "え、美咲の部屋？"
    misaki_c "うん。一人だと暇で。ご飯作るから"

    menu:
        "どうする？"
        "行く":
            call M03_go
        "断る":
            call M03_decline

    return


label M03_go:
    scene bg_placeholder with fade
    "美咲の部屋に来た。"
    "清潔で、でも少し生活感がある部屋。"
    "本棚には仕事の資料が並んでいる。"

    himo "いい部屋じゃん"
    misaki_c "散らかってるけど。ごはん、何食べたい？"
    himo "なんでも"
    misaki_c "じゃあパスタにする。得意なんだ"

    "美咲がキッチンに立った。"
    "なんか、自然な感じだな。"

    himo "（...こういう生活、普通に悪くない）"

    "料理をしてもらって、一緒に食べた。"

    misaki_c "どうだった？"
    himo "うまかった。マジで"
    misaki_c "よかった。...ねえ、今日泊まってく？"

    menu:
        "どうする？"
        "泊まる":
            himo "いいの？"
            misaki_c "うん。なんか...一人だと静かすぎて"
            "泊めてもらうことになった。"
            $ location_flags["misaki_room_unlocked"] = True
            $ location_flags["staying_at_misaki"] = True
            $ change_trust(15)
            $ change_dependence(15)
            $ change_stamina(30)      # よく休めた
            $ change_cleanliness(20)  # シャワー借りた
            $ himo_aptitude["easy_choices"] += 1

            "翌朝、美咲はスーツを着て出勤していった。"
            "俺は昼まで美咲の部屋で寝ていた。"
            himo "...これ、完全にヒモじゃん"
            himo "まあいっか"

        "断る（今日は帰る）":
            himo "今日は帰るわ。また誘って"
            misaki_c "そっか。また来てね"
            $ change_trust(10)
            $ change_dependence(8)
            $ location_flags["misaki_room_unlocked"] = True   # 場所は解放される
            $ himo_aptitude["showed_concern"] += 1

    $ misaki_events["M03_done"] = True
    return


label M03_decline:
    himo "今日はちょっと..."
    misaki_c "そっか。じゃあまた今度ね"
    "少し声が沈んだ気がした。"
    $ change_trust(-3)
    $ change_dependence(-2)
    $ misaki_events["M03_done"] = True
    return
```

**呼び出し元（night_actions に追加）**:

```python
label night_actions:
    menu:
        "【[game_date[day]]日目・夜】何をする？"

        # Phase 2追加: M-03 週末のみ表示
        "美咲の部屋に行く" if (is_weekend()
                              and misaki_events["M03_unlocked"]
                              and not misaki_events["M03_done"]
                              and not daily_flags["date_planned_tonight"]):
            call misaki_event_M03

        # 美咲宅が解放済みなら週末は定期的に使える（M-03完了後）
        "美咲の部屋に行く（週末）" if (is_weekend()
                                    and misaki_events["M03_done"]
                                    and location_flags["misaki_room_unlocked"]
                                    and not misaki["met_today"]
                                    and not daily_flags["date_planned_tonight"]):
            call misaki_room_visit

        # ...既存の選択肢...
```

**美咲の部屋訪問（M-03以降の定期行動）**:

```python
label misaki_room_visit:
    "美咲の部屋に来た。"
    misaki_c "いらっしゃい。今日は何食べたい？"

    menu:
        "何をする？"
        "ご飯を食べる（美咲の手料理）":
            "一緒にご飯を食べた。"
            $ misaki["met_today"] = True
            $ change_trust(5)
            $ change_dependence(5)
            $ change_stamina(15)

        "泊まる":
            "今日も泊まらせてもらった。"
            $ misaki["met_today"] = True
            $ location_flags["staying_at_misaki"] = True
            $ change_trust(3)
            $ change_dependence(10)
            $ change_stamina(30)
            $ change_cleanliness(20)
            $ himo_aptitude["easy_choices"] += 1

    return
```

---

### M-04「カナとのバッティング」（Phase 3スタブ）

Phase 3でカナが実装されるまで、この枠は**空のスタブ**として配置するだけでよい。  
現時点でプレイヤーが触れることはない。

```python
# misaki_events.rpy に追記（スタブ）

label misaki_event_M04:
    # Phase 3で実装
    # 発生条件: カナと美咲両方と関係があり、約束をすっぽかした場合
    return
```

---

### M-05「お小遣いの話」

**発生条件**: `misaki_events["M05_unlocked"] == True`（信頼度60以上・20日目以降・残金20,000円未満）

夜の行動メニュー、または美咲に連絡した際に選択肢が出現する。

```python
# misaki_events.rpy に追記

label misaki_event_M05:
    if misaki_events["M05_done"]:
        return

    scene bg_placeholder
    "――ある夜――"
    "美咲と一緒にいるとき、ふと真剣な顔になった。"

    misaki_c "ねえ、ちょっと聞いてもいい？"
    himo "なに？"
    misaki_c "お金、大丈夫？"

    "...鋭い。"

    himo "え、なんで？"
    misaki_c "なんとなく。最近ちょっと元気なさそうだったから"

    menu:
        "正直に話す":
            himo "...正直に言うと、結構やばい"
            misaki_c "そっか。..."

            "美咲は少し考えてから、財布を出した。"

            misaki_c "これ、使って。返さなくていいから"
            himo "...いいの？"
            misaki_c "いいよ。でも"

            "真剣な目で、こちらを見た。"

            misaki_c "ちゃんと、どうするか考えてね。ずっとは...難しいから"

            "ぐっとくるものがあった。"
            "美咲はわかってる。それでも、お金をくれた。"

            python:
                import random
                gift_amount = random.randint(20000, 30000)
            $ change_money(gift_amount)
            "¥[gift_amount:,]をもらった。"
            $ change_trust(8)
            $ change_dependence(15)
            $ himo_aptitude["honest_moments"] += 2

            menu:
                "何と言う？"
                "ありがとう、考える":
                    himo "...ありがとう。ちゃんと考える"
                    misaki_c "うん"
                    $ himo_aptitude["showed_concern"] += 1

                "ありがとう（流す）":
                    himo "ありがとう、助かる"
                    misaki_c "...うん"
                    "美咲の表情が、少し曇った。"
                    $ change_trust(-3)
                    $ himo_aptitude["easy_choices"] += 1

        "誤魔化す":
            himo "大丈夫大丈夫、何とかなるっしょ"
            misaki_c "...そっか"

            "美咲はそれ以上聞かなかった。"
            "でも、目が笑っていなかった。"

            $ stats["lies_told"] += 1
            $ himo_aptitude["lies"] += 1
            $ change_trust(-5)
            $ add_suspicion("vague_answer")

        "お願いする（直接的に）":
            himo "...実は、ちょっと貸してほしいんだけど"
            misaki_c "貸す、じゃなくてあげるよ"

            python:
                import random
                gift_amount = random.randint(15000, 25000)
            $ change_money(gift_amount)
            "¥[gift_amount:,]をもらった。"
            $ change_trust(-2)
            $ change_dependence(18)
            $ himo_aptitude["money_requests"] += 1
            $ himo_aptitude["easy_choices"] += 1

            "...楽な道を選んだ。"

    $ misaki_events["M05_done"] = True
    return
```

**呼び出し元（contact_misaki または night_actions に追加）**:

```python
label contact_misaki:
    # ...既存コード...
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

        # Phase 2追加: M-05 アンロック済みなら専用イベントへ
        "お金の話をする（真剣に）" if (misaki_events["M05_unlocked"]
                                       and not misaki_events["M05_done"]):
            call misaki_event_M05
            return
```

---

## 5. events/daily_events.rpy の変更

### 30日対応：SNS投稿のバリエーション追加

Phase 1のSNS投稿は4パターンのみ。30日だと同じ投稿が繰り返されるため、バリエーションを増やす。

```python
# daily_events.rpy の check_sns ラベルの sns_posts リストを差し替え

label check_sns:
    "SNSのタイムラインを見た。"

    python:
        import random
        sns_posts = [
            # Phase 1から
            ("同級生・健太", "本日付で主任に昇進しました！", "positive"),
            ("同級生・由美", "マイホーム購入！35年ローン頑張ります", "neutral"),
            ("同級生・大輔", "転職成功！でも試用期間中は緊張する", "neutral"),
            ("バイト仲間・拓也", "バイトだるい〜 でも気楽でいいか", "relatable"),
            # Phase 2追加
            ("同級生・翔太", "子ども生まれた！これからが大変だけど頑張る", "milestone"),
            ("大学の友人・みほ", "フリーランス2年目突入！仕事増えてきた", "positive"),
            ("高校の先輩", "会社の飲み会が憂鬱すぎる 毎回同じ話", "relatable"),
            ("元バイト仲間・ケン", "正社員になりました！給料上がった！", "positive"),
            ("SNSのフォロワー", "生きてるだけで丸儲けとか言うけど金はいるよな", "relatable"),
            ("知らない人のバズポスト", "20代のうちに貯金しとかないと老後やばいぞ", "scary"),
        ]
        post = random.choice(sns_posts)
        poster, content, tone = post

    "[poster]:"
    "[content]"

    if tone == "positive":
        himo "すごいな〜"
        himo "でも大変そう"

    elif tone == "neutral":
        himo "みんな色々背負って生きてるな"
        himo "俺には無理だわ"
        $ himo_aptitude["avoided_work"] += 1

    elif tone == "relatable":
        himo "わかる〜"
        himo "...って、俺はそれすらないんだけど"
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

    python:
        if random.random() < 0.15 and not flags["had_doubt_moment"]:
            renpy.call("moment_of_doubt")

    return
```

### 週末の行動変化

```python
# afternoon_actions に追記（週末の特別選択肢）

label afternoon_actions:
    "――昼、14時――"

    if is_weekend():
        himo "週末の昼か。最高すぎる"
    else:
        himo "平日の昼か。みんな働いてるのに"

    menu:
        "【[game_date[day]]日目([get_weekday_string()])・昼】何をする？"

        "街に出る" if flags["street_unlocked"]:
            call afternoon_street

        # 週末限定
        "買い物に行く（週末）" if is_weekend():
            call weekend_shopping

        "美咲に連絡する":
            call contact_misaki

        "昼寝する":
            "昼寝タイム。"
            himo "最高の贅沢だな、これ"
            $ change_stamina(35)
            $ himo_aptitude["easy_choices"] += 1

        "ステータス確認":
            call screen status_detail
            jump afternoon_actions

    return


label weekend_shopping:
    scene bg_placeholder
    "週末のスーパーに来た。"
    "家族連れで賑わっている。"
    himo "週末はにぎやかだな"

    menu:
        "何を買う？"
        "食材を買う（300〜800円）":
            if not can_afford(500):
                himo "...お金が..."
                return
            python:
                import random
                cost = random.randint(300, 800)
            $ change_money(-cost)
            $ change_stamina(8)
            himo "自炊するか"

        "お菓子を買う（200〜500円）":
            if not can_afford(200):
                himo "...節約しないと"
                return
            python:
                import random
                cost = random.randint(200, 500)
            $ change_money(-cost)
            $ change_stamina(5)
            himo "まあいっか、たまには"
            $ himo_aptitude["easy_choices"] += 1

        "何も買わずに帰る":
            himo "...金使わないほうがいいか"

    return
```

---

## 6. events/endings.rpy の変更

Phase 1の7日目エンディングを**30日目エンディング**に差し替える。  
条件を30日間のプレイに合わせて再設計。

```python
# endings.rpy（Phase 2版）

label day7_ending:
    # Phase 2ではこのラベルは使わない
    # main_loopの終了条件は GAME_DAYS = 30 に変更済みのため
    # ラベル名は互換性のため残しておく
    jump ending_30days

label ending_30days:
    scene bg_placeholder with fade
    "――30日目、夜――"

    python:
        can_pay = player["money"] >= 0    # 家賃は月次処理で引き落とし済み
        is_honest    = stats["lies_told"] <= 3
        is_dependent = misaki["dependence"] >= 65
        met_often    = stats["times_met"] >= 10
        concern_shown = himo_aptitude["showed_concern"] >= 5
        all_misaki_events = (misaki_events["M02_done"]
                             and misaki_events["M03_done"]
                             and misaki_events["M05_done"])

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
    "30日目。"
    "気がついたら、ひと月が経っていた。"

    misaki_c "ヒモ太郎、最近ちょっと変わったよね"
    himo "え、そうか？"
    misaki_c "なんか...ちゃんと向き合ってくれる感じがして"
    himo "...そりゃまあ"

    "自分でもよくわからないけど、何かが変わった気がした。"
    "ヒモのままかもしれない。でも、美咲との関係は本物だと思う。"

    "【GOOD END】"
    "「少し、前に進めた気がした」"

    call show_himo_aptitude_result
    return


label ending_himou_30days:
    scene bg_placeholder with fade
    "30日目。"
    "振り返ると、美咲に頼りっぱなしのひと月だった。"

    misaki_c "ねえ、ヒモ太郎って...私がいないとダメだよね？"
    himo "...そうかもな"
    misaki_c "...そっか"

    "美咲の顔には、愛情と、あと何か複雑な感情があった。"
    "この関係が、どこへ向かうのかわからない。"

    "【GRAY END】"
    "「楽な道は、終わらない」"

    call show_himo_aptitude_result
    return


label ending_unstable_30days:
    scene bg_placeholder with fade
    "30日目。"
    "なんとか生き延びた。"

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

## 7. script.rpy の変更

### status_bar に曜日表示を追加

```python
screen status_bar():
    frame:
        xalign 0.5
        yalign 0.02
        padding (15, 8)

        hbox:
            spacing 30

            # Phase 2: 曜日を追加
            text "[game_date[day]]日目([get_weekday_string()])" size 24
            text get_time_string()                               size 24
            text "所持金: ¥[player[money]:,]"                  size 24 color "#FFD700"
            text "信頼: [misaki[trust]]"                        size 22 color "#87CEEB"
            text "依存: [misaki[dependence]]"                   size 22 color "#FF69B4"

            if player["stamina"] < 30:
                text "[[疲労]" size 20 color "#ff6b6b"
            if player["cleanliness"] < 30:
                text "[[不潔]" size 20 color "#4ecdc4"
```

### main_loop の美咲イベント自動チェック

```python
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

---

## 8. 実装順序（推奨）

Week 4〜6 の作業を以下の順で進めると詰まりにくい。

**Week 4**
1. `constants.rpy` の定数更新（GAME_DAYS=30, 家賃定数）
2. `variables.rpy` に新フラグ追加
3. `time_system.rpy` の曜日・月次処理実装
4. `endings.rpy` を30日版に差し替え
5. 動作確認：30日ループが回るか、月次請求が発生するか

**Week 5**
1. M-02「終電後の電話」実装 → 動作確認
2. M-03「週末の部屋」実装 → 動作確認（美咲宅フラグ）
3. M-05「お小遣いの話」実装 → 動作確認
4. M-04スタブ配置
5. SNS投稿バリエーション追加・週末行動追加

**Week 6**
1. 美咲5イベント通しプレイ
2. パラメータバランス調整（下記チェックリスト参照）
3. 「美咲だけで3〜4時間遊べるか」確認

---

## 9. バランスチェックリスト（Week 6）

30日間のプレイを通じて以下を確認する。

| チェック項目 | 目標値 | 調整箇所 |
|---|---|---|
| 家賃を払い続けられるか | 月1回払えれば合格 | 日雇いバイト収入・美咲からの援助額 |
| 信頼度60に到達できるか | 20〜25日目あたり | change_trustの+値 |
| M-02〜M-05が自然に発生するか | ゲームの流れに沿っている | イベントのunlocked条件 |
| 依存度が上がりすぎないか | 30日でmax80程度が上限目安 | change_dependenceの値 |
| GOOD ENDに到達できるか | 条件を意識したプレイで到達できる | ending_30daysの条件式 |
| BAD ENDに追い込めるか | 怠けプレイで発生する | 家賃収支のバランス |

---

## 10. Phase 2 完了チェック

Phase 3（カナルート）に進む前に以下を確認。

- [ ] 30日ループが崩れずに回る
- [ ] 月次家賃（50,000円）が正常に引き落とされる
- [ ] M-02「終電後の電話」が発生する
- [ ] M-03「週末の部屋」が発生し、美咲宅が使える
- [ ] M-05「お小遣いの話」が発生する
- [ ] 3つのエンディング（GOOD/GRAY/BAD）に到達できる
- [ ] 曜日表示が正しく更新される
- [ ] 週末と平日で行動メニューが変わる
- [ ] 美咲だけで3〜4時間プレイできる

---

*phase2_misaki_route_v1.0.md - 2026年2月19日作成*
