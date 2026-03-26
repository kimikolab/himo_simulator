# ヒモ男シミュレーター セリフログ実装指示書

最終更新日: 2026年3月26日

---

## 概要

テストプレイ時のセリフ・テキストの流れをレビューするためのログ出力システムを実装する。
既存のパラメータデバッグログ（`debug_log.rpy` → `debug_log_{timestamp}.txt`）とは**別ファイル**で出力し、必要に応じて個別にレビューできるようにする。

両ファイルには共通のターンヘッダーを入れ、突き合わせが必要な場合は対応箇所をすぐ探せるようにする。

---

## ファイル構成

### 新規作成

| ファイル | 役割 |
|---------|------|
| `game/systems/dialogue_log.rpy` | セリフログのフック・蓄積・出力処理 |

### 既存ファイルの修正

| ファイル | 修正内容 |
|---------|---------|
| `game/systems/debug_log.rpy` | ターンヘッダー関数の共通化、セリフログの書き出し呼び出し追加 |
| `game/data/characters.rpy` | 全Characterオブジェクトに `callback` パラメータを追加 |
| `game/data/variables.rpy` | セリフログ用のリスト変数を追加 |
| `game/events/endings.rpy` | エンディング到達時にセリフログを書き出す呼び出しを追加 |

---

## 出力フォーマット

### ファイル名

```
dialogue_log_{YYYYMMDD_HHMMSS}.txt
```

既存パラメータログの `debug_log_{YYYYMMDD_HHMMSS}.txt` と同じタイムスタンプ命名規則。

### ターンヘッダー（パラメータログと共通）

```
========== [Day 3 / afternoon] ==========
```

パラメータログ側にも同じフォーマットのヘッダーを挿入する（後述の「既存ログとの連携」参照）。

### セリフ行のフォーマット

```
[話者名] セリフテキスト
```

話者別の表記ルール:

| 種類 | 表記 | 例 |
|------|------|-----|
| ヒモ太郎のセリフ | `[ヒモ太郎]` | `[ヒモ太郎] まあいっか` |
| 美咲のセリフ | `[美咲]` | `[美咲] 私のこと...利用してる？` |
| カナのセリフ | `[カナ]` | `[カナ] 暇〜。ヒモ太郎も暇？` |
| ナレーション | `[---]` | `[---] 美咲と会った。` |
| メニュー選択 | `[>>> CHOICE]` | `[>>> CHOICE] 正直に認める` |
| システム通知 | `[NOTIFY]` | `[NOTIFY] 街に出られるようになった` |

### 出力例

```
=== ヒモ男シミュレーター セリフログ ===
出力日時: 20260326_143025

========== [Day 1 / morning] ==========
[---] 俺の名前はヒモ太郎。25歳。
[---] 高校卒業後、フリーター生活を満喫中。
[---] ...だったんだけど。
[---] 先週、バイトをクビになった。
[ヒモ太郎] まあ、あのバイト飽きてたし、ちょうど良かったかも
[---] スマホの残高通知。
[---] 残高: 3,458円
[ヒモ太郎] ...おお、意外と残ってるじゃん

========== [Day 1 / afternoon] ==========
[---] ――昼、14時――
[ヒモ太郎] ランチタイムも終わりか
[>>> CHOICE] 美咲に連絡する
[---] 美咲にLINEを送った...
[---] しばらくして返信が来た。
[美咲] どうしたの？
[>>> CHOICE] 雑談する
[---] 他愛もない話をした。
[ヒモ太郎] まあ、気楽に生きてるよ

========== [Day 5 / night] ==========
[---] ――5日目――
[---] 美咲と会っている時、ふと美咲が真面目な顔になった。
[美咲] ...ねえ、ヒモ太郎
[ヒモ太郎] ん？
[美咲] 正直に聞いていい？
[---] ...なんだろう、いつもと雰囲気が違う。
[美咲] 私のこと...利用してる？
[ヒモ太郎] え
[---] 心臓がドキッとした。
[>>> CHOICE] 正直に認める
[ヒモ太郎] ...正直に言うと、最初はそうだった
[美咲] ...やっぱり
[---] 美咲の顔が、少し寂しそうになる。
```

---

## 実装詳細

### 1. 変数定義（`variables.rpy`）

```python
# セリフログ用リスト
default dialogue_log_entries = []
```

### 2. セリフログ本体（`dialogue_log.rpy` 新規作成）

