# ヒモ男シミュレーター Phase 4 ステップ1 修正指示書 v1.4

**前提**: Phase 4 ステップ1 v1.3.1が実装済みであること  
最終更新日: 2026年3月11日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | イベント①（美咲LINE）がターンを消費する | midgame_events.rpy / script.rpy |
| 2 | バグ | カナとの約束後にドタキャンされる | script.rpy |
| 3 | バグ | 美咲からのLINE後にお金要求できる | midgame_events.rpy / misaki_events.rpy |

---

## 修正1: イベント①がターンを消費する問題

### 原因

`check_midgame_events()` がイベント①で `return True` → `script.rpy` の `morning_actions` 内で `if midgame_fired: return` → 朝ターンが丸ごとスキップされる。

イベント①（美咲「最近忙しいの？」）はLINEメッセージであり、ターンを消費すべきではない。SNS受動通知と同じ「行動前に差し込まれる情報」として扱うべき。

### 修正方針

ターンを消費しないイベント（LINE系）と消費するイベント（カナ急な呼び出し等）を区別する。`check_midgame_events()` の戻り値を3種類にする。

### ファイル: `midgame_events.rpy`

```python
init python:
    def check_midgame_events():
        """
        main_loopの各ターン開始時に呼び出す
        戻り値:
          False  - イベントなし
          "notify" - イベント発生したがターン消費しない（LINE系）
          True   - イベント発生してターン消費する（強制行動系）
        """
        day = game_date["day"]
        time = game_date["time"]

        # --- 中盤前半（9〜15日） ---

        # イベント①: 美咲「最近忙しいの？」
        # → LINE系。ターン消費しない
        if (day >= 9 and day <= 15
            and not flags.get("midgame_busymisaki_done", False)
            and kana_flags["met"]
            and misaki["last_contact"] >= 3
            and time == "morning"):
            _pending_events.append(("midgame_misaki_busy", None))
            return "notify"    # ← 変更: True → "notify"

        # イベント④: カナからの急な呼び出し
        # → 強制行動系。ターン消費する
        if (day >= 10 and day <= 20
            and kana_flags["met"]
            and kana["dependence"] >= 20
            and time == "afternoon"
            and not kana["met_today"]):
            if renpy.random.random() < 0.20:
                _pending_events.append(("midgame_kana_urgent", None))
                return True    # ターン消費

        # --- 中盤後半（16〜23日） ---

        # イベント⑤: ダブルブッキング危機
        # → LINE系。選択はあるがターン自体は消費しない（夜のデート先が変わるだけ）
        if (day >= 16 and day <= 25
            and not flags.get("midgame_doublebooking_done", False)
            and kana_flags["met"]
            and misaki["stage"] >= STAGE_FRIEND
            and kana["trust"] >= 25
            and time == "afternoon"
            and not daily_flags["double_booking_checked"]):
            if renpy.random.random() < 0.30:
                _pending_events.append(("midgame_double_booking", None))
                return "notify"    # ← 変更: True → "notify"

        # イベント⑥⑦⑧ は夜の強制イベント → ターン消費のままでOK
        # （既存コードのまま return True）

        # イベント⑥: 目撃情報 → 修羅場
        if (flags.get("midgame_sighting_done", False)
            and not flags.get("midgame_sighting_confronted", False)
            and time == "night"):
            if renpy.random.random() < 0.40:
                _pending_events.append(("midgame_sighting_confrontation", None))
                return True

        # イベント⑦: カナの突撃訪問
        if (day >= 18
            and not flags.get("midgame_kana_raid_done", False)
            and kana_flags["met"]
            and kana["dependence"] >= 40
            and time == "night"
            and not kana["met_today"]):
            if renpy.random.random() < 0.20:
                _pending_events.append(("midgame_kana_raid", None))
                return True

        # イベント⑧: 美咲の直球質問 ver.2
        if (day >= 18
            and not flags.get("midgame_misaki_direct_done", False)
            and suspicion["misaki"] >= SUSPICION_SHURABA_THRESHOLD
            and misaki["trust"] >= 50
            and time == "night"):
            _pending_events.append(("midgame_misaki_direct", None))
            return True

        return False
```

### ファイル: `script.rpy`

