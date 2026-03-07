# ヒモ男シミュレーター Phase 4 ステップ1 修正指示書 v1.3

**前提**: Phase 4 ステップ1 v1.2が実装済みであること  
最終更新日: 2026年3月8日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | 「今週末会えるよね？」直後に「昨日来なかったね」が発生 | time_system.rpy / midgame_events.rpy |
| 2 | 設計 | 「最近どうしてる？」イベントが会った扱いになりお金要求できる | midgame_events.rpy |
| 3 | バグ | 正直に認めたのに「乗り切った」→美咲が謝る矛盾 | lie_puzzle.rpy / midgame_events.rpy |
| 4 | 機能追加 | 土日に美咲と昼デート可能にする | script.rpy / misaki_events.rpy |
| 5 | バランス | カナが積極的すぎて体験版ENDが早すぎる | kana_events.rpy / constants.rpy |

---

## 修正1: 約束系イベントの連鎖バグ

**問題**: 美咲「来週の土曜、空いてる？」の探りで「空いてるよ」を選択 → `misaki_saturday_promise` フラグが立つ → その約束を果たす前（あるいは直後）に「昨日来なかったね」が発生する。約束の日のチェックロジックが曖昧。

**原因**: 「約束の日」がいつなのかを具体的に記録していない。フラグだけでは「いつの約束か」が分からない。

**ファイル**: `data/variables.rpy` / `systems/time_system.rpy`

### 修正方針: 約束を日付指定で管理する

```python
# variables.rpy に追加
default appointments = {
    "misaki": None,    # 約束がある日（整数 or None）
    "kana": None
}
```

```python
# 約束を入れるとき（date_incidents.rpy の schedule 探り）
elif probe_key == "schedule":
    menu:
        "空いてるよ":
            misaki_c "じゃあ約束ね！"
            # Phase 4 v1.3: 具体的な日付を記録
            # 次の土曜日を計算
            python:
                current_day = game_date["day"]
                weekday_index = (current_day - 1) % 7  # 0=日,1=月,...6=土
                days_until_saturday = (6 - weekday_index) % 7
                if days_until_saturday == 0:
                    days_until_saturday = 7  # 今日が土曜なら来週
                appointments["misaki"] = current_day + days_until_saturday
            "（来週の土曜に約束した）"

        "まだ分からない":
            misaki_c "...そう"
            $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)
```

```python
# time_system.rpy の advance_day() 内
# 約束不履行チェックを日付ベースに変更

# 美咲の約束チェック
python:
    misaki_appointment = appointments.get("misaki", None)
    if misaki_appointment is not None and game_date["day"] > misaki_appointment:
        # 約束の日を過ぎた
        if not flags.get("misaki_appointment_kept", False):
            # 約束を破った
            renpy.call("misaki_appointment_broken")
        # フラグリセット
        appointments["misaki"] = None
        flags["misaki_appointment_kept"] = False

    # カナも同様
    kana_appointment = appointments.get("kana", None)
    if kana_appointment is not None and game_date["day"] > kana_appointment:
        if not flags.get("kana_appointment_kept", False):
            renpy.call("kana_appointment_broken")
        appointments["kana"] = None
        flags["kana_appointment_kept"] = False
```

```python
# 約束の日にデートした場合のフラグ設定
# date_misaki_places.rpy の共通処理に追加

# Phase 4 v1.3: 約束の履行チェック
python:
    if (appointments.get("misaki", None) is not None
        and game_date["day"] == appointments["misaki"]):
        flags["misaki_appointment_kept"] = True
```

