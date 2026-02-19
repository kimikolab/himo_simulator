# ヒモ男シミュレーター 7日間プロトタイプ 実装指示書 v2.5（最終版）

**更新内容**:
- パラメータ表示を3つに絞り込み
- 美咲の疑念イベント追加（5日目）
- ヒモ適性診断システム実装
- 就職ルートは匂わせるのみ
- **Ren'py Characterオブジェクトによるキャラクター定義に統一**

---

## プロジェクト概要

- **プロジェクト名**: himo-simulator-prototype
- **目標**: 1-2週間で完成する動くゲーム
- **プレイ時間**: 30分-1時間
- **キャラクター**: 美咲（25歳）1人のみ
- **エンディング**: 3種類 + ヒモ適性診断

---

## ディレクトリ構造

```
himo-simulator/
├── game/
│   ├── script.rpy
│   ├── options.rpy
│   ├── screens.rpy
│   │
│   ├── data/
│   │   ├── characters.rpy        # ★キャラクター定義（新規追加）
│   │   ├── variables.rpy
│   │   └── constants.rpy
│   │
│   ├── systems/
│   │   ├── time_system.rpy
│   │   └── parameter_system.rpy
│   │
│   ├── events/
│   │   ├── intro.rpy
│   │   ├── tutorial.rpy
│   │   ├── misaki_events.rpy
│   │   ├── daily_events.rpy
│   │   └── endings.rpy
│   │
│   └── images/
│       └── bg_placeholder.png
```

---

## Ren'pyキャラクター定義ルール

### 台詞の書き方

```python
# ✅ 正しい書き方
himo "まあ何とかなるっしょ"
misaki_c "久しぶり！ご飯行こうよ♪"
"これはナレーション（地の文）"
"（心の声もナレーションとして書く）"

# ❌ 間違った書き方（名前がウィンドウに表示されない）
"ヒモ太郎「まあ何とかなるっしょ」"
"美咲『久しぶり！ご飯行こうよ♪』"
```

### 使い分け

| 書き方 | 用途 |
|-------|------|
| `himo "台詞"` | ヒモ太郎の台詞 |
| `misaki_c "台詞"` | 美咲の台詞 |
| `"テキスト"` | ナレーション・地の文・心の声 |
| `centered "テキスト"` | 画面中央表示（タイトル等） |

---

## 実装ファイル詳細

### 1. data/characters.rpy（新規作成）

```python
# characters.rpy
# キャラクター定義
# 全ての台詞はここで定義したエイリアスを使う

# プレイヤーキャラクター
define himo = Character("ヒモ太郎", color="#ffffff")

# メインキャラクター
define misaki_c = Character("美咲", color="#ffb7c5")

# Phase 2以降に追加予定（今はコメントアウト）
# define kana_c  = Character("カナ",   color="#ffe066")
# define reiko_c = Character("麗子",   color="#b7d7ff")
# define yui_c   = Character("ゆい",   color="#c8f7c5")
# define airi_c  = Character("あいり", color="#e8b7ff")
# define risa_c  = Character("理沙",   color="#ffd4b7")
```

---

### 2. data/constants.rpy

```python
# constants.rpy

define TIMES_OF_DAY = ["morning", "afternoon", "night"]
define WEEKDAYS = ["日", "月", "火", "水", "木", "金", "土"]

define WEEKLY_RENT = 12500
define PHONE_BILL = 750

define STAMINA_DECAY_PER_TURN = 3
define CLEANLINESS_DECAY_PER_TURN = 7

define STAGE_ACQUAINTANCE = 1
define STAGE_FRIEND = 2
define STAGE_CLOSE = 3
define STAGE_DATING = 4

define GAME_DAYS = 7
define DOUBT_EVENT_DAY = 5
```

---

### 3. data/variables.rpy

