# ヒモ男シミュレーター Phase 4 ステップ1 修正指示書 v1.2

**前提**: Phase 4 ステップ1 v1.1が実装済みであること  
最終更新日: 2026年3月7日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | 地雷イベントにも序盤ガードが必要 | date_incidents.rpy |
| 2 | バグ | 美咲との約束の日に部屋泊まり→「昨日来なかったね」矛盾 | misaki_events.rpy / time_system.rpy |
| 3 | バグ | 嘘パズル時間切れが「誤魔化せた」扱いになるケースがある | lie_puzzle.rpy |
| 4 | バグ | 所持金バレリスク後に再度お金要求→「さっきもらった」表示 | misaki_events.rpy |
| 5 | バグ | パチンコイベント後にターンが消費されない | midgame_events.rpy / daily_events.rpy |
| 6 | 改善 | カナに昼連絡するメリットが薄い | kana_events.rpy |
| 7 | 将来設計メモ | LINE専用UIの構想 | （実装なし・設計メモ） |

---

## 修正1: 地雷イベントにも序盤ガード

**問題**: 1日目の美咲デート後に「いつもありがとう」「俺のこと養ってよ」の地雷選択肢が出る。まだ関係が浅い段階でこの会話は不自然。

**ファイル**: `events/date_incidents.rpy`

`should_trigger_landmine` に日数ガードを追加。

```python
init python:
    def should_trigger_landmine():
        """地雷が発生するか判定"""
        import random

        # Phase 4 v1.2: 序盤（9日目以前）は地雷発生しない
        if game_date["day"] <= 9:
            return False

        return random.random() < 0.15
```

---

## 修正2: 美咲との約束の日の部屋泊まり矛盾

**問題**: 美咲と夜の約束がある日に「美咲の部屋」を選んで泊まった場合、翌日に「昨日来なかったね」と言われる。美咲の部屋にいるのに約束を破った扱いになっている。

**原因**: `flags["misaki_tonight"]`（約束フラグ）と、デート場所で美咲の部屋を選んだ判定が連動していない。

**ファイル**: `events/misaki_events.rpy` / `events/date_misaki_places.rpy`

### 修正方針

美咲との夜の約束がある日にデートが発生した場合、約束を果たしたとして `misaki_tonight` フラグを消化する。

```python
# date_misaki_places.rpy の共通処理に追加

label misaki_date_with_location:
    scene bg_placeholder

    "美咲と会うことになった。"

    # （場所選択メニュー — 既存）

    # デート後の共通処理
    $ misaki["met_today"] = True
    $ stats["times_met"] += 1
    $ daily_flags["date_with"] = "misaki"
    $ reset_contact()

    # Phase 4 v1.2: 約束フラグを消化
    if flags.get("misaki_tonight", False):
        $ flags["misaki_tonight"] = False

    call check_date_incidents("misaki")

    return
```

さらに、美咲の部屋デートは「約束の夜」として十分成立するので、部屋泊まりも約束履行扱いにする。

```python
# time_system.rpy の advance_day() 内
# 約束不履行チェックの条件に「美咲の部屋に泊まった」を除外

# 修正前（想定される既存ロジック）
# if flags.get("misaki_tonight", False) and not misaki["met_today"]:
#     # 約束を破った扱い

# 修正後
if flags.get("misaki_tonight", False) and not misaki["met_today"]:
    # 美咲の部屋に泊まった場合は除外（date_locationで判定）
    if daily_flags.get("date_location", None) != "misaki_room":
        # 約束を破った扱い
        $ change_trust(-8)
        $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
        misaki_c "昨日、来なかったね..."

$ flags["misaki_tonight"] = False
```

---

## 修正3: 嘘パズル時間切れが軽い結果になるケースの修正

**問題**: デート中にカナからLINE通知が来て、嘘パズルで時間切れ→「…」で済んでしまう。時間切れは「沈黙で逃げた」であって「誤魔化せた」ではない。現状 `BARE_SILENCE = 40` だが、探り中のハプニング経由で呼ばれた場合、バレ度40でも `uneasy`（なんとか誤魔化せた）判定になる。

