# 自動テスト導入 アクション計画

**作成日**: 2026年3月14日
**最終更新**: 2026年3月15日（実装完了・全テストPASS確認済み）
**ベース指示書**: `docs/autotest_implementation_v1.md`（Web版Claude作成）
**本計画の役割**: 指示書と実コードの差異を解消し、正確な実装手順を定める

---

## テスト実行結果（2026年3月15日）

```
[rpytest] Test suites:     1 |     1 passed
[rpytest] Test cases :     9 |     9 passed
[rpytest] Assertions :     7 |     7 passed
[rpytest] Time: 629.385 s [10:29]
[rpytest] Status: PASSED
```

| テストケース | 所要時間 | 結果 |
|---|---|---|
| smoke_random_playthrough (seed=42) | 71.3s | PASS |
| smoke_random_playthrough_seed2 (seed=123) | 72.4s | PASS |
| smoke_random_playthrough_seed3 (seed=999) | 65.5s | PASS |
| param_bounds_midgame (15日目) | 70.1s | PASS |
| param_bounds_endgame (25日目) | 69.9s | PASS |
| daily_flags_reset (5日目朝) | 68.9s | PASS |
| appointment_integrity_midgame (15日目) | 70.7s | PASS |
| appointment_integrity_endgame (25日目) | 68.8s | PASS |
| ending_type_is_set | 71.1s | PASS |

---

## 指示書と実コードの差異サマリー

| # | 指示書の想定 | 実コード | 対応 |
|---|-------------|---------|------|
| 1 | ラベル名 `ending_balance` 等 | `ending_balance_30days` 等 | 実ラベル名を使用 |
| 2 | 新変数 `_game_ended` を追加 | `flags["game_ended"]` が既存 | 新変数不要。ヘルパー関数でラップ |
| 3 | `lie_puzzle_start` / `lie_puzzle_result` | `run_lie_puzzle(scenario, target)` / `lie_puzzle["result"]` | 実ラベル・変数を使用 |
| 4 | `evidence_qte_start` / `qte_result` | `run_evidence_qte(scenario)` / `flags["qte_failed_badly"]` | 実ラベル・変数を使用 |
| 5 | `appointments` がネスト辞書 | `{"misaki": int_or_None, "kana": int_or_None}` | ヘルパー関数を書き直し |
| 6 | `daily_flags` が6キー | 14キー（Phase 4含む）。`cooked_today` は未使用のため削除済み | リセット対象の14キーでテスト |
| 7 | `demo_end_scene` 未考慮 | `kana_events.rpy:539` で `flags["game_ended"]=True` | `_ending_type = "demo"` を追加 |

---

## 実装時に発見・解決した問題

### Ren'Py testcase構文の修正

| # | 問題 | 原因 | 修正 |
|---|------|------|------|
| 1 | `click until test_game_ended()` → "Invalid condition" | testcase構文でPython式には `eval()` ラッパーが必要 | `click until eval (test_game_ended())` |
| 2 | `assert eval (...), timeout 1.0` → "end of line expected" | `assert` のtimeoutの前にカンマ不可 | `assert eval (...) timeout 1.0` |
| 3 | `define config.test_transition_timeout = 0.5` → 起動エラー | Ren'Py 8.5.2に存在しない設定変数 | 行を削除 |

### テスト実行時の問題と対策

| # | 問題 | 原因 | 修正 |
|---|------|------|------|
| 4 | 全テストが5秒でタイムアウト（メインメニューで停止） | テストはメインメニューから開始。`click` だけではスタートボタンを押せない | 各テスト冒頭に `click "スタート"` を追加 |
| 5 | スタート後も5秒でタイムアウト | デフォルトのグローバルタイムアウト `_test.timeout = 5.0` が短すぎ | `$ _test.timeout = 600` + `click until ... timeout 600` に変更 |
| 6 | メニュー画面でゲームが進行しない | `click`（引数なし）は画面のランダム座標にクリック。1920×1080でメニューボタンに当たる確率が極めて低い | `screens.rpy` の `choice` スクリーンにテスト時自動選択タイマーを追加 |
| 7 | 「ステータス確認」モーダル画面で停止 | `call screen status_detail` はchoiceスクリーンではないため自動選択が効かない | `status_detail` スクリーンにもテスト時自動閉じタイマーを追加 |
| 8 | テスト間の遷移でタイムアウト | Ren'Pyテストランナーはテスト間でゲームを自動リスタートしない。前テストがゲーム中のまま次テストが `click "スタート"` を探す | 全テスト末尾に `click until eval(test_at_main_menu()) timeout 30` を追加 |

---

## タスク1: `_ending_type` 変数の追加 ✅

### 1-1. variables.rpy に変数追加
**ファイル**: `game/data/variables.rpy`（158-160行目）

```python
# エンディング種別記録（テスト・実績・デバッグ用）
# 値: "good" / "gray" / "normal" / "bad_bankruptcy" / "demo"
default _ending_type = ""
```

### 1-2. endings.rpy の4ラベルに `_ending_type` セットを追加
**ファイル**: `game/events/endings.rpy`

各ラベルの `$ flags["game_ended"] = True` の直後に1行追加:

| ラベル | 追加内容 |
|--------|---------|
| `ending_balance_30days` | `$ _ending_type = "good"` |
| `ending_himou_30days` | `$ _ending_type = "gray"` |
| `ending_unstable_30days` | `$ _ending_type = "normal"` |
| `ending_bankruptcy_30days` | `$ _ending_type = "bad_bankruptcy"` |

### 1-3. kana_events.rpy の demo_end_scene にも追加
**ファイル**: `game/events/kana_events.rpy`