```python
# variables.rpy

default player = {
    "name": "ヒモ太郎",
    "age": 25,
    "money": 3458,
    "stamina": 100,
    "max_stamina": 100,
    "charm": 50,
    "cleanliness": 50
}

default game_date = {
    "day": 1,
    "time": "morning"
}

default misaki = {
    "name": "佐藤美咲",
    "age": 25,
    "trust": 30,
    "dependence": 10,
    "stage": 1,
    "last_contact": 0,
    "met_today": False
}

default suspicion_count = 0

default flags = {
    "tutorial_done": False,
    "first_money": False,
    "first_date": False,
    "street_unlocked": False,
    "had_doubt_moment": False,
    "doubt_event_done": False
}

default stats = {
    "total_earned": 0,
    "times_met": 0,
    "times_asked_money": 0,
    "lies_told": 0,
    "optimistic_choices": 0
}

# ヒモ適性診断（裏で集計、プレイヤーには非表示）
default himo_aptitude = {
    "easy_choices": 0,
    "money_requests": 0,
    "lies": 0,
    "honest_moments": 0,
    "avoided_work": 0,
    "showed_concern": 0
}
```

---

### 4. systems/time_system.rpy

```python
# time_system.rpy

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

        player["stamina"] = max(0, player["stamina"] - STAMINA_DECAY_PER_TURN)
        player["cleanliness"] = max(0, player["cleanliness"] - CLEANLINESS_DECAY_PER_TURN)

        misaki["last_contact"] += 1

        if player["stamina"] <= 15:
            renpy.call("event_low_stamina")

    def advance_day():
        global game_date, misaki, flags

        game_date["day"] += 1
        misaki["met_today"] = False

        if game_date["day"] == 4:
            flags["street_unlocked"] = True
            renpy.notify("街に出られるようになった")

        if game_date["day"] == DOUBT_EVENT_DAY and not flags["doubt_event_done"]:
            renpy.call("misaki_doubt_event")

        if game_date["day"] > GAME_DAYS:
            renpy.call("day7_ending")

    def get_time_string():
        time_jp = {"morning": "朝", "afternoon": "昼", "night": "夜"}
        return time_jp.get(game_date["time"], "???")


label event_low_stamina:
    "（体が重い...）"
    "（疲れすぎてる。少し休まないと）"
    return
```

---

### 5. systems/parameter_system.rpy

```python
# parameter_system.rpy

init python:
    def clamp(value, min_val, max_val):
        return max(min_val, min(max_val, value))

    def change_money(amount, source=""):
        global player, stats
        player["money"] += amount
        if amount > 0:
            stats["total_earned"] += amount

    def change_stamina(amount):
        global player
        player["stamina"] = clamp(player["stamina"] + amount, 0, player["max_stamina"])

    def change_charm(amount):
        global player
        player["charm"] = clamp(player["charm"] + amount, 0, 100)

    def change_cleanliness(amount):
        global player
        player["cleanliness"] = clamp(player["cleanliness"] + amount, 0, 100)

    def change_trust(amount):
        global misaki
        old_stage = misaki["stage"]
        misaki["trust"] = clamp(misaki["trust"] + amount, 0, 100)
        update_misaki_stage()

        if misaki["stage"] > old_stage:
            stage_names = {2: "友達", 3: "いい雰囲気", 4: "恋人"}
            if misaki["stage"] in stage_names:
                renpy.notify("美咲との関係が「" + stage_names[misaki["stage"]] + "」になった")

    def change_dependence(amount):
        global misaki
        misaki["dependence"] = clamp(misaki["dependence"] + amount, 0, 100)
        update_misaki_stage()

    def reset_contact():
        global misaki
        misaki["last_contact"] = 0

    def update_misaki_stage():
        global misaki
        trust = misaki["trust"]
        depend = misaki["dependence"]

        if trust >= 70 and depend >= 50:
            misaki["stage"] = STAGE_DATING
        elif trust >= 50:
            misaki["stage"] = STAGE_CLOSE
        elif trust >= 35:
            misaki["stage"] = STAGE_FRIEND
        else:
            misaki["stage"] = STAGE_ACQUAINTANCE

    def request_money_from_misaki(amount_type="small"):
        global stats, suspicion_count, himo_aptitude

        stats["times_asked_money"] += 1
        himo_aptitude["money_requests"] += 1

        required = {"small": 35, "medium": 55, "large": 75}
        if misaki["trust"] < required[amount_type]:
            return False, 0, "信頼度が足りない"

        import random
        amounts = {
            "small": (3000, 8000),
            "medium": (8000, 15000),
            "large": (15000, 25000)
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

    def add_suspicion(reason):
        global suspicion_count
        suspicion_count += 1

        messages = {
            "contact_delay": "美咲: 「最近忙しそうだね」",
            "vague_answer": "美咲: 「...そうなんだ」",
            "too_many_requests": "美咲: 「また？」",
            "avoided_question": "美咲: 「...」",
            "deflected": ""
        }
        if reason in messages and messages[reason]:
            renpy.notify(messages[reason])
```