```python
# 約束を破った場合のイベント

label misaki_appointment_broken:
    "美咲からLINEが来ていた。"
    misaki_c "昨日、約束してたよね...？"

    menu:
        "ごめん、忘れてた":
            misaki_c "...そう"
            $ change_trust(-10)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 3, SUSPICION_MAX)

        "急用が入って（嘘）":
            call run_lie_puzzle("double_booking", "misaki")

    return


label kana_appointment_broken:
    "カナからLINEが来ていた。"
    kana_c "昨日なんで来なかったの？"

    menu:
        "ごめん":
            kana_c "もう...許さない"
            kana_c "...嘘。許す。でも次はないからね"
            $ change_trust_kana(-8)

        "体調悪くて（嘘）":
            call run_lie_puzzle("double_booking", "kana")

    return
```

さらに、`flags["misaki_tonight"]` の約束不履行チェックにもガードを追加。当日中に美咲とデート済みなら不履行にしない。

```python
# advance_day() 内の misaki_tonight チェック修正

if flags.get("misaki_tonight", False):
    if not misaki["met_today"]:
        # 約束を破った
        $ change_trust(-5)
        $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
        # ※翌朝にメッセージ表示（advance_day内ではセリフ表示しない）
        $ flags["misaki_tonight_broken"] = True
    $ flags["misaki_tonight"] = False
```

---

## 修正2: 「最近どうしてる？」イベントの扱い

**問題**: イベント①「美咲『最近忙しいの？』」でLINEのやり取りをすると、`reset_contact()` が呼ばれて `last_contact` がリセットされ、会ったのと同じ扱いになる。その結果、同日中にお金の相談ができてしまう。

**設計判断**: LINEでの連絡と対面は区別すべき。LINEだけでは「会った」扱いにしない。お金の相談は対面（デート）時のみ可能にする。

**ファイル**: `events/midgame_events.rpy`

```python
label midgame_misaki_busy:
    scene bg_placeholder

    "朝、スマホを見ると美咲からLINEが来ていた。"
    misaki_c "おはよう。最近連絡ないけど、忙しいの？"

    "...3日以上連絡してなかった。"

    menu:
        "すぐ返信する":
            himo "ごめん、ちょっとバタバタしてて"
            misaki_c "...そうなんだ。元気ならいいんだけど"
            "少し間があった。"
            misaki_c "最近、全然連絡くれないなって思って"
            $ change_trust(-5)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)

            # Phase 4 v1.3: last_contactはリセットするが、met_todayはFalseのまま
            $ misaki["last_contact"] = 0
            # ※ reset_contact() を使わず直接代入。met_todayは変更しない

        "後で返そう（スルー）":
            "後で返せばいいか。"
            himo "まあいっか"
            $ change_trust(-10)
            $ suspicion["misaki"] = min(suspicion["misaki"] + 2, SUSPICION_MAX)
            $ himo_aptitude["easy_choices"] += 1
            # last_contactもリセットしない

    $ flags["midgame_busymisaki_done"] = True
    return
```

**補足**: `reset_contact()` は「対面で会った」時にのみ使用する。LINE上のやり取りでは `misaki["last_contact"] = 0` のみ行い、`met_today` は変更しない。お金の相談は既に `met_today` または対面デート中のみ発生する設計のため、この修正で自然に制限される。

ただし現状のお金要求（`misaki_money_request`）は美咲に「連絡する」からも呼べる構造になっている可能性がある。お金要求は必ず**デート中**または**直近で会った後**のみ可能にする:

```python
# misaki_events.rpy

label misaki_money_request:
    # Phase 4 v1.3: 対面していない（last_contact > 1）場合はお金要求不可
    if misaki["last_contact"] > 1 and not misaki["met_today"]:
        himo "（最近会ってないし、いきなりお金の話はしづらいな...）"
        return

    # 既存チェック...
```

---

## 修正3: 正直ルートの結果矛盾

**問題**: 嘘パズルで「正直に認める」を選択 → `lie_puzzle["bare_gauge"]` が0にリセット → `resolve_lie_puzzle(0)` → `safe` → 「乗り切った」表示。さらに呼び出し元（`midgame_misaki_direct`）で `result == "safe"` の分岐に入り、美咲「ごめん、疑って」が表示される。正直に認めたのに「疑ってごめん」は矛盾。

