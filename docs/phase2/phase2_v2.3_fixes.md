# ヒモ男シミュレーター Phase 2 修正指示書 v2.3

**前提**: Phase 2 v2.2が実装済みであること  
最終更新日: 2026年2月21日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | 美咲宅翌日に「最近何してる？」再発 | misaki_events.rpy |
| 2 | バグ | 土曜宿泊→日曜スーツ出社が再発 | misaki_events.rpy |
| 3 | 設計 | 約束がある夜は美咲以外の選択肢を出さない | script.rpy / variables.rpy |
| 4 | 設計 | 約束なしでは会いにくくする（信頼度による制限） | misaki_events.rpy |
| 5 | バランス | お金要求時の依存上昇をさらに下げる | parameter_system.rpy |
| 6 | バランス | 気遣い系選択肢で依存が微減するように | misaki_events.rpy |

---

## 修正1: 美咲宅翌日「最近何してる？」再発

**原因**: `misaki_room_visit` の末尾で `reset_contact()` が呼ばれていない可能性が高い。

**ファイル**: `events/misaki_events.rpy`

`misaki_room_visit` の末尾（returnの直前）に追加。

```python
label misaki_room_visit:
    # ...既存コード...

    # v2.3確認: 以下が末尾に存在するか確認し、なければ追加
    $ reset_contact()
    $ misaki["met_today"] = True
    return
```

合わせて `check_misaki_initiative()` の条件も念のため強化。

```python
def check_misaki_initiative():
    import random
    global misaki

    # met_todayも確認（二重チェック）
    if misaki["last_contact"] < 3 or misaki["met_today"]:
        return

    if random.random() < 0.6:
        renpy.call("misaki_check_in")
```

---

## 修正2: 土曜宿泊→日曜スーツ出社が再発

**原因**: 前回の曜日分岐が `misaki_date` にしか適用されておらず、`misaki_room_visit` の描写が未修正のまま。

**ファイル**: `events/misaki_events.rpy`

`misaki_room_visit` 内の美咲の外見描写を曜日分岐に差し替え。

```python
# misaki_room_visit 内（「スーツを脱いだばかりの美咲」などの描写を以下に差し替え）
if is_weekend():
    "部屋着の美咲。リラックスした雰囲気。"
    "休日の夜、特別な時間が流れる。"
else:
    "スーツを脱いだばかりの美咲。少し疲れた様子。"
    "残業明けでも、笑顔を見せてくれた。"
```

`misaki_sunday_morning_scene` の翌朝描写も確認。

```python
label misaki_sunday_morning_scene:
    scene bg_placeholder
    "目が覚めると、美咲の部屋だった。"
    "カーテンの隙間から日差しが入ってくる。"
    "休日の朝。"   # ← この一行が必ずある状態に
    # ...以降既存コード
```

---

## 修正3: 約束がある夜は美咲以外の選択肢を出さない

### variables.rpy

`flags` 辞書に追加。

```python
"misaki_tonight": False,   # 今夜美咲と約束がある
```

1日目はこのフラグを最初から立てる。

```python
# intro.rpy または script.rpy の start ラベル内
$ flags["misaki_tonight"] = True   # 1日目は最初から美咲と約束
```

### script.rpy

`night_actions` の冒頭に追加。

```python
label night_actions:
    "――夜、21時――"

    # v2.3追加: 約束がある夜は美咲一択
    if flags.get("misaki_tonight", False):
        "今夜は美咲と約束がある。"
        $ flags["misaki_tonight"] = False
        call misaki_date
        return

    # 以降は既存の夜メニュー
    if game_date["day"] <= 5:
        "夜9時。サラリーマンは終電心配してる時間。"
        himo "大変だなあ"

    menu:
        # ...既存の選択肢...
```

### 約束設定のタイミング

美咲と「今夜会う約束」をしたとき（デートの約束をする選択肢を選んだ時点）でフラグを立てる。