---

### 6. events/intro.rpy

```python
# intro.rpy

label intro_scene:
    scene bg_placeholder with fade

    centered "{size=40}ヒモ男シミュレーター{/size}\n{size=25}7日間プロトタイプ{/size}"

    scene bg_placeholder

    "俺の名前はヒモ太郎。25歳。"
    "高校卒業後、フリーター生活を満喫中。"
    "...だったんだけど。"
    "先週、バイトをクビになった。"

    himo "まあ、あのバイト飽きてたし、ちょうど良かったかも"

    "スマホの残高通知。"
    "残高: 3,458円"

    himo "...おお、意外と残ってるじゃん"

    "暇だしSNS見るか。"
    "タイムラインには同級生の投稿。"
    "『昇進しました！』"
    "『マイホーム購入！』"

    himo "へー、みんな頑張ってんな"
    himo "ローンとか大変そう。俺は自由でいいわ"
    himo "...って、いやまあ、俺も何とかしないとな"
    himo "まあ、死にはしないでしょ"

    "その時、通知。"

    misaki_c "ヒモ太郎！久しぶり〜！ご飯行こうよ♪"

    himo "お、美咲じゃん"

    "高校の同級生。確か大手企業入ったって聞いたな。"

    himo "大手OLか〜、すげえな"
    himo "でも残業とか大変そう"
    himo "...あれ、もしかして"
    himo "俺、いいとこ取りできるんじゃね？"
    himo "よし、会ってみるか"

    "深く考えずに、返信ボタンを押した。"
    "こうして、俺の『ヒモ生活』が始まった――"
    "（本人はまだ自覚していない）"

    return
```

---

### 7. events/tutorial.rpy

```python
# tutorial.rpy

label tutorial:
    scene bg_placeholder

    "【チュートリアル】"
    "このゲームは7日間のプロトタイプです。"
    "1日は朝・昼・夜の3ターン。"
    "目標: 7日目の家賃支払い（12,500円）を乗り切ること"

    "重要なパラメータ:"
    "・所持金 ― 家賃が払えないとBAD END"
    "・信頼度 ― 高いほどお金をもらいやすい"
    "・依存度 ― 高いほど束縛される"

    "（体力や清潔感も重要ですが、画面には表示されません）"
    "あなたの選択で、7日間の結末が変わります。"

    return
```

---

### 8. events/misaki_events.rpy

