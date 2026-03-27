# ヒモ男シミュレーター Phase 4 ステップ2 修正指示書 v1.1

**前提**: Phase 4 ステップ2 v1.0が実装済みであること  
最終更新日: 2026年3月16日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | 初回のお金要求で「また？」テロップが出る | parameter_system.rpy / misaki_events.rpy |
| 2 | 調査 | 昼ターンが飛ぶ（原因特定用ログ追加） | time_system.rpy / debug_log.rpy |
| 3 | 機能追加 | カナがヒモ太郎の部屋に泊まるイベント | kana_events.rpy / date_kana_places.rpy |
| 4 | ログ拡充 | 対面交渉の結果をデバッグログに記録 | misaki_events.rpy / debug_log.rpy |

---

## 修正1: 初回のお金要求で「また？」が出る

### 原因

2つの疑念通知システムが共存しており、意図しないタイミングでテロップが出ている。

**旧システム**（`parameter_system.rpy` 内の `request_money_from_misaki`）:
```python
if stats["times_asked_money"] >= 3:
    suspicion_count += 1
    if suspicion_count == 2:
        renpy.notify("美咲: 「...お金、大丈夫？」")
```

**新システム**（ステップ2で追加した `add_suspicion("too_many_requests")`）:
```python
messages = {
    "too_many_requests": "美咲: 「また？」",
    ...
}
```

旧システムの `suspicion_count` と新システムの `suspicion["misaki"]` が両方蓄積されており、`add_suspicion("too_many_requests")` がLINE経由の `request_money_from_misaki` 内でも呼ばれている。7日目時点で `suspicion_count` が既に蓄積されていた可能性がある。

### 修正方針

旧システムの `renpy.notify` によるテロップ通知を**削除**し、新システムの `add_suspicion` に一本化する。`renpy.notify` でのテロップは対面交渉の反応テキスト（美咲のセリフ）で代替されているため不要。

### ファイル: `systems/parameter_system.rpy`

`request_money_from_misaki` 関数から旧テロップ通知を削除する。

```python
# === 削除する箇所 ===
# request_money_from_misaki 関数内の以下のブロックを削除

# if stats["times_asked_money"] >= 3:
#     suspicion_count += 1
#     if suspicion_count == 2:
#         renpy.notify("美咲: 「...お金、大丈夫？」")
```

代わりに、週間カウントに基づく疑念加算のみを残す。ただし `request_money_from_misaki` 自体には新たな疑念処理を追加しない（呼び出し元の `misaki_money_request` ラベルで `money_request_weekly` を参照して制御するため）。

### ファイル: `events/misaki_events.rpy`

`misaki_money_request`（LINE経由）の週4回拒否処理で `add_suspicion` を呼ぶ箇所の `"too_many_requests"` を、週間カウントが2回目以降でのみ呼ぶように修正。

```python
label misaki_money_request:
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    # 週間カウント加算
    $ money_request_weekly["count"] += 1

    # 週間カウントに応じた反応（修正版）
    if money_request_weekly["count"] >= NEGOTIATION_WEEKLY_LIMIT:
        misaki_c "...最近、お金のことばっかりだね"
        himo "（ヤバい、頼みすぎた）"
        $ add_suspicion("too_many_requests")
        return
    elif money_request_weekly["count"] == 3:
        # 3回目: テロップなし、成功率は既存ロジックで下がる
        pass
    elif money_request_weekly["count"] == 2:
        # 2回目: テロップなし、成功率は既存ロジックで下がる
        pass
    # 1回目: 何もしない（初回は通常対応）

    # 以下、既存の処理を続行
    himo "実は...お金が厳しくて"
    # ...
```

### 確認用: デバッグログに週間カウントを出力

`misaki_money_request` と `misaki_negotiation_start` の両方で、お金要求時に週間カウントをログに記録する。

```python
    $ log_action("美咲にお金要求 weekly=" + str(money_request_weekly["count"]) + " 信頼" + str(misaki["trust"]))
```

---

## 修正2: 昼ターンが飛ぶ問題の調査

### 原因候補