```python
# dialogue_log.rpy
# テストプレイ用のセリフ・テキスト全文ログ
# DEBUG_MODE = True のときのみ機能する

init python:

    def log_dialogue(speaker, text):
        """セリフをログに記録する"""
        if not DEBUG_MODE:
            return

        # speaker が None の場合はナレーション
        if speaker is None or speaker == "":
            tag = "---"
        else:
            tag = speaker

        entry = {
            "day": game_date["day"],
            "time": game_date["time"],
            "tag": tag,
            "text": text,
        }
        dialogue_log_entries.append(entry)


    def log_choice(choice_text):
        """メニュー選択をログに記録する"""
        if not DEBUG_MODE:
            return

        entry = {
            "day": game_date["day"],
            "time": game_date["time"],
            "tag": ">>> CHOICE",
            "text": choice_text,
        }
        dialogue_log_entries.append(entry)


    def log_notify(text):
        """システム通知をログに記録する"""
        if not DEBUG_MODE:
            return

        entry = {
            "day": game_date["day"],
            "time": game_date["time"],
            "tag": "NOTIFY",
            "text": text,
        }
        dialogue_log_entries.append(entry)


    def _dialogue_callback(event, interact=True, **kwargs):
        """Characterオブジェクトのcallback。セリフ表示開始時にログ記録する。

        Ren'Py の Character callback は以下のタイミングで呼ばれる:
        - event="begin": セリフ表示開始
        - event="show":  テキスト表示
        - event="slow_done": テキスト表示完了
        - event="end":   セリフ表示終了

        "begin" のタイミングでセリフテキストを記録する。
        ただし、Character callback にはセリフテキスト(what)が引数として渡されない。
        そのため、セリフテキストは別の方法で取得する必要がある。
        → 下記「セリフテキスト取得方法」を参照。
        """
        pass  # 実装は「セリフテキスト取得方法」の選定後に確定


    def export_dialogue_log():
        """セリフログをファイルに書き出す"""
        if not DEBUG_MODE:
            return
        if not dialogue_log_entries:
            return

        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "dialogue_log_" + timestamp + ".txt"

        lines = []
        lines.append("=== ヒモ男シミュレーター セリフログ ===")
        lines.append("出力日時: " + timestamp)
        lines.append("")

        current_day = None
        current_time = None

        for e in dialogue_log_entries:
            # ターンが変わったらヘッダーを挿入
            if e["day"] != current_day or e["time"] != current_time:
                current_day = e["day"]
                current_time = e["time"]
                lines.append("")
                lines.append("========== [Day " + str(current_day) + " / " + current_time + "] ==========")

            lines.append("[" + e["tag"] + "] " + e["text"])

        lines.append("")
        lines.append("=== ログ終了 ===")

        content = "\n".join(lines)

        try:
            log_path = renpy.config.basedir + "/" + filename
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(content)
            renpy.notify("セリフログを出力しました: " + filename)
        except Exception as ex:
            renpy.notify("セリフログ出力エラー: " + str(ex))
```

### 3. セリフテキスト取得方法（重要）

Ren'Py の `Character` の `callback` にはセリフテキスト（`what`）が直接渡されない。
以下のアプローチから**動作するものを選んで実装する**こと。優先順位順に記載。

#### アプローチA: `config.all_character_callbacks`（推奨・要動作確認）

Ren'Py 8.x では `config.all_character_callbacks` が利用可能な場合がある。
このコールバックのシグネチャと引数を確認し、セリフテキストが取得できるか検証する。

```python
init python:
    # 動作確認: config.all_character_callbacks が存在するか
    # 存在する場合、コールバックの引数にwhoとwhatが含まれるか
    pass
```

#### アプローチB: Character の `screen` を経由（代替案1）

Character が使う say screen をカスタマイズし、セリフ表示時にグローバル変数にテキストを保存する。

```python
init python:
    _last_say_who = None
    _last_say_what = None

# say screen をカスタマイズして who/what をキャプチャ
screen say(who, what, **kwargs):
    $ _last_say_who = who
    $ _last_say_what = what
    # ... 既存の say screen の内容 ...
```

Character の `callback` で `event="begin"` 時に `_last_say_who` / `_last_say_what` を読み取ってログに記録。

**注意**: say screen の実行タイミングと callback のタイミングの順序を確認すること。

#### アプローチC: `config.history_callbacks`（代替案2）

Ren'Pyのセリフ履歴システムを利用する。`_history_list` に HistoryEntry が追加されるたびにコールバックが呼ばれる。

