# ヒモ男シミュレーター Phase 3 修正指示書 v1.4

**前提**: Phase 3 v1.3が実装済みであること  
最終更新日: 2026年3月1日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | 同日朝夜で2回お金要求できる | time_system.rpy |
| 2 | バグ | ゲームオーバー後も美咲からメッセージが来る | time_system.rpy |
| 3 | バグ | カナデート後に美咲へのお金要求ができる | kana_events.rpy |
| 4 | UX | お金要求ブロック時にターンを消費しない | misaki_events.rpy |

---

## 修正1: 同日朝夜で2回お金要求できる

**原因**: `asked_money_today`のリセットが`advance_time()`内で行われており、夜のタイミングでリセットされてしまっている可能性がある。

**ファイル**: `systems/time_system.rpy`

`advance_time()` 内の `daily_flags` リセット処理を**すべて削除**し、`advance_day()` のみでリセットするよう統一する。

```python
def advance_time():
    global game_date, player, misaki, kana

    if game_date["time"] == "morning":
        game_date["time"] = "afternoon"
    elif game_date["time"] == "afternoon":
        game_date["time"] = "night"
    else:
        game_date["time"] = "morning"
        advance_day()   # 夜→朝の切り替え時のみadvance_dayを呼ぶ

    player["stamina"]     = max(0, player["stamina"]     - STAMINA_DECAY_PER_TURN)
    player["cleanliness"] = max(0, player["cleanliness"] - CLEANLINESS_DECAY_PER_TURN)

    misaki["last_contact"] += 1
    if kana_flags["met"]:
        kana["last_contact"] += 1

    if player["stamina"] <= 15:
        renpy.call("event_low_stamina")
    if player["cleanliness"] <= 0:
        renpy.call("event_low_cleanliness")

    # ❌ ここでdaily_flagsをリセットしてはいけない
    # daily_flagsのリセットはadvance_day()のみで行う


def advance_day():
    global game_date, misaki, kana, flags, daily_flags

    game_date["day"] += 1
    misaki["met_today"] = False
    kana["met_today"]   = False

    # daily_flagsのリセットはここだけで行う
    daily_flags["asked_money_today"]  = False
    daily_flags["ignored_today"]      = False
    daily_flags["ignored_kana_today"] = False
    daily_flags["ate_today"]          = False

    # ...以降既存コード（イベントチェック等）
```

---

## 修正2: ゲームオーバー後も美咲からメッセージが来る

**ファイル**: `systems/time_system.rpy`

`check_misaki_initiative()` および `check_kana_initiative()` の先頭に `game_ended` ガードを追加。

```python
def check_misaki_initiative():
    if flags.get("game_ended", False):   # 追加
        return
    import random
    global misaki
    # ...以降既存コード


def check_kana_initiative():
    if flags.get("game_ended", False):   # 追加
        return
    import random
    global kana
    # ...以降既存コード
```

---

## 修正3: カナデート後に美咲へのお金要求ができる

**原因**: `kana_date` または `kana_visit` 内で `misaki["last_contact"]` がリセットされているか、またはカナ関連の処理が誤って美咲の`last_contact`に触れている。

**ファイル**: `events/kana_events.rpy`

`kana_date` および `kana_visit` 内を確認し、以下の点を修正する。

```python
label kana_date:
    # ...既存コード...

    # ❌ 以下があれば削除（misaki.last_contactに触れてはいけない）
    # $ reset_contact()          ← 美咲のlast_contactをリセットしてしまう
    # $ misaki["last_contact"] = 0  ← 同上

    # ✅ カナのlast_contactのみリセット
    $ kana["last_contact"] = 0
    $ kana["met_today"] = True
    $ kana_dates_count += 1
    return


label kana_visit:
    # ...既存コード...

    # ❌ 同様に確認・削除
    # $ reset_contact()

    # ✅ カナのlast_contactのみリセット
    $ kana["last_contact"] = 0
    $ kana["met_today"] = True
    $ kana_dates_count += 1
    return
```

**合わせて確認**: `reset_contact()` 関数の定義を確認し、美咲の`last_contact`だけをリセットする関数になっているか確認する。カナ用は別関数にする。

```python
# parameter_system.rpy

def reset_contact():
    """美咲のlast_contactをリセット（実際に会った時のみ呼ぶ）"""
    global misaki
    misaki["last_contact"] = 0

def reset_contact_kana():
    """カナのlast_contactをリセット（実際に会った時のみ呼ぶ）"""
    global kana
    kana["last_contact"] = 0
```

---

## 修正4: お金要求ブロック時にターンを消費しない

**コンセプト**: 「最近会っていないのでお金を要求しにくい」と判断したとき、ターンを消費せずに元のメニューに戻る。

**ファイル**: `events/misaki_events.rpy`

`misaki_money_request` のブロック処理を `return` から元メニューへの分岐に変更。

```python
label misaki_money_request:
    # 1日1回制限
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return   # これはターン消費なしでOK（選択後すぐ戻る）

    # 最近会っていない場合 → ターン消費なしでメニューに戻る
    if misaki["last_contact"] > 1:
        himo "（最近会ってないし、さすがにお金の話はしにくいな）"
        # ターンを消費しないためにjumpで呼び出し元に戻す
        # 呼び出し元（morning_actions / afternoon_actions / night_actions）を
        # returnで抜けてメニューを再表示する
        return   # ← 呼び出し側のmenuがreturnを受け取り再表示される

    # ...以降既存コード（信頼チェック・金額抽選等）
```

**注意**: Ren'pyのmenu構造では、`call misaki_money_request` → `return` でメニューの次の行に進んでしまう場合がある。その場合は `call` ではなく `jump` で呼び出すか、呼び出し元のmenuラベルに `jump` で戻す構造にすること。Claude Codeの判断に委ねる。

---

## テスト確認項目

- [ ] 同日に朝・夜の2回お金を要求できない
- [ ] BAD END後に美咲からのメッセージが来ない
- [ ] カナデート後に美咲へのお金要求がブロックされる（last_contactが進んでいる）
- [ ] お金要求ブロック時に「しにくいな」と表示されてメニューに戻る（ターン消費なし）
- [ ] デートした当日・翌日は美咲にお金を要求できる
- [ ] デートから3ターン以上経過するとブロックされる

---

*phase3_v1.4_fixes.md - 2026年3月1日作成*