**ファイル**: `systems/lie_puzzle.rpy`

`resolve_lie_puzzle` の閾値を調整。「時間切れ1回で suspicious」になるようにする。

```python
init python:
    def resolve_lie_puzzle(bare_gauge):
        """バレ度に基づいて結果を返す"""
        if bare_gauge >= BARE_MAX:
            return "busted"
        elif bare_gauge >= 60:        # 旧: 70
            return "suspicious"
        elif bare_gauge >= 30:        # 旧: 40
            return "uneasy"
        else:
            return "safe"
```

これにより:
- 時間切れ1回（+40）→ `suspicious`（怪しまれてる）
- 矛盾回答1回（+35）→ `uneasy`（不穏な空気）
- 完璧回答2回（+3+3=6）→ `safe`

さらに、ハプニング経由のLINE通知で嘘パズルが呼ばれた後の結果テキストを改善。

```python
# date_incidents.rpy の date_happening ラベル内
# line_notification → 相手の前で普通に見る → 名前が見えた場合

# 嘘パズル後の追加演出
python:
    result = lie_puzzle["result"]

if result == "busted":
    "完全にバレた。言い逃れできない。"
elif result == "suspicious":
    "相手の表情が曇った。信じてはいない。"
elif result == "uneasy":
    "なんとか場をやり過ごした。でも違和感は残っている。"
# "safe" の場合は run_lie_puzzle 内の処理で十分
```

---

## 修正4: 所持金バレリスク後のお金要求フラグ

**問題**: 所持金¥30,000超で美咲にお金要求→「本当にお金ないの？」で失敗する。しかし `asked_money_today` が `True` にセットされるため、同日中に再度要求しようとすると「さっきもらったばかり」と表示される。もらってないのに。

さらに、所持金バレリスクで失敗し続けると家賃¥50,000に到達できず、パチンコに頼るしかなくなる。

**ファイル**: `events/midgame_events.rpy` / `events/misaki_events.rpy`

### 修正A: 所持金バレリスク後のフラグ名を分ける

```python
# midgame_events.rpy のイベント⑨

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

    # Phase 4 v1.2: asked_money_today ではなく専用フラグを使う
    # → 「さっきもらったばかり」ではなく「さっき断られた」扱いにする
    $ daily_flags["money_refused_today"] = True

    return
```

```python
# misaki_events.rpy の misaki_money_request

label misaki_money_request:
    # 1日1回制限（成功した場合）
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    # Phase 4 v1.2: 断られた場合の制限（別メッセージ）
    if daily_flags.get("money_refused_today", False):
        himo "...さっき断られたし、今日は無理だな"
        return

    # 所持金バレリスク
    if player["money"] >= MONEY_SUSPICION_THRESHOLD:
        call midgame_money_suspicion
        return

    # 通常の処理...
```

### 修正B: 所持金バレリスクの閾値を調整

現状の閾値 ¥30,000 だと、家賃¥50,000に到達する前にずっとブロックされる。

```python
# constants.rpy

# 修正前
# define MONEY_SUSPICION_THRESHOLD = 30000

# 修正後: 閾値を引き上げ
define MONEY_SUSPICION_THRESHOLD = 40000
```

さらに、所持金バレリスクは毎回ではなく確率で発生するようにする（毎回だとお金を貯める手段が完全に断たれる）。

```python
# misaki_events.rpy

label misaki_money_request:
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    if daily_flags.get("money_refused_today", False):
        himo "...さっき断られたし、今日は無理だな"
        return

    # Phase 4 v1.2: 所持金バレリスク（確率発生）
    if player["money"] >= MONEY_SUSPICION_THRESHOLD:
        python:
            import random
            # 60%の確率で疑われる（40%はスルーされる）
            money_suspicious = random.random() < 0.60
        if money_suspicious:
            call midgame_money_suspicion
            return

    # 通常の処理...
```

これにより:
- ¥40,000以上持ってても40%の確率でお金を要求できる
- ただし疑われるリスクがあるから、必要最低限だけ貯める戦略が生まれる