```python
# misaki_events.rpy

label contact_misaki:
    $ reset_contact()

    "美咲にLINEを送った..."

    if misaki["trust"] >= 60:
        "すぐに返信が来た。"
    elif misaki["trust"] >= 40:
        "しばらくして返信が来た。"
    else:
        "既読スルーされた..."
        $ change_trust(-2)
        return

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


label misaki_chat:
    "他愛もない話をした。"
    himo "まあ、気楽に生きてるよ"

    $ change_trust(3)
    $ change_dependence(2)
    $ himo_aptitude["showed_concern"] += 1

    return


label misaki_date_request:
    if misaki["met_today"]:
        misaki_c "今日もう会ったよ？笑"
        himo "あ、そっか"
        return

    if game_date["time"] == "night":
        misaki_c "今から？いいよ♪"
        call misaki_date
        return
    else:
        misaki_c "夜なら空いてるよ"
        himo "了解〜"
        return


label misaki_date:
    scene bg_placeholder

    "美咲と会った。"

    misaki_c "お疲れ様！"

    if player["cleanliness"] < 30:
        misaki_c "...あれ、ヒモ太郎、ちょっと疲れてる？"

    "スーツ姿の美咲。ちょっと疲れてそう。"

    himo "お疲れ〜。残業？"
    misaki_c "うん、今日も遅かった..."
    himo "大変だな〜"

    $ misaki["met_today"] = True
    $ stats["times_met"] += 1
    $ change_stamina(-15)

    menu:
        "何を話す？"

        "仕事の愚痴を聞く":
            himo "仕事、そんなきついの？"
            misaki_c "きついけど...やりがいはあるんだ"
            himo "へー、えらいな"
            himo "俺には無理だわ、そんな責任ある仕事"
            misaki_c "ヒモ太郎は気楽でいいよね〜"
            himo "...まあね"
            misaki_c "あ、ごめん！嫌味じゃなくて"
            himo "いやいや、わかってるって"

            $ change_trust(5)
            $ change_dependence(5)
            $ himo_aptitude["showed_concern"] += 1

        "美咲を励ます":
            himo "まあでも、頑張ってる美咲かっこいいよ"

            "顔が赤くなった。"

            misaki_c "...ありがとう"
            himo "お、効いた効いた"

            $ change_trust(8)
            $ change_dependence(7)
            $ himo_aptitude["showed_concern"] += 2

        "自分の話（ポジティブに）":
            himo "俺？めっちゃ自由だよ"
            misaki_c "いいな〜"
            himo "朝起きて、昼寝して、夜寝る"
            himo "完璧な生活"
            misaki_c "あはは！でもそれ、飽きない？"
            himo "...たまに飽きる"
            misaki_c "正直！笑"

            $ stats["optimistic_choices"] += 1
            $ himo_aptitude["easy_choices"] += 1
            $ change_trust(6)
            $ change_dependence(4)

        "自分の話（正直に）":
            himo "...実は、バイトクビになったんだ"
            misaki_c "え！？大丈夫？"
            himo "まあ、何とかなるっしょ"
            misaki_c "...ヒモ太郎、ちゃんとしてる？"
            himo "ちゃんとはしてないかも"
            misaki_c "もう...何か手伝えることある？"

            "優しいな、美咲。"

            $ change_trust(10)
            $ change_dependence(8)
            $ himo_aptitude["honest_moments"] += 1

    if misaki["trust"] >= 45:
        misaki_c "今日は私が出すね"
        himo "マジ？ありがと〜"
        "気軽に受け取った。"

        if stats["times_met"] >= 3:
            "（...これで何回目だっけ）"
            "（まあいっか）"

        $ change_money(3000, "美咲（デート代）")
    else:
        "会計は割り勘。"
        himo "あ、財布..."
        $ change_money(-2000)

    misaki_c "また誘ってね！"
    himo "おう、また"

    "明日も美咲は満員電車で会社に行く。"
    "俺は...まあ、自由に過ごす。"

    himo "...これでいいのかな"
    himo "まあいっか！"

    if not flags["first_date"]:
        $ flags["first_date"] = True

    return


label misaki_money_request:
    himo "実は...お金が厳しくて"

    python:
        success, amount, msg = request_money_from_misaki("small")

    if success:
        misaki_c "...分かった。これ、使って"
        "美咲から¥[amount:,]をもらった。"
        himo "ありがと！助かる〜"

        if not flags["first_money"]:
            "（初めてお金もらった）"
            "（...これ、ヒモってやつじゃね？）"
            "（まあいっか）"
            $ flags["first_money"] = True

        menu:
            "何と言う？"

            "ありがとう、助かる":
                misaki_c "...困った時はいつでも言ってね"
                $ change_dependence(5)
                $ himo_aptitude["showed_concern"] += 1

            "すぐ返すから":
                misaki_c "いいよ、返さなくて"
                himo "マジ？ラッキー"
                $ change_trust(-2)
                $ change_dependence(3)
                $ stats["optimistic_choices"] += 1
                $ himo_aptitude["easy_choices"] += 1
    else:
        misaki_c "ごめん...今月厳しくて"
        "断られてしまった。"
        himo "そっか、しゃーない"

    return


# ========================================
# 美咲の疑念イベント（5日目）
# ========================================

label misaki_doubt_event:
    scene bg_placeholder

    "――[game_date[day]]日目――"
    "美咲と会っている時、ふと美咲が真面目な顔になった。"

    misaki_c "...ねえ、ヒモ太郎"
    himo "ん？"
    misaki_c "正直に聞いていい？"

    "...なんだろう、いつもと雰囲気が違う。"

    misaki_c "私のこと...利用してる？"
    himo "え"

    "心臓がドキッとした。"

    menu:
        "何と答える？"

        "正直に認める":
            himo "...正直に言うと、最初はそうだった"
            misaki_c "...やっぱり"

            "美咲の顔が、少し寂しそうになる。"

            himo "でも、今は違う。お前と一緒にいて、色々考えた"
            misaki_c "...本当？"
            himo "本当。...だと思う"
            misaki_c "...そっか"

            "美咲は、少し考え込むような顔をした。"

            misaki_c "...ありがとう、正直に言ってくれて"

            $ change_trust(10)
            $ himo_aptitude["honest_moments"] += 2
            $ flags["doubt_event_done"] = True

        "誤魔化す":
            himo "何言ってんの、そんなわけないじゃん"
            misaki_c "...そうだよね、ごめん"

            "でも、美咲の目は笑っていなかった。"
            "なんだか、気まずい空気が流れる。"

            misaki_c "...私、考えすぎかな"
            himo "そうそう、深く考えすぎ"

            "...嘘ついた。"

            $ change_trust(-5)
            $ stats["lies_told"] += 1
            $ himo_aptitude["lies"] += 1
            $ add_suspicion("avoided_question")
            $ flags["doubt_event_done"] = True

        "冗談でごまかす":
            himo "俺が美咲を利用？逆だろ〜、美咲に癒されてるし"
            misaki_c "...そう？"
            himo "そうそう。助かってるよ、マジで"
            misaki_c "...ならいいんだけど"

            "美咲は、あまり納得していない様子だった。"

            $ add_suspicion("deflected")
            $ himo_aptitude["easy_choices"] += 1
            $ flags["doubt_event_done"] = True

    "その後、少し気まずい空気が流れた。"
    "でも美咲は、いつもの笑顔に戻った。"
    "...本当に、いつもの笑顔なのだろうか。"

    return
```

