# ヒモ男シミュレーター Phase 3 実装指示書 v1.0

**前提**: Phase 2 v2.4が実装済みであること  
最終更新日: 2026年2月21日

---

## 概要

Phase 3ではカナルートを追加し、2人の女性を同時管理する緊張感を実装する。

**実装スコープ**
- Week 7: カナ基本システム（出会い・恩恵・K-01〜K-03）
- Week 8: ブッキング・衝突イベント・エナジーシステム（K-04・M-04）
- Week 9: クライマックス・体験版エンド（K-05・整合チェック）

**エナジーシステムはWeek 8以降に実装**（Week 7の複雑化を避けるため）

---

## Week 7: カナ基本システム

### 1. キャラクター定義

**ファイル**: `data/characters.rpy`

```python
# コメントアウトを外す
define kana_c = Character("カナ", color="#ffe066")
```

**ファイル**: `data/variables.rpy`

```python
# カナのパラメータ（美咲と同じ構造）
default kana = {
    "name": "桜井カナ",
    "age": 21,
    "trust": 0,
    "dependence": 0,
    "stage": 0,       # 0=未出会い、1以降は美咲と同じ定義
    "last_contact": 0,
    "met_today": False,
}

# カナ関連フラグ
default kana_flags = {
    "met": False,             # 出会い済みか
    "k01_done": False,
    "k02_done": False,
    "k03_done": False,
    "k04_done": False,
    "k05_done": False,
    "sns_risk": 0,            # SNSバレリスク蓄積値
    "room_key": False,        # カナの部屋の鍵を持っているか
}

# カナ宅に関するロケーションフラグ（既存のlocation_flagsに追加）
# "staying_at_kana": False   ← location_flagsに追加
```

**`flags` 辞書にも追加**

```python
"kana_tonight": False,    # 今夜カナと約束がある
```

---

### 2. ナンパシステム

**コンセプト**: 魅力値が高いほど成功しやすい。カナとの出会いはナンパ経由のみ。

**ファイル**: `events/daily_events.rpy`

`afternoon_street` のメニューに追加（カナ未出会いの場合のみ表示）。

```python
"ナンパしてみる" if not kana_flags["met"]:
    call nanpa_event
```

```python
label nanpa_event:
    scene bg_placeholder

    "繁華街をぶらぶらしていた。"

    python:
        import random
        charm = player["charm"]
        if charm >= 70:
            success_rate = 0.60
        elif charm >= 50:
            success_rate = 0.40
        elif charm >= 35:
            success_rate = 0.25
        else:
            success_rate = 0.10

        nanpa_success = random.random() < success_rate

    if not nanpa_success:
        "声をかけてみたが、うまくいかなかった。"
        himo "...まあ、そんなもんか"
        $ change_stamina(-5)
        return

    # 成功
    "前を歩く女の子に声をかけた。"
    himo "あの、ちょっといいですか"

    "振り返ったのは、明るそうな女の子だった。"

    jump k01_nanpa_success
```

---

### 3. K-01「ナンパの成功」

**ファイル**: `events/kana_events.rpy`（新規作成）

```python
# kana_events.rpy

label k01_nanpa_success:
    scene bg_placeholder

    kana_c "え、なに？ナンパ？"
    himo "まあ...そんな感じです"
    kana_c "あはは、正直じゃん"

    "屈託のない笑顔だった。"
    "なんか、美咲とは全然違うタイプだな。"

    kana_c "カナ。桜井カナ。大学3年"
    himo "ヒモ太郎。25歳"
    kana_c "無職？笑"
    himo "...まあ"
    kana_c "いいじゃん、自由で"

    "連絡先を交換した。"

    $ kana["trust"] = 15
    $ kana["dependence"] = 0
    $ kana["stage"] = 1
    $ kana_flags["met"] = True
    $ kana_flags["k01_done"] = True

    "こうして、カナと知り合った。"
    "美咲とは全然違う空気。"
    himo "...なんか、新鮮だな"

    return
```

---

### 4. カナの恩恵システム

**コンセプト**

| 恩恵 | 条件 | 効果 |
|---|---|---|
| 昼間から部屋に来られる | カナと関係（Stage 2以上） | 昼の行動選択肢が増える |
| 食事をもらえる | カナ宅訪問時 | スタミナ+20、`ate_today=True` |
| シャワーを借りられる | カナ宅訪問時 | 清潔感+30 |
| 魅力値が微増 | カナと会うたび | 魅力+1（上限70まで） |
| エナ消費時の依存上昇が少ない | Week 8で実装 | 依存上昇が美咲の半分 |

