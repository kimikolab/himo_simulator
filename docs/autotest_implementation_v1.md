# ヒモ男シミュレーター 自動テスト実装指示書 v1.0

**前提**: Phase 3（デモ版）が動作確認済みであること  
**参考**: Ren'Py テストケース公式 https://ja.renpy.org/doc/html/testcases.html  
最終更新日: 2026年3月14日

---

## 概要

Ren'Py 組み込みの `testcase` 機能を使い、自動テストを導入する。
目的は「コード変更後にクラッシュや変数矛盾を素早く検出する」こと。
ゲーム体験・キャラの演技・会話の質は引き続き目視チェックで担保する。

---

## 実装タスク一覧

| # | 種別 | 内容 | ファイル |
|---|------|------|----------|
| 1 | 本編変更 | `_ending_type` 変数の追加 | variables.rpy / endings.rpy |
| 2 | 本編変更 | 嘘パズル・QTEのテストモード対応 | lie_puzzle.rpy / evidence_qte.rpy |
| 3 | 新規 | テスト用ヘルパー | test_helpers.rpy |
| 4 | 新規 | スモークテスト（Layer 1） | tests/smoke_test.rpy |
| 5 | 新規 | システム検証テスト（Layer 2） | tests/system_test.rpy |

**重要**: Layer 3（シナリオルートテスト）は今回の範囲外。ゲーム内容が安定してから別途作成する。

---

## ファイル配置

```
game/
├── test_helpers.rpy              # テスト用ヘルパー関数
├── tests/
│   ├── smoke_test.rpy            # Layer 1: クラッシュしないことの確認
│   └── system_test.rpy           # Layer 2: パラメータ・フラグの整合性
├── data/
│   └── variables.rpy             # ← _ending_type を追加
├── events/
│   ├── endings.rpy               # ← _ending_type のセットを追加
│   ├── lie_puzzle.rpy            # ← テストモード分岐を追加
│   └── evidence_qte.rpy          # ← テストモード分岐を追加
```

---

## タスク1: `_ending_type` 変数の追加

テストからエンディング種別を確認できるようにする。
テスト以外にも、今後のSteam実績連携やデバッグに有用。

### ファイル: `data/variables.rpy`

以下の変数を追加する。

```python
# variables.rpy に追加

# エンディング種別の記録（テスト・実績・デバッグ用）
default _ending_type = ""
# 値: "good" / "gray" / "normal" / "bad_bankruptcy"

# ゲーム終了フラグ（テストの終了判定用）
default _game_ended = False
```

### ファイル: `events/endings.rpy`

各エンディングラベルの**冒頭**で `_ending_type` をセットし、
各エンディングラベルの**末尾**（`return` の直前）で `_game_ended` をセットする。

```python
label ending_balance:
    $ _ending_type = "good"            # ← 追加
    scene bg_placeholder with fade
    # ... 既存の演出 ...
    call show_himo_aptitude_result
    $ _game_ended = True               # ← 追加
    return


label ending_himou:
    $ _ending_type = "gray"            # ← 追加
    scene bg_placeholder with fade
    # ... 既存の演出 ...
    call show_himo_aptitude_result
    $ _game_ended = True               # ← 追加
    return


label ending_unstable:
    $ _ending_type = "normal"          # ← 追加
    scene bg_placeholder with fade
    # ... 既存の演出 ...
    call show_himo_aptitude_result
    $ _game_ended = True               # ← 追加
    return


label ending_bankruptcy:
    $ _ending_type = "bad_bankruptcy"   # ← 追加
    scene bg_placeholder with fade
    # ... 既存の演出 ...
    call show_himo_aptitude_result
    $ _game_ended = True               # ← 追加
    return
```

**注意**: demo END / GRAY END / BAD END など、現在の実装に合わせてラベル名は適宜読み替えること。存在する全エンディングラベルに対して同様の処理を入れる。

---

## タスク2: 嘘パズル・QTEのテストモード対応

### 方針

本編コードに `renpy.is_in_test()` を入れるのは**このタスクのみ**に限定する。
嘘パズルとQTEはリアルタイム入力が必要なため、テスト時は結果変数を直接セットして処理をスキップする。

### ファイル: `events/lie_puzzle.rpy`

嘘パズルのメインラベル（パズルUIを表示する直前）に以下を追加。

```python
label lie_puzzle_start:
    # テスト実行時: パズルUIをスキップし、成功として処理
    if renpy.is_in_test():
        $ lie_puzzle_result = "success"
        return

    # 通常時: 以下は既存のパズル処理
    # ...
```