### `daily_flags` に追加

```python
# variables.rpy の daily_flags に追加
"money_refused_today": False,
```

```python
# time_system.rpy の advance_day() リセット処理に追加
daily_flags["money_refused_today"] = False
```

---

## 修正5: パチンコイベント後のターン消費

**問題**: 街に出てパチンコイベントが発生した後、通常の街メニューがそのまま表示される。パチンコに行ったのにまだ行動できるのは不自然。

**ファイル**: `events/midgame_events.rpy` / `events/daily_events.rpy`

パチンコに「入る」を選んだ場合、ターンを消費する。

```python
# midgame_events.rpy

label midgame_pachinko_temptation:
    scene bg_placeholder

    "街を歩いていると、パチンコ屋の前を通りかかった。"
    "「新台入替！大盤振舞！」"

    himo "...ちょっと覗くだけ"

    menu:
        "入る":
            "気づいたら座っていた。"
            himo "まあちょっとだけ..."

            # （既存の勝ち負けロジック）

            $ change_stamina(-15)
            $ himo_aptitude["easy_choices"] += 1

            # Phase 4 v1.2: ターン消費フラグ
            $ flags["afternoon_consumed"] = True

        "通り過ぎる":
            himo "...いや、やめとこ"
            "誘惑に打ち勝った。"
            # 通り過ぎた場合はターン消費しない → 通常メニューへ

    $ flags["midgame_pachinko_triggered"] = True
    return
```

```python
# daily_events.rpy の afternoon_street

label afternoon_street:
    scene bg_placeholder

    # パチンコの誘惑チェック
    if (player["money"] >= 15000
        and game_date["day"] >= 10
        and not flags.get("midgame_pachinko_triggered", False)):
        python:
            import random
            if random.random() < 0.25:
                renpy.call("midgame_pachinko_temptation")

    # Phase 4 v1.2: パチンコに入った場合はターン消費済み
    if flags.get("afternoon_consumed", False):
        $ flags["afternoon_consumed"] = False
        return

    # 以下、通常の街メニュー...
```

---

## 修正6: カナに昼連絡するメリット追加

**問題**: カナに昼連絡しても「雑談する」か「会いたいと言う」しかなく、夜にカナデートの約束をするだけ。昼の段階でカナに連絡するメリットが薄い。

**ファイル**: `events/kana_events.rpy`

カナへの昼連絡に「おねだりする」「写真を送ってもらう」等の選択肢を追加。カナからの恩恵（清潔感向上のアドバイス、食事の差し入れ等）を昼の段階で受けられるようにする。

```python
label contact_kana:
    $ kana["last_contact"] = 0

    "カナにLINEを送った..."

    # （既存の返信判定）

    menu:
        kana_c "なに？"

        "雑談する":
            kana_c "暇〜。ヒモ太郎も暇？"
            himo "暇だよ"
            kana_c "じゃあ今夜会おう"
            $ flags["kana_tonight"] = True
            $ change_trust_kana(3)

        "今日会いたいと言う":
            call kana_date_request

        # Phase 4 v1.2: 追加選択肢
        "写真送って" if kana["trust"] >= 20:
            kana_c "え〜、何の？"
            himo "なんでもいいよ"
            kana_c "しょうがないな〜"
            "カナが自撮りを送ってきた。"
            himo "おー、かわいいじゃん"
            kana_c "でしょ！？"
            $ change_trust_kana(2)
            $ change_dependence_kana(2)
            # メリット: 魅力UP（カナの影響でおしゃれ意識）
            $ change_charm(2)

        "なんか食べたい" if kana["trust"] >= 30:
            kana_c "えー、作ってほしいの？"
            himo "コンビニでいいからさ"
            kana_c "しょうがないな〜。じゃあ持ってく"
            "しばらくして、カナがコンビニ弁当を届けてくれた。"
            $ change_trust_kana(3)
            $ change_dependence_kana(3)
            $ change_stamina(15)
            $ daily_flags["ate_today"] = True
            # メリット: 食事＋体力回復。会いに行かなくても飯が手に入る

        "甘える" if kana["trust"] >= 40 and kana["dependence"] >= 20:
            himo "会いたいな〜"
            kana_c "...もう、急にそういうこと言う"
            kana_c "じゃあ今夜絶対ね"
            $ flags["kana_tonight"] = True
            $ change_trust_kana(5)
            $ change_dependence_kana(5)
            # メリット: 夜の約束＋信頼依存が両方上がる

    return
```

