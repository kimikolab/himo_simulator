# ヒモ男シミュレーター 自動テスト実装計画

## 概要

Ren'Py 組み込みの `testcase` 機能を活用し、ゲームの品質保証を自動化する。
手動での全ルート確認が現実的でない規模（30日 × 3ターン × 複数選択肢）のため、
自動テストによるクラッシュ検出・回帰テストの導入価値は高い。

### 参考ドキュメント
- Ren'Py テストケース公式: https://ja.renpy.org/doc/html/testcases.html

---

## 現在のプロジェクト状況

| 項目 | 内容 |
|------|------|
| エンジン | Ren'Py 8.5.2 |
| ゲーム期間 | 30日（1日 = 朝・昼・夜の3ターン = 計90ターン） |
| ヒロイン | 美咲（メイン）、カナ（サブ） |
| エンディング | 4種（GOOD / GRAY / NORMAL / BAD:破産） |
| 主要システム | 時間管理、パラメータ減衰、関係ステージ、嘘パズル、QTE、SNS通知 |
| テスト用ファイル | なし（未導入） |

---

## テスト戦略

### レイヤー構成

```
Layer 3: シナリオルートテスト（特定ルートを選択肢で辿る）
Layer 2: システム検証テスト（パラメータ・フラグの整合性assert）
Layer 1: スモークテスト（クラッシュしないことの確認）  ← まずここから
```

### ファイル配置

```
game/
  tests/
    smoke_test.rpy          # Layer 1: スモークテスト
    route_tests.rpy          # Layer 3: 主要ルートテスト
  test_helpers.rpy           # テスト用ヘルパー（シード固定等）
```

> Ren'Py の `testcase` は `.rpy` ファイルのトップレベルに書くと自動的に `global` スイートに追加される。
> `game/tests/` 配下に配置すれば本編コードと分離できる。

---

## Layer 1: スモークテスト（最優先）

### 目的
- ゲームが `label start` から最後まで**クラッシュせずに完走する**ことを確認
- 新しいイベント追加後の回帰チェックに使用

### 実装内容

```renpy
# game/tests/smoke_test.rpy

testcase smoke_skip_through:
    description "全体スキップ通し走行"
    # fast skip でゲーム全体を高速走行
    # 選択肢はランダムに自動選択される
    skip fast
    until renpy.get_return_stack() == []
```

### 期待される効果
- 未定義変数エラーの即時検出
- `call expression` で呼ばれる動的ラベルの存在確認
- `_pending_events` キュー経由のイベントチェーン全体の動作確認

### 注意点
- `renpy.random` によるランダム分岐があるため、1回の実行で全パスは通らない
- 複数回実行するか、Layer 3 で主要パスを明示的にテストする

---

## Layer 2: システム検証テスト

### 目的
- ゲーム進行中のパラメータ・フラグの整合性を検証
- 過去に発生したバグの再発防止（回帰テスト）

### 2-1. テスト用ヘルパー

```renpy
# game/test_helpers.rpy

init python:
    def setup_test_state(**overrides):
        """テスト用に変数を任意の状態にセットする"""
        if not renpy.is_in_test():
            return

        # ランダムシード固定（再現性確保）
        renpy.random.seed(42)

        # overrides で指定された変数を上書き
        for key, value in overrides.items():
            if key == "day":
                game_date["day"] = value
            elif key == "money":
                player["money"] = value
            elif key == "trust":
                misaki["trust"] = value
            elif key == "dependence":
                misaki["dependence"] = value
            # ... 必要に応じて追加
```

### 2-2. パラメータ境界値テスト

```renpy
testcase param_bounds:
    description "パラメータが範囲外にならないことを確認"
    # ゲーム中盤まで進める
    skip fast
    until game_date["day"] >= 15

    # 境界チェック
    assert player["stamina"] >= 0
    assert player["stamina"] <= 100
    assert player["cleanliness"] >= 0
    assert player["cleanliness"] <= 100
    assert misaki["trust"] >= 0
    assert misaki["trust"] <= 100
    assert misaki["dependence"] >= 0
    assert misaki["dependence"] <= 100
```

### 2-3. 回帰テスト（過去バグ対応）

以下は v1.4 で修正された既知バグに対応するテスト案：

| バグ | テスト内容 |
|------|-----------|
| イベント①がターンを消費する | `check_midgame_events()` が `"notify"` を返した時、通常メニューが表示されること |
| カナとの約束後にドタキャンされる | `kana_tonight_source == "player"` の時、`kana_shows_up` が `True` であること |
| 美咲LINE後にお金要求できる | `last_contact == 1`（LINEのみ）の時、お金要求メニューが出ないこと |

> **制約**: Ren'Py testcase 内では Python 関数の直接単体テストはできない。
> 回帰テストは「特定の状態を作り → 特定の選択をし → assert で結果確認」という
> インテグレーションテスト形式になる。

---

## Layer 3: シナリオルートテスト

### 目的
- 4種のエンディングに確実に到達できることを確認
- 主要イベントチェーン（美咲イベント M01〜M05、カナイベント K01〜K05）の動作確認

### 3-1. エンディング到達テスト

```renpy
# game/tests/route_tests.rpy

testcase ending_good:
    description "GOOD END 到達テスト"
    # チュートリアルをスキップ
    skip fast
    until flags["tutorial_done"]

    # 信頼を上げる行動を繰り返す
    # （具体的な選択肢クリックは実装時に調整）
    repeat 80:
        if renpy.current_screen() and "menu" in str(renpy.current_screen()):
            # 美咲を気遣う選択肢を選ぶ
            click "美咲に連絡する"
        advance

    # GOOD END条件: 正直 & 頻繁に会う & 依存度低 & 気遣い多
    until flags["game_ended"]
    # assert でエンディング種別を確認（要: エンディング種別変数の追加）

testcase ending_bankruptcy:
    description "BAD END（破産）到達テスト"
    # お金を使い切る行動を繰り返す
    skip fast
    until _game_over == "bankruptcy" or flags["game_ended"]
```

