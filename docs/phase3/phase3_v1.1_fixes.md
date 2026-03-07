# ヒモ男シミュレーター Phase 3 修正指示書 v1.1

**前提**: Phase 3 v1.0が実装済みであること  
最終更新日: 2026年2月21日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | 削除 | カフェ・100円ショップを街の選択肢から削除 | daily_events.rpy |
| 2 | バグ | 昼の行動にカナへの連絡がない | script.rpy |
| 3 | バグ | カナパラメータがUIに未表示 | screens.rpy |
| 4 | 機能追加 | デバッグ表示画面 | screens.rpy / constants.rpy |
| 5 | UX | 空腹警告アイコンの追加 | screens.rpy |
| 6 | バランス | カナの当日誘い成功率を調整 | kana_events.rpy |
| 7 | 機能追加 | カナの自発的連絡システム | kana_events.rpy / time_system.rpy |
| 8 | 機能追加 | 朝の強制イベント3種 | daily_events.rpy |
| 9 | 機能追加 | 昼の強制イベント2種 | daily_events.rpy |

---

## 修正1: カフェ・100円ショップを削除

**ファイル**: `events/daily_events.rpy`

`afternoon_street` のメニューから該当選択肢を削除。

```python
# 削除する選択肢
# "カフェで休憩":
#     ...
# "100円ショップに行く":
#     ...

# 残す選択肢
menu:
    "【街】何をする？"

    "買い物をする":        # 現状維持。後でアイテム追加予定
        call shopping_event

    "ナンパしてみる" if not kana_flags["met"]:
        call nanpa_event

    "求人情報を見る":
        call check_job_hint

    "自宅に戻る":
        pass
```

---

## 修正2: 昼の行動にカナへの連絡を追加

**ファイル**: `script.rpy`

`afternoon_actions` のメニューに追加。

```python
"カナに連絡する" if kana_flags["met"]:
    call contact_kana
```

```python
# kana_events.rpy に追加
label contact_kana:
    $ kana["last_contact"] = 0

    "カナにLINEを送った..."

    if kana["trust"] >= 40:
        "すぐに返信が来た。"
    elif kana["trust"] >= 20:
        "しばらくして返信が来た。"
    else:
        "既読スルーされた..."
        $ change_trust_kana(-1)
        $ daily_flags["ignored_kana_today"] = True
        return

    menu:
        kana_c "なに？"

        "雑談する":
            kana_c "暇〜。ヒモ太郎も暇？"
            himo "暇だよ"
            kana_c "じゃあ会おう"
            $ flags["kana_tonight"] = True
            $ change_trust_kana(3)

        "今日会いたいと言う":
            call kana_date_request

    return
```

`daily_flags` に `ignored_kana_today` を追加し、`advance_day()` のリセット対象に含める。

```python
# variables.rpy の daily_flags に追加
"ignored_kana_today": False,

# time_system.rpy の advance_day() リセット処理に追加
daily_flags["ignored_kana_today"] = False
```

---

## 修正3: カナパラメータをUIに表示

**ファイル**: `screens.rpy`

`status_bar` にカナのパラメータを追加。

```python
screen status_bar():
    frame:
        xalign 0.5
        yalign 0.02
        padding (15, 8)

        vbox:
            spacing 4

            # 1行目: 基本情報
            hbox:
                spacing 25
                text "[game_date[day]]日目" size 24
                text get_time_string() size 24
                text "所持金: ¥[player[money]:,]" size 24 color "#FFD700"

                if player["stamina"] < 30:
                    text "[疲労]" size 20 color "#ff6b6b"
                if player["cleanliness"] < 30:
                    text "[不潔]" size 20 color "#4ecdc4"
                if not daily_flags["ate_today"] and game_date["time"] == "night":
                    text "[空腹]" size 20 color "#ffaa00"

            # 2行目: キャラクターパラメータ
            hbox:
                spacing 25
                text "美咲 信頼:[misaki[trust]] 依存:[misaki[dependence]]" size 20 color "#ffb7c5"

                if kana_flags["met"]:
                    text "カナ 信頼:[kana[trust]] 依存:[kana[dependence]]" size 20 color "#ffe066"
```

---

## 修正4: デバッグ表示画面

**ファイル**: `data/constants.rpy`

```python
define DEBUG_MODE = True   # リリース前に False に変更
```

**ファイル**: `screens.rpy`