**ファイル**: `events/kana_events.rpy`

```python
label kana_visit:
    scene bg_placeholder

    "カナの部屋に来た。"

    if game_date["time"] == "afternoon":
        "昼間から部屋に来られるのは、カナならでは。"
        kana_c "来た来た！暇だったんだよね〜"
    else:
        kana_c "いらっしゃい"

    # 食事
    if not daily_flags["ate_today"]:
        kana_c "ごはん食べた？なんか作るよ"

        menu:
            "食べていく":
                "カナが料理を作ってくれた。"
                kana_c "たいしたもんじゃないけど"
                himo "いや、うまい"
                $ change_stamina(20)
                $ daily_flags["ate_today"] = True
                $ change_trust_kana(3)

            "いい、気にしないで":
                himo "大丈夫、気にしないで"
                kana_c "そう？遠慮しなくていいのに"

    # シャワー
    if player["cleanliness"] < 50:
        kana_c "シャワー使う？タオルあるよ"

        menu:
            "借りる":
                "シャワーを借りた。"
                $ change_cleanliness(30)
                $ change_trust_kana(2)

            "いい":
                pass

    # 魅力値微増（上限70）
    if player["charm"] < 70:
        $ change_charm(1)

    $ kana["met_today"] = True
    $ kana["last_contact"] = 0

    return
```

**`change_trust_kana` と `change_dependence_kana` を `parameter_system.rpy` に追加**

```python
def change_trust_kana(amount):
    global kana
    old_stage = kana["stage"]
    kana["trust"] = clamp(kana["trust"] + amount, 0, 100)
    update_kana_stage()

    if kana["stage"] > old_stage:
        stage_names = {2: "友達", 3: "いい雰囲気", 4: "恋人"}
        if kana["stage"] in stage_names:
            renpy.notify("カナとの関係が「" + stage_names[kana["stage"]] + "」になった")

def change_dependence_kana(amount):
    global kana
    if amount > 0:
        depend = kana["dependence"]
        if depend >= 60:
            amount = int(amount * 0.3)
        elif depend >= 40:
            amount = int(amount * 0.5)

    old = kana["dependence"]
    kana["dependence"] = clamp(kana["dependence"] + amount, 0, 100)

    if old < 100 <= kana["dependence"]:
        renpy.notify("カナ: 「ヒモ太郎のことしか考えられない」")

def update_kana_stage():
    global kana
    trust  = kana["trust"]
    depend = kana["dependence"]

    if trust >= 70 and depend >= 50:
        kana["stage"] = STAGE_DATING
    elif trust >= 50:
        kana["stage"] = STAGE_CLOSE
    elif trust >= 35:
        kana["stage"] = STAGE_FRIEND
    elif trust > 0:
        kana["stage"] = STAGE_ACQUAINTANCE
    else:
        kana["stage"] = 0
```

---

### 5. K-02「インスタのストーリー」

**発生条件**: カナと知り合い後、信頼20以上、昼の自由時間

**ファイル**: `events/kana_events.rpy`

```python
label k02_insta_story:
    scene bg_placeholder

    "スマホを見ていると、カナのインスタのストーリーが上がっていた。"
    "今いる場所の写真。"
    "...繁華街だ。美咲と会うことが多いエリア。"

    himo "（あ、これまずいかも）"
    himo "（美咲に見られたら...）"

    "カナはインスタのフォロワーが5万人いる。"
    "誰でも見られる。"

    menu:
        "どうする？"

        "気にしない":
            himo "まあ、バレないだろ"
            $ kana_flags["sns_risk"] += 5
            $ himo_aptitude["easy_choices"] += 1

        "カナに非公開にしてもらうよう頼む":
            himo "（でも、なんて言えば...）"
            himo "（怪しまれるか）"
            "結局、何も言えなかった。"
            $ kana_flags["sns_risk"] += 3

        "自分のアカウントを非公開にする":
            himo "とりあえず、俺のアカウントを非公開にしておくか"
            "応急処置程度だが、気休めにはなる。"
            $ kana_flags["sns_risk"] += 1

    "SNS経由でバレるリスクが、じわじわ高まっている気がした。"

    $ kana_flags["k02_done"] = True
    return
```

---

### 6. K-03「お金ない自慢」

**発生条件**: カナの信頼35以上