```python
init python:
    def _on_history_entry(h):
        """セリフ履歴にエントリが追加されたときに呼ばれる"""
        # h.who = 話者名（文字列 or None）
        # h.what = セリフテキスト
        log_dialogue(h.who, h.what)

    config.history_callbacks = [_on_history_entry]
```

**注意**: `config.history_callbacks` が Ren'Py 8.5.2 で利用可能か確認すること。`config.history_length` が 0 になっていないこと（0だと履歴が無効化される）。

#### アプローチD: Character定義にラッパー関数（代替案3・最も確実）

Character オブジェクトを直接使わず、セリフ出力をラッパー関数経由にする方法。
既存コードの変更量が最も多いが、動作は最も確実。

```python
init python:
    def say_with_log(character, text, **kwargs):
        """セリフをログに記録してから表示する"""
        if character is not None:
            speaker = character.name
        else:
            speaker = None
        log_dialogue(speaker, text)
        character(text, **kwargs)
```

**→ 既存コードの変更量が大きいため、他のアプローチが動作しない場合のみ採用する。**

#### 実装時の判断基準

1. まずアプローチAを試す（`config.all_character_callbacks` の存在確認）
2. なければアプローチCを試す（`config.history_callbacks` の動作確認）
3. どちらも使えなければアプローチBを試す（say screen 経由）
4. 最終手段としてアプローチD

**どのアプローチを採用したかをコメントに明記すること。**

### 4. メニュー選択のログ

メニュー選択はセリフとは異なるフック方法が必要。以下のいずれかで実装する。

#### 方法1: `choice` screen のカスタマイズ（推奨）

`screens.rpy` の `screen choice` を修正し、選択肢がクリックされたときに `log_choice()` を呼ぶ。

```python
screen choice(items):
    style_prefix "choice"
    vbox:
        for i in items:
            textbutton i.caption:
                action [Function(log_choice, i.caption), i.action]
```

**注意**: `Function()` と `i.action` を `[]` リストで並べることで、ログ記録後に元のアクションが実行される。この書き方が Ren'Py で動作するか確認すること。動作しない場合は以下の代替案を使う。

#### 方法2: 選択直後に手動呼び出し（代替案）

既存の `menu:` の各選択肢の直後に `$ log_choice("選択肢テキスト")` を手動追加する。
**既存コードの変更量が非常に多いため、方法1が動作しない場合のみ採用する。**

### 5. システム通知のログ

既存の `renpy.notify()` 呼び出し箇所に `log_notify()` を追加する。
主要な箇所のみで良い（全箇所ではなく、ゲームプレイに影響する通知のみ）。

対象例:
- 関係ステージの昇格通知
- 街の解放通知
- 美咲の疑念セリフ通知
- SNS通知

---

## 既存ログとの連携

### パラメータログへのターンヘッダー追加

既存の `debug_log.rpy` の `log_action()` に、ターンが変わった際にヘッダー行を挿入する処理を追加する。

```python
init python:
    _last_logged_day = None
    _last_logged_time = None

    def get_turn_header():
        """現在のターンヘッダー文字列を返す"""
        return "========== [Day " + str(game_date["day"]) + " / " + game_date["time"] + "] =========="

    # 既存の log_action を修正
    def log_action(action_name, notes=""):
        global _last_logged_day, _last_logged_time

        if not DEBUG_MODE:
            return

        # ターンが変わったらヘッダーを挿入
        if game_date["day"] != _last_logged_day or game_date["time"] != _last_logged_time:
            _last_logged_day = game_date["day"]
            _last_logged_time = game_date["time"]
            # ヘッダー行をログエントリとして追加（特別なフラグ付き）
            header_entry = {
                "is_header": True,
                "text": get_turn_header(),
            }
            debug_log_entries.append(header_entry)

        # 既存のエントリ追加処理（変更なし）
        entry = {
            "is_header": False,
            "day": game_date["day"],
            # ... 既存のフィールド ...
        }
        debug_log_entries.append(entry)
```

`export_debug_log()` 側でも `is_header` フラグを判定してヘッダー行を出力する。

---

## エンディング時の書き出し

`events/endings.rpy` の既存の `export_debug_log()` 呼び出し箇所の直後に `export_dialogue_log()` を追加。

```python
# endings.rpy のエンディングラベル内（既存の export_debug_log() の後）
$ export_dialogue_log()
```

