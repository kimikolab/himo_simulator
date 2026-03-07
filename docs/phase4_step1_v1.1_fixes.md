# ヒモ男シミュレーター Phase 4 ステップ1 修正指示書 v1.1

**前提**: Phase 4 ステップ1が実装済みであること  
最終更新日: 2026年3月7日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | 初日デートで「昨日の夜何してた？」が発生する | date_incidents.rpy |
| 2 | バグ | デートで食事しても食事判定(ate_today)が入らない | date_misaki_places.rpy |
| 3 | バランス | カナの既読スルー率が高すぎて序盤に接触困難 | kana_events.rpy |
| 4 | テキスト | カナ友達のセリフが逆（ヒモ太郎→カナ） | date_kana_places.rpy |
| 5 | 改善 | デバッグログにイベント・フラグ情報を追加 | debug_system（該当箇所） |

---

## 修正1: 初日デートの探り発生ガード

**問題**: 1日目の美咲デートで居酒屋を選んだ際、「昨日の夜何してたの？LINE返ってこなかったけど」が発生する。ゲーム開始直後に「昨日」の行動を聞かれるのは矛盾。

**ファイル**: `events/date_incidents.rpy`

`should_trigger_probe` に日数ガードを追加。さらに「昨日の夜」系の探りは前日にもう片方とデートした実績がある場合のみ発生するよう制限。

```python
init python:
    def should_trigger_probe(target):
        """探りが発生するか判定"""
        import random

        # Phase 4 v1.1: 序盤（7日目以前）は探り発生しない
        if game_date["day"] <= 7:
            return False

        sus = suspicion.get(target, 0)
        location = daily_flags.get("date_location", None)

        base_rate = 0.10
        if sus >= 1:
            base_rate += 0.15
        if sus >= 3:
            base_rate += 0.15
        if location == "izakaya":
            base_rate += 0.15

        return random.random() < base_rate
```

さらに、`date_probe` ラベル内の `last_night` 探りに追加ガード。

```python
    if probe_key == "last_night":
        # Phase 4 v1.1: 前日にもう片方とデートした実績がなければこの探りは発生しない
        # → 代わりに "lately" 探りにフォールバック
        python:
            # 実際には前日のデート相手を追跡する仕組みが必要だが
            # 簡易実装として、もう片方のキャラのlast_contactで判定
            if target == "misaki":
                other_recent = kana.get("last_contact", 99) <= 1 if kana_flags["met"] else False
            else:
                other_recent = misaki.get("last_contact", 99) <= 1

        if not other_recent:
            # last_night探りの代わりに軽い探りに差し替え
            if target == "misaki":
                misaki_c "最近、楽しそうだね"
            else:
                kana_c "最近なんか楽しそうじゃん"
            himo "そう？"
            $ suspicion[target] = min(suspicion[target] + 1, SUSPICION_MAX)
            return

        # 以下、既存の last_night 処理
        if daily_flags.get("date_with", None) is not None:
            call run_lie_puzzle("last_night", target)
        else:
            himo "家でゴロゴロしてた"
            # ...
```

---

## 修正2: デートで食事判定を入れる

**問題**: ファミレス・居酒屋・レストラン等で食事しているはずなのに `ate_today` が `False` のまま。夜に空腹アイコンが出る矛盾。体力不足で身動きが取れなくなる。

**ファイル**: `events/date_misaki_places.rpy`

各デート場所ラベルの処理に `ate_today = True` と体力回復を追加。

```python
label misaki_date_famires:
    "ファミレスに入った。"
    misaki_c "ここ落ち着くよね"
    himo "安いしな"

    "美咲が奢ってくれた。"

    $ change_trust(3)
    $ change_dependence(2)
    $ change_stamina(-10)
    $ change_stamina(20)   # 食事による体力回復（差し引き+10）
    $ daily_flags["ate_today"] = True

    return


label misaki_date_izakaya:
    "居酒屋に入った。"
    misaki_c "たまにはこういうのもいいね"

    "お酒が入って、美咲の口数が増える。"
    "美咲が奢ってくれた。"

    $ change_trust(5)
    $ change_dependence(5)
    $ change_stamina(-15)
    $ change_stamina(20)   # 食事による体力回復（差し引き+5）
    $ daily_flags["ate_today"] = True

    return


label misaki_date_room:
    "美咲の部屋に行った。"
    misaki_c "散らかっててごめんね"
    himo "いいっていいって"

    "2人きりの空間。"
    "美咲が何か作ってくれた。"

    $ change_trust(5)
    $ change_dependence(8)
    $ change_stamina(-10)
    $ change_stamina(15)   # 軽い食事
    $ change_cleanliness(15)
    $ daily_flags["ate_today"] = True

    python:
        weekday_index = (game_date["day"] - 1) % 7
        if weekday_index == 5:
            flags["misaki_sunday_morning"] = True

    return


label misaki_date_fancy:
    "少しいい店に入った。"
    "自分から奢りを申し出た。"
    misaki_c "え、いいの？"
    himo "たまにはな"

    misaki_c "...ありがとう"
    "美咲が嬉しそうに笑った。"

    $ change_money(-3000)
    $ change_trust(10)
    $ change_dependence(3)
    $ change_stamina(-10)
    $ change_stamina(25)   # いい店なので満足度高い（差し引き+15）
    $ daily_flags["ate_today"] = True

    return
```