**原因**: 正直ルートはバレ度0で `safe` 扱いになるが、`safe` の意味が「嘘がバレなかった」と「正直に話して解決した」で混同されている。

**ファイル**: `systems/lie_puzzle.rpy` / `events/midgame_events.rpy`

### 修正方針: 正直ルート専用の結果を追加

```python
# lie_puzzle.rpy

label lie_puzzle_other_woman(target="misaki"):
    # （既存処理）

    if answer1 == "honest":
        # 正直ルート — 嘘パズル中断
        "ヒモ太郎「...正直に言うと、他にも会ってる人がいる」"
        if target == "misaki":
            misaki_c "...やっぱり"
            "長い沈黙。"
            misaki_c "...分かってた。薄々"
            $ change_trust(-15)
            $ himo_aptitude["honest_moments"] += 2
            $ suspicion["misaki"] = max(suspicion["misaki"] - 10, 0)
        else:
            kana_c "...は？マジで？"
            $ change_trust_kana(-15)
            $ himo_aptitude["honest_moments"] += 2
            $ suspicion["kana"] = max(suspicion["kana"] - 10, 0)

        # Phase 4 v1.3: 正直ルート専用の結果コードを設定
        $ lie_puzzle["bare_gauge"] = 0
        $ lie_puzzle["result"] = "honest"    # ← 直接resultを設定
        return

    # （以降は嘘ルートの処理）
```

```python
# run_lie_puzzle ラベル内の結果判定を修正

label run_lie_puzzle(scenario="generic", target="misaki"):
    # （嘘パズル実行）

    # 結果判定
    python:
        # Phase 4 v1.3: 正直ルートで直接設定された場合はスキップ
        if lie_puzzle.get("result", None) != "honest":
            result = resolve_lie_puzzle(lie_puzzle["bare_gauge"])
            lie_puzzle["result"] = result
        else:
            result = "honest"
        lie_puzzle["active"] = False

    # Phase 4 v1.3: 正直ルートは専用処理（lie_puzzle内で既に処理済み）
    if result == "honest":
        # 信頼低下等は lie_puzzle 内で処理済みなのでここでは何もしない
        return

    if result == "busted":
        "（完全にバレた...）"
        # （既存処理）
    elif result == "suspicious":
        "（...怪しまれてる）"
        # （既存処理）
    elif result == "uneasy":
        "（なんとか誤魔化せた...かな）"
        # （既存処理）
    else:  # safe
        "（...乗り切った）"
        $ himo_aptitude["lie_skill"] = himo_aptitude.get("lie_skill", 0) + 1

    # （嘘カウント等）
    # Phase 4 v1.3: 正直ルートでは嘘カウントを増やさない
    if result != "honest":
        $ himo_aptitude["lies"] += 1
        $ stats["lies_told"] += 1

    return
```

```python
# midgame_events.rpy のイベント⑧の結果分岐を修正

label midgame_misaki_direct:
    # （既存処理: 美咲の追及、嘘パズル呼び出し）

    python:
        result = lie_puzzle["result"]

    # Phase 4 v1.3: 正直ルート専用分岐
    if result == "honest":
        "長い沈黙が続いた。"
        misaki_c "...正直に言ってくれたのは、ありがたい"
        misaki_c "でも...どうすればいいか、分からない"
        "美咲は静かに下を向いていた。"
        # 信頼は下がるが、疑念はリセットされる
        # （信頼低下は lie_puzzle 内で処理済み）

    elif result == "busted":
        misaki_c "...もういい"
        misaki_c "分かってた。薄々"
        "美咲は静かに泣いていた。"
        $ change_trust(-25)
        $ change_dependence(-10)

    elif result == "suspicious":
        misaki_c "...信じたいけど"
        "美咲は何かを飲み込んだような顔をした。"
        $ change_trust(-10)

    elif result == "safe":
        # safe は「嘘で乗り切った」場合のみ
        misaki_c "...ごめん、疑って"
        himo "いいって。ちゃんと話してくれてありがとう"
        $ change_trust(5)

    # uneasy の場合は run_lie_puzzle 内で処理済み

    $ flags["midgame_misaki_direct_done"] = True
    return
```