### ファイル: `events/evidence_qte.rpy`

証拠隠滅QTEのメインラベルに同様の処理を追加。

```python
label evidence_qte_start:
    # テスト実行時: QTEをスキップし、成功として処理
    if renpy.is_in_test():
        $ qte_result = "success"
        return

    # 通常時: 以下は既存のQTE処理
    # ...
```

**注意**: ラベル名・結果変数名は現在の実装に合わせて読み替えること。
分岐は各ミニゲームの**入口に1箇所ずつだけ**入れる。本編の他の場所には `renpy.is_in_test()` を入れない。

---

## タスク3: テスト用ヘルパー

### ファイル: `game/test_helpers.rpy`（新規作成）

```python
# test_helpers.rpy
# テスト実行時のみ使用されるヘルパー関数

init python:

    def test_fix_random_seed(seed=42):
        """テスト用にランダムシードを固定する"""
        renpy.random.seed(seed)

    def test_assert_param_bounds():
        """
        全パラメータが定義された範囲内にあるかチェックする。
        範囲外の値があれば文字列でエラー内容を返す。
        問題なければ空文字列を返す。
        """
        errors = []

        # プレイヤーパラメータ
        if player["stamina"] < 0 or player["stamina"] > 100:
            errors.append("stamina out of range: {}".format(player["stamina"]))
        if player["cleanliness"] < 0 or player["cleanliness"] > 100:
            errors.append("cleanliness out of range: {}".format(player["cleanliness"]))
        if player["charm"] < 0 or player["charm"] > 100:
            errors.append("charm out of range: {}".format(player["charm"]))

        # 美咲パラメータ
        if misaki["trust"] < 0 or misaki["trust"] > 100:
            errors.append("misaki trust out of range: {}".format(misaki["trust"]))
        if misaki["dependence"] < 0 or misaki["dependence"] > 100:
            errors.append("misaki dependence out of range: {}".format(misaki["dependence"]))

        # カナパラメータ（出会い済みの場合のみ）
        if kana_flags.get("met", False):
            if kana["trust"] < 0 or kana["trust"] > 100:
                errors.append("kana trust out of range: {}".format(kana["trust"]))
            if kana["dependence"] < 0 or kana["dependence"] > 100:
                errors.append("kana dependence out of range: {}".format(kana["dependence"]))

        return ", ".join(errors)

    def test_assert_daily_flags_reset():
        """
        daily_flags が全てリセット状態かチェックする。
        advance_day() 直後に呼ぶことを想定。
        問題なければ空文字列を返す。
        """
        errors = []

        if daily_flags.get("asked_money_today", False):
            errors.append("asked_money_today not reset")
        if daily_flags.get("ignored_today", False):
            errors.append("ignored_today not reset")
        if daily_flags.get("ignored_kana_today", False):
            errors.append("ignored_kana_today not reset")
        if daily_flags.get("ate_today", False):
            errors.append("ate_today not reset")

        return ", ".join(errors)

    def test_assert_appointment_integrity():
        """
        約束管理システムの整合性チェック。
        - 過去の日付の約束が残っていないか
        - 同じ時間帯に2つ以上の約束がないか
        問題なければ空文字列を返す。
        """
        errors = []

        # appointments 辞書が存在する場合のみチェック
        if not hasattr(store, 'appointments') or appointments is None:
            return ""

        current_day = game_date["day"]

        for key, appt in appointments.items():
            # 過去の約束が残っていないかチェック
            appt_day = appt.get("day", 0)
            if appt_day < current_day and appt.get("active", True):
                errors.append("stale appointment: day {} key {}".format(appt_day, key))

        # 同日同時間帯の重複チェック
        time_slots = {}
        for key, appt in appointments.items():
            if not appt.get("active", True):
                continue
            slot_key = "{}_{}".format(appt.get("day", 0), appt.get("time", ""))
            if slot_key in time_slots:
                errors.append("double booking: day {} time {} ({} vs {})".format(
                    appt.get("day", 0), appt.get("time", ""),
                    time_slots[slot_key], key
                ))
            else:
                time_slots[slot_key] = key

        return ", ".join(errors)
```

**注意**: `appointments` 辞書や `kana_flags` / `kana` 変数の構造は現在の実装に合わせて調整すること。変数名やキー名が異なる場合は適宜読み替える。

---

## タスク4: スモークテスト（Layer 1）