```python
    $ _ending_type = "demo"
```

---

## タスク2: 嘘パズル・QTEのテストモード対応 ✅

### 方針
本編コードへの `renpy.is_in_test()` 分岐は計4箇所:
- `lie_puzzle.rpy` — パズルUIスキップ
- `evidence_qte.rpy` — QTEスキップ
- `screens.rpy` choice スクリーン — メニュー自動選択（タスク6で追加）
- `screens.rpy` status_detail スクリーン — モーダル自動閉じ（タスク6で追加）

### 2-1. lie_puzzle.rpy
**ファイル**: `game/systems/lie_puzzle.rpy`

```python
    # テスト実行時: パズルUIをスキップし、安全クリアとして処理
    if renpy.is_in_test():
        $ lie_puzzle["result"] = "safe"
        $ lie_puzzle["active"] = False
        return
```

### 2-2. evidence_qte.rpy
**ファイル**: `game/systems/evidence_qte.rpy`

```python
    # テスト実行時: QTEをスキップし、成功として処理
    if renpy.is_in_test():
        $ flags["qte_failed_badly"] = False
        return
```

---

## タスク3: テスト用ヘルパー ✅

**ファイル**: `game/test_helpers.rpy`

```python
# test_helpers.rpy
# テスト実行時のみ使用されるヘルパー関数

init python:

    def test_fix_random_seed(seed=42):
        """テスト用にランダムシードを固定する"""
        renpy.random.seed(seed)

    def test_game_ended():
        """flags["game_ended"] のラッパー"""
        return flags.get("game_ended", False)

    def test_at_main_menu():
        """メインメニューに戻ったかどうか"""
        return renpy.get_screen("main_menu") is not None

    def test_assert_param_bounds():
        """全パラメータが0-100範囲内か確認。エラーがあれば文字列で返す"""
        # player: stamina, cleanliness, charm
        # misaki: trust, dependence
        # kana: trust, dependence (met時のみ)
        ...

    def test_assert_daily_flags_reset():
        """advance_day()後にdaily_flagsがリセットされているか確認"""
        # 14キーをチェック（cooked_today は未使用のため除外）
        ...

    def test_assert_appointment_integrity():
        """約束管理の整合性チェック（過去の約束残存・同日重複）"""
        ...
```

---

## タスク4: スモークテスト ✅

**ファイル**: `game/tests/smoke_test.rpy`

```renpy
testcase smoke_random_playthrough:
    description "全体通し走行（seed=42）"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30
```

同パターンで seed=123, seed=999 の計3テスト。

---

## タスク5: システム検証テスト ✅

**ファイル**: `game/tests/system_test.rpy`

```renpy
testcase param_bounds_midgame:
    description "15日目パラメータ境界値チェック"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (game_date["day"] >= 15) timeout 600
    $ _bounds_error = test_assert_param_bounds()
    assert eval (_bounds_error == "") timeout 1.0
    # ゲーム終了→メインメニューまで走り切る
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30
```

同パターンで計6テスト（param_bounds×2, daily_flags_reset, appointment_integrity×2, ending_type_is_set）。

---

## タスク6: テスト自動化のための本編コード修正 ✅

### 6-1. choice スクリーンにテスト時自動選択を追加
**ファイル**: `game/screens.rpy`（choice スクリーン）

```python
    # テスト実行時: 自動でランダム選択
    if renpy.is_in_test():
        timer 0.1 action renpy.random.choice(items).action
```

テスト時のみ、メニュー表示0.1秒後にランダムな選択肢を自動選択。通常プレイには影響なし。

### 6-2. status_detail スクリーンにテスト時自動閉じを追加
**ファイル**: `game/screens.rpy`（status_detail スクリーン）

```python
    # テスト実行時: 自動で閉じる
    if renpy.is_in_test():
        timer 0.1 action Return()
```

---

## 変更ファイル一覧（最終）

| ファイル | 変更種別 | タスク |
|---------|---------|-------|
| `game/data/variables.rpy` | 2行追加 | 1 |
| `game/events/endings.rpy` | 4行追加 | 1 |
| `game/events/kana_events.rpy` | 1行追加 | 1 |
| `game/systems/lie_puzzle.rpy` | 4行追加 | 2 |
| `game/systems/evidence_qte.rpy` | 3行追加 | 2 |
| `game/screens.rpy` | 4行追加（choice + status_detail） | 6 |
| `game/test_helpers.rpy` | 新規作成 | 3 |
| `game/tests/smoke_test.rpy` | 新規作成 | 4 |
| `game/tests/system_test.rpy` | 新規作成 | 5 |

---

## テスト実行方法

1. Ren'Py ランチャーで「Force Recompile」
2. 「Run Testcases」をクリック
3. 全9テスト完走まで約10分待つ
4. コンソールに `Status: PASSED` が表示されれば成功

### Ren'Py testcase構文 重要メモ

- Python式には `eval ()` ラッパーが必要: `click until eval (condition)`
- `assert` のtimeoutの前にカンマ不可: `assert eval (...) timeout 1.0`
- `config.test_transition_timeout` はRen'Py 8.5.2に存在しない
- `click`（引数なし）は画面のランダム座標にクリック。メニュー選択には不十分
- テスト間でゲームは自動リスタートされない。各テストは `click "スタート"` で開始し、メインメニューまで戻って終了する必要がある
- グローバルタイムアウト `_test.timeout` のデフォルトは5秒。30日ゲームには `$ _test.timeout = 600` が必要

---

*autotest_action_plan.md - 2026年3月14日作成 / 2026年3月15日更新（実装完了）*