---

## 修正4: 土日に美咲と昼デート可能にする

**問題**: 美咲は平日勤務のOLなので平日昼は会えない設定だが、土日は休みのはず。現状は夜しかデートできない。

**ファイル**: `script.rpy` / `events/misaki_events.rpy`

### 修正方針: 曜日判定を追加し、土日は昼の行動に「美咲を昼に誘う」を追加

```python
# variables.rpy または time_system.rpy にヘルパー関数追加

init python:
    def is_weekend():
        """今日が土日かどうか"""
        weekday_index = (game_date["day"] - 1) % 7  # 0=日,1=月,...6=土
        return weekday_index == 0 or weekday_index == 6

    def get_weekday_name():
        """今日の曜日名を返す"""
        weekday_index = (game_date["day"] - 1) % 7
        return WEEKDAYS[weekday_index]
```

```python
# script.rpy の afternoon_actions

label afternoon_actions:
    # （SNS通知、中盤イベントチェック等）

    menu:
        "【[game_date[day]]日目（[get_weekday_name()]）・昼】何をする？"

        "街に出る" if flags["street_unlocked"]:
            call afternoon_street

        "美咲に連絡する":
            call contact_misaki

        # Phase 4 v1.3: 土日は美咲を昼に誘える
        "美咲を昼デートに誘う" if is_weekend() and not misaki["met_today"]:
            call misaki_daytime_date_request

        "カナに連絡する" if kana_flags["met"]:
            call contact_kana

        "昼寝する":
            # 既存処理

        "ステータス確認":
            call screen status_detail
            jump afternoon_actions

    return
```

```python
# misaki_events.rpy に追加

label misaki_daytime_date_request:
    "美咲に昼から会えないか聞いてみた。"

    if not is_weekend():
        misaki_c "ごめん、今仕事中..."
        return

    # 既読スルーチェック
    if daily_flags.get("ignored_today", False):
        "さっき既読スルーされたばかりだし..."
        return

    # 成功判定
    python:
        import random
        trust = misaki["trust"]
        if trust >= 60:
            success_rate = 0.90
        elif trust >= 45:
            success_rate = 0.75
        elif trust >= 30:
            success_rate = 0.60
        else:
            success_rate = 0.40
        daytime_success = random.random() < success_rate

    if daytime_success:
        misaki_c "いいよ！今日休みだし"
        call misaki_date_with_location
    else:
        misaki_c "ごめん、今日ちょっと用事あって..."
        misaki_c "夜なら空くかも"
        himo "了解〜"

    return
```

### ダブルブッキング連携

土日昼に美咲とデートした場合、夜にカナとの約束があると時間的にギリギリになる演出を追加できる（将来拡張）。

```python
# 昼に美咲とデート → 夜にカナとの約束がある場合
if daily_flags.get("date_with") == "misaki" and flags.get("kana_tonight", False):
    "（やばい、夜はカナと約束が...）"
    "（美咲に長居されたら間に合わない）"
    # 美咲が「もうちょっといようよ」と言い出すリスク（依存度依存）
    if misaki["dependence"] >= 50:
        python:
            import random
            if random.random() < 0.40:
                renpy.call("misaki_wants_to_stay")
```

---

## 修正5: カナの積極性調整

**問題**: カナの信頼が100に到達して体験版ENDが22日目で発生。カナからの自発的連絡が頻繁すぎて、プレイヤーが意図的に関わらなくても信頼が上がりすぎる。

