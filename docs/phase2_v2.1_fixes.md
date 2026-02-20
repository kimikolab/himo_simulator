# ヒモ男シミュレーター Phase 2 修正指示書 v2.1

**前提**: Phase 2 v2.0が実装済みであること  
最終更新日: 2026年2月19日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | 会った翌日に「昨日どこにいたの？」が発生 | misaki_events.rpy |
| 2 | バグ | 信頼が下がって再度70になると恋人テロップ再表示 | parameter_system.rpy |
| 3 | バグ | 土日に美咲がスーツで仕事に行く | misaki_events.rpy |
| 4 | バグ | 週末じゃないのに「昨日来なかったね」が発生 | time_system.rpy |
| 5 | バランス | 断られることがほぼなくなった・金が貯まりすぎる | parameter_system.rpy |
| 6 | バランス | 「私のこと好き？」の頻度が高い | misaki_events.rpy |
| 7 | 機能追加 | 土曜宿泊後の日曜朝シーン | time_system.rpy / misaki_events.rpy / variables.rpy |

---

## 修正1: 会った翌日に「昨日どこにいたの？」

**ファイル**: `events/misaki_events.rpy`

`misaki_dependence_milestone` の `DEPEND_MILD` 分岐の先頭に追加。

```python
label misaki_dependence_milestone(threshold):
    if threshold == DEPEND_MILD:
        # 追加: 当日または前日に会っている場合はスキップ
        if misaki["met_today"] or stats["times_met"] == 0:
            return
        "翌朝、美咲からLINEが来ていた。"
        "'昨日どこにいたの？ 連絡してよ'"
        himo "...あれ、急に？"
        "なんか、変わってきた気がする。"
    # 以降変更なし
```

---

## 修正2: 恋人テロップの再表示

**ファイル**: `systems/parameter_system.rpy`

`update_misaki_stage()` 内のSTAGE_DATING移行処理を修正。

```python
def update_misaki_stage():
    global misaki
    old_stage = misaki["stage"]

    trust  = misaki["trust"]
    depend = misaki["dependence"]

    if trust >= 70 and depend >= 50:
        misaki["stage"] = STAGE_DATING
    elif trust >= 50:
        misaki["stage"] = STAGE_CLOSE
    elif trust >= 35:
        misaki["stage"] = STAGE_FRIEND
    else:
        misaki["stage"] = STAGE_ACQUAINTANCE

    # STAGE_DATING移行処理（v2.1修正）
    if old_stage < STAGE_DATING and misaki["stage"] == STAGE_DATING:
        if not flags.get("confession_done", False):
            # 告白イベント未実施なら発火
            renpy.call("misaki_confession")
        elif flags.get("confession_accepted", False):
            # 告白を受け入れていた場合のみテロップ表示
            renpy.notify("美咲との関係: 恋人")
        # confession_done済みで受け入れていない場合はテロップなし

    # それ以外のステージ上昇通知（変更なし）
    elif misaki["stage"] > old_stage:
        stage_names = {2: "友達", 3: "いい雰囲気"}
        if misaki["stage"] in stage_names:
            renpy.notify("美咲との関係が「" + stage_names[misaki["stage"]] + "」になった")
```

---

## 修正3: 土日に美咲がスーツで仕事

**ファイル**: `events/misaki_events.rpy`

`misaki_date` および `misaki_room_visit` 内の美咲の外見描写を曜日分岐に変更。

```python
# misaki_date 内（「スーツ姿の美咲」という描写を以下に差し替え）
if is_weekend():
    "私服の美咲。普段より表情が柔らかい。"
else:
    "スーツ姿の美咲。少し疲れた顔をしている。"

# misaki_room_visit 内も同様に差し替え
if is_weekend():
    "部屋着の美咲。リラックスした雰囲気。"
else:
    "スーツを脱いだばかりの美咲。少し疲れた様子。"
```

---

## 修正4: 週末でないのに「昨日来なかったね」が発生

**ファイル**: `systems/time_system.rpy`

`advance_day()` 内の約束チェック処理を以下に差し替え。