1. カナ泊まり翌朝イベント（`kana_morning_after_event`）で `morning_consumed = True` になった後、`advance_time()` が朝→昼に進めるが、昼の行動選択が表示されずにもう一度 `advance_time()` が走る
2. 体力低下イベント（`event_low_stamina`）が朝に発動した後のフロー
3. 強制イベントの `afternoon_consumed` フラグが前日から残っている

### 修正方針

原因を特定するため、ターン遷移ログを追加する。

### ファイル: `script.rpy`

`main_loop` の各時間帯の行動呼び出し前後にログを追加。

```python
label main_loop:
    if game_date["day"] > GAME_DAYS:
        call day_ending
        return

    scene bg_placeholder
    show screen status_bar

    # === デバッグ: ターン遷移ログ ===
    $ log_action("TURN_START " + str(game_date["day"]) + "日" + get_time_string())

    if game_date["time"] == "morning":
        call morning_actions
    elif game_date["time"] == "afternoon":
        $ log_action("AFTERNOON_ENTER")
        call afternoon_actions
        $ log_action("AFTERNOON_EXIT")
    else:
        call night_actions

    hide screen status_bar

    $ advance_time()
    jump main_loop
```

### ファイル: `systems/time_system.rpy`

`advance_time()` にログを追加。

```python
init python:
    def advance_time():
        global game_date, player, misaki

        old_time = game_date["time"]

        if game_date["time"] == "morning":
            game_date["time"] = "afternoon"
        elif game_date["time"] == "afternoon":
            game_date["time"] = "night"
        else:
            game_date["time"] = "morning"
            advance_day()

        log_action("TIME_ADVANCE " + old_time + " -> " + game_date["time"])

        # 以下、既存の減衰処理...
```

### ファイル: `events/daily_events.rpy`

強制イベントのフラグクリアが確実に行われているか確認。

```python
label morning_actions:
    # 強制イベントチェック前にフラグを念のためクリア
    $ flags["morning_consumed"] = False

    call check_forced_morning_event

    if flags.get("morning_consumed", False):
        $ flags["morning_consumed"] = False
        return

    # 通常メニュー...
```

```python
label afternoon_actions:
    # 同様にクリア
    $ flags["afternoon_consumed"] = False

    # 街に出る場合の強制イベントチェック...
```

---

## 修正3: カナがヒモ太郎の部屋に泊まるイベント

### 問題

デート場所が「ヒモ太郎の部屋」の場合、カナの `kana_stay_offer` で「今日泊まってくよね？」と言うのは不自然。カナがヒモ太郎の部屋にいるのだから、泊まるのはカナの方。

### 修正方針

`kana_stay_offer` の先頭で場所判定を入れ、ヒモ太郎の部屋デートの場合は専用の泊まりイベントに分岐する。

### ファイル: `events/kana_events.rpy`

#### `kana_stay_offer` の修正

```python
label kana_stay_offer:
    if game_date["time"] != "night" or kana["trust"] < 30:
        return

    # === ヒモ太郎の部屋デートの場合は別ルート ===
    if daily_flags.get("date_location", "") == "himo_room":
        call kana_stay_at_himo_room
        return

    # === 以下、カナの部屋での泊まり（既存）===
    if kana["dependence"] >= 50:
        kana_c "今日泊まってくよね？"
    elif kana["dependence"] >= 30:
        kana_c "泊まってく？"
    else:
        kana_c "もし良かったら...泊まってく？"

    menu:
        "泊まる":
            call kana_stay_event
            return

        "帰る":
            call kana_stay_decline
            return
```

#### 新規ラベル: カナがヒモ太郎の部屋に泊まる

