# ヒモ男シミュレーター Phase 2 修正指示書 v2.2

**前提**: Phase 2 v2.1が実装済みであること  
最終更新日: 2026年2月20日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バランス | 依存度の逓減を強化 | parameter_system.rpy |
| 2 | バランス | お金要求の金額を上方修正 | parameter_system.rpy |
| 3 | バランス | ランダム出費の発生確率を下げる | daily_events.rpy |
| 4 | バグ | 会った翌日に「最近どうしてる？」が発生 | time_system.rpy |
| 5 | 機能追加 | パチンコシステム実装 | daily_events.rpy / variables.rpy |

---

## 修正1: 依存度の逓減を強化

**ファイル**: `systems/parameter_system.rpy`

`change_dependence()` 内の逓減処理を修正。

```python
def change_dependence(amount):
    global misaki

    if amount > 0:
        depend = misaki["dependence"]
        # 逓減処理（強化版）
        if depend >= 60:
            amount = int(amount * 0.3)   # 旧: 0.4
        elif depend >= 40:
            amount = int(amount * 0.5)   # 旧: 0.7

    old = misaki["dependence"]
    misaki["dependence"] = clamp(misaki["dependence"] + amount, 0, 100)

    # 依存度100到達時の一言
    if old < 100 <= misaki["dependence"]:
        renpy.notify("美咲: 「ずっと一緒にいたい」")

    # マイルストーンイベント（既存コード）
    for threshold in [DEPEND_MILD, DEPEND_MEDIUM, DEPEND_HEAVY]:
        if old < threshold <= misaki["dependence"]:
            if not flags.get(f"depend_milestone_{threshold}", False):
                flags[f"depend_milestone_{threshold}"] = True
                renpy.call("misaki_dependence_milestone", threshold)
```

---

## 修正2: お金要求の金額を上方修正

**ファイル**: `systems/parameter_system.rpy`

`request_money_from_misaki()` 内の金額テーブルを修正。

```python
# 変更前
amounts = {
    "small":  (1500, 3000),
    "medium": (3000, 6000),
    "large":  (5000, 10000),
}

# 変更後
amounts = {
    "small":  (2000, 4000),
    "medium": (4000, 7000),
    "large":  (6000, 12000),
}
```

---

## 修正3: ランダム出費の発生確率を下げる

**ファイル**: `events/daily_events.rpy`

`random_expense_event` の発生確率を変更。

```python
# advance_day() または morning_actions 内の呼び出し箇所

# 変更前
if random.random() < 0.20:   # 20%（約6日に1回）
    renpy.call("random_expense_event")

# 変更後
if random.random() < 0.12:   # 12%（約8〜9日に1回）
    renpy.call("random_expense_event")
```

---

## 修正4: 会った翌日に「最近どうしてる？」が発生するバグ

**ファイル**: `systems/time_system.rpy`

`check_misaki_initiative()` に `last_contact` の確認を追加。

```python
def check_misaki_initiative():
    import random
    global misaki

    # 修正: last_contactが3以上の場合のみ発火
    # （美咲に会った・連絡した日はreset_contact()でlast_contact=0になるはず）
    # それでも発生するなら reset_contact() の呼び出し漏れを確認すること
    if misaki["last_contact"] < 3:
        return

    if random.random() < 0.6:
        renpy.call("misaki_check_in")
```

**合わせて確認**: `misaki_date` および `contact_misaki` の末尾で `reset_contact()` が呼ばれているか確認し、呼ばれていない箇所があれば追加する。

---

## 修正5: パチンコシステム実装（新規追加）

### 設計概要

```
掛け金: 1000円 / 3000円 / 5000円 から選択
結果抽選:
  勝ち  20% → 掛け金の2〜5倍を獲得
  引き分け 30% → 掛け金戻ってくる（プラマイゼロ）
  負け  50% → 掛け金全額失う

時間消費:
  通常: 昼ターンを1消費
  長丁場（20%の確率）: 昼＋夜ターンを消費
  → 長丁場になった場合、美咲との夜の約束が守れないリスクが生まれる
```

---

### variables.rpy

`stats` 辞書に追加。

```python
default stats = {
    # ...既存...
    "pachinko_wins":   0,
    "pachinko_losses": 0,
    "pachinko_profit": 0,   # 累計収支（マイナスもあり）
}
```

---

### daily_events.rpy

`afternoon_street` のメニューに「パチンコに行く」を追加し、ラベルを新規作成。

```python
# afternoon_street のメニューに追加
"パチンコに行く":
    call pachinko_event
```