---

### 9. events/daily_events.rpy

```python
# daily_events.rpy

label check_sns:
    "SNSのタイムラインを見た。"

    python:
        import random
        sns_posts = [
            ("同級生・健太", "『本日付で主任に昇進しました！』", "positive"),
            ("同級生・由美", "『マイホーム購入🏠 35年ローン頑張ります...』", "neutral"),
            ("同級生・大輔", "『転職成功！でも試用期間中緊張する💦』", "neutral"),
            ("バイト仲間・拓也", "『バイトだるい〜 でも気楽でいいか🍺』", "relatable"),
        ]
        post = random.choice(sns_posts)
        poster, content, tone = post

    "[poster]の投稿:"
    "[content]"

    if tone == "positive":
        himo "おー、すげえじゃん"
        himo "でも大変そうだな"
        $ stats["optimistic_choices"] += 1

    elif tone == "neutral":
        himo "ローンとか責任とか、色々背負うんだな"
        himo "俺はそういうの無理だわ"
        $ stats["optimistic_choices"] += 1
        $ himo_aptitude["avoided_work"] += 1

    elif tone == "relatable":
        himo "わかる〜"
        himo "...って、俺バイトないんだった"
        himo "まあいっか"

    python:
        import random
        if random.random() < 0.2 and not flags["had_doubt_moment"]:
            renpy.call("moment_of_doubt")

    return


label moment_of_doubt:
    himo "...あれ、俺このままで大丈夫かな"
    himo "まあ、何とかなるっしょ"

    $ flags["had_doubt_moment"] = True
    $ change_stamina(-3)
    return


label afternoon_street:
    scene bg_placeholder

    "街に出た。"

    if game_date["day"] <= 5:
        "平日の昼下がり。"
        "スーツ姿のサラリーマンが急いで歩いてる。"

        himo "みんな忙しそうだな"
        himo "俺は自由でいいわ〜"

        if game_date["day"] >= 5:
            "...でも、ちょっと羨ましい気もする。"
            himo "いや、俺は自由がいい！"

    menu:
        "何をする？"

        "カフェで休憩":
            "カフェに入った。"
            himo "平日昼のカフェ、最高"
            "周りはノーパソ開いてる人とか打ち合わせとか。"
            himo "みんな働いてんな〜"
            himo "俺はコーヒー飲むだけ！楽勝！"
            "...500円か。ちょっと痛いな。"

            $ change_money(-500)
            $ change_stamina(10)
            $ himo_aptitude["easy_choices"] += 1

        "服を見る":
            "服屋に入った。"
            himo "ちょっといい服買っとくか"

            $ change_money(-3000)
            $ change_charm(5)

            himo "おっ、いい感じ"

        "100円ショップに行く":
            "100円ショップをぶらぶら。"
            himo "100円で色々買えるの、最高だな"

            $ change_money(-300)

        "求人情報を見る":
            call check_job_hint

        "自宅に戻る":
            himo "帰るか"
            pass

    return


label check_job_hint:
    "街角の求人情報を見た。"
    "『未経験歓迎！』"
    "『20代活躍中！』"
    "『正社員登用あり！』"

    himo "...働くって選択肢もあるんだよな"
    "でも、今は美咲もいるし。"
    himo "まあ、また今度考えよう"

    $ himo_aptitude["avoided_work"] += 1

    return
```