```python
label kana_stay_at_himo_room:
    # カナがヒモ太郎の部屋に泊まりたがる
    "夜も更けてきた。"

    if kana["dependence"] >= 50:
        kana_c "ねえ、今日泊まっていい？ ...っていうか泊まるけど"
    elif kana["dependence"] >= 30:
        kana_c "今日泊まっていい？"
    else:
        kana_c "...帰るの遅くなっちゃったし、泊まっていい？"

    menu:
        "いいよ":
            call kana_stay_at_himo_room_event
            return

        "今日は帰ってくれ":
            call kana_stay_at_himo_decline
            return


label kana_stay_at_himo_room_event:
    himo "いいよ、泊まってけ"
    kana_c "やった！"

    "カナがヒモ太郎の部屋に泊まることになった。"
    "狭い部屋に二人。"

    $ stats["kana_stayed_over"] = stats.get("kana_stayed_over", 0) + 1
    $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1

    # 恩恵（カナの部屋より少ない。自分の部屋なので清潔感回復なし）
    $ change_stamina(20)
    $ change_trust_kana(KANA_STAY_TRUST)
    $ change_dependence_kana(KANA_STAY_DEPENDENCE + 3)   # ヒモ太郎の部屋＝距離が近い→依存UP多め

    # 泊まりフラグ
    $ flags["kana_at_himo_room"] = True

    # === エナ期待の匂わせ ===
    "..."
    "カナがくっついてきた。"
    "一緒に過ごした。"

    kana_c "...ヒモ太郎の部屋、狭いけど落ち着く"

    # 翌朝演出用フラグ
    $ flags["kana_himo_room_morning"] = True

    return


label kana_stay_at_himo_decline:
    himo "今日はちょっと..."

    if kana["dependence"] >= 60:
        kana_c "...なんで？ 嫌なの？"
        "カナの声が震えている。"
        $ change_trust_kana(-5)
        $ suspicion["kana"] = suspicion.get("kana", 0) + 2

        if not daily_flags.get("kana_mood_resolved", False):
            call gokiragen_qte_start
    elif kana["dependence"] >= 30:
        kana_c "え〜...分かった"
        $ change_trust_kana(-3)
    else:
        kana_c "そっか、じゃあ帰るね"
        $ change_trust_kana(-1)

    return
```

#### 新規ラベル: カナがヒモ太郎の部屋に泊まった翌朝

```python
label kana_himo_room_morning_event:
    scene bg_placeholder

    "自分の部屋で目が覚めた。"
    "隣でカナが寝ている。"

    kana_c "...んん...おはよ"

    "カナがキッチンに立った。"
    kana_c "冷蔵庫...何もないじゃん"
    himo "...すまん"
    kana_c "しょうがないな〜。コンビニ行ってくるね"

    "カナがコンビニで朝ごはんを買ってきてくれた。"

    $ daily_flags["ate_today"] = True
    $ change_stamina(10)
    $ change_trust_kana(2)

    kana_c "ヒモ太郎の部屋、もうちょっと片付けなよ"
    himo "...はい"

    "気づいたら昼になっていた。"
    "（朝の時間が消えた）"

    return
```

### ファイル: `events/daily_events.rpy`

`check_forced_morning_event` にヒモ太郎の部屋泊まり翌朝を追加。

```python
    # イベント: カナがヒモ太郎の部屋に泊まった翌朝
    if flags.get("kana_himo_room_morning", False):
        $ flags["kana_himo_room_morning"] = False
        $ flags["kana_at_himo_room"] = False
        call kana_himo_room_morning_event
        $ flags["morning_consumed"] = True
        return
```

### ファイル: `data/variables.rpy`

`flags` に追加:

```python
    "kana_at_himo_room": False,
    "kana_himo_room_morning": False,
```

---

## 修正4: デバッグログの拡充（対面交渉の結果記録）

### 追加するログ項目

対面交渉の各段階でログを出力し、「何が起きて成功/失敗したか」をテストプレイ後に追跡できるようにする。

### ファイル: `events/misaki_events.rpy`

#### `misaki_negotiation_start` にログ追加

```python
    # 切り出し方を選んだ後（第2段階呼び出し前）
    $ log_action("対面交渉_開始 approach=" + _nego_approach + " base_rate=" + str(_nego_base_rate) + " weekly=" + str(money_request_weekly["count"]))
```

#### `misaki_negotiation_reaction` にログ追加

```python
    # 成功率計算後
    $ log_action("対面交渉_判定 rate=" + str(_nego_success_rate) + " loc=" + location + " loc_bonus=" + str(location_bonus) + " weekly_pen=" + str(weekly_penalty) + " susp_pen=" + str(suspicion_penalty))
```

#### `misaki_negotiation_amount` にログ追加

