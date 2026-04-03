# CLAUDE.md

このファイルは、このリポジトリで作業する Claude Code (claude.ai/code) へのガイダンスを提供します。

## GitHubリポジトリURL
https://github.com/RS-PON/himo_simulator

## 言語設定

**すべての回答・メッセージは日本語で出力すること。**

## プロジェクト概要

**ヒモ男シミュレーター** — Ren'Py 製の大人向けコメディ恋愛シム / リソース管理ゲーム（R-17）。プレイヤーは「ヒモ男」としてヒロイン・佐藤美咲と7日間の関係を管理しながら、お金・信頼・依存度のバランスを取る。

- エンジン: **Ren'Py 8.5.2**
- 解像度: 1920×1080
- テキスト言語: 日本語（フォント: `SourceHanSansLite.ttf`）
- 配信プラットフォーム: PC（Steam 予定）

## ゲームの起動方法

npm / make などのビルドコマンドは存在しない。**Ren'Py SDK ランチャー**から起動する:

1. Ren'Py ランチャーを開く
2. プロジェクト `himo_simulator` を選択
3. 「Launch Project」で起動、「Force Recompile」で `.rpyc` を再ビルド

開発中はゲーム内で **Shift+R** を押すと `.rpy` ファイルをリロードできる。

## 現在の実装状況

**Phase 4 Step 2 v1.4 修正済み。** 30日間のゲームループ、美咲・カナ両ヒロインのイベント、5種エンディング、経済圏システム（対面交渉・泊まり・ご機嫌取りQTE）、自動テスト基盤が稼働中。

### ファイル構成（`game/` 以下）

```
game/
  script.rpy            # メインループ・行動選択メニュー
  screens.rpy           # UI スクリーン定義
  options.rpy           # ゲーム設定
  gui.rpy               # UI スタイル・フォント・カラー
  test_helpers.rpy      # テスト用ヘルパー関数

data/
  characters.rpy        # キャラクター定義
  constants.rpy         # 閾値・ステージ定義・イベントID
  variables.rpy         # 全ゲーム変数の default 宣言

systems/
  time_system.rpy       # 日時進行・パラメータ減衰ロジック
  parameter_system.rpy  # パラメータ更新・通知処理
  sns_system.rpy        # SNS/LINE システム
  dialogue_log.rpy      # セリフログ（テストプレイ用）
  debug_log.rpy         # デバッグログ出力
  lie_puzzle.rpy        # 嘘パズルミニゲーム
  evidence_qte.rpy      # 証拠QTEミニゲーム
  gokiragen_qte.rpy     # ご機嫌取りQTEミニゲーム

events/
  intro.rpy             # オープニング
  tutorial.rpy          # チュートリアル
  daily_events.rpy      # 時間帯ごとの日常イベント
  misaki_events.rpy     # 美咲イベント・リアクション
  kana_events.rpy       # カナイベント
  midgame_events.rpy    # 中盤イベント（疑念・修羅場等）
  date_misaki_places.rpy # 美咲デート場所
  date_kana_places.rpy  # カナデート場所
  date_incidents.rpy    # デート中のハプニング
  endings.rpy           # 5種エンディング＋ヒモ適性診断

tests/
  smoke_test.rpy        # Layer 1: 通し走行テスト（3シード）
  system_test.rpy       # Layer 2: パラメータ・フラグ整合性（6テスト）
```

### 設計資料（`docs/` 以下）
- `game_design_document2_6.md` — ゲーム設計全体仕様（最新）
- `phase_goals.md` — フェーズ別目標
- `phase4_step1_design.md` — Phase 4 Step 1 設計
- `character_economy_and_energy_design.md` — エコノミー・エナジー設計
- `current_state.md` — **コードベース状態スナップショット**（後述）

## コアゲームシステム

### 時間システム
- 30日間サイクル。1日 = 朝 → 午後 → 夜 の3ターン
- 変数: `game_date["day"]`（1〜30）、`game_date["time"]`（morning / afternoon / night）
- 各ターン: パラメータが減衰 → プレイヤーが行動を選択

### パラメータ

**可視（プレイヤーに表示）:**
- `money` — 初期値 3,458 円。月末に家賃 50,000 円が発生
- `trust` — 美咲の信頼度（0〜100）
- `dependence` — 美咲の依存度（0〜100）

**隠し:**
- `stamina`（0〜100）、`cleanliness`（0〜100）、`charm`（0〜100）
- `suspicion_count` — 金銭要求の繰り返しを追跡。5〜6日目の疑念イベントを発火させる

### 関係ステージ
```
STAGE_ACQUAINTANCE (1) → STAGE_FRIEND (2) → STAGE_CLOSE (3) → STAGE_DATING (4)
```
信頼度・依存度の閾値到達で昇格する。

### ヒモ適性トラッキング（隠し）
エンディング時の診断（例: 「筋金入りのヒモ」）に使用:
`easy_choices`、`money_requests`、`lies_told`、`honest_moments`、`work_avoided`、`showed_concern`

