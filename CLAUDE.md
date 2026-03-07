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

**開発初期段階。** フレームワークは設定済みだが、ゲーム本体のロジックは未実装。

| ファイル | 状態 |
|---------|------|
| `game/options.rpy` | 完了 — ゲーム設定・バージョン・セーブディレクトリ |
| `game/gui.rpy` | 完了 — UIスタイル・フォント・カラー |
| `game/screens.rpy` | 完了 — 標準 Ren'Py スクリーン定義 |
| `game/script.rpy` | **テンプレートのみ** — 実装が必要 |

設計資料（ゲームコードではない）:
- `game_design_document2.5.md` — ゲーム設計全体仕様
- `phase1_7days_v2.5.md` — Phase 1 実装仕様（コード例あり）

## 予定ファイル構成

ゲームロジックを実装する際は、`game/` 以下を以下のモジュール構成で整理する:

```
data/
  constants.rpy       # 閾値・ステージ定義・イベントID
  variables.rpy       # 全ゲーム変数の default 宣言
systems/
  time_system.rpy     # 日時進行・パラメータ減衰ロジック
  parameter_system.rpy # パラメータ更新・通知処理
events/
  intro.rpy
  tutorial.rpy
  misaki_events.rpy   # 美咲のセリフ・リアクション
  daily_events.rpy    # 時間帯ごとの行動選択メニュー
  endings.rpy         # 3エンド＋診断
```

## コアゲームシステム

### 時間システム
- 7日間サイクル。1日 = 朝 → 午後 → 夜 の3ターン
- 変数: `current_day`（1〜7）、`current_time`（morning / afternoon / night）
- 各ターン: パラメータが減衰 → プレイヤーが行動を選択

### パラメータ

**可視（プレイヤーに表示）:**
- `money` — 初期値 3,458 円。週末に家賃 12,500 円が発生
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
```python
flags = {
    "tutorial_done", "first_money", "first_date",
    "street_unlocked",    # 4日目に解放
    "had_doubt_moment", "doubt_event_done"
}
```

### エンディング
信頼度・依存度のバランス、誠実さ vs 欺瞞の選択、ヒモ適性診断の組み合わせで3種類のエンディングが決定される。

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