### 3-2. 主要イベントチェーンテスト

```renpy
testcase misaki_event_chain:
    description "美咲イベント M01→M05 チェーン確認"
    skip fast
    until misaki_events["M02_unlocked"]

    # M02: 終電後の電話
    # 夜まで進めて選択
    advance
    until game_date["time"] == "night"
    click "美咲と電話する"
    advance
    until misaki_events["M02_done"]

    # 以降 M03, M05 も同様に...
```

---

## テスト実行方法

### Ren'Py ランチャーから
1. ランチャーを開く
2. プロジェクト `himo_simulator` を選択
3. 「Run Testcases」ボタンをクリック（グローバルスイートに1つ以上のテストがある場合に表示される）

### コマンドラインから
```bash
# Ren'Py SDK のパスに応じて調整
renpy.sh /path/to/himo_simulator --test
```

---

## ランダム性への対処

このゲームは `renpy.random` を多用しており、テスト結果が実行ごとに変わる。

### 対策

1. **シード固定**: `test_helpers.rpy` で `renpy.random.seed(42)` を設定
2. **テスト分岐**: `renpy.is_in_test()` を使い、テスト時のみ確定的な動作にする
3. **複数回実行**: スモークテストは異なるシードで複数回実行し、カバレッジを上げる

```renpy
# 例: テスト時はドタキャンを無効化
python:
    if renpy.is_in_test():
        kana_shows_up = True
    else:
        kana_shows_up = renpy.random.random() < success_rate
```

> **注意**: `renpy.is_in_test()` 分岐を本編コードに入れすぎると、
> 「テストでは通るが本番では通らない」状態になるリスクがある。
> 最小限に留め、基本はシード固定で対応する。

---

## 実装ロードマップ

### Phase A: スモークテスト導入（工数: 小）

| # | タスク | 詳細 |
|---|--------|------|
| A-1 | `game/tests/smoke_test.rpy` 作成 | `skip fast` による通し走行テスト |
| A-2 | `game/test_helpers.rpy` 作成 | シード固定・テスト判定ヘルパー |
| A-3 | 動作確認 | ランチャーの「Run Testcases」で実行、クラッシュが無いことを確認 |

### Phase B: 回帰テスト追加（工数: 中）

| # | タスク | 詳細 |
|---|--------|------|
| B-1 | パラメータ境界テスト | stamina/cleanliness/trust/dependence の範囲チェック |
| B-2 | 既知バグ回帰テスト | v1.4 修正分（ターン消費・ドタキャン・お金要求）の再発防止 |
| B-3 | daily_flags リセットテスト | `advance_day()` 後に全 daily_flags がリセットされることを確認 |

### Phase C: ルートテスト追加（工数: 大）

| # | タスク | 詳細 |
|---|--------|------|
| C-1 | エンディング到達テスト | 4種エンディングへの到達確認 |
| C-2 | 美咲イベントチェーン | M01→M05 の順序・条件テスト |
| C-3 | カナイベントチェーン | K01→K05 の順序・条件テスト |
| C-4 | ダブルブッキング分岐 | 3択（美咲優先/カナ優先/両方すっぽかす）の全分岐確認 |

---

## 技術的な制約と限界

### Ren'Py testcase でできないこと

| 制約 | 説明 | 代替手段 |
|------|------|----------|
| Python関数の単体テスト | `testcase` ブロック内はテストステートメントのみ | `assert` + ゲーム内状態チェックで代替 |
| 高速CI実行 | ゲーム描画を伴うため遅い | スモークテストの `skip fast` で最速化 |
| 網羅的カバレッジ | 30日×3ターン×N選択肢の組合せ爆発 | 主要ルートに絞り、スモークテストで補完 |
| 嘘パズル・QTE のテスト | リアルタイム入力が必要 | `renpy.is_in_test()` で自動パス or テスト専用の入力シミュレーション |

### 嘘パズル・QTE への対応方針

嘘パズル（`lie_puzzle.rpy`）と証拠QTE（`evidence_qte.rpy`）はリアルタイム入力が必要なため、
テスト時は以下のいずれかで対応する：

1. **テスト時自動パス**: `renpy.is_in_test()` で成功/失敗を直接セット
2. **タイマー無効化**: テスト時のみ制限時間を無制限に設定
3. **テスト専用入力**: `keysym` / `click` コマンドでボタンを直接操作

推奨は **方法1**（最小の本編コード変更で実現可能）。

---

## エンディング種別の判定について（提案）

現在、エンディング種別は各ラベル内でのみ判定されており、テストから結果を確認しにくい。
テスト用に以下の変数追加を推奨：

```renpy
# variables.rpy に追加
default _ending_type = ""  # "good" / "gray" / "normal" / "bad_bankruptcy"
```

各エンディングラベルの冒頭で設定すれば、テストから `assert _ending_type == "good"` で確認可能。

---

## まとめ

| 項目 | 内容 |
|------|------|
| **最優先** | Phase A（スモークテスト） — 工数最小で最大の効果 |
| **推奨** | Phase B（回帰テスト） — 過去バグの再発防止 |
| **将来** | Phase C（ルートテスト） — ゲーム内容が安定してから |
| **導入コスト** | `.rpy` ファイル2〜3個追加のみ。既存コードの変更は最小限 |
| **実行方法** | Ren'Py ランチャーの「Run Testcases」ボタン |