`morning_actions` と `afternoon_actions` の判定を修正。

```python
label morning_actions:
    # Phase 4追加: SNS受動通知
    $ check_sns_notification()

    # Phase 4追加: 中盤イベントチェック
    python:
        midgame_fired = check_midgame_events()

    # v1.4修正: "notify"の場合はターンを消費しない（通常メニューに進む）
    # pending_eventsに入ったイベントは process_pending_events で処理される
    # Trueの場合のみターン消費
    if midgame_fired == True:
        return

    # "notify" の場合はここを通過して通常メニューへ
    # （pending_eventsのイベントは main_loop の process_pending_events で先に処理される）

    # v1.1追加: 強制朝イベントのチェック
    call check_forced_morning_event
    # ... 以下既存 ...
```

**注意**: `process_pending_events` が `morning_actions` の前（`main_loop` 内）で呼ばれるか、後で呼ばれるかの順序を確認する必要がある。現状の `script.rpy` を見ると、`process_pending_events` は `advance_time()` の後に呼ばれている（73-74行目）。つまり前のターンの `advance_day()` でキューに入ったイベントが処理される。

イベント①は `check_midgame_events()` 内で `_pending_events.append()` されるから、同ターン内の `process_pending_events` （68-69行目、アクション後）で処理される。ただし `morning_actions` がまだ実行されていない段階でキューに入るため、実行順序は:

1. `morning_actions` 呼び出し
2. その中で `check_midgame_events()` → `_pending_events` にイベント①追加
3. `midgame_fired == "notify"` なのでreturnしない
4. 通常メニュー表示
5. `morning_actions` return
6. `process_pending_events` でイベント①実行

この順序だと、通常メニューで行動選択した**後に**美咲のLINEが表示される。これは不自然。

**より良い方式**: `check_midgame_events()` 内で `_pending_events.append()` ではなく、直接 `renpy.call()` する方式にイベント①を変更する。あるいは `notify` 型イベントの場合は `morning_actions` の先頭で即実行する。

```python
label morning_actions:
    $ check_sns_notification()

    python:
        midgame_fired = check_midgame_events()

    if midgame_fired == True:
        return

    # v1.4: notify型イベントはここで先に処理（ターンは消費しない）
    call process_pending_events

    # 以下通常メニュー
    call check_forced_morning_event
    # ...
```

これなら美咲のLINE → 通常メニュー → 行動選択、の順序になる。

---

## 修正2: カナとの約束後のドタキャン

### 原因

`script.rpy` 257-273行目で、`kana_tonight` が `True` の場合に一律で成功率チェックが入る。プレイヤーが「会おう」と約束した場合もドタキャンされる。

### 修正方針

ドタキャンは「カナ主導の約束」の場合のみ発生。プレイヤーが主導した場合は確定で会える。

区別のために `kana_tonight` の代わりにフラグに発信元情報を持たせる。

### ファイル: `data/variables.rpy`

```python
# daily_flags に追加
# "kana_tonight_source": None,  # "player" or "kana" or None
```

### ファイル: 各所でフラグを立てる箇所

```python
# プレイヤーが主導で約束した場合（kana_events.rpy の雑談等）
$ flags["kana_tonight"] = True
$ daily_flags["kana_tonight_source"] = "player"

# カナ主導で約束した場合（kana_initiative_event等）
$ flags["kana_tonight"] = True
$ daily_flags["kana_tonight_source"] = "kana"
```

### ファイル: `script.rpy`

```python
    # 3. カナの約束のみある場合
    if flags.get("kana_tonight") and not flags.get("misaki_tonight"):
        "今夜はカナと約束がある。"
        $ flags["kana_tonight"] = False

        # v1.4修正: プレイヤー主導の約束は確定で会える
        python:
            source = daily_flags.get("kana_tonight_source", "kana")
            if source == "player":
                kana_shows_up = True
            else:
                # カナ主導の場合のみドタキャンリスクあり
                trust = kana["trust"]
                if trust >= 50:   success_rate = 0.95
                elif trust >= 35: success_rate = 0.85
                elif trust >= 20: success_rate = 0.75
                else:             success_rate = 0.60
                kana_shows_up = renpy.random.random() < success_rate

        $ daily_flags["kana_tonight_source"] = None

        if kana_shows_up:
            call kana_date_with_location
        else:
            kana_c "ごめん、やっぱり今日バイト入っちゃって"
            himo "そっか、しゃーない"
            $ change_trust_kana(-2)
        return
```