```python
screen debug_overlay():
    if DEBUG_MODE:
        frame:
            xalign 1.0
            yalign 0.0
            padding (10, 10)
            background "#00000099"

            vbox:
                spacing 3
                text "=== DEBUG ===" size 15 color "#ff4444"
                text "体力: [player[stamina]]" size 13 color "#ffffff"
                text "清潔感: [player[cleanliness]]" size 13 color "#ffffff"
                text "魅力: [player[charm]]" size 13 color "#ffffff"
                text "食事済: [daily_flags[ate_today]]" size 13 color "#ffffff"
                text "美咲streak: [misaki[last_contact]]" size 13 color "#ffb7c5"

                if kana_flags["met"]:
                    text "カナstreak: [kana[last_contact]]" size 13 color "#ffe066"
                    text "SNSリスク: [kana_flags[sns_risk]]" size 13 color "#ffe066"

                if energy is not None:
                    text "エナジー: [energy]/[energy_max]" size 13 color "#aaffaa"
                    text "満タン日数: [energy_full_days]" size 13 color "#aaffaa"

# main_loop の show screen status_bar の後に追加
show screen debug_overlay
```

---

## 修正5: 空腹警告アイコン

修正3のstatus_bar内に実装済み（夜のみ表示）。

```python
# 夜になるまでは表示しない（朝から出ると不自然なため）
if not daily_flags["ate_today"] and game_date["time"] == "night":
    text "[空腹]" size 20 color "#ffaa00"
```

---

## 修正6: カナの当日誘い成功率を調整

**ファイル**: `events/kana_events.rpy`

`kana_date_request` の成功率テーブルを変更。

```python
python:
    import random
    trust = kana["trust"]
    # カナは美咲より会いやすい（暇な大学生）
    if trust >= 50:
        success_rate = 0.90
    elif trust >= 35:
        success_rate = 0.75   # 旧: 0.70
    elif trust >= 20:
        success_rate = 0.65   # 旧: 0.50（信頼20以上で大幅改善）
    elif trust >= 15:
        success_rate = 0.50   # 旧: 0.50
    else:
        success_rate = 0.30
```

---

## 修正7: カナの自発的連絡システム

**コンセプト**: 美咲の `check_misaki_initiative` と同様に、カナが自発的にLINEを送ってくる仕組み。ただしカナの方が軽いトーンで、より頻繁に来る。

**ファイル**: `systems/time_system.rpy`

`advance_day()` 内に追加。

```python
# advance_day() に追加（美咲のinitiativeチェックの後）
if kana_flags["met"]:
    check_kana_initiative()
```

**ファイル**: `events/kana_events.rpy`

```python
init python:
    def check_kana_initiative():
        import random
        global kana

        # last_contactが2以上かつ依存度が一定以上で発火
        if kana["last_contact"] < 2:
            return
        if kana["met_today"]:
            return

        # 依存度が高いほど頻繁に来る
        depend = kana["dependence"]
        if depend >= 60:
            fire_rate = 0.60
        elif depend >= 30:
            fire_rate = 0.40
        else:
            fire_rate = 0.25

        if random.random() < fire_rate:
            renpy.call("kana_initiative_event")


label kana_initiative_event:
    python:
        import random
        messages = [
            ("暇〜。ヒモ太郎も暇？", "casual"),
            ("今日会える？", "meetup"),
            ("なんかいいことあった？", "check"),
            ("ご飯行かない？", "food"),
        ]
        # 依存度が高いと「会いたい」系が増える
        if kana["dependence"] >= 50:
            messages += [
                ("会いたい", "needy"),
                ("今どこにいる？", "location"),
            ]
        msg, msg_type = random.choice(messages)

    "カナからLINEが来た。"
    kana_c "[msg]"

    menu:
        "返信する":
            if msg_type in ["meetup", "food", "needy"]:
                menu:
                    "今夜会おう":
                        $ flags["kana_tonight"] = True
                        $ kana["last_contact"] = 0
                        $ change_trust_kana(2)
                    "今日は無理":
                        himo "今日はちょっと"
                        kana_c "そっか〜"
                        $ change_trust_kana(-1)
                        $ kana["last_contact"] = 0
            else:
                himo "まあまあかな"
                kana_c "そっか〜"
                $ kana["last_contact"] = 0
                $ change_trust_kana(2)

        "既読スルーする":
            "既読スルーした。"
            $ change_trust_kana(-2)

    return
```

---