---

### 10. events/endings.rpy

```python
# endings.rpy

label day7_ending:
    scene bg_placeholder with fade

    "――7日目、夜――"
    "スマホに通知が来た。"
    "『家賃引き落とし: ¥12,500』"

    python:
        can_pay = player["money"] >= WEEKLY_RENT

    if can_pay:
        $ change_money(-WEEKLY_RENT)
        "口座から引き落とされた。"
        "残高: ¥[player[money]:,]"
        himo "よっしゃ、払えた"
    else:
        "残高不足で引き落とせませんでした。"
        jump ending_bankruptcy

    python:
        is_honest      = stats["lies_told"] <= 1
        is_dependent   = misaki["dependence"] >= 60
        met_often      = stats["times_met"] >= 4
        showed_concern = himo_aptitude["showed_concern"] >= 3

    if can_pay and is_honest and met_often and not is_dependent and showed_concern:
        jump ending_balance
    elif can_pay and (is_dependent or not is_honest):
        jump ending_himou
    else:
        jump ending_unstable


label ending_balance:
    scene bg_placeholder with fade

    centered "{size=40}エンディング: 新しい関係{/size}"

    misaki_c "7日間、ありがとう"
    misaki_c "...実は分かってたよ。ヒモ太郎が困ってること"
    himo "...マジで？"
    misaki_c "でも、ちゃんと向き合ってくれたから"
    misaki_c "これからも、友達として...いや、もっと良い関係になれたらいいな"
    himo "...おう、よろしく"

    "こうして、俺と美咲の関係は新しい段階へ。"
    "ヒモではなく、対等なパートナーとして――"

    centered "{size=30}GOOD END{/size}"

    call show_himo_aptitude_result
    return


label ending_himou:
    scene bg_placeholder with fade

    centered "{size=40}エンディング: ヒモへの道{/size}"

    misaki_c "...ねえ、ヒモ太郎"
    misaki_c "私がいないと、ダメだよね？"

    "その目には、愛情と...何か別の感情。"

    himo "...ありがとう、美咲"

    "こうして、俺は美咲に頼る生活を続けることに。"

    himo "まあ、これはこれでアリかも"

    centered "{size=30}GRAY END{/size}"

    call show_himo_aptitude_result
    return


label ending_unstable:
    scene bg_placeholder with fade

    centered "{size=40}エンディング: 不安定な日々{/size}"

    "家賃は払えた。"
    himo "よし、何とかなった"

    "でも、この生活がいつまで続くのか。"
    "美咲との関係も、どこか歯車が合っていない気がする。"

    himo "...まあ、何とかなるっしょ"

    "不安定な日々は、まだ続く――"

    centered "{size=30}NORMAL END{/size}"

    call show_himo_aptitude_result
    return


label ending_bankruptcy:
    scene bg_placeholder with fade

    centered "{size=40}エンディング: 破滅{/size}"

    "家賃が払えなかった。"
    himo "...あれ、マジで？"
    "大家『来月までに...』"
    himo "やばい、何とかしないと"

    "でも、もう手遅れだった――"

    centered "{size=30}BAD END{/size}"
    centered "『楽観も、ほどほどに』"

    call show_himo_aptitude_result
    return


# ----------------------------------------
# ヒモ適性診断（全エンディング共通）
# ----------------------------------------

label show_himo_aptitude_result:
    scene bg_placeholder

    python:
        total = (
            himo_aptitude["easy_choices"] +
            himo_aptitude["honest_moments"] +
            himo_aptitude["showed_concern"] +
            max(himo_aptitude["avoided_work"], 1)
        )
        easy_ratio   = himo_aptitude["easy_choices"]   / max(total, 1)
        honest_ratio = himo_aptitude["honest_moments"] / max(total, 1)

        if easy_ratio > 0.6 and himo_aptitude["avoided_work"] >= 3:
            aptitude_type = "筋金入りのヒモ"
            aptitude_desc = "楽な選択を優先し、働くことを避ける傾向が強い"
        elif honest_ratio > 0.4 and himo_aptitude["showed_concern"] >= 3:
            aptitude_type = "根は真面目"
            aptitude_desc = "楽な道があっても、踏みとどまることができる"
        elif himo_aptitude["lies"] >= 3:
            aptitude_type = "口先巧者"
            aptitude_desc = "嘘で誤魔化すことに慣れている"
        else:
            aptitude_type = "日和見主義者"
            aptitude_desc = "状況次第で態度を変える"

    centered "━━━━━━━━━━━━━━━━━━"
    centered "{size=35}あなたのヒモ適性診断{/size}"
    centered "━━━━━━━━━━━━━━━━━━"

    centered "{size=28}タイプ: 『[aptitude_type]』{/size}"
    centered "[aptitude_desc]"

    centered "――行動統計――"
    centered "楽な選択: [himo_aptitude[easy_choices]]回"
    centered "お金の要求: [himo_aptitude[money_requests]]回"
    centered "嘘: [himo_aptitude[lies]]回"
    centered "正直な瞬間: [himo_aptitude[honest_moments]]回"
    centered "働くことを避けた: [himo_aptitude[avoided_work]]回"
    centered "美咲を気遣った: [himo_aptitude[showed_concern]]回"

    centered "プレイありがとうございました"

    return
```

