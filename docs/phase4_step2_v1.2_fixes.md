# ヒモ男シミュレーター Phase 4 ステップ2 修正指示書 v1.2

**前提**: Phase 4 ステップ2 v1.1が実装済みであること  
最終更新日: 2026年3月27日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | 設計追加 | 疑念緩和手段＋美咲の態度変化による間接的疑念UI | misaki_events.rpy / parameter_system.rpy |
| 2 | バランス | 疑念ペナルティ係数を3→2に緩和 | misaki_events.rpy |
| 3 | バグ | セリフログの2重出力 | debug_log.rpy |
| 4 | セリフ | 美咲の返信バリエーション追加 | misaki_events.rpy |
| 5 | セリフ | 居酒屋デートのセリフバリエーション | date_misaki_places.rpy |
| 6 | セリフ | ナンパ失敗のセリフバリエーション | kana_events.rpy / daily_events.rpy |
| 7 | バグ | SNS投稿の重複表示防止 | daily_events.rpy |

---

## 修正1: 疑念緩和手段＋美咲の態度変化

### 1-1. 美咲の態度変化（間接的疑念UI）

疑念度に応じて美咲のLINE返信テキストとヒモ太郎の独白が変化する。プレイヤーは数値を見なくても「まずい」と察知できる。

**ファイル**: `events/misaki_events.rpy`

`contact_misaki` ラベルの返信テキスト部分を差し替える。

```python
label contact_misaki:
    $ reset_contact()

    "美咲にLINEを送った..."

    # === 既読判定（既存・変更なし）===
    if misaki["trust"] >= 60:
        "すぐに返信が来た。"
    elif misaki["trust"] >= 40:
        "しばらくして返信が来た。"
    else:
        "既読スルーされた..."
        $ change_trust(-2)
        $ daily_flags["ignored_today"] = True
        return

    # === 疑念度による美咲の返信テキスト（新規）===
    python:
        _susp = suspicion.get("misaki", 0)

    if _susp >= 16:
        # 警戒レベル
        python:
            _reply = renpy.random.choice([
                "...なに",
                "また何かお願い？",
                "...用事？",
            ])
        misaki_c "[_reply]"
        himo "（やばい、美咲の態度がおかしい。何か変えないと）"

    elif _susp >= 11:
        # 明確な冷たさ
        python:
            _reply = renpy.random.choice([
                "...どうしたの",
                "何か用？",
                "ん...なに？",
            ])
        misaki_c "[_reply]"
        himo "（美咲、最近冷たくない？）"

    elif _susp >= 6:
        # 微妙な変化
        python:
            _reply = renpy.random.choice([
                "...どうしたの？",
                "ん、なに？",
                "どうしたの",
            ])
        misaki_c "[_reply]"
        if renpy.random.random() < 0.4:
            himo "（なんか、反応がいつもと違う気がする）"

    else:
        # 通常（疑念低い）
        python:
            _reply = renpy.random.choice([
                "どうしたの？",
                "わ、ヒモ太郎！",
                "おっ、久しぶり！",
                "お、なになに？",
            ])
        misaki_c "[_reply]"

    # === 以下、既存の選択肢メニューへ ===
    menu:
        # ...（既存の選択肢。変更なし）
```

**補足**: 既存の `contact_misaki` では `misaki_c "どうしたの？"` がハードコードされている。この部分を上記のブロックに置き換える。選択肢メニュー（雑談する / 会いたいと言う / お金の相談をする）は変更なし。

### 1-2. 疑念緩和手段の追加

美咲を気遣う行動で疑念が下がる。以下の箇所に疑念減少を追加する。

**ファイル**: `events/misaki_events.rpy`

#### (a) デート中の気遣い選択肢

既存のデート会話で「仕事の愚痴を聞く」「美咲を励ます」等の選択肢に疑念減少を追加。

```python
# misaki_date 内（既存の選択肢の処理に追加）

"仕事の愚痴を聞く":
    # ...既存のセリフ・パラメータ変化...
    $ change_trust(5)
    $ change_dependence(5)
    $ himo_aptitude["showed_concern"] += 1
    # ステップ2追加: 疑念緩和
    $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 1)

"美咲を励ます":
    # ...既存のセリフ・パラメータ変化...
    $ change_trust(8)
    $ change_dependence(7)
    $ himo_aptitude["showed_concern"] += 2
    # ステップ2追加: 疑念緩和
    $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 2)

"自分の話（正直に）":
    # ...既存のセリフ・パラメータ変化...
    $ change_trust(10)
    $ change_dependence(8)
    $ himo_aptitude["honest_moments"] += 1
    # ステップ2追加: 疑念緩和（正直さは最も効果的）
    $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 3)
```