### イベントフラグ
フラグは用途別に4つの辞書で管理される:
- `flags` — 永続フラグ（40個超。告白・中盤イベント・泊まり翌朝など）
- `location_flags` — 場所関連（`staying_at_misaki`, `staying_at_kana`, `misaki_room_unlocked`）
- `daily_flags` — 1日ごとにリセット（16個。`ate_today`, `date_location` など）
- `appointments` — 約束日管理（`"misaki"`: int/None, `"kana"`: int/None）

全キーの一覧は `docs/current_state.md` セクション3を参照。

### エンディング
信頼度・依存度のバランス、誠実さ vs 欺瞞の選択、ヒモ適性診断の組み合わせで5種類のエンディングが決定される:
- `good` — バランスエンド（理想的な関係）
- `gray` — ヒモウエンド（依存関係の維持）
- `normal` — 不安定エンド（中途半端な結末）
- `bad_bankruptcy` — 破産エンド（お金が尽きた）
- `demo` — デモ版エンド（カナルート到達時）

## Ren'Py の規約

- ソースファイルは `.rpy`。コンパイル済みバイトコード `.rpyc` / `.rpymc` は自動生成されるため編集しない
- ゲームのエントリーポイントは `label start:`
- 全ゲーム変数は `variables.rpy` に `default` 文で宣言する
- スクリーンは `screens.rpy` に定義。`gui.rpy` の値は Ren'Py GUI エディタ経由か慎重に手編集すること
- インゲームのセリフ・UI文字列はすべて日本語

### ⚠️ pickle制約: `import random` 禁止

**Ren'Pyの `.rpy` ファイルでは `import random` を絶対に使わないこと。** 代わりに `renpy.random` を使う。

- Ren'Pyはセーブ/クイックセーブ時にゲーム状態をpickleでシリアライズする
- `import random` を使うと、`random` モジュールへの参照がストアに残り `Could not pickle <module 'random'>` エラーになる
- これは `init python` 内の関数定義でも、label内の `python:` ブロックでも同様に発生する
- **正しい書き方:**
  ```python
  # OK: renpy.random を使う（pickle安全、常に利用可能）
  renpy.random.random()
  renpy.random.choice(items)
  renpy.random.shuffle(items)
  renpy.random.randint(a, b)
  ```
- **禁止:**
  ```python
  # NG: pickle エラーの原因になる
  import random
  random.random()
  ```
- この制約は `random` に限らず、すべての標準ライブラリモジュールの `import` に適用される可能性がある。Ren'Py組み込みの代替があればそちらを優先すること

## 自動テスト

### テストの実行方法
1. Ren'Py ランチャーで「Force Recompile」
2. 「Run Testcases」をクリック
3. 全9テスト完走まで約10分待つ（`Status: PASSED` で成功）

### テストファイル構成
- `game/test_helpers.rpy` — テスト用ヘルパー関数
- `game/tests/smoke_test.rpy` — Layer 1: クラッシュせず完走するか（3シード）
- `game/tests/system_test.rpy` — Layer 2: パラメータ・フラグの整合性（6テスト）

### テスト運用ルール
- **バグ修正時**: 修正と同時に `system_test.rpy` にそのバグを検出するテストケースを追加する。回帰テストを自然に育てる
- **素材追加時**: 立ち絵・背景の `show` 文追加後にスモークテストを実行し、画像ファイル不在エラーを検出する
- **コード変更後**: 変更の影響範囲が広い場合は全テストを実行してリグレッションがないことを確認する

### Ren'Py testcase構文の注意点
- Python式には `eval ()` ラッパーが必要: `click until eval (condition)`
- `assert` のtimeoutの前にカンマ不可: `assert eval (...) timeout 1.0`
- `click`（引数なし）はランダム座標クリック。メニュー選択には不十分
- テスト間でゲームは自動リスタートされない。各テストは `click "スタート"` で開始し、メインメニューまで戻って終了する
- グローバルタイムアウト `_test.timeout` のデフォルトは5秒。長時間テストには `$ _test.timeout = 600` が必要
- 本編コードへの `renpy.is_in_test()` 分岐は計6箇所（`lie_puzzle.rpy`, `evidence_qte.rpy`, `screens.rpy` の choice/status_detail, `gokiragen_qte.rpy` の通常版/疑念版）

## Web Claude との連携

修正指示書は Web Claude（claude.ai）で作成し、Claude Code が実装する運用を取っている。

### `docs/current_state.md`（状態スナップショット）

Web Claude がコードベースを直接読めない問題を補うために、**ラベル名・フラグ名・変数構造の正規一覧**を `docs/current_state.md` に保持している。

- **更新タイミング**: Claude Code で大きな変更を加えた後（ユーザーが「スナップショット更新して」と指示）
- **参照タイミング**: Web Claude で修正指示書を書く前に、プロジェクトナレッジまたはチャットに添付する
- **編集権限**: Claude Code のみ。Web Claude 側では編集しない

### 修正指示書のベストプラクティス
- ラベル名・変数名は `current_state.md` を参照し、正確な名前を使う
- コード例を書くより**方針**（何を・なぜ・どこで）を書く方がズレにくい
- 関連箇所のコードを貼る場合は20行程度で十分
