# ヒモ男シミュレーター Phase 3 修正指示書 v1.2

**前提**: Phase 3 v1.1が実装済みであること  
最終更新日: 2026年2月21日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | ナンパ解禁後に時間経過せず再ナンパできる | daily_events.rpy |
| 2 | バグ | カナ信頼度UIが未表示（再確認） | screens.rpy |
| 3 | バグ | 美咲の告白イベントが朝に発生する | misaki_events.rpy |
| 4 | バグ | お泊り翌日夜にmet_todayがリセットされない | time_system.rpy |
| 5 | バグ | カナ部屋で食事済みだと全選択肢が消える | kana_events.rpy |
| 6 | バランス | LINEだけでお金要求できる問題を修正 | parameter_system.rpy |
| 7 | 設計 | カナのStage4を「推しの人」に変更 | parameter_system.rpy |
| 8 | 機能追加 | 朝にカナへの連絡を追加 | script.rpy |
| 9 | 機能追加 | デバッグログ出力システム | systems/debug_log.rpy（新規） |

---

## 修正1: ナンパ解禁後に再ナンパできる

**ファイル**: `events/daily_events.rpy`

`event_nanpa_unlock` の末尾に `afternoon_consumed` フラグを追加。

```python
label event_nanpa_unlock:
    "街を歩いていると、前を歩く男が女の子に声をかけていた。"
    # ...既存コード...

    menu:
        "試してみる":
            call nanpa_event

        "今日はやめとく":
            himo "まあ、今日はいいか"

    $ flags["afternoon_consumed"] = True   # 追加: 昼ターンを消費
    return
```

---

## 修正2: カナ信頼度UIが未表示

**ファイル**: `screens.rpy`

`status_bar` を以下の構造に**完全に書き換える**。既存コードの部分修正ではなく全体を差し替えること。

```python
screen status_bar():
    frame:
        xalign 0.5
        yalign 0.02
        padding (15, 8)

        vbox:
            spacing 4

            # 1行目: 基本情報
            hbox:
                spacing 25
                text "[game_date[day]]日目" size 24
                text get_time_string() size 24
                text "所持金: ¥[player[money]:,]" size 24 color "#FFD700"

                if player["stamina"] < 30:
                    text "[疲労]" size 20 color "#ff6b6b"
                if player["cleanliness"] < 30:
                    text "[不潔]" size 20 color "#4ecdc4"
                if not daily_flags["ate_today"] and game_date["time"] == "night":
                    text "[空腹]" size 20 color "#ffaa00"

            # 2行目: キャラクターパラメータ
            hbox:
                spacing 25

                text "美咲 信頼:[misaki[trust]] 依存:[misaki[dependence]]" size 20 color "#ffb7c5"

                if kana_flags["met"]:
                    text "カナ 信頼:[kana[trust]] 依存:[kana[dependence]]" size 20 color "#ffe066"
```

---

## 修正3: 美咲の告白イベントが朝に発生

**ファイル**: `events/misaki_events.rpy`

`misaki_confession` のトリガー箇所（`update_misaki_stage` 内またはステージ移行チェック箇所）に時間帯ガードを追加。

```python
# update_misaki_stage() 内、またはSTAGE_DATING移行チェックの箇所

if misaki["stage"] != old_stage and misaki["stage"] == STAGE_DATING:
    if not flags.get("confession_done", False):
        # 夜以外はその場で発生させず、フラグだけ立てて夜に持ち越す
        if game_date["time"] == "night":
            renpy.call("misaki_confession")
        else:
            flags["confession_pending"] = True   # 夜に持ち越し
```

`night_actions` の先頭に告白ペンディングチェックを追加。

```python
label night_actions:
    # 告白ペンディングチェック
    if flags.get("confession_pending", False) and not flags.get("confession_done", False):
        $ flags["confession_pending"] = False
        call misaki_confession

    # 約束がある夜は美咲一択（既存）
    if flags.get("misaki_tonight", False):
        ...
```

`variables.rpy` の `flags` に追加。

```python
"confession_pending": False,
```

---

## 修正4: お泊り翌日夜にmet_todayがリセットされない

**ファイル**: `systems/time_system.rpy`

`advance_day()` 内でカナの `met_today` もリセットされているか確認し、なければ追加。

```python
def advance_day():
    global game_date, misaki, kana, flags, daily_flags

    game_date["day"] += 1
    misaki["met_today"] = False   # 確認: これが存在するか
    kana["met_today"]   = False   # 確認: これが存在するか、なければ追加

    # daily_flags リセット
    daily_flags["asked_money_today"]  = False
    daily_flags["ignored_today"]      = False
    daily_flags["ignored_kana_today"] = False
    daily_flags["ate_today"]          = False   # 確認: これが存在するか

    # ...以降既存コード
```

---

## 修正5: カナ部屋で食事済みだと全選択肢が消える

**ファイル**: `events/kana_events.rpy`

`kana_visit` を食事・シャワー・魅力増加を**それぞれ独立したチェック**に分離。
食事済みでも他の選択肢が表示されるようにする。