**ファイル**: `events/date_kana_places.rpy`

カナのデートは既に `ate_today = True` が共通処理にあるが、場所別の体力回復が不足。

```python
label kana_date_cafe:
    "カフェに入った。"
    kana_c "ここインスタ映えする〜"

    "カナがスマホを取り出して写真を撮り始めた。"
    "カナが奢ってくれた。"

    $ change_trust_kana(5)
    $ change_dependence_kana(3)
    $ change_stamina(-10)
    $ change_stamina(15)   # カフェの軽食（差し引き+5）
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 2

    return


label kana_date_karaoke:
    "カラオケに行った。"
    kana_c "何歌う？"
    himo "適当に"

    "盛り上がった。カナの歌が意外と上手い。"
    "途中で軽く食べた。"

    $ change_money(-500)
    $ change_trust_kana(8)
    $ change_dependence_kana(5)
    $ change_stamina(-15)
    $ change_stamina(10)   # 軽食（差し引き-5。はしゃいだので消耗の方が大きい）

    return


label kana_date_campus:
    "カナの大学の近くで会った。"
    kana_c "この辺よく来るんだ〜"

    "カナの友達とすれ違った。"
    kana_c "あ、まりちゃん！紹介するね、ヒモ太郎！"

    "...紹介された。"
    "近くの店でご飯を食べた。カナが奢ってくれた。"

    $ change_trust_kana(8)
    $ change_dependence_kana(4)
    $ change_stamina(-10)
    $ change_stamina(20)   # 食事（差し引き+10）
    $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 1

    if not flags.get("kana_friend_info_obtained", False):
        "友達と少し話す機会があった。"
        "友達「カナってさ、前の彼氏に浮気されてから男性不信なんだよね」"
        "友達「だからカナのこと大事にしてあげてね」"
        himo "（...なるほど）"
        $ flags["kana_friend_info_obtained"] = True
        "カナの過去を知った。今後の会話で地雷を避けやすくなるかもしれない。"

    return


label kana_date_himo_room:
    "ヒモ太郎の部屋で会うことにした。"

    if player["cleanliness"] >= 50:
        kana_c "意外と綺麗にしてるじゃん"
        $ change_trust_kana(5)
    elif player["cleanliness"] >= 30:
        kana_c "...まあ、男の人の部屋ってこんなもんか"
        $ change_trust_kana(3)
    else:
        kana_c "...汚い"
        $ change_trust_kana(-3)

    $ change_dependence_kana(6)
    $ change_stamina(-5)

    $ himo_aptitude["intimacy_exp"] = himo_aptitude.get("intimacy_exp", 0) + 1

    # 部屋デートは食事なし → ate_today は変更しない
    # 共通処理の ate_today = True を上書きする必要あり

    return
```

**重要**: `kana_date_with_location` の共通処理で `ate_today = True` を一律設定している箇所を修正。場所によって食事判定が変わるようにする。

```python
label kana_date_with_location:
    # （場所選択・デート処理）

    # デート後の共通処理
    $ kana["met_today"] = True
    $ kana["last_contact"] = 0
    $ daily_flags["date_with"] = "kana"

    # Phase 4 v1.1: ate_today は場所別に設定（部屋以外は食事あり）
    if daily_flags["date_location"] != "himo_room":
        $ daily_flags["ate_today"] = True

    call check_date_incidents("kana")

    return
```

---

## 修正3: カナの既読スルー率を緩和

**問題**: カナの信頼が低い序盤で既読スルーされやすく、ターンが無駄になる。カナと接触する手段が「向こうからの連絡を待つ」しかなくなる。

**ファイル**: `events/kana_events.rpy`

`contact_kana` の既読スルー閾値を緩和。さらに既読スルー時も完全な無駄にせず、次回の返信率を上げる仕組み（好感度微増）を追加。

```python
label contact_kana:
    $ kana["last_contact"] = 0

    "カナにLINEを送った..."

    # Phase 4 v1.1: 閾値を緩和（旧: 40/20 → 新: 25/10）
    if kana["trust"] >= 25:
        "すぐに返信が来た。"
    elif kana["trust"] >= 10:
        "しばらくして返信が来た。"
    else:
        # 信頼10未満でも確率で返信あり
        python:
            import random
            # 50%の確率で返信が来る（完全無視ではない）
            kana_responds = random.random() < 0.50

        if kana_responds:
            "...しばらくして返信が来た。"
        else:
            "既読スルーされた..."
            $ change_trust_kana(-1)   # 旧: -1のまま（変更なし）
            $ daily_flags["ignored_kana_today"] = True
            "（でも、LINEを送ったことは覚えてくれてるはず）"
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

---

## 修正4: カナ友達のセリフ修正

**問題**: 「だからヒモ太郎のこと大事にしてあげてね」は意味が逆。カナの友達がヒモ太郎にお願いしている場面なので「カナのこと」が正しい。

**ファイル**: `events/date_kana_places.rpy`

修正2のコードに反映済み。該当箇所:

```python
# 修正前
"友達「だからヒモ太郎のこと大事にしてあげてね」"