```python
    # 成功/失敗判定後
    if success:
        $ log_action("対面交渉_成功 type=" + _nego_amount_type + " amount=" + str(amount) + " final_rate=" + str(final_rate))
    else:
        $ log_action("対面交渉_失敗 type=" + _nego_amount_type + " final_rate=" + str(final_rate))
```

#### LINE経由のお金要求にもログ追加

```python
    # misaki_money_request の成功/失敗後
    if success:
        $ log_action("LINE要求_成功 amount=" + str(amount) + " weekly=" + str(money_request_weekly["count"]))
    else:
        $ log_action("LINE要求_失敗 weekly=" + str(money_request_weekly["count"]))
```

### クリア時サマリーに追加

```python
# === クリア時サマリーに追加する項目 ===

# --- 経済圏統計 ---
# 対面交渉: [成功回数]/[試行回数]
# LINE要求: [成功回数]/[試行回数]
# 週間要求カウント最大: [最大値]
# カナ泊まり回数: [回数]（うちヒモ太郎の部屋: [回数]）
# カナ恩恵受取: [回数]
# ご機嫌取りQTE: [成功]/[失敗]
# カナ搾取スコア: [値]
```

追跡用カウンタを `stats` に追加:

```python
# variables.rpy の stats に追加
#   "negotiation_attempts": 0,       # 対面交渉の試行回数
#   "negotiation_success": 0,        # 対面交渉の成功回数
#   "negotiation_total_earned": 0,   # 対面交渉の総収入
#   "line_request_attempts": 0,      # LINE要求の試行回数
#   "line_request_success": 0,       # LINE要求の成功回数
#   "kana_stayed_himo_room": 0,      # カナがヒモ太郎の部屋に泊まった回数
```

対面交渉の各ラベルでカウンタを更新:

```python
# misaki_negotiation_start でキャンセル以外の選択時
$ stats["negotiation_attempts"] = stats.get("negotiation_attempts", 0) + 1

# misaki_negotiation_amount の成功時
$ stats["negotiation_success"] = stats.get("negotiation_success", 0) + 1
$ stats["negotiation_total_earned"] = stats.get("negotiation_total_earned", 0) + amount

# misaki_money_request（LINE経由）の処理開始時
$ stats["line_request_attempts"] = stats.get("line_request_attempts", 0) + 1

# misaki_money_request の成功時
$ stats["line_request_success"] = stats.get("line_request_success", 0) + 1

# kana_stay_at_himo_room_event 内
$ stats["kana_stayed_himo_room"] = stats.get("kana_stayed_himo_room", 0) + 1
```

---

## テスト確認項目

### 修正1: 初回テロップ
- [ ] 週の1回目のお金要求（LINE・対面とも）で「また？」テロップが出ない
- [ ] 週の2回目以降で反応が段階的に変わる
- [ ] デバッグログに `weekly=` の値が正しく記録される

### 修正2: 昼ターン飛び
- [ ] デバッグログに `TURN_START` `AFTERNOON_ENTER` `AFTERNOON_EXIT` `TIME_ADVANCE` が記録される
- [ ] 昼ターンが飛んだ場合、直前のログから原因を特定できる
- [ ] `morning_consumed` `afternoon_consumed` が翌日に持ち越されていない

### 修正3: カナのヒモ太郎部屋泊まり
- [ ] ヒモ太郎の部屋デート後に「泊まっていい？」と聞かれる（「泊まってくよね？」ではない）
- [ ] 依存度で聞き方が変わる（50以上で半強制、30未満で控えめ）
- [ ] 泊まった翌朝にカナがコンビニで朝食を買ってくるイベントが発生する
- [ ] 翌朝イベントで朝の時間が消費される
- [ ] 断った場合、依存度に応じた反応が変わる
- [ ] 依存60以上で断るとご機嫌取りQTEが発動する

### 修正4: デバッグログ
- [ ] 対面交渉の開始・判定・結果がログに記録される
- [ ] LINE要求の成功/失敗と週間カウントがログに記録される
- [ ] クリア時サマリーに経済圏統計が出力される

---

*phase4_step2_v1.1_fixes.md - 2026年3月16日作成*