## 修正8: 朝の強制イベント3種

**コンセプト**: 通常の朝の行動選択を「スキップ」する特殊な朝。プレイヤーの計画が崩れる緊張感を演出。

**ファイル**: `events/daily_events.rpy`

`morning_actions` の先頭に強制イベントチェックを追加。

```python
label morning_actions:
    # v1.1追加: 強制朝イベントのチェック
    call check_forced_morning_event

    # 強制イベントが発生してターンが消費された場合は通常行動をスキップ
    if flags.get("morning_consumed", False):
        $ flags["morning_consumed"] = False
        return

    # 通常の朝メニュー（既存）
    ...
```

```python
label check_forced_morning_event:

    # イベント1: 日曜朝・美咲宅でイチャイチャして昼になる
    if flags.get("misaki_sunday_morning", False):
        $ flags["misaki_sunday_morning"] = False
        call misaki_sunday_morning_icha
        $ flags["morning_consumed"] = True
        return

    # イベント2: 疲労MAX → 昼まで寝てしまう
    if player["stamina"] <= 10:
        call event_oversleep
        $ flags["morning_consumed"] = True
        return

    # イベント3: 美咲 or カナから朝の電話（依存度が高い場合）
    python:
        import random
        phone_call_chance = False

        if misaki["dependence"] >= 70 and misaki["last_contact"] >= 2:
            if random.random() < 0.30:
                phone_call_chance = "misaki"

        if kana_flags["met"] and kana["dependence"] >= 50 and kana["last_contact"] >= 2:
            if random.random() < 0.25:
                phone_call_chance = "kana"

    if phone_call_chance == "misaki":
        call morning_phone_misaki
    elif phone_call_chance == "kana":
        call morning_phone_kana

    return


label misaki_sunday_morning_icha:
    scene bg_placeholder

    "日曜の朝。美咲の部屋。"
    "カーテン越しに柔らかい光が差し込んでいた。"

    misaki_c "...おはよう"
    himo "おう、おはよ"

    "美咲がくっついてきた。"
    misaki_c "今日、どこか行く？"
    himo "どうしよっか"

    "結局、昼まで部屋でゆっくりした。"

    $ change_stamina(20)
    $ change_trust(5)
    $ change_dependence(8)
    $ reset_contact()
    $ daily_flags["ate_today"] = True   # 美咲が朝食を出してくれた扱い

    "気づいたら昼になっていた。"
    "（朝の時間が消えた）"

    return


label event_oversleep:
    scene bg_placeholder

    "――朝――"
    "体が重い。"
    himo "（疲れすぎてる...）"
    himo "（ちょっとだけ...）"

    "気づいたら昼になっていた。"

    $ change_stamina(30)   # 寝たので回復
    $ himo_aptitude["easy_choices"] += 1

    himo "やばい、昼じゃん"

    return


label morning_phone_misaki:
    scene bg_placeholder

    "朝から美咲の電話が鳴った。"

    himo "もしもし"
    misaki_c "おはよう。昨日、連絡なかったから"
    himo "あ、ごめん寝てた"
    misaki_c "...そうなんだ"

    "少し沈黙。"

    menu:
        "フォローする":
            himo "夜に連絡するから"
            misaki_c "...うん、待ってる"
            $ change_trust(3)
            $ flags["misaki_tonight"] = True
            $ reset_contact()

        "適当にごまかす":
            himo "バタバタしててさ〜"
            misaki_c "...そっか"
            "美咲は何も言わなかった。"
            $ add_suspicion("vague_answer")
            $ reset_contact()

    return


label morning_phone_kana:
    scene bg_placeholder

    "朝から着信。カナだ。"

    himo "もしもし"
    kana_c "おはよ〜！昨日連絡なかったじゃん"
    himo "悪い悪い"
    kana_c "今日どうする？暇？"

    menu:
        "今日会おう":
            himo "夜なら"
            kana_c "やった！じゃあ夜ね"
            $ flags["kana_tonight"] = True
            $ kana["last_contact"] = 0
            $ change_trust_kana(3)

        "今日は無理":
            himo "今日はちょっと用事あって"
            kana_c "え〜、また？"
            $ change_trust_kana(-3)
            $ kana["last_contact"] = 0

    return
```

`variables.rpy` の `flags` に追加。

```python
"morning_consumed": False,
```

---

## 修正9: 昼の強制イベント2種

**コンセプト**: 街に出たとき、状況に応じて強制的にイベントが始まる。