**ファイル**: `events/kana_events.rpy`

```python
label k03_money_talk:
    scene bg_placeholder

    "カナと話していると、突然こんなことを言い出した。"

    kana_c "ねえ、今月マジで金ないんだけど"
    himo "え"
    kana_c "仕送り使い果たしてさ〜、バイトも先月サボりすぎて"
    kana_c "笑えるよね"

    "笑えない。"
    himo "（美咲と真逆だな）"

    menu:
        "大変だな（同情する）":
            himo "それは大変だな"
            kana_c "でしょ〜。ヒモ太郎も金ないんだっけ？"
            himo "俺も大概だよ"
            kana_c "じゃあ二人で貧乏同盟だ！"
            "なんか、妙な連帯感が生まれた。"
            $ change_trust_kana(8)
            $ change_dependence_kana(5)

        "少し渡す（1000円）" if can_afford(1000):
            himo "ちょっとだけど"
            kana_c "え、いいの？！"
            himo "まあ、俺も余裕ないけど"
            kana_c "ありがと〜！好きだわヒモ太郎"
            $ change_money(-1000)
            $ change_trust_kana(15)
            $ change_dependence_kana(10)

        "俺も金ない（正直に言う）":
            himo "俺も同じ状況だよ"
            kana_c "え、マジで？！"
            kana_c "じゃあどうやって生きてんの？"
            himo "...なんとかなってる"
            kana_c "謎すぎる。でもなんかウケる"
            $ change_trust_kana(10)
            $ himo_aptitude["honest_moments"] += 1

    "カナとお金の話をした。"
    "美咲とのお金の話とは、全然違う空気だった。"

    $ kana_flags["k03_done"] = True
    return
```

---

### 7. カナイベントのトリガー設定

**ファイル**: `script.rpy`

既存の `afternoon_actions` および `night_actions` にカナ関連のトリガーを追加。

```python
# afternoon_actions のメニューに追加
"カナの部屋に行く" if kana_flags["met"] and kana["stage"] >= 2:
    call kana_visit

    # K-02トリガー（信頼20以上・未発生）
    if kana["trust"] >= 20 and not kana_flags["k02_done"]:
        call k02_insta_story

    # K-03トリガー（信頼35以上・未発生）
    if kana["trust"] >= 35 and not kana_flags["k03_done"]:
        call k03_money_talk

# night_actions のメニューに追加
"カナを誘う" if kana_flags["met"] and not kana["met_today"]:
    call kana_date_request
```

```python
label kana_date_request:
    if daily_flags.get("ignored_kana_today", False):
        himo "今日はやめとこう"
        return

    if kana["met_today"]:
        kana_c "今日もう会ったじゃん"
        return

    python:
        import random
        trust = kana["trust"]
        # カナは美咲より会いやすい（暇な大学生）
        if trust >= 50:
            success_rate = 0.90
        elif trust >= 35:
            success_rate = 0.70
        elif trust >= 15:
            success_rate = 0.50
        else:
            success_rate = 0.30

        can_meet = random.random() < success_rate

    if not can_meet:
        kana_c "今日はちょっと〜、バイトあるんだよね"
        himo "そっか"
        return

    if game_date["time"] == "night":
        call kana_date
    else:
        kana_c "夜なら大丈夫だよ"
        $ flags["kana_tonight"] = True
        himo "了解"

    return


label kana_date:
    scene bg_placeholder

    "カナと会った。"
    kana_c "ヒモ太郎〜！"

    "いつも元気だな。"

    $ kana["met_today"] = True
    $ kana["last_contact"] = 0
    $ change_stamina(-10)   # 美咲より体力消費が少ない

    # 魅力値微増（上限70）
    if player["charm"] < 70:
        $ change_charm(1)

    menu:
        "何を話す？"

        "カナの話を聞く":
            kana_c "最近さ、TikTokにハマってて〜"
            himo "へー"
            kana_c "フォロワー増えてきた！"
            himo "すごいじゃん"
            "あんまりよくわからないけど、楽しそうだった。"
            $ change_trust_kana(5)
            $ change_dependence_kana(3)

        "一緒にいるだけ":
            "特に何も話さなかった。"
            "でも、それでいい空気だった。"
            $ change_trust_kana(3)
            $ change_dependence_kana(2)

        "自分の話をする":
            himo "最近暇でさ〜"
            kana_c "いいじゃん、一緒に暇しよ"
            "カナはこういうのを責めない。"
            $ change_trust_kana(4)
            $ change_dependence_kana(3)
            $ himo_aptitude["easy_choices"] += 1

    # 食事（ate_todayが未設定なら）
    if not daily_flags["ate_today"]:
        kana_c "ごはん、どっか行く？"
        himo "いいな"
        "カナが安い定食屋に連れて行ってくれた。"
        "割り勘だったが、安かった。"
        $ change_money(-600)
        $ change_stamina(15)
        $ daily_flags["ate_today"] = True

    return
```