### ファイル: `game/tests/smoke_test.rpy`（新規作成）

```renpy
# game/tests/smoke_test.rpy
# Layer 1: ゲームがクラッシュせずに完走することを確認するテスト

# === テスト設定 ===
# テスト実行時のトランジション待ち時間を短縮
define config.test_transition_timeout = 0.5


# === スモークテスト: ランダム選択で通し走行 ===
testcase smoke_random_playthrough:
    description "全体スキップ通し走行（ランダム選択肢）"

    # ランダムシード固定（再現性確保）
    $ test_fix_random_seed(42)

    # ゲーム全体を高速スキップ
    # 選択肢はランダムに自動選択される
    click until _game_ended


# === スモークテスト: 別シードで2回目 ===
testcase smoke_random_playthrough_seed2:
    description "全体スキップ通し走行（シード違い）"

    $ test_fix_random_seed(123)

    click until _game_ended


# === スモークテスト: さらに別シード ===
testcase smoke_random_playthrough_seed3:
    description "全体スキップ通し走行（シード違い2）"

    $ test_fix_random_seed(999)

    click until _game_ended
```

### 解説

- `click until _game_ended` は、`_game_ended` が `True` になるまでクリックし続ける。選択肢が出たらランダムに選択される。
- 異なるシードで3回実行することで、ランダム分岐のカバレッジを広げる。
- 嘘パズル・QTEはタスク2のテストモード対応により自動スキップされる。
- このテストが通れば「どのルートに入ってもクラッシュしない」ことが確認できる。

---

## タスク5: システム検証テスト（Layer 2）

### ファイル: `game/tests/system_test.rpy`（新規作成）

```renpy
# game/tests/system_test.rpy
# Layer 2: パラメータ・フラグの整合性を検証するテスト


# === パラメータ境界値テスト ===
# ゲーム途中でパラメータが範囲外になっていないことを確認
testcase param_bounds_midgame:
    description "ゲーム中盤でのパラメータ境界値チェック"

    $ test_fix_random_seed(42)

    # 15日目まで進める
    click until eval (game_date["day"] >= 15)

    # パラメータ範囲チェック
    $ _bounds_error = test_assert_param_bounds()
    assert eval (_bounds_error == ""), timeout 1.0


testcase param_bounds_endgame:
    description "ゲーム終盤でのパラメータ境界値チェック"

    $ test_fix_random_seed(42)

    # 25日目まで進める
    click until eval (game_date["day"] >= 25)

    # パラメータ範囲チェック
    $ _bounds_error = test_assert_param_bounds()
    assert eval (_bounds_error == ""), timeout 1.0


# === daily_flags リセットテスト ===
# advance_day() 後に daily_flags が正しくリセットされるか確認
testcase daily_flags_reset:
    description "日付更新後のdaily_flagsリセット確認"

    $ test_fix_random_seed(42)

    # 5日目の朝まで進める（朝 = advance_day直後）
    click until eval (game_date["day"] >= 5 and game_date["time"] == "morning")

    # daily_flags がリセットされているか確認
    $ _reset_error = test_assert_daily_flags_reset()
    assert eval (_reset_error == ""), timeout 1.0


# === 約束管理システム整合性テスト ===
# 約束の重複や過去の約束の残存がないか確認
testcase appointment_integrity_midgame:
    description "ゲーム中盤での約束管理整合性チェック"

    $ test_fix_random_seed(42)

    # 15日目まで進める
    click until eval (game_date["day"] >= 15)

    # 約束の整合性チェック
    $ _appt_error = test_assert_appointment_integrity()
    assert eval (_appt_error == ""), timeout 1.0


testcase appointment_integrity_endgame:
    description "ゲーム終盤での約束管理整合性チェック"

    $ test_fix_random_seed(42)

    # 25日目まで進める
    click until eval (game_date["day"] >= 25)

    $ _appt_error = test_assert_appointment_integrity()
    assert eval (_appt_error == ""), timeout 1.0


# === エンディング到達テスト ===
# ゲームがいずれかのエンディングに到達し、_ending_type がセットされることを確認
testcase ending_type_is_set:
    description "エンディング到達時に_ending_typeがセットされる"

    $ test_fix_random_seed(42)

    click until _game_ended

    # _ending_type が空でないことを確認
    assert eval (_ending_type != ""), timeout 1.0

    # _ending_type が有効な値であることを確認
    assert eval (_ending_type in ["good", "gray", "normal", "bad_bankruptcy"]), timeout 1.0
```