```python
label kana_visit:
    scene bg_placeholder

    "カナの部屋に来た。"

    if game_date["time"] == "afternoon":
        "昼間から来られるのは、カナならでは。"
        kana_c "来た来た！暇だったんだよね〜"
    else:
        kana_c "いらっしゃい"

    # --- 食事（独立チェック）---
    if not daily_flags["ate_today"]:
        kana_c "ごはん食べた？なんか作るよ"
        menu:
            "食べていく":
                "カナが料理を作ってくれた。"
                kana_c "たいしたもんじゃないけど"
                himo "いや、うまい"
                $ change_stamina(20)
                $ daily_flags["ate_today"] = True
                $ change_trust_kana(3)
            "いい、気にしないで":
                himo "大丈夫"
                kana_c "遠慮しなくていいのに"
    # else: 食事済みでも以下の処理は続く

    # --- シャワー（独立チェック）---
    if player["cleanliness"] < 50:
        kana_c "シャワー使う？タオルあるよ"
        menu:
            "借りる":
                "シャワーを借りた。"
                $ change_cleanliness(30)
                $ change_trust_kana(2)
            "いい":
                pass

    # --- 魅力増加（無条件）---
    if player["charm"] < 70:
        $ change_charm(1)

    $ kana["met_today"] = True
    $ kana["last_contact"] = 0

    return
```

---

## 修正6: LINEだけでお金を要求できる問題

**コンセプト**: 最近会っていない状態ではお金を要求しにくい。
`last_contact` が2以上（2ターン以上連絡・接触がない）の場合は要求をブロック。

**ファイル**: `systems/parameter_system.rpy`

`request_money_from_misaki()` の先頭に追加。

```python
def request_money_from_misaki(amount_type="small"):
    global stats, himo_aptitude

    # v1.2追加: 最近会っていないとお金を要求しにくい
    if misaki["last_contact"] > 1:
        return False, 0, "最近会っていない"

    # ...以降既存コード
```

**ファイル**: `events/misaki_events.rpy`

`misaki_money_request` ラベルに対応するメッセージを追加。

```python
label misaki_money_request:
    # 1日1回制限（既存）
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    # v1.2追加: 最近会っていない場合
    if misaki["last_contact"] > 1:
        himo "（最近会ってもいないし、さすがにお金の話はしにくいな）"
        return

    # ...以降既存コード
```

---

## 修正7: カナのStage4を「推しの人」に変更

**ファイル**: `systems/parameter_system.rpy`

`update_kana_stage()` および通知メッセージを変更。

```python
def update_kana_stage():
    global kana
    trust  = kana["trust"]
    depend = kana["dependence"]

    if trust >= 70 and depend >= 30:      # 依存条件を50→30に緩和
        kana["stage"] = STAGE_OSHI       # 新ステージ定数
    elif trust >= 50:
        kana["stage"] = STAGE_CLOSE
    elif trust >= 35:
        kana["stage"] = STAGE_FRIEND
    elif trust > 0:
        kana["stage"] = STAGE_ACQUAINTANCE
    else:
        kana["stage"] = 0
```

**ファイル**: `data/constants.rpy`

```python
define STAGE_OSHI = 4   # カナ専用ステージ（美咲のSTAGE_DATINGに相当）
```

**ステージ名表示の変更**

`status_detail` スクリーンおよびステージ移行通知のステージ名辞書を分岐させる。

```python
# parameter_system.rpy の change_trust_kana() 内

stage_names_kana = {
    2: "友達",
    3: "いい感じ",
    4: "推しの人"   # 旧: 恋人
}
if kana["stage"] in stage_names_kana:
    renpy.notify("カナとの関係が「" + stage_names_kana[kana["stage"]] + "」になった")
```

```python
# screens.rpy の status_detail 内

python:
    # 美咲
    stage_names_misaki = {1: "知り合い", 2: "友達", 3: "いい雰囲気", 4: "恋人"}
    misaki_stage_name  = stage_names_misaki.get(misaki["stage"], "???")

    # カナ
    stage_names_kana = {1: "知り合い", 2: "友達", 3: "いい感じ", 4: "推しの人"}
    kana_stage_name  = stage_names_kana.get(kana["stage"], "???") if kana_flags["met"] else ""

text "美咲との関係: [misaki_stage_name]" size 22
if kana_flags["met"]:
    text "カナとの関係: [kana_stage_name]" size 22
```

---

## 修正8: 朝にカナへの連絡を追加

**ファイル**: `script.rpy`

`morning_actions` のメニューに追加。

```python
label morning_actions:
    # ...既存コード...

    menu:
        "【[game_date[day]]日目・朝】何をする？"

        "シャワーを浴びる":
            # 既存

        "美咲に連絡する":
            # 既存

        "カナに連絡する" if kana_flags["met"]:   # 追加
            call contact_kana

        "SNSを見る":
            # 既存

        "二度寝する":
            # 既存
```

---

## 修正9: デバッグログ出力システム

**ファイル**: `systems/debug_log.rpy`（新規作成）