**ファイル**: `events/daily_events.rpy`

`afternoon_street` の先頭に強制イベントチェックを追加。

```python
label afternoon_street:
    scene bg_placeholder

    # v1.1追加: 昼の強制イベントチェック
    call check_forced_afternoon_event

    if flags.get("afternoon_consumed", False):
        $ flags["afternoon_consumed"] = False
        return

    # 通常の街メニュー（既存）
    ...
```

```python
label check_forced_afternoon_event:
    python:
        import random

    # イベント1: ナンパ解禁トリガー（カナ未出会い・魅力35以上・5日目以降）
    if (not kana_flags["met"]
        and not flags.get("nanpa_unlocked", False)
        and player["charm"] >= 35
        and game_date["day"] >= 5):
        call event_nanpa_unlock
        return

    # イベント2: 町中でカナと偶然遭遇（カナ出会い済み・信頼30未満・ランダム）
    if (kana_flags["met"]
        and kana["trust"] < 50
        and not kana["met_today"]
        and random.random() < 0.15):
        call event_kana_encounter
        $ flags["afternoon_consumed"] = True
        return

    return


label event_nanpa_unlock:
    "街を歩いていると、前を歩く男が女の子に声をかけていた。"
    "...ナンパだ。"

    "女の子は笑顔で立ち止まった。"
    "連絡先を交換している。"

    himo "..."
    himo "（俺でも、できるかな）"

    $ flags["nanpa_unlocked"] = True

    "なんか、やってみたくなった。"
    "ナンパができるようになった。"

    # そのままナンパを試みるか選択
    menu:
        "試してみる":
            call nanpa_event

        "今日はやめとく":
            himo "まあ、今日はいいか"

    return


label event_kana_encounter:
    scene bg_placeholder

    "街を歩いていると、見覚えのある顔が目に入った。"
    "カナだ。"

    kana_c "あ、ヒモ太郎！なにしてんの？"
    himo "散歩"
    kana_c "暇人じゃん。一緒にいていい？"

    "断る理由もないので、そのままカナと合流した。"

    $ kana["met_today"] = True
    $ kana["last_contact"] = 0

    # カナの恩恵（食事）
    kana_c "お腹減った。なんか食べよ"
    "近くのカフェに入った。"
    "カナがおごってくれた。"

    $ change_stamina(15)
    $ change_trust_kana(8)
    $ change_dependence_kana(4)
    $ daily_flags["ate_today"] = True

    "思わぬ形でカナと過ごすことになった。"
    "（昼の時間が消費された）"

    return
```

`variables.rpy` の `flags` に追加。

```python
"nanpa_unlocked": False,
"afternoon_consumed": False,
```

**注意**: `nanpa_event` の表示条件を `not kana_flags["met"]` から `flags["nanpa_unlocked"]` に変更する。

```python
# 変更前
"ナンパしてみる" if not kana_flags["met"]:

# 変更後
"ナンパしてみる" if flags["nanpa_unlocked"] and not kana_flags["met"]:
```

---

## テスト確認項目

### 削除・UI
- [ ] カフェ・100円ショップの選択肢がなくなっている
- [ ] 美咲・カナのパラメータが両方UIに表示される
- [ ] デバッグ画面が右上に表示される
- [ ] 夜に食事していない場合に[空腹]アイコンが出る

### カナシステム
- [ ] 昼の行動からカナに連絡できる
- [ ] 信頼20以上で当日誘いが65%程度通る
- [ ] カナから自発的にLINEが来る（2〜3日連絡しないと）
- [ ] カナのLINEに返信すると夜の約束が入る

### 強制朝イベント
- [ ] 日曜朝・美咲宅泊まり後にイチャイチャシーンが発生し昼になる
- [ ] 体力10以下で昼まで寝てしまう
- [ ] 美咲の依存70以上・2日以上連絡なしで朝電話が来る
- [ ] カナの依存50以上・2日以上連絡なしで朝電話が来る

### 強制昼イベント
- [ ] 5日目以降・魅力35以上で街に出るとナンパ解禁シーンが発生する
- [ ] ナンパ解禁後は街のメニューに「ナンパしてみる」が出る
- [ ] カナ出会い済みで街に出ると15%の確率でカナと遭遇する
- [ ] カナ遭遇イベント後に昼ターンが消費される

---

*phase3_v1.1_fixes.md - 2026年2月21日作成*