これにより:
- 信頼20以上で「写真送って」→ 魅力UP（おしゃれ意識）
- 信頼30以上で「なんか食べたい」→ 食事＋体力回復（ターン消費なしで飯確保）
- 信頼40以上で「甘える」→ 夜の約束＋両パラメータUP

カナに連絡する理由がフェーズごとに増えていく構造。

---

## 修正7: 将来設計メモ — LINE専用UI

**※今回は実装なし。将来の設計検討用メモ。**

### 構想

LINEのやり取りを専用UIで表示する。Ren'Pyの `screen` で実現可能。

```
┌──────────────────────┐
│  美咲              ○ │  ← 相手の名前＋アイコン
├──────────────────────┤
│                      │
│         おはよう     │  ← 相手の吹き出し（左寄せ）
│                      │
│    おう、おはよ      │  ← 自分の吹き出し（右寄せ）
│                      │
│  ...本当にお金       │  ← 相手（ドキッとするメッセージ）
│  ないの？            │
│                      │
│  【選択肢が下に表示】 │
│  ① 誤魔化す         │
│  ② 正直に言う       │
└──────────────────────┘
```

### 実装イメージ

```python
screen line_chat(messages, choices=None):
    frame:
        xalign 0.5
        yalign 0.5
        xsize 500
        ysize 700
        background "#eeeeee"

        vbox:
            # ヘッダー
            frame:
                xfill True
                background "#6cc655"
                padding (15, 10)
                text "[chat_partner]" color "#ffffff" size 22

            # メッセージ領域
            viewport:
                scrollbars None
                ysize 500
                vbox:
                    spacing 10
                    for msg in messages:
                        if msg["from"] == "other":
                            # 左寄せ吹き出し
                            frame:
                                xalign 0.0
                                xmaximum 350
                                background "#ffffff"
                                padding (12, 8)
                                text msg["text"] size 18
                        else:
                            # 右寄せ吹き出し
                            frame:
                                xalign 1.0
                                xmaximum 350
                                background "#6cc655"
                                padding (12, 8)
                                text msg["text"] size 18 color "#ffffff"

            # 選択肢
            if choices:
                vbox:
                    spacing 8
                    for choice in choices:
                        textbutton choice["text"]:
                            action Return(choice["key"])
```

### 効果

- 「本当にお金ないの？」がLINE画面で突然来ると心理的インパクトが大きい
- 既読/未読の演出が可能（既読スルーの緊張感）
- 通知音SEとの組み合わせで没入感UP
- 配信映えする（視聴者にもLINE画面が分かりやすい）

### 実装タイミング

Phase 4の素材整備フェーズ（ステップ4）、またはPhase 5のUI仕上げで検討。コアシステムが安定してから着手が望ましい。

---

## テスト確認項目

- [ ] 9日目以前にデートの地雷イベントが発生しない
- [ ] 美咲との約束日に美咲の部屋デート→翌日「来なかったね」が出ない
- [ ] 嘘パズル時間切れ1回で `suspicious` 判定になる
- [ ] 所持金バレリスクで断られた後、再要求時に「さっき断られたし」と表示される
- [ ] 所持金¥40,000以上でも40%の確率でお金要求が通る
- [ ] パチンコに入った場合、その後の街メニューが表示されない
- [ ] パチンコを通り過ぎた場合は通常メニューが表示される
- [ ] カナに昼連絡で「写真送って」「なんか食べたい」「甘える」が信頼度に応じて出る
- [ ] カナの「なんか食べたい」で食事判定＋体力回復が入る

---

*phase4_step1_v1.2_fixes.md - 2026年3月7日作成*