### 解説

- 各テストケースは独立して実行される（Ren'Pyはテストケースごとにゲームをリスタートする）。
- `click until eval (条件)` で条件が満たされるまでクリックし続け、その時点でassertを実行する。
- ヘルパー関数の戻り値を一時変数に入れ、`assert eval` で確認するパターンを統一している。
- `timeout 1.0` はassertの待機時間。条件が即座に判定できるはずなので短めに設定。

---

## テスト実行方法

### Ren'Py ランチャーから

1. Ren'Py ランチャーを開く
2. `himo_simulator` プロジェクトを選択
3. 「テストケースの実行」ボタンをクリック

### コマンドラインから

```bash
# 全テスト実行（globalスイート）
renpy.sh /path/to/himo_simulator test

# 特定のテストケースのみ実行
renpy.sh /path/to/himo_simulator test smoke_random_playthrough
renpy.sh /path/to/himo_simulator test param_bounds_midgame
```

---

## 実装時の注意事項

### 1. 変数名・ラベル名の読み替え

この指示書のコードは設計ドキュメントに基づいている。
実装で変数名やラベル名が異なる場合は適宜読み替えること。
特に以下は要確認:

- `appointments` 辞書の構造とキー名
- `kana_flags` / `kana` 辞書の構造
- `daily_flags` に含まれるキーの一覧
- 嘘パズル・QTEのラベル名と結果変数名
- エンディングのラベル名（`ending_balance` 等）

### 2. `renpy.is_in_test()` の使用箇所

本編コードへの `renpy.is_in_test()` 分岐は**タスク2の2箇所のみ**に限定する。
他の場所には絶対に入れない。テスト時の制御はシード固定とヘルパー関数で行う。

### 3. テストで検出できないこと

以下は自動テストの対象外。引き続き目視テストプレイで確認する:

- セリフの自然さ・キャラクターの一貫性
- 演出のタイミング・雰囲気
- UIの見た目・レイアウト
- BGM・SEの適切さ
- ゲームバランス（お金の貯まりやすさ等）

### 4. テスト追加のタイミング

今後バグが見つかったら、修正と同時に該当バグを検出するテストを `system_test.rpy` に追加する。
これにより回帰テストが蓄積され、同じバグの再発を防げる。

---

## テスト確認項目

### タスク1: _ending_type
- [ ] `_ending_type` が `variables.rpy` に定義されている
- [ ] `_game_ended` が `variables.rpy` に定義されている
- [ ] 全エンディングラベルの冒頭で `_ending_type` がセットされる
- [ ] 全エンディングラベルの末尾で `_game_ended = True` がセットされる

### タスク2: ミニゲームのテストモード
- [ ] 嘘パズルのラベル冒頭に `renpy.is_in_test()` 分岐がある
- [ ] QTEのラベル冒頭に `renpy.is_in_test()` 分岐がある
- [ ] 通常プレイ時にミニゲームが正常動作する（テスト分岐が影響しない）

### タスク3: ヘルパー
- [ ] `test_helpers.rpy` が `game/` 直下に配置されている
- [ ] `test_assert_param_bounds()` が現在の変数構造に合っている
- [ ] `test_assert_daily_flags_reset()` が現在のdaily_flags全キーをカバーしている
- [ ] `test_assert_appointment_integrity()` が現在のappointments構造に合っている

### タスク4: スモークテスト
- [ ] 3つのスモークテストがクラッシュなしで完走する
- [ ] 嘘パズル・QTEが含まれるルートを通ってもクラッシュしない

### タスク5: システム検証テスト
- [ ] パラメータ境界値テストがパスする
- [ ] daily_flagsリセットテストがパスする
- [ ] 約束管理整合性テストがパスする
- [ ] エンディング到達テストがパスする

---

## 将来の拡張（Layer 3: シナリオルートテスト）

ゲーム内容が安定した後に以下を追加予定。今回は実装しない。

- 4種エンディングへの明示的な到達テスト（特定の選択肢を辿る）
- 美咲イベントチェーン M01→M05 の順序確認
- カナイベントチェーン K01→K05 の順序確認
- ダブルブッキング3分岐の全パス確認

Layer 3は選択肢の文言やメニュー構造に依存するため、頻繁にメンテナンスが必要になる。
ゲームのテキストとイベント構造がフリーズしてから着手する。

---

*autotest_implementation_v1.md - 2026年3月14日作成*