---

## Week 8: ブッキング・衝突イベント・エナジーシステム

### 8. ダブルブッキング検知システム（シンプル版）

**コンセプト**: 同じターンに美咲とカナの両方と約束が入ったとき検知する。複雑な分岐は製品版へ。

**ファイル**: `systems/time_system.rpy`

```python
def check_double_booking():
    """同ターンに両方と約束が入っていないかチェック"""
    if flags.get("misaki_tonight") and flags.get("kana_tonight"):
        renpy.call("double_booking_event")

# advance_time() の末尾に追加
# （時間が進む前に翌ターンの約束チェック）
```

```python
label double_booking_event:
    "スマホを見ると、二つの約束が重なっていることに気づいた。"
    "美咲とカナ、両方と今夜の約束が入っている。"

    himo "...やばい"

    menu:
        "どちらを優先する？"

        "美咲を優先":
            "カナにLINEを送った。"
            himo "ごめん、今日急用が入って"
            kana_c "え〜、そうなんだ。まあいいけど"
            $ flags["kana_tonight"] = False
            $ change_trust_kana(-5)
            $ change_dependence_kana(3)

        "カナを優先":
            "美咲にLINEを送った。"
            himo "ごめん、今日急用が入って"
            misaki_c "...そうなんだ。分かった"
            $ flags["misaki_tonight"] = False
            $ change_trust(-8)
            $ change_dependence(5)
            $ add_suspicion("contact_delay")

        "両方すっぽかす":
            himo "...両方に謝るか"
            "美咲とカナ、両方に言い訳のLINEを送った。"
            $ flags["misaki_tonight"] = False
            $ flags["kana_tonight"] = False
            $ change_trust(-5)
            $ change_trust_kana(-5)
            $ himo_aptitude["lies"] += 1

    return
```

---

### 9. M-04「カナとのバッティング」

**発生条件**: 美咲・カナ両方と関係あり、約束すっぽかし後

**ファイル**: `events/misaki_events.rpy`

```python
label m04_batting:
    scene bg_placeholder

    "美咲と会っていると、スマホが鳴った。"
    "カナからのLINE。"
    "既読をつけないようにしながら、ポケットにしまった。"

    misaki_c "...今、誰から？"
    himo "友達"
    misaki_c "そうなんだ"

    "美咲は何も言わなかった。"
    "でも、その「そうなんだ」が少し重かった。"

    $ add_suspicion("vague_answer")
    $ stats["lies_told"] += 1
    $ himo_aptitude["lies"] += 1

    "後で確認すると、カナのLINEは『今日会えない？』だった。"
    himo "...まずいな"

    return
```

---

### 10. K-04「突然の訪問」

**発生条件**: カナの依存度40以上・美咲宅または自宅にいるとき

**ファイル**: `events/kana_events.rpy`

```python
label k04_sudden_visit:
    scene bg_placeholder

    "突然、カナからLINEが来た。"
    "'今から行っていい？'"

    python:
        at_misaki = location_flags.get("staying_at_misaki", False)

    if at_misaki:
        himo "（美咲の部屋にいるのに）"
        himo "（まずい）"

        menu:
            "断る（美咲の家にいることは言わない）":
                himo "今日ちょっと無理、ごめん"
                kana_c "え〜なんで〜"
                kana_c "じゃあ明日ね"
                "なんとか切り抜けた。"
                $ change_trust_kana(-3)
                $ change_dependence_kana(5)
                $ himo_aptitude["lies"] += 1

            "正直に言う（外出中と伝える）":
                himo "今、外出中でさ"
                kana_c "どこ？"
                himo "ちょっと遠くて..."
                kana_c "なんか怪しいな〜"
                "疑われた。でも乗り切った。"
                $ change_trust_kana(-5)
                $ change_dependence_kana(8)
                $ kana_flags["sns_risk"] += 5
    else:
        himo "（まあ、今日は大丈夫か）"
        kana_c "今から行っていい？"
        himo "いいよ"
        "カナが来た。"
        call kana_visit

    $ kana_flags["k04_done"] = True
    return
```