```python
label pachinko_event:
    scene bg_placeholder

    "繁華街のパチンコ店に入った。"
    "平日昼間でも、それなりに人がいる。"
    himo "まあ、ちょっとだけな"

    # 掛け金選択
    menu:
        "いくら賭ける？"

        "1,000円":
            $ pachinko_bet = 1000

        "3,000円":
            $ pachinko_bet = 3000

        "5,000円" if can_afford(5000):
            $ pachinko_bet = 5000

    # 所持金チェック
    if not can_afford(pachinko_bet):
        himo "...財布の中身が足りない"
        himo "やめとくか"
        return

    $ change_money(-pachinko_bet)

    "台に向かった。"

    # 長丁場判定（20%）
    python:
        import random
        is_long_session = random.random() < 0.20

    if is_long_session:
        "なんか、ハマってしまった。"
        himo "もうちょっとだけ..."
        himo "あ、もうちょっとだけ..."
        "気づいたら夕方になっていた。"

        # 夜のターンも消費（advance_timeを1回追加で呼ぶ）
        $ advance_time()

        # 美咲との約束チェック
        if flags.get("weekend_promised", False) or misaki.get("tonight_plan", False):
            "スマホを見ると、美咲からのLINEが溜まっていた。"
            "'今日会う約束だったよね？'"
            "'どこにいるの？'"
            himo "...やばい"
            $ change_trust(-8)
            $ change_dependence(5)
            $ add_suspicion("contact_delay")
            "長丁場のせいで、約束を破ってしまった。"
        else:
            "気づいたら夕方になっていたが、今日は特に約束もなかった。"
            himo "...まあいっか"
    else:
        "1〜2時間で切り上げた。"

    # 結果抽選
    python:
        import random
        roll = random.random()
        if roll < 0.20:
            pachinko_result = "win"
            multiplier = random.uniform(2.0, 5.0)
            pachinko_gain = int(pachinko_bet * multiplier)
        elif roll < 0.50:
            pachinko_result = "draw"
            pachinko_gain = pachinko_bet   # 掛け金が戻る
        else:
            pachinko_result = "loss"
            pachinko_gain = 0

    if pachinko_result == "win":
        "大当たりが来た。"
        himo "よっしゃ！"
        "¥[pachinko_gain:,]を獲得した。"
        $ change_money(pachinko_gain)
        $ stats["pachinko_wins"]  += 1
        $ stats["pachinko_profit"] += pachinko_gain - pachinko_bet
        $ himo_aptitude["easy_choices"] += 1

    elif pachinko_result == "draw":
        "なんとかプラマイゼロで終わった。"
        himo "まあ、負けなかっただけいいか"
        $ change_money(pachinko_gain)   # 掛け金を返還
        $ stats["pachinko_profit"] += 0

    else:
        "全部飲まれた。"
        himo "...まあしゃーない"

        if player["money"] < 3000:
            "（残り¥[player[money]:,]か...）"
            "（明日の飯代、大丈夫かな）"
            himo "まあ何とかなるっしょ"

        $ stats["pachinko_losses"]  += 1
        $ stats["pachinko_profit"] -= pachinko_bet
        $ himo_aptitude["easy_choices"] += 1

    # スタミナ消費
    $ change_stamina(-20)

    return
```

---

### ヒモ適性診断への反映

`show_himo_aptitude_result` の統計表示部分にパチンコ結果を追加。

```python
# show_himo_aptitude_result 内の統計表示に追記

if stats["pachinko_wins"] + stats["pachinko_losses"] > 0:
    centered "パチンコ勝率: [stats[pachinko_wins]]勝 [stats[pachinko_losses]]敗"
    python:
        profit = stats["pachinko_profit"]
        profit_str = f"+{profit:,}" if profit >= 0 else f"{profit:,}"
    centered "パチンコ収支: ¥[profit_str]円"
```

---

## バランス期待値の確認

### パチンコの期待収支

```
掛け金1000円の場合:
  勝ち: 0.20 × 平均3500円獲得 = 期待値 +700円
  引き分け: 0.30 × 0円 = 0円
  負け: 0.50 × -1000円 = -500円
  期待値合計: +200円（ほぼ互角）

掛け金5000円の場合:
  勝ち: 0.20 × 平均17500円 = +3500円
  引き分け: 0円
  負け: 0.50 × -5000円 = -2500円
  期待値合計: +1000円
```

期待値は若干プラスですが長丁場リスクと体力消費があるため、美咲との約束がある日は使いにくい設計になっています。「リスクのある副収入手段」として機能します。

---

## 修正後のバランス目標

```
30日間の収支目標（テストプレイで確認）:
  収入: 美咲からの援助 70,000〜100,000円
      パチンコ（使った場合）: ±α
  支出: 家賃 50,000円
      食費 約15,000円
      ランダム出費 約10,000〜15,000円（12%に下げた想定）
  
  残高: 10,000〜30,000円程度でクリア可能
  →「余裕があるが油断すると詰む」くらいが理想
```

---

## テスト確認項目

- [ ] 依存度が信頼度より大幅に先行しなくなった
- [ ] お金をもらえる金額が上がった（期待値 3,000〜5,000円/回程度）
- [ ] ランダム出費が減って「多すぎる」感がなくなった
- [ ] 「最近どうしてる？」が会った翌日に発生しなくなった
- [ ] パチンコで掛け金を選択できる
- [ ] 勝ち/引き分け/負けの3パターンが発生する
- [ ] 長丁場になった場合に夜ターンが消費される
- [ ] 長丁場＋美咲の約束がある場合に信頼が下がる
- [ ] パチンコの収支がヒモ適性診断に表示される

---

*phase2_v2.2_fixes.md - 2026年2月20日作成*