```python
# debug_log.rpy
# テストプレイ用のログ出力システム
# DEBUG_MODE = True のときのみ機能する

init python:
    debug_log_entries = []

    def log_action(action_name, notes=""):
        """行動ログを記録する"""
        if not DEBUG_MODE:
            return

        entry = {
            "day":         game_date["day"],
            "time":        game_date["time"],
            "action":      action_name,
            "notes":       notes,
            "money":       player["money"],
            "stamina":     player["stamina"],
            "cleanliness": player["cleanliness"],
            "charm":       player["charm"],
            "m_trust":     misaki["trust"],
            "m_depend":    misaki["dependence"],
            "k_trust":     kana["trust"]    if kana_flags["met"] else "-",
            "k_depend":    kana["dependence"] if kana_flags["met"] else "-",
        }
        debug_log_entries.append(entry)

    def export_debug_log():
        """ログをファイルに書き出す"""
        if not DEBUG_MODE:
            return

        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"debug_log_{timestamp}.txt"

        lines = []
        lines.append("=== ヒモ男シミュレーター デバッグログ ===")
        lines.append(f"出力日時: {timestamp}")
        lines.append("")

        # ヘッダー
        lines.append("日  時  行動                所持金    体力 清潔 魅力 美信 美依 カ信 カ依 備考")
        lines.append("-" * 100)

        for e in debug_log_entries:
            lines.append(
                f"{e['day']:2}日 {e['time']:9} "
                f"{e['action']:18} "
                f"¥{e['money']:7,} "
                f"{e['stamina']:3} "
                f"{e['cleanliness']:3} "
                f"{e['charm']:3} "
                f"{e['m_trust']:3} "
                f"{e['m_depend']:3} "
                f"{str(e['k_trust']):3} "
                f"{str(e['k_depend']):3} "
                f"{e['notes']}"
            )

        lines.append("")
        lines.append("=== クリア時サマリー ===")
        lines.append(f"最終所持金:       ¥{player['money']:,}")
        lines.append(f"美咲 信頼/依存:   {misaki['trust']}/{misaki['dependence']}")
        if kana_flags["met"]:
            lines.append(f"カナ 信頼/依存:   {kana['trust']}/{kana['dependence']}")
        lines.append(f"総収入:           ¥{stats['total_earned']:,}")
        lines.append(f"美咲と会った回数: {stats['times_met']}回")
        lines.append(f"お金を要求:       {stats['times_asked_money']}回")
        lines.append(f"嘘をついた回数:   {stats['lies_told']}回")
        lines.append(f"パチンコ収支:     ¥{stats.get('pachinko_profit', 0):,}")
        lines.append(f"SNSリスク:        {kana_flags.get('sns_risk', 0)}")

        content = "\n".join(lines)

        try:
            with renpy.open_file(filename, "w") as f:
                f.write(content)
            renpy.notify(f"ログを出力しました: {filename}")
        except Exception as ex:
            renpy.notify(f"ログ出力エラー: {ex}")
```

**主要な行動の呼び出し箇所に `log_action()` を追加**

```python
# 各ラベルの要所に追記（例）

label misaki_date:
    $ log_action("美咲デート")
    ...

label misaki_money_request:
    $ log_action("美咲にお金要求", f"信頼{misaki['trust']}")
    ...

label kana_date:
    $ log_action("カナデート")
    ...

label nanpa_event:
    $ log_action("ナンパ")
    ...

label pachinko_event:
    $ log_action("パチンコ", f"賭け{pachinko_bet}円")
    ...
```

**エンディングラベルでログを書き出す**

```python
# endings.rpy の各エンディング先頭に追加

label ending_good_30days:
    $ flags["game_ended"] = True
    $ log_action("GOOD END")
    $ export_debug_log()
    ...

label ending_gray_30days:
    $ flags["game_ended"] = True
    $ log_action("GRAY END")
    $ export_debug_log()
    ...

label ending_bankruptcy_30days:
    $ flags["game_ended"] = True
    $ log_action("BAD END 破産")
    $ export_debug_log()
    ...
```

**出力ファイルの場所**
Ren'pyの`renpy.open_file()`はデフォルトで`game/`フォルダに書き出されます。テストプレイ後にそのファイルをこちらに貼り付けてもらえるとバランス分析に使えます。

---

## テスト確認項目

### バグ修正
- [ ] ナンパ解禁後に昼ターンが消費され再ナンパできない
- [ ] カナの信頼度・依存度がUIの2行目に表示される
- [ ] 美咲の告白イベントが夜のみ発生する
- [ ] お泊り翌日の夜に「今日もう会ったよ」と言われない
- [ ] カナ部屋で食事済みでもシャワー選択肢が表示される

### バランス
- [ ] 美咲と会わずにLINEだけでお金を要求しようとするとブロックされる
- [ ] 会った当日・翌日ならお金を要求できる

### 設計変更
- [ ] カナのステージ4が「推しの人」と表示される
- [ ] 朝の行動からカナに連絡できる

### デバッグログ
- [ ] エンディング到達時に `debug_log_YYYYMMDD_HHMMSS.txt` が生成される
- [ ] 各日程の行動とパラメータ値がログに記録されている
- [ ] クリア時サマリーがログ末尾に出力されている

---

*phase3_v1.2_fixes.md - 2026年2月21日作成*