---

### 11. エナジーシステム（Week 8実装）

**コンセプト**: 使いすぎると枯渇、溜めすぎると暴走。適度に使うのが最適解。

**ファイル**: `data/variables.rpy`

```python
default energy = 3        # 現在値（最大3）
default energy_max = 3
default energy_full_days = 0   # 満タン継続日数
```

**ファイル**: `systems/parameter_system.rpy`

```python
def use_energy(target="misaki"):
    """エナジーを1消費。targetで依存上昇量が変わる"""
    global energy, energy_full_days

    if energy <= 0:
        return False, "energy_empty"

    energy -= 1
    energy_full_days = 0

    # 依存上昇（カナは美咲の約半分）
    if target == "misaki":
        change_dependence(15)
    elif target == "kana":
        change_dependence_kana(8)

    return True, "success"

def recover_energy():
    """1日休むと+1回復。advance_day()から呼ぶ"""
    global energy, energy_full_days

    if energy < energy_max:
        energy = min(energy + 1, energy_max)
        energy_full_days = 0
    else:
        energy_full_days += 1

        # 溜めすぎペナルティ
        if energy_full_days >= 7:
            renpy.call("energy_overflow_event")
        elif energy_full_days >= 5:
            change_charm(-10)
        elif energy_full_days >= 3:
            change_charm(-5)
```

```python
label energy_overflow_event:
    "なんか、余裕がなくなってきた。"
    himo "...ちょっと落ち着かないな"

    menu:
        "独りで発散する（エナる）":
            "エナってしまった。"
            himo "...エナっちまった"
            $ energy -= 1
            $ energy_full_days = 0
            $ himo_aptitude["easy_choices"] += 1

        "我慢する（70%で失敗）":
            python:
                import random
                gaman_success = random.random() < 0.30

            if gaman_success:
                "なんとか落ち着いた。"
                $ energy_full_days = 0
            else:
                "結局、エナってしまった。"
                himo "...エナっちまった"
                $ energy -= 1
                $ energy_full_days = 0
                $ himo_aptitude["easy_choices"] += 1

        "栄養ドリンクを飲む（1500円）" if can_afford(1500):
            "栄養ドリンクを飲んで気を紛らわせた。"
            $ change_money(-1500)
            $ energy_full_days = 0

    return
```

**エナジー消費イベント（美咲・カナ共通）**

```python
# misaki_room_visit / kana_visit 内に追加
# 「一緒に過ごす」選択肢からエナジーを消費

"一緒に過ごす" if energy > 0:
    python:
        success, msg = use_energy("misaki")   # カナなら"kana"

    if success:
        "――暗転――"
        "しばらくして。"
        misaki_c "...よかった"   # カナなら kana_c
        himo "...俺も"
        "エナジーを1消費した。残り[energy]/[energy_max]"
    return

"一緒に過ごす（エナジー不足）" if energy <= 0:
    himo "（今日はちょっと無理かな）"
    himo "疲れてて..."
    misaki_c "...そう。大丈夫？"
    $ change_trust(-3)
    $ add_suspicion("avoided_question")
    return
```

---

## Week 9: クライマックス・体験版エンド

### 12. K-05「俺のこと好き？」

**発生条件**: カナの依存度50以上

**ファイル**: `events/kana_events.rpy`

```python
label k05_do_you_like_me:
    scene bg_placeholder

    "カナとの時間が増えてきた頃。"
    "ふと、カナが真顔になった。"

    kana_c "ねえ、ヒモ太郎って私のこと好き？"
    himo "え"
    kana_c "普通に聞いてるだけ。好きか嫌いかってこと"

    "美咲と違う。ストレートだ。"

    menu:
        "好き":
            himo "好きだよ"
            kana_c "...ほんとに？"
            himo "ほんとに"
            kana_c "じゃあ私も好き。ちゃんと言っとく"
            "なんか、あっさりしてるけど、それがカナらしかった。"
            $ change_trust_kana(10)
            $ change_dependence_kana(15)
            $ flags["k05_accepted"] = True

        "まあ、嫌いじゃない":
            himo "嫌いじゃないよ"
            kana_c "なにそれ笑"
            kana_c "まあいいか"
            "カナは深く追及しなかった。"
            $ change_trust_kana(5)
            $ change_dependence_kana(8)
            $ flags["k05_ambiguous"] = True

        "正直に言えない":
            himo "...難しい質問だな"
            kana_c "なにそれ、ウケる"
            kana_c "まあ、逃げてるってことは嫌いじゃないってことにしとく"
            $ change_trust_kana(3)
            $ change_dependence_kana(5)

    $ kana_flags["k05_done"] = True
    return
```