#### (b) LINE連絡の気遣い選択肢

信頼度別のLINE選択肢のうち、気遣い系に疑念減少を追加。

```python
# 既存のLINE選択肢処理に追加

"仕事の愚痴聞くよ":
    # ...既存処理...
    $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 1)

"何か手伝えることある？":
    # ...既存処理...
    $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 1)

"声聞きたくて":
    # ...既存処理...
    $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 1)

"甘えていい？":
    # ...既存処理...
    $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 2)
```

#### (c) 対面交渉をキャンセルした場合

お金の話を切り出そうとしてやめた場合、疑念は増えないが好感度微増。

```python
# misaki_negotiation_start 内の「やっぱりやめる」選択

"...（やっぱりやめる）":
    himo "（...やっぱり言えなかった）"
    $ money_request_weekly["count"] -= 1
    $ daily_flags["asked_money_today"] = False
    $ himo_aptitude["money_requests"] -= 1
    # ステップ2追加: 踏みとどまった分の微緩和
    $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 1)
    return
```

#### (d) 「このまま楽しむ」を選んだ場合

デート中にお金の話をせず楽しんだ場合、疑念が微減する。

```python
# date_misaki_places.rpy の各デート場所ラベル末尾の交渉メニュー

menu:
    "会話が落ち着いてきた。"

    "お金の話を切り出す":
        call misaki_negotiation_start

    "このまま楽しむ":
        # ステップ2追加: お金の話をしなかった→好印象
        if suspicion.get("misaki", 0) >= 6:
            himo "（今日はお金の話はやめとこう）"
        $ suspicion["misaki"] = max(0, suspicion.get("misaki", 0) - 1)
```

### 1-3. 疑念変化のデバッグログ

疑念が増減したタイミングでログに記録する。

**ファイル**: `systems/parameter_system.rpy`

`add_suspicion` 関数にログ出力を追加。

```python
init python:
    def add_suspicion(reason, target="misaki"):
        # ...既存処理...
        log_action("疑念UP " + target + " reason=" + reason + " now=" + str(suspicion.get(target, 0)))
```

疑念減少の箇所にもログを追加（各所に手動で入れるのが面倒な場合、ヘルパー関数を作る）。

```python
init python:
    def reduce_suspicion(target, amount, reason=""):
        suspicion[target] = max(0, suspicion.get(target, 0) - amount)
        log_action("疑念DOWN " + target + " -" + str(amount) + " now=" + str(suspicion.get(target, 0)) + " " + reason)
```

上記の修正1-2で直接 `suspicion["misaki"] = max(0, ...)` と書いた箇所を、このヘルパー関数に置き換える。

```python
# 使用例
$ reduce_suspicion("misaki", 2, "励まし")
$ reduce_suspicion("misaki", 3, "正直に話した")
$ reduce_suspicion("misaki", 1, "交渉キャンセル")
```

---

## 修正2: 疑念ペナルティ係数の緩和

### 問題

疑念度17で `susp_pen = 51`（17 × 3）。成功率を50%以上削っており、後半の交渉がほぼ不可能になっている。

### 修正

**ファイル**: `events/misaki_events.rpy`

`misaki_negotiation_reaction` 内の疑念ペナルティ計算を変更。

```python
    # 修正前
    # suspicion_penalty = suspicion.get("misaki", 0) * 3

    # 修正後: 係数を2に緩和＋上限30%キャップ
    suspicion_penalty = min(30, suspicion.get("misaki", 0) * 2)
```

これにより疑念17でも `susp_pen = 30`（上限）。いい店（+20）や高信頼の切り出し方（base_rate 65〜75）で十分カバーできる範囲になる。

---

## 修正3: セリフログの2重出力

### 原因の調査方針

Ren'Pyの `say` コールバックが2回登録されている、または `config.say_menu_text_filter` が影響している可能性。

### ファイル: `systems/debug_log.rpy`（またはセリフログの実装箇所）

以下を確認・修正する。

#### (a) コールバックの重複登録チェック