両ファイルが同時に出力されるため、タイムスタンプがほぼ同一になり対応関係が分かりやすい。

---

## テスト確認項目

### 基本動作
- [ ] `DEBUG_MODE = True` でプレイしてエンディング到達後、`dialogue_log_{timestamp}.txt` が出力される
- [ ] `DEBUG_MODE = False` ではログが出力されない
- [ ] 出力ファイルの文字コードが UTF-8 である

### ログ内容
- [ ] ヒモ太郎のセリフが `[ヒモ太郎]` タグで記録されている
- [ ] 美咲のセリフが `[美咲]` タグで記録されている
- [ ] カナのセリフが `[カナ]` タグで記録されている（カナ登場後）
- [ ] ナレーション（話者なし）が `[---]` タグで記録されている
- [ ] メニュー選択が `[>>> CHOICE]` タグで記録されている
- [ ] ターンが変わるたびに `========== [Day N / time] ==========` ヘッダーが挿入されている

### パラメータログとの連携
- [ ] パラメータログにも同じフォーマットのターンヘッダーが挿入されている
- [ ] 両ファイルのターンヘッダーが対応している（同じターンで同じヘッダー）

### エッジケース
- [ ] `centered` テキスト（エンディングタイトル等）もログに記録されている
- [ ] Ren'Py のテキストタグ（`{size=40}` 等）がログ内で適切に扱われている（可能であれば除去、無理ならそのまま出力でOK）
- [ ] 嘘パズルや証拠QTEなどのミニゲーム中のテキストもログに含まれている
- [ ] セーブ/ロードしてもログが破損しない（pickle安全であること）

### pickle安全性
- [ ] `dialogue_log_entries` リストが pickle 可能である（辞書のリストなのでOKのはず）
- [ ] `import random` や `import datetime` がストアに残らない（`datetime` は `export_dialogue_log` 内でのみ使用）
- [ ] `export_dialogue_log` 内の `import datetime` が問題を起こす場合は `renpy.time.time()` 等で代替する

---

## 注意事項

### CLAUDE.md の pickle制約を厳守

`dialogue_log.rpy` 内で `import random` を使わないこと。`import datetime` は `export_dialogue_log()` 関数内のローカルスコープで使用しているため通常は問題ないが、万が一 pickle エラーが出た場合は以下で代替する:

```python
# datetime の代替
import os
timestamp = str(int(os.path.getmtime(renpy.config.basedir))) if False else "manual"
# → より安全な方法: renpy.config.basedir のパスからタイムスタンプを生成
```

### Ren'Pyテキストタグの扱い

ログに記録されるテキストには `{size=40}`, `{color=#fff}` 等の Ren'Py テキストタグが含まれる可能性がある。完全な除去は複雑なので、**v1ではそのまま出力してよい**。レビュー時に目視で読み飛ばせる範囲であれば問題ない。将来的に正規表現で除去する処理を追加してもよい。

### ログサイズの目安

30日間フルプレイで推定3000〜5000行程度。ファイルサイズは数百KB以内に収まる見込み。

---

## 将来の拡張（素材追加後に実装）

### 背景・キャラクターCG表示ログ

背景やキャラクタースプライトの表示・切り替えタイミングをセリフログに記録する。ビジュアル素材が実装された後（Phase 5以降）に追加。

**記録対象と表記:**

| 種類 | 表記 | 例 |
|------|------|-----|
| 背景切替（`scene`文） | `[SCENE]` | `[SCENE] bg_cafe` |
| キャラ表示（`show`文） | `[SHOW]` | `[SHOW] misaki smile` |
| キャラ非表示（`hide`文） | `[HIDE]` | `[HIDE] misaki` |
| トランジション | `[TRANS]` | `[TRANS] dissolve` |

**出力イメージ:**

```
========== [Day 3 / night] ==========
[SCENE] bg_izakaya
[SHOW] misaki tired
[---] 美咲と会った。
[美咲] お疲れ様！
[SHOW] misaki smile
[ヒモ太郎] お疲れ〜。残業？
[美咲] うん、今日も遅かった...
[SHOW] misaki sad
```

**実装方針メモ:** Ren'Pyの `config.scene_callbacks` や `config.show_callbacks`（または `show`/`scene` 文のオーバーライド）でフック可能か調査。セリフログと同じ `dialogue_log_entries` リストに追記する形で統合する。

---

*dialogue_log_implementation.md - 2026年3月26日作成*