```python
# 変更前（削除）
if weekend_promised and is_weekend() and not misaki["met_today"]:
    renpy.call("misaki_broken_promise")

# 変更後（差し替え）
# 月曜になったタイミングで週末の約束を判定する
if game_date["weekday"] == 1:   # 月曜
    if weekend_promised:
        if not flags.get("met_misaki_this_weekend", False):
            renpy.call("misaki_broken_promise")
        flags["met_misaki_this_weekend"] = False
        weekend_promised = False
```

`misaki_date` および `misaki_room_visit` の末尾に以下を追加。

```python
# 週末に会った記録
if is_weekend():
    $ flags["met_misaki_this_weekend"] = True
```

`variables.rpy` の `flags` 辞書に追加。

```python
"met_misaki_this_weekend": False,
```

---

## 修正5: ムード補正の再調整

**ファイル**: `systems/parameter_system.rpy`

セーフティ（3連続失敗で次は必ず成功）は維持しつつ、成功率を少し下げる。

```python
# 変更前
mood_modifier = {
    "good":     1.2,
    "normal":   1.0,
    "tired":    0.8,
    "stressed": 0.5,
}

# 変更後
mood_modifier = {
    "good":     1.2,
    "normal":   1.0,
    "tired":    0.75,
    "stressed": 0.4,
}
```

セーフティのコード自体は変更なし。

---

## 修正6: 「私のこと好き？」の頻度を下げる

**ファイル**: `events/misaki_events.rpy`

`misaki_date` 末尾の連続デートリスク処理のしきい値を変更。

```python
# 変更前
if misaki_streak >= 5:
    # 「好き？」
if misaki_streak >= 3:
    # 「毎日会ってるね」

# 変更後
if misaki_streak >= 7:
    misaki_c "ねえ、ヒモ太郎って私のこと好き？"
    himo "...え"
    "なんか、重くなってきた気がする。"
    $ change_dependence(12)
elif misaki_streak >= 4:
    "美咲: 「最近毎日会ってるね...」"
    $ change_dependence(8)
```

---

## 修正7: 土曜宿泊後の日曜朝シーン（新規追加）

### variables.rpy

`flags` 辞書に追加。

```python
"misaki_sunday_morning": False,
```

### time_system.rpy

`advance_day()` の先頭（既存処理の前）に追加。

```python
def advance_day():
    global game_date, misaki, flags, daily_flags
    global location_flags, misaki_events, misaki_streak

    # 日曜朝シーン処理（v2.1追加）
    # 土曜宿泊フラグが立っていれば日曜の朝に実行
    if flags.get("misaki_sunday_morning", False):
        location_flags["staying_at_misaki"] = True
        flags["misaki_sunday_morning"] = False
        renpy.call("misaki_sunday_morning_scene")

    # 以降既存コード（game_date["day"] += 1 など）
```

`misaki_room_visit` の泊まる選択肢の末尾に追加。

```python
# 土曜宿泊の場合、翌日曜のフラグを立てる
if is_weekend() and game_date["weekday"] == 6:   # 土曜
    $ flags["misaki_sunday_morning"] = True
```

### misaki_events.rpy

新規ラベルを追加。

```python
label misaki_sunday_morning_scene:
    scene bg_placeholder
    "目が覚めると、美咲の部屋だった。"
    "カーテンの隙間から日差しが入ってくる。"
    "休日の朝。"

    misaki_c "おはよう。コーヒー飲む？"
    himo "...いただきます"

    "キッチンで美咲がコーヒーを淹れている音が聞こえる。"
    "こういう朝も、悪くないな。"

    misaki_c "昨日泊まってくれて、よかった"
    himo "俺も"

    "少し照れくさいけど、本当のことだった。"

    $ change_stamina(20)
    $ change_trust(3)
    $ change_dependence(5)
    $ daily_flags["ate_today"] = True   # 朝食扱い

    return
```

---

## テスト確認項目

- [ ] 美咲に会った日にマイルストーンLINEが来ない
- [ ] 信頼が下がって再上昇しても恋人テロップが再表示されない
- [ ] 土日に美咲が私服で登場する
- [ ] 週末でない日に「昨日来なかったね」が発生しない
- [ ] ムード補正でたまに断られるがセーフティで連続拒否にならない
- [ ] 「私のこと好き？」が7日連続以降に発生する
- [ ] 土曜宿泊後の日曜朝シーンが発生する
- [ ] 日曜朝に美咲の部屋にいる状態で開始する

---

*phase2_v2.1_fixes.md - 2026年2月19日作成*