```python
init python:
    def dialogue_log_callback(event, interact=True, **kwargs):
        # ...ログ出力処理...
        pass

    # 重複防止: 既に登録されていたら追加しない
    if dialogue_log_callback not in config.all_character_callbacks:
        config.all_character_callbacks.append(dialogue_log_callback)
```

#### (b) `init` の優先順位問題

`init python` が複数箇所で呼ばれて二重登録されている可能性。`init python` ブロックが1箇所だけであることを確認する。

#### (c) prediction による二重呼び出し

Ren'Pyは次の画面をpredictionのために先読みすることがある。`interact` パラメータで判別可能。

```python
init python:
    def dialogue_log_callback(event, interact=True, **kwargs):
        if not interact:
            return  # prediction時はログに記録しない
        # ...通常のログ出力処理...
```

上記3つのうちどれが原因かは実装を見ないと確定できないが、**(c) のinteractチェック**が最も可能性が高い。Ren'Pyのsayコールバックは`interact=False`でprediction呼び出しされるため、これをフィルタすれば解決する見込み。

---

## 修正4: 美咲の返信バリエーション

修正1で疑念度ベースの返信を実装するため、ここでは**デート中の美咲のセリフバリエーション**を追加する。

### ファイル: `events/misaki_events.rpy`

#### (a) デート誘い成功時の返信

```python
label misaki_date_request:
    if daily_flags.get("ignored_today", False):
        "さっき既読スルーされたばかりだし..."
        himo "今日はやめとこう"
        return

    if misaki["met_today"]:
        # バリエーション追加
        python:
            _met_reply = renpy.random.choice([
                "今日もう会ったよ？笑",
                "え、さっき会ったばっかりじゃん",
                "また？ 嬉しいけど笑",
            ])
        misaki_c "[_met_reply]"
        himo "あ、そっか"
        return

    if game_date["time"] == "night":
        # バリエーション追加
        python:
            _ok_reply = renpy.random.choice([
                "今から？いいよ",
                "うん、行こ！",
                "待ってた！...って言ったら重い？笑",
            ])
        misaki_c "[_ok_reply]"
        call misaki_date
        return
    else:
        python:
            _later_reply = renpy.random.choice([
                "夜なら空いてるよ",
                "夜でもいい？",
                "仕事終わってからでいい？",
            ])
        misaki_c "[_later_reply]"
        himo "了解〜"
        return
```

---

## 修正5: 居酒屋デートのセリフバリエーション

### ファイル: `events/date_misaki_places.rpy`

```python
label misaki_date_izakaya:
    "居酒屋に入った。"

    # 回数に応じてセリフを変える
    python:
        _izakaya_count = stats.get("date_locations", {}).get("izakaya", 0)

    if _izakaya_count <= 1:
        misaki_c "たまにはこういうのもいいね"
    elif _izakaya_count <= 3:
        python:
            _iz_line = renpy.random.choice([
                "また居酒屋？笑 好きだね〜",
                "ここ、落ち着くよね",
                "今日は何飲む？",
            ])
        misaki_c "[_iz_line]"
    elif _izakaya_count <= 6:
        python:
            _iz_line = renpy.random.choice([
                "いつもの席、空いてるかな",
                "もう常連だね、ここ",
                "店員さんに覚えられてそう",
            ])
        misaki_c "[_iz_line]"
    else:
        python:
            _iz_line = renpy.random.choice([
                "...またここ？たまには別の店行かない？",
                "いつもの、でいい？もう分かるでしょ",
                "ヒモ太郎って居酒屋好きすぎない？笑",
            ])
        misaki_c "[_iz_line]"

    "お酒が入って、美咲の口数が増える。"
    "美咲が奢ってくれた。"

    $ change_trust(5)
    $ change_dependence(5)
    $ change_stamina(-15)
    $ change_stamina(20)
    $ daily_flags["ate_today"] = True

    return
```

同様にファミレス・いい店・美咲の部屋にも回数ベースのバリエーションを追加する。ただし居酒屋が最も使用頻度が高い（今回8回）ので優先度最高。残りは次回でもよい。

---

## 修正6: ナンパ失敗のセリフバリエーション

### ファイル: ナンパ処理の該当箇所（`daily_events.rpy` または `kana_events.rpy`）

