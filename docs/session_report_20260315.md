# Phase 4 修正セッション報告 — 2026年3月15日

## 実施内容サマリー

本セッションでは以下の3つの修正指示書を実装し、テスト中に発見された追加バグも修正した。

| 修正指示書 | 修正数 | 状態 |
|-----------|--------|------|
| phase4_v1.3.1_critical_fixes.md | 2件 | 完了・テスト済み |
| phase4_step1_v1.4_fixes.md | 3件 | 完了・テスト済み |
| デバッグログ出力先変更 | 1件 | 完了 |
| テスト中の追加バグ修正 | 3件 | 完了・テスト済み |

---

## 1. v1.3.1 致命的バグ修正

### 修正1: 家賃請求とエンディング判定

**問題:** `advance_day()` で `day > GAME_DAYS` の早期returnにより月次請求処理に到達しない。30日制の体験版では家賃¥50,000が一度も請求されない。エンディング判定も `player["money"] >= 0` で甘すぎる。

**修正方針:** エンディング突入時に家賃を精算する方式に変更。

**変更ファイル:**

| ファイル | 変更内容 |
|---------|---------|
| `endings.rpy` | `ending_30days` に家賃¥50,000＋通信費¥3,000の精算ロジック追加。残高不足→BAD END、支払後にエンディング分岐 |
| `time_system.rpy` | 月次請求処理（`monthly_billing`）をコメントアウト。体験版ではエンディングで精算 |

### 修正2: 約束管理システムの統合

**問題:** 約束管理が旧システム（`weekend_promised` + `met_misaki_this_weekend`）と新システム（`appointments` + `misaki_appointment_kept`）の2系統並行。泊まりが約束履行として認識されない。

**修正方針:** 旧システムを廃止し `appointments` 系に一本化。履行判定に `staying_at_misaki` を追加。

**変更ファイル:**

| ファイル | 変更内容 |
|---------|---------|
| `time_system.rpy` | 旧 `weekend_promised` ブロック削除。`misaki_tonight` チェックに泊まり判定追加。約束チェックを `met_today` / `staying_at_*` で直接判定に変更（`appointment_kept` フラグ不要に） |
| `misaki_events.rpy` | `weekend_promised = True` → `appointments["misaki"]` に変更。`met_misaki_this_weekend` 設定を2箇所削除 |
| `date_misaki_places.rpy` | `misaki_appointment_kept` 設定を削除 |
| `variables.rpy` | `weekend_promised`、`met_misaki_this_weekend`、`misaki_appointment_kept`、`kana_appointment_kept` を削除 |

---

## 2. v1.4 バグ修正

### 修正1: イベント①がターンを消費する問題

**問題:** `check_midgame_events()` がイベント①（美咲LINE）で `return True` → 朝ターンが丸ごとスキップされる。LINEはターンを消費すべきでない。

**修正方針:** 戻り値を3種類に変更: `False`（なし）/ `"notify"`（ターン消費しない）/ `True`（ターン消費する）。

**変更ファイル:**

| ファイル | 変更内容 |
|---------|---------|
| `midgame_events.rpy` | イベント①（美咲LINE）とイベント⑤（ダブルブッキング）を `return "notify"` に変更 |
| `script.rpy` | `morning_actions` / `afternoon_actions` で `midgame_fired == True` のみreturn。`"notify"` 時は `process_pending_events` で先に処理してから通常メニューへ |

### 修正2: カナとの約束後にドタキャンされる

**問題:** プレイヤーが「会おう」と約束した場合もドタキャンされる。

**修正方針:** `daily_flags["kana_tonight_source"]` でプレイヤー主導 (`"player"`) とカナ主導 (`"kana"`) を区別。

**変更ファイル:**

| ファイル | 変更内容 |
|---------|---------|
| `variables.rpy` | `daily_flags` に `"kana_tonight_source": None` 追加 |
| `time_system.rpy` | daily_flags リセットに `kana_tonight_source` 追加 |
| `script.rpy` | カナ夜デート: プレイヤー主導は確定、カナ主導のみドタキャンリスク（成功率60%〜95%） |
| `kana_events.rpy` | 雑談・甘える・date_request → `"player"`、initiative → `"kana"` |
| `daily_events.rpy` | カナ朝イニシアチブ → `"kana"` |
| `midgame_events.rpy` | 急な呼び出し・ダブルブッキング → `"kana"` |

### 修正3: 美咲LINE後にお金要求できる

**問題:** イベント①で `last_contact = 0` にリセットされ、LINEだけの接触でもお金要求が通る。

**修正方針:** `daily_flags["misaki_lined_only"]` フラグで LINE のみの接触を明示し、お金要求をブロック。`last_contact > 3`（2日以上未接触）でもブロック。

**変更ファイル:**

| ファイル | 変更内容 |
|---------|---------|
| `variables.rpy` | `daily_flags` に `"misaki_lined_only": False` 追加 |
| `time_system.rpy` | daily_flags リセットに `misaki_lined_only` 追加 |
| `midgame_events.rpy` | `midgame_misaki_busy` の返信時 `last_contact` を `0→1` に変更、`misaki_lined_only = True` セット |
| `misaki_events.rpy` | `misaki_money_request` に2段階ガード追加（LINE only / last_contact > 3） |

---

## 3. テスト中に発見・修正した追加バグ