---

### 13. 体験版エンドシーン（麗子への言及）

**発生条件**: K-05クリア後

**ファイル**: `events/kana_events.rpy`

```python
label demo_ending_scene:
    scene bg_placeholder

    kana_c "...ねえ、ほんとに私だけ？"
    himo "......"
    kana_c "まあいいけど"

    "カナは追及しなかった。"
    "でも、その一言が少し刺さった。"

    kana_c "あ、そういえばさ"
    himo "ん？"
    kana_c "麗子さんって人、ヒモ太郎のこと知ってるって言ってたよ？"
    himo "麗子？誰だそれ"
    kana_c "私も知らない。なんか大人っぽい感じの人。"
    kana_c "ヒモ太郎のこと、『面白い』って言ってたって聞いたけど"

    "――暗転――"

    centered "俺のヒモ生活は、まだ始まったばかりだった"

    centered "【体験版 END】"
    centered "製品版へ続く"

    return
```

---

## 追加変数・定数まとめ

### constants.rpy に追加

```python
define ENERGY_MAX = 3
define ENERGY_OVERFLOW_DAY = 7    # 何日満タンで強制イベント
define KANA_CHARM_CAP = 70        # カナ魅力値上限
```

### variables.rpy に追加（まとめ）

```python
# カナパラメータ
default kana = { ... }            # 上記参照
default kana_flags = { ... }      # 上記参照

# エナジー（Week 8）
default energy = 3
default energy_max = 3
default energy_full_days = 0

# flagsへの追記
"kana_tonight": False,
"game_ended": False,              # v2.4で追加済み
"k05_accepted": False,
"k05_ambiguous": False,
```

### status_bar への追加（screens.rpy）

```python
# カナと関係ができたら表示
if kana_flags["met"]:
    text "カナ信頼: [kana[trust]]"  size 20 color "#ffe066"
    text "カナ依存: [kana[dependence]]" size 20 color "#ffaa44"

# Week 8でエナジーも追加
text "エナ: [energy]/[energy_max]" size 20 color "#aaffaa"
```

---

## 実装順序

### Week 7（カナ基本）

1. `characters.rpy` にカナ定義を追加
2. `variables.rpy` にカナ変数・フラグを追加
3. `parameter_system.rpy` にカナ用関数を追加
4. `kana_events.rpy` を新規作成（K-01〜K-03・kana_visit・kana_date）
5. `daily_events.rpy` にナンパシステムを追加
6. `script.rpy` にカナ関連のトリガーを追加
7. `screens.rpy` にカナパラメータ表示を追加
8. **通しテストプレイ（カナとの基本的な関係が成立するか確認）**

### Week 8（衝突・エナジー）

1. `time_system.rpy` にダブルブッキング検知を追加
2. `misaki_events.rpy` にM-04を追加
3. `kana_events.rpy` にK-04を追加
4. `variables.rpy` にエナジー変数を追加
5. `parameter_system.rpy` にエナジー関数を追加
6. `misaki_events.rpy` / `kana_events.rpy` にエナジー消費選択肢を追加
7. `screens.rpy` にエナジー表示を追加
8. **通しテストプレイ（ブッキングとエナジーが機能するか確認）**

### Week 9（クライマックス）

1. `kana_events.rpy` にK-05を追加
2. `kana_events.rpy` に体験版エンドシーンを追加
3. `endings.rpy` に2キャラ対応の30日エンディングを追加
4. **2キャラ通しテストプレイ（整合性・バランス確認）**

---

## テスト確認項目（Week 7終了時）

- [ ] 魅力値に応じてナンパ成功率が変わる
- [ ] カナとの出会いイベントが正常に動作する
- [ ] カナの部屋で食事・シャワー・魅力上昇が機能する
- [ ] K-02（インスタ）・K-03（お金ない自慢）が発生する
- [ ] 美咲とカナの両方に同時にアプローチできる
- [ ] カナは美咲より会いやすい（当日誘い成功率が高い）

---

*phase3_kana_route_v1.0.md - 2026年2月21日作成*
