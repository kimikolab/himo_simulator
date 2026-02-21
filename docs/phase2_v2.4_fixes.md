# ヒモ男シミュレーター Phase 2 修正指示書 v2.4

**前提**: Phase 2 v2.3が実装済みであること  
最終更新日: 2026年2月21日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | 昼間宿泊なのに日曜朝シーンが発動 | misaki_events.rpy |
| 2 | バグ | 朝なのに「ある夜〜」テキストが表示 | misaki_events.rpy |
| 3 | バグ | 破滅END後にスタミナ警告が表示 | endings.rpy / time_system.rpy |
| 4 | 設計 | 当日誘いの制限を「完全ブロック」から「成功率段階変化」に緩和 | misaki_events.rpy |
| 5 | バランス | お金要求の金額をさらに上方修正 | parameter_system.rpy |

---

## 修正1: 昼間宿泊なのに日曜朝シーンが発動

**ファイル**: `events/misaki_events.rpy`

`misaki_room_visit` 内のフラグ設定に時間帯チェックを追加。

```python
# 変更前
if is_weekend() and game_date["weekday"] == 6:
    $ flags["misaki_sunday_morning"] = True

# 変更後: 土曜の「夜」に泊まった場合のみ
if is_weekend() and game_date["weekday"] == 6 and game_date["time"] == "night":
    $ flags["misaki_sunday_morning"] = True
```

---

## 修正2: 朝なのに「ある夜〜」テキストが表示

**ファイル**: `events/misaki_events.rpy`

`misaki_money_request` 内のテキストを時間帯分岐に変更。

```python
# 変更前
"ある夜、美咲に切り出した。"

# 変更後
python:
    time_str = {
        "morning":   "ある朝",
        "afternoon": "ある昼間",
        "night":     "ある夜",
    }
    time_text = time_str.get(game_date["time"], "ある日")

"[time_text]、美咲に切り出した。"
```

---

## 修正3: 破滅END後にスタミナ警告が表示

**ファイル**: `data/variables.rpy` および `events/endings.rpy` および `systems/time_system.rpy`

### variables.rpy

`flags` 辞書に追加。

```python
"game_ended": False,
```

### endings.rpy

全エンディングラベルの先頭に追加。

```python
label ending_bankruptcy_30days:
    $ flags["game_ended"] = True
    # ...以降既存コード

label ending_good_30days:
    $ flags["game_ended"] = True
    # ...

label ending_gray_30days:
    $ flags["game_ended"] = True
    # ...

label ending_normal_30days:
    $ flags["game_ended"] = True
    # ...
```

### time_system.rpy

`event_low_stamina` の先頭にガード追加。

```python
label event_low_stamina:
    if flags.get("game_ended", False):
        return
    "（体が重い...）"
    "（疲れすぎてる。少し休まないと）"
    return
```

---

## 修正4: 当日誘いの制限を緩和

**ファイル**: `events/misaki_events.rpy`

`misaki_date_request` の信頼度判定を変更。

```python
label misaki_date_request:
    # 既読スルーチェック（既存）
    if daily_flags.get("ignored_today", False):
        himo "今日はやめとこう"
        return

    # 既に会っているチェック（既存）
    if misaki["met_today"]:
        misaki_c "今日もう会ったよ？笑"
        return

    # v2.4修正: 約束なし当日誘いの成否判定（緩和版）
    if not flags.get("misaki_tonight", False):
        python:
            import random
            trust = misaki["trust"]
            if trust >= 70:
                success_rate = 0.85
            elif trust >= 50:
                success_rate = 0.65
            elif trust >= 35:
                success_rate = 0.40
            else:
                success_rate = 0.20   # 信頼35未満でも20%で会える

            can_meet = random.random() < success_rate

        if not can_meet:
            # 信頼度に応じた断り方
            if misaki["trust"] < 35:
                misaki_c "急に言われても...今日はちょっと難しいかな"
                himo "そっか、しゃーない"
                "（もう少し仲良くなれば会いやすくなるかも）"
            else:
                misaki_c "ごめん、今日はもう予定入っちゃってて"
                himo "そっか、また今度"

            $ change_trust(-1)
            return

    # 成功 → デートへ
    if game_date["time"] == "night":
        call misaki_date
    else:
        misaki_c "夜なら空いてるよ"
        $ flags["misaki_tonight"] = True
        himo "了解〜"

    return
```

**事前約束ルートは信頼度に関係なく確実に会える仕様を維持する。**
「前日または当日の昼に約束を取り付ける → 夜に確実に会える」という導線を残すことで、計画的プレイへの誘導になる。

---

## 修正5: お金要求の金額をさらに上方修正

**ファイル**: `systems/parameter_system.rpy`

```python
# 変更前（v2.2）
amounts = {
    "small":  (2000, 4000),
    "medium": (4000, 7000),
    "large":  (6000, 12000),
}

# 変更後（v2.4）
amounts = {
    "small":  (3000, 6000),
    "medium": (6000, 10000),
    "large":  (9000, 15000),
}
```

---

## 修正後のバランス目標

```
30日間の期待収支（美咲との関係を順調に育てた場合）:

収入:
  美咲からの援助（small × 15回程度）: 45,000〜90,000円
  パチンコ（任意）: 〜α

支出:
  家賃: 50,000円
  食費（昼食 + コンビニ飯）: 約18,000円
  ランダム出費（12%）: 約10,000〜15,000円

目標残高: +10,000〜30,000円でGOOD/GRAY END到達可能
詰む条件: 序盤に会えず収入が途絶えた場合 or パチンコ大敗
```

---

## テスト確認項目

### バグ修正
- [ ] 昼間に美咲宅に泊まっても日曜朝シーンが発動しない
- [ ] 朝・昼・夜でお金の相談テキストが正しく変わる
- [ ] 破滅END後にスタミナ警告が表示されない

### 設計変更
- [ ] 信頼30程度でも20%の確率で当日誘いが通る
- [ ] 信頼が上がるほど当日誘いが通りやすくなる
- [ ] 断られたとき信頼度に応じて台詞が変わる
- [ ] 事前に約束すれば信頼度に関係なく確実に会える

### バランス
- [ ] 序盤（1〜10日目）から美咲に会える機会が確保できる
- [ ] 30日クリア時に家賃50,000円を払えている
- [ ] 金額がv2.2より上がっている（small: 3,000〜6,000円程度）

---

*phase2_v2.4_fixes.md - 2026年2月21日作成*