---

### 11. script.rpy

```python
# script.rpy

label start:
    call intro_scene

    if not flags["tutorial_done"]:
        call tutorial
        $ flags["tutorial_done"] = True

    jump main_loop


label main_loop:
    if game_date["day"] > GAME_DAYS:
        call day7_ending
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


label morning_actions:
    if game_date["day"] <= 5:
        "――朝、10時――"
        himo "...よし、起きるか"
        "平日の朝10時。サラリーマンはもう満員電車。"
        himo "俺は自由だわ〜"

    menu:
        "【[game_date[day]]日目・朝】何をする？"

        "シャワーを浴びる":
            "シャワーを浴びた。"
            himo "平日昼間のシャワー、最高！"
            $ change_stamina(-3)
            $ change_cleanliness(35)

        "美咲に連絡する":
            "美咲にLINEするか。"
            call contact_misaki

        "SNSを見る":
            call check_sns

        "二度寝する":
            "もうちょっと寝よう。"
            himo "これが自由ってやつだ"

            if game_date["day"] >= 4:
                "...って、これでいいのか？"
                himo "まあいっか！寝よ寝よ"

            $ change_stamina(25)
            $ himo_aptitude["easy_choices"] += 1

    return


label afternoon_actions:
    "――昼、14時――"

    if game_date["day"] <= 5:
        "平日の昼下がり。"
        himo "ランチタイムも終わりか"
        himo "俺はこれから昼飯でも食うかな"

    menu:
        "【[game_date[day]]日目・昼】何をする？"

        "街に出る" if flags["street_unlocked"]:
            call afternoon_street

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


label night_actions:
    "――夜、21時――"

    if game_date["day"] <= 5:
        "夜9時。サラリーマンは終電心配してる時間。"
        himo "大変だなあ"

    menu:
        "【[game_date[day]]日目・夜】何をする？"

        "美咲を誘う" if not misaki["met_today"]:
            call misaki_date_request

        "美咲に連絡する":
            call contact_misaki

        "コンビニ飯":
            "コンビニ弁当買ってきた。"
            himo "うまいうまい"

            if game_date["day"] >= 5:
                "...一人で食うの、ちょっと寂しいな。"
                himo "まあいっか"

            $ change_money(-500)
            $ change_stamina(12)

        "風呂入って寝る":
            "風呂入って寝よう。"
            himo "明日も自由だ〜"
            $ change_cleanliness(30)
            $ change_stamina(50)

    return
```