```python
# ナンパ失敗時のテキストをランダム化
python:
    _nanpa_fail_lines = [
        ("声をかけてみたが、うまくいかなかった。", "...まあ、そんなもんか"),
        ("笑顔で話しかけたが、無視された。", "...つれないな"),
        ("いい感じに話せたけど、連絡先は教えてもらえなかった。", "惜しかったな...多分"),
        ("声をかける前に相手が去っていった。", "タイミングって大事だな"),
        ("話しかけたら彼氏がいると言われた。", "そりゃそうだよな"),
    ]
    _fail_text, _fail_himo = renpy.random.choice(_nanpa_fail_lines)

"[_fail_text]"
himo "[_fail_himo]"
```

---

## 修正7: SNS投稿の重複表示防止

### 問題

4日目と5日目で由美の「マイホーム購入」が連続で出ている。ランダム抽選に重複防止がない。

### ファイル: `events/daily_events.rpy`

`check_sns` ラベルの投稿選択ロジックを修正。

```python
label check_sns:
    "SNSのタイムラインを見た。"

    python:
        sns_posts = [
            ("同級生・健太", "『本日付で主任に昇進しました！』", "positive"),
            ("同級生・由美", "『マイホーム購入 35年ローン頑張ります...』", "neutral"),
            ("同級生・大輔", "『転職成功！試用期間中で緊張する』", "neutral"),
            ("バイト仲間・拓也", "『バイトだるい〜 でも気楽でいいか』", "relatable"),
            ("知り合い・翔太", "『起業して半年、やっと黒字化』", "positive"),
            ("同級生・あかり", "『第一子誕生！育休中です』", "neutral"),
            ("先輩・大和", "『海外赴任決まりました』", "positive"),
            ("バイト仲間・ケンタ", "『やっと正社員なれた〜泣』", "neutral"),
        ]

        # 前回表示した投稿を除外
        last_sns = flags.get("last_sns_poster", "")
        available = [p for p in sns_posts if p[0] != last_sns]
        if not available:
            available = sns_posts  # 全除外された場合はリセット

        post = renpy.random.choice(available)
        poster, content, tone = post
        flags["last_sns_poster"] = poster

    "[poster]の投稿:"
    "[content]"

    # ...既存のtoneによる反応...
```

### 追加: SNS投稿プールの拡充

現状4〜5件では30日間で必ず繰り返しが目立つ。上記のように8件に増やす。さらに将来的には日付帯に応じた投稿（月初は給料系、月末は「金欠」系）を入れてもよいが、今回はランダムプールの拡充で十分。

---

## テスト確認項目

### 修正1: 疑念の間接表示＋緩和手段
- [ ] 疑念0〜5で美咲が通常トーンで返信する（「どうしたの？」「わ、ヒモ太郎！」等）
- [ ] 疑念6〜10で返信が微妙に冷たくなる（「...どうしたの？」「ん、なに？」）
- [ ] 疑念6〜10でヒモ太郎の独白が40%の確率で出る
- [ ] 疑念11〜15で明確に冷たくなり、ヒモ太郎が毎回「冷たくない？」と思う
- [ ] 疑念16以上で「また何かお願い？」等の警戒反応＋ヒモ太郎の焦り独白
- [ ] 「仕事の愚痴を聞く」で疑念-1される
- [ ] 「美咲を励ます」で疑念-2される
- [ ] 「自分の話（正直に）」で疑念-3される
- [ ] 「このまま楽しむ」で疑念-1される
- [ ] 疑念が0以下にならない
- [ ] デバッグログに「疑念UP」「疑念DOWN」が記録される

### 修正2: 疑念ペナルティ緩和
- [ ] 疑念17で対面交渉の疑念ペナルティが30（上限）になっている
- [ ] いい店（+20）＋高信頼の切り出し（base_rate 65〜75）で成功率が30%以上残る

### 修正3: セリフログ2重出力
- [ ] セリフログの各行が1回だけ出力される

### 修正4-6: セリフバリエーション
- [ ] 美咲への連絡で「どうしたの？」以外の返信が出る
- [ ] 居酒屋2回目以降で「たまにはこういうのもいいね」以外のセリフが出る
- [ ] 居酒屋7回以上で「またここ？」系のセリフが出る
- [ ] ナンパ失敗で毎回違うテキストが出る

### 修正7: SNS投稿
- [ ] 同じ人の投稿が2日連続で出ない
- [ ] 投稿プールが8件以上ある

---

*phase4_step2_v1.2_fixes.md - 2026年3月27日作成*