### 追加修正A: 美咲からの自発的連絡で `reset_contact()` が呼ばれていた

**問題:** `misaki_check_in`（LINEイベント）と `misaki_stress_call`（深夜電話）で `reset_contact()` → `last_contact = 0` が設定され、「対面で会った」と同等の扱いになっていた。

**修正:**
- `misaki_check_in`: `reset_contact()` → `misaki["last_contact"] = 1` + `misaki_lined_only = True`
- `misaki_stress_call`: 同上

### 追加修正B: デバッグオーバーレイの表示バグ

**問題:** `screens.rpy` のデバッグオーバーレイで「美咲streak」と表示していたが、実際には `misaki['last_contact']` を参照していた。テスト時に `misaki_streak` がリセットされたと誤認する原因になった。

**修正:** `"美咲streak: [misaki_streak] contact: [misaki['last_contact']]"` に変更し、両方の値を表示。

### 追加修正C: misaki_streak 判定のタイミング問題

**問題:** `advance_day()` 内で streak 判定が `queue_misaki_initiative()` より前に実行されていたため、美咲からの自発的連絡（`misaki_check_in` / `misaki_stress_call`）による streak 維持が効かなかった。

**根本原因の分析:**
```
advance_day() の旧実行順序:
  1. streak判定（met_today + misaki_lined_only チェック）  ← ここで判定
  2. daily_flags リセット（misaki_lined_only = False）
  3. queue_misaki_initiative() → misaki_check_in をキュー  ← ここでフラグセット（手遅れ）
  4. process_pending_events → misaki_check_in 実行          ← advance_day() の外
```

**修正:** streak判定を `queue_misaki_initiative()` の後に移動。3つの情報源を統合:
- `_met_today_prev`: 前日に対面で会ったか（advance_day冒頭で保存）
- `_had_line_contact`: 前日にLINE/電話があったか（midgame_misaki_busy等、advance_day冒頭で保存）
- `daily_flags["misaki_lined_only"]`: queue_misaki_initiative で今日の連絡予定があるか

```python
# advance_day() 修正後の実行順序:
_met_today_prev = misaki["met_today"]           # 保存
_had_line_contact = daily_flags["misaki_lined_only"]  # 保存
# ... 日付進行、daily_flags リセット ...
queue_misaki_initiative()  # misaki_lined_only を再セットする可能性あり
# streak判定（3つの情報源を統合）
if not _met_today_prev and not _had_line_contact and not daily_flags["misaki_lined_only"]:
    misaki_streak = max(0, misaki_streak - 1)
```

---

## 4. その他の変更

### デバッグログ出力先変更

`debug_log.rpy` の出力先を `game/` → `game/debug_log/` に変更。ディレクトリが存在しない場合は自動作成。

### ステータス詳細画面にログ出力ボタン追加

`screens.rpy` の `status_detail` 画面に「ログ出力」ボタンを追加。ゲーム中にいつでもデバッグログを出力可能に。

### デバッグログ項目の追加（一時的）

テスト用に以下のデバッグログを追加（今後のテストにも有用なため残置）:
- `ADVANCE_DAY`: 日付切替時の全状態（streak, met_today, lined_only, last_contact）
- `QUEUE_CHECKIN` / `QUEUE_STRESSCALL`: 美咲の自発的連絡キュー時
- `CHECK_IN` / `STRESS_CALL`: イベント実行時
- `STREAK DOWN`: streakが減少した時の全条件値
- `お金要求ブロック`: ガードが発動した時

---

## テスト結果

体験版（25日）を通しプレイで確認:

- [x] 家賃精算はエンディングで正常に動作（30日到達時）
- [x] お金要求ブロックが LINE 後に正しく動作（4日目、5日目、16日目、19日目で確認）
- [x] 美咲 streak が LINE/電話で不正にリセットされない
- [x] `STREAK DOWN` ログが一度も発生していない
- [x] イベント①（美咲LINE）がターンを消費しない
- [x] 体験版ENDに正常到達

---

## 変更ファイル一覧

| ファイル | 修正内容 |
|---------|---------|
| `game/data/variables.rpy` | `weekend_promised` 等の旧変数削除、`kana_tonight_source` / `misaki_lined_only` 追加 |
| `game/systems/time_system.rpy` | 約束チェック統合、月次請求コメントアウト、streak判定タイミング修正、`queue_misaki_initiative` に連絡フラグ追加 |
| `game/events/endings.rpy` | 家賃精算ロジック追加 |
| `game/events/midgame_events.rpy` | `check_midgame_events` の notify 対応、`last_contact` 修正、`kana_tonight_source` 追加 |
| `game/events/misaki_events.rpy` | お金要求ガード追加、`reset_contact()` 誤用修正、旧フラグ削除 |
| `game/events/kana_events.rpy` | `kana_tonight_source` 追加 |
| `game/events/daily_events.rpy` | `kana_tonight_source` 追加 |
| `game/events/date_misaki_places.rpy` | `misaki_appointment_kept` 削除 |
| `game/script.rpy` | `midgame_fired == True` 判定修正、notify型 `process_pending_events` 追加、カナドタキャン判定修正 |
| `game/screens.rpy` | デバッグオーバーレイ修正、ログ出力ボタン追加 |
| `game/systems/debug_log.rpy` | 出力先を `game/debug_log/` に変更 |

*session_report_20260315.md — 2026年3月15日作成*