**ログ分析**:
- 5日目にカナ出会い → 22日目に信頼100/依存67
- 17日間で信頼85上昇 = 1日あたり+5ペース
- カナデート回数: カフェ5+大学2+部屋1 = 8回
- デート以外でも自発連絡経由で信頼が上がっている

**ファイル**: `events/kana_events.rpy` / `data/constants.rpy`

### 修正A: カナの自発連絡による信頼上昇を抑制

```python
# kana_events.rpy の kana_initiative_event

label kana_initiative_event:
    # （既存の連絡内容表示）

    menu:
        "返信する":
            if msg_type in ["meetup", "food", "needy"]:
                menu:
                    "今夜会おう":
                        $ flags["kana_tonight"] = True
                        $ kana["last_contact"] = 0
                        # Phase 4 v1.3: 自発連絡の返信では信頼微増のみ
                        $ change_trust_kana(1)    # 旧: 2
                    "今日は無理":
                        himo "今日はちょっと"
                        kana_c "そっか〜"
                        $ change_trust_kana(-1)
                        $ kana["last_contact"] = 0
            else:
                himo "まあまあかな"
                kana_c "そっか〜"
                $ kana["last_contact"] = 0
                $ change_trust_kana(1)    # 旧: 2

        "既読スルーする":
            "既読スルーした。"
            $ change_trust_kana(-2)

    return
```

### 修正B: カナのデートでの信頼上昇量を全体的に下方修正

```python
# date_kana_places.rpy

# カフェ
$ change_trust_kana(4)     # 旧: 5

# カラオケ
$ change_trust_kana(6)     # 旧: 8

# 大学付近
$ change_trust_kana(6)     # 旧: 8

# 部屋
# 清潔感依存は変更なし
# change_trust_kana(5)  → change_trust_kana(4)  （清潔感50以上）
# change_trust_kana(3)  → change_trust_kana(2)  （清潔感30以上）
```

### 修正C: カナの自発連絡の発火率を下げる

```python
# kana_events.rpy の check_kana_initiative

init python:
    def check_kana_initiative():
        import random
        global kana

        if kana["last_contact"] < 2:
            return
        if kana["met_today"]:
            return

        depend = kana["dependence"]
        # Phase 4 v1.3: 発火率を下方修正
        if depend >= 60:
            fire_rate = 0.45    # 旧: 0.60
        elif depend >= 30:
            fire_rate = 0.30    # 旧: 0.40
        else:
            fire_rate = 0.15    # 旧: 0.25

        if random.random() < fire_rate:
            renpy.call("kana_initiative_event")
```

### 修正D: 体験版ENDの発生条件を調整

現在カナの信頼100で体験版ENDが発生するが、これだけでは早すぎる。**信頼だけでなく依存度やストーリー進行も条件に加える**。

```python
# 体験版END条件を変更
# 修正前: カナ信頼 >= 100
# 修正後: カナ信頼 >= 95 AND カナ依存 >= 50 AND game_date["day"] >= 25

# ※最低でも25日目以降にしか体験版ENDが発生しないようにする
```

---

## テスト確認項目

- [ ] 美咲との約束が具体的な日付で管理され、約束の日以外に「来なかったね」が出ない
- [ ] 約束の日に美咲とデート（部屋含む）→ 翌日に不履行扱いにならない
- [ ] 「最近どうしてる？」のLINEやり取りだけではお金要求できない
- [ ] 正直ルートで「乗り切った」が表示されず、専用の重いテキストが出る
- [ ] 土日の昼に美咲をデートに誘える選択肢が表示される
- [ ] 平日昼には土日デート選択肢が表示されない
- [ ] カナの信頼100到達が25日目以降になるペース
- [ ] カナの自発連絡頻度が体感で「適度」になっている
- [ ] 体験版ENDが25日目以前に発生しない

---

*phase4_step1_v1.3_fixes.md - 2026年3月8日作成*