```python
# contact_misaki または misaki_date_request 内
# 「今夜会う約束をした」流れの末尾に追加
$ flags["misaki_tonight"] = True
misaki_c "じゃあ夜に！"
himo "了解〜"
return
```

---

## 修正4: 約束なしでは会いにくくする

**ファイル**: `events/misaki_events.rpy`

`misaki_date_request` に信頼度による当日誘いの成否判定を追加。

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

    # v2.3追加: 約束なし当日誘いの成否判定
    if not flags.get("misaki_tonight", False):
        python:
            import random
            trust = misaki["trust"]
            if trust >= 70:
                success_rate = 0.70
            elif trust >= 50:
                success_rate = 0.50
            else:
                success_rate = 0.0   # 信頼50未満は当日誘い不可

            can_meet = random.random() < success_rate

        if trust < 50:
            misaki_c "急に言われても...今日は難しいかな"
            himo "そっか、しゃーない"
            "（事前に約束しておかないとダメか）"
            $ change_trust(-1)
            return

        if not can_meet:
            misaki_c "ごめん、今日はもう予定入っちゃってて"
            himo "そっか、また今度"
            $ change_trust(-1)
            return

    # 成功 → 夜のデートへ
    if game_date["time"] == "night":
        call misaki_date
    else:
        misaki_c "夜なら空いてるよ"
        $ flags["misaki_tonight"] = True
        himo "了解〜"

    return
```

---

## 修正5: お金要求時の依存上昇を下げる

**ファイル**: `systems/parameter_system.rpy`

`request_money_from_misaki()` 内の依存上昇を変更。

```python
# 変更前
change_dependence(8)

# 変更後
change_dependence(2)
```

---

## 修正6: 気遣い系選択肢で依存が微減

**ファイル**: `events/misaki_events.rpy`

`misaki_date` 内の気遣い系選択肢（「仕事の愚痴を聞く」「美咲を励ます」）に依存微減を追加。

```python
"仕事の愚痴を聞く":
    himo "仕事、そんなきついの？"
    misaki_c "きついけど...やりがいはあるんだ"
    # ...既存の台詞...
    $ change_trust(5)
    $ change_dependence(3)    # 変更前: 5
    $ change_dependence(-2)   # v2.3追加: 気遣いで依存微減
    $ himo_aptitude["showed_concern"] += 1

"美咲を励ます":
    himo "まあでも、頑張ってる美咲かっこいいよ"
    # ...既存の台詞...
    $ change_trust(8)
    $ change_dependence(5)    # 変更前: 7
    $ change_dependence(-3)   # v2.3追加: 励ましで依存微減
    $ himo_aptitude["showed_concern"] += 2
```

※ `change_dependence` を2回呼ぶのが冗長であれば、合算した値（+1、+2）に書き換えてOKです。

---

## 修正後のパラメータ目標値

```
30日間の理想的な進行:
  信頼: 65〜75程度でクリア
  依存: 60〜80程度でクリア（信頼と近い値）

  信頼と依存の差: 10〜15以内が理想
  （現状: 信頼68・依存100 → 差が32と大きすぎる）
```

---

## テスト確認項目

### バグ修正
- [ ] 美咲宅に泊まった翌日に「最近何してる？」が来ない
- [ ] 土日に美咲が私服で登場する（スーツなし）

### 設計変更
- [ ] 1日目の夜は美咲との約束のみ表示される
- [ ] 約束中に「美咲に連絡する」選択肢が出ない
- [ ] 信頼50未満で当日誘いが断られる
- [ ] 信頼50〜69で当日誘いが50%で失敗する
- [ ] 信頼70以上で当日誘いが通りやすい

### バランス
- [ ] 30日クリア時の依存度が80〜90程度に収まる
- [ ] 信頼と依存の差が20以内程度に収まる
- [ ] 気遣い系の選択肢を選ぶと依存の上昇が抑えられる

---

*phase2_v2.3_fixes.md - 2026年2月21日作成*