また、カナ主導の場合も成功率を全体的に引き上げた（旧: 50%〜90% → 新: 60%〜95%）。カナから誘ってきたのにドタキャン率が高すぎるのは不自然。

---

## 修正3: 美咲LINE後にお金要求できる問題

### 原因

イベント①（`midgame_misaki_busy`）で `misaki["last_contact"] = 0` にリセットされる。v1.3修正2で「対面していない場合はお金要求不可」の指示を出したが、`contact_misaki` からの `misaki_money_request` 呼び出し経路で `last_contact` チェックが入っていない可能性。

さらに根本的な問題として、「LINEで連絡した」と「対面で会った」の区別が `last_contact` の値だけでは不十分。

### 修正方針

`daily_flags` に「今日対面で会ったか」を明示的に記録し、お金要求はそれを条件にする。`met_today` は既に存在するが、これが一部の経路で正しく設定されていない可能性があるため、お金要求専用のガードを追加する。

### ファイル: `events/midgame_events.rpy`

イベント①で `last_contact` のリセットを慎重に行う。

```python
label midgame_misaki_busy:
    scene bg_placeholder

    "朝、スマホを見ると美咲からLINEが来ていた。"
    misaki_c "おはよう。最近連絡ないけど、忙しいの？"

    "...3日以上連絡してなかった。"

    menu:
        "すぐ返信する":
            himo "ごめん、ちょっとバタバタしてて"
            misaki_c "...そうなんだ。元気ならいいんだけど"
            "少し間があった。"
            misaki_c "最近、全然連絡くれないなって思って"
            $ change_trust(-5)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)
            # v1.4修正: last_contactは1にする（0だと「今日会った」と同等になる）
            # 0 = 今日会った、1 = 昨日連絡した、2以上 = しばらく連絡なし
            $ misaki["last_contact"] = 1

        "後で返そう（スルー）":
            "後で返せばいいか。"
            himo "まあいっか"
            $ change_trust(-10)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
            $ himo_aptitude["easy_choices"] += 1

    $ flags["midgame_busymisaki_done"] = True
    return
```

### ファイル: `events/misaki_events.rpy`

`misaki_money_request` に対面チェックを追加。

```python
label misaki_money_request:
    # 1日1回制限（成功した場合）
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    # v1.2: 断られた場合の制限
    if daily_flags.get("money_refused_today", False):
        himo "...さっき断られたし、今日は無理だな"
        return

    # v1.4追加: LINEだけでは対面していないので、お金の相談は不自然
    # last_contact == 0（今日会った）または met_today == True の場合のみ可能
    if not misaki["met_today"] and misaki["last_contact"] > 0:
        himo "（最近会ってないし、LINEでいきなりお金の話はしづらいな...）"
        himo "（まずは会って、それから相談しよう）"
        return

    # v1.2: 所持金バレリスク
    if player["money"] >= MONEY_SUSPICION_THRESHOLD:
        python:
            money_suspicious = renpy.random.random() < 0.60
        if money_suspicious:
            call midgame_money_suspicion
            return

    # 通常の処理...
    himo "実は...お金が厳しくて"
    # （以降既存コード）
```

---

## テスト確認項目

- [ ] イベント①（美咲LINE）発生後、朝の行動メニューが表示される（ターン消費しない）
- [ ] イベント④（カナ急な呼び出し）は従来通りターンを消費する
- [ ] プレイヤーが「会おう」と約束した後のカナデートでドタキャンされない
- [ ] カナ主導の約束では低確率でドタキャンが発生する
- [ ] 美咲からのLINE（イベント①）後に「美咲に連絡する」→お金要求ができない
- [ ] 美咲と対面デートした後は通常通りお金要求できる

---

## 将来対応メモ（今回は実装なし）

- 初日の美咲との会話に特別セリフ → テキスト追加タスクとして別途
- SNS通知へのヒモ太郎のコメントバリエーション → テキスト追加タスクとして別途

---

*phase4_step1_v1.4_fixes.md - 2026年3月11日作成*