# 修正後
"友達「だからカナのこと大事にしてあげてね」"
```

---

## 修正5: デバッグログの拡充

**ファイル**: デバッグログ出力処理（該当箇所）

クリア時サマリーに以下の情報を追加。

```python
# === クリア時サマリーに追加する項目 ===

# 中盤イベント発生状況
# midgame_busymisaki_done:    True/False
# midgame_doublebooking_done: True/False
# midgame_sighting_done:      True/False
# midgame_sighting_confronted: True/False
# midgame_kana_raid_done:     True/False
# midgame_misaki_direct_done: True/False

# 疑念度
# suspicion_misaki: [値]
# suspicion_kana:   [値]

# 嘘パズル実績
# lie_skill_exp:    [値]
# lie_puzzles_faced: [回数]
# lie_puzzles_busted: [バレた回数]

# デート場所統計
# date_locations: {"famires": 3, "izakaya": 2, "cafe": 1, ...}

# 食事回数
# meals_eaten: [回数] / [総日数]
```

サマリーの出力フォーマット例:

```
=== クリア時サマリー ===
最終所持金:       ¥28,527
美咲 信頼/依存:   74/78
カナ 信頼/依存:   69/29
総収入:           ¥42,069
美咲と会った回数: 8回
お金を要求:       7回
嘘をついた回数:   2回
パチンコ収支:     ¥0
SNSリスク:        25

=== Phase 4 追加情報 ===
疑念度 美咲/カナ:  5/3
嘘パズル: 3回挑戦 / 0回バレ
食事回数: 22/30日

--- 中盤イベント発生状況 ---
美咲「最近忙しい？」:  発生済
ダブルブッキング危機:  発生済
目撃情報:              未発生
カナ突撃訪問:          未発生
美咲直球質問v2:        発生済

--- デート場所統計 ---
美咲: ファミレス3 / 居酒屋2 / 部屋1 / いい店1
カナ: カフェ2 / カラオケ3 / 大学1 / 部屋0
```

**実装方針**: デバッグログ出力関数にPhase 4の変数を追加出力する。変数追跡用のカウンタが必要な項目（嘘パズル回数、デート場所統計、食事回数）は `stats` 辞書に追加する。

```python
# variables.rpy の stats に追加
# "lie_puzzles_faced": 0,
# "lie_puzzles_busted": 0,
# "meals_eaten": 0,
# "date_locations": {},
```

`daily_flags["ate_today"]` が `True` の日に `stats["meals_eaten"]` をインクリメントする処理を `advance_day()` に追加。

```python
# time_system.rpy の advance_day() に追加
if daily_flags.get("ate_today", False):
    stats["meals_eaten"] = stats.get("meals_eaten", 0) + 1
```

デート場所の統計は各デートラベルで記録。

```python
# 各デート場所ラベルで追加（例: misaki_date_famires）
$ stats["date_locations"] = stats.get("date_locations", {})
$ stats["date_locations"]["famires"] = stats["date_locations"].get("famires", 0) + 1
```

---

## テスト確認項目

- [ ] 1日目〜7日目のデートで探りが発生しない
- [ ] 8日目以降、居酒屋デートで探り発生率がUPしている
- [ ] last_night探りは前日に別キャラとデートした場合のみ発生する
- [ ] ファミレス・居酒屋・レストラン・美咲の部屋デートで食事判定が入る
- [ ] カナの部屋デートでは食事判定が入らない
- [ ] デート後に夜の空腹アイコンが出ない（食事した場合）
- [ ] カナの信頼10未満でも50%の確率で返信が来る
- [ ] カナの友達のセリフが「カナのこと大事にしてあげてね」になっている
- [ ] クリア時サマリーにPhase 4の追加情報が出力される

---

## 今後の方向性（メモ）

テストプレイのフィードバックより:
- **セリフの濃度を上げたい**: 各デート場所のテキスト量を増やし、キャラの個性が出る会話バリエーションを追加
- **イベントをもっと増やしたい**: 中盤前半・後半それぞれにあと2〜3種類のランダムイベントを追加検討
- **デートバリエーション拡充**: 同じ場所でも2回目以降は会話が変わる仕組み

→ これらはバグ修正後の次回設計相談で詰める

---

*phase4_step1_v1.1_fixes.md - 2026年3月7日作成*