---

### 12. screens.rpy

```python
# screens.rpy

screen status_bar():
    frame:
        xalign 0.5
        yalign 0.02
        padding (15, 8)

        hbox:
            spacing 30

            text "[game_date[day]]日目"           size 24
            text get_time_string()                 size 24
            text "所持金: ¥[player[money]:,]"     size 24 color "#FFD700"
            text "信頼: [misaki[trust]]"           size 22 color "#87CEEB"
            text "依存: [misaki[dependence]]"      size 22 color "#FF69B4"

            # 体力・魅力・清潔感は表示しない（裏で機能）


screen status_detail():
    modal True

    frame:
        xalign 0.5
        yalign 0.5
        xsize 700
        ysize 600
        padding (30, 30)

        vbox:
            spacing 20

            text "ステータス詳細" size 35

            text "■プレイヤー" size 28
            text "所持金: ¥[player[money]:,]" size 22
            text "体力: [player[stamina]]/100  （非表示）"  size 20 color "#999999"
            text "清潔感: [player[cleanliness]]  （非表示）" size 20 color "#999999"

            null height 20

            text "■美咲との関係" size 28
            text "信頼度: [misaki[trust]]" size 22
            text "依存度: [misaki[dependence]]" size 22

            python:
                stage_names = {1: "知り合い", 2: "友達", 3: "いい雰囲気", 4: "恋人"}
                stage_name  = stage_names.get(misaki["stage"], "???")

            text "関係: [stage_name]" size 22

            null height 20

            text "■統計" size 28
            text "総収入: ¥[stats[total_earned]:,]" size 22
            text "会った回数: [stats[times_met]]" size 22
            text "お金を要求: [stats[times_asked_money]]回" size 20

            null height 20

            textbutton "閉じる" action Hide("status_detail") xalign 0.5
```

---

## テスト項目

### 基本動作
- [ ] ゲームが起動する
- [ ] イントロ〜チュートリアルが表示される
- [ ] 7日間プレイできる
- [ ] 3つのエンディングに到達できる

### キャラクター表示
- [ ] ヒモ太郎の台詞で名前ウィンドウに「ヒモ太郎」と表示される
- [ ] 美咲の台詞で名前ウィンドウに「美咲」と表示される
- [ ] ナレーションは名前なしで表示される

### v2.5機能
- [ ] 表示パラメータが3つのみ（所持金・信頼・依存）
- [ ] 体力低下でイベント発生
- [ ] 5日目に疑念イベント発生
- [ ] 全エンディングでヒモ適性診断が表示される

### バランス
- [ ] 家賃12,500円が稼げる（難しすぎない）
- [ ] 選択によって展開が変わる

---

## 完成の目安

- 30分-1時間でクリアできる
- 選択によって展開が変わる
- ヒモ適性診断が楽しい
- バグがない
- 「また遊びたい」と思える

---

## Phase 2への拡張準備

Phase 1完成後に追加予定:
- サブキャラシステム
- ナンパシステム
- ゲーム期間を30日に延長
- キャラクター追加（カナ・麗子）
- エンディング8種類

**characters.rpy のコメントアウトを外すだけで新キャラを追加可能**

---