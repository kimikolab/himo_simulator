# ヒモ男シミュレーター Phase 4 緊急バグ修正 v1.3.1

**前提**: Phase 4 ステップ1 v1.3が実装済みであること  
最終更新日: 2026年3月8日

---

## 修正一覧

| # | 種別 | 深刻度 | 内容 | ファイル |
|---|---|---|---|---|
| 1 | バグ | **致命的** | 家賃が一度も請求されない＋エンディング判定が甘い | time_system.rpy / endings.rpy |
| 2 | バグ | **重大** | 約束管理が2系統並行しており泊まりが約束履行として認識されない | time_system.rpy |

---

## 修正1: 家賃請求とエンディング判定

### 問題の構造

2つの問題が重なっている。

**問題A**: `advance_day()` の120-121行目で `game_date["day"] > GAME_DAYS` の場合に早期returnするため、132行目の月次請求処理に到達しない。30日制のゲームで `(day - 1) % 30 == 0` は31日目に発火するが、その前にreturnされる。つまり**家賃¥50,000が一度も請求されない**。

**問題B**: `endings.rpy` の判定が `player["money"] >= 0` になっており、家賃を払えるかではなく残高がマイナスでないかしか見ていない。

### 修正方針

30日制の体験版では、月次請求ではなく**エンディング判定時に家賃を精算する**方式に変更する。

### ファイル: `endings.rpy`

```python
label ending_30days:
    scene bg_placeholder with fade
    "――30日目、夜――"
    "スマホに通知が来た。"
    "『家賃引き落とし: ¥[MONTHLY_RENT:,]』"
    "『通信費引き落とし: ¥[PHONE_BILL:,]』"

    python:
        total_bill = MONTHLY_RENT + PHONE_BILL
        can_pay = player["money"] >= total_bill

    if can_pay:
        $ change_money(-total_bill)
        "合計¥[total_bill:,]が引き落とされた。"
        "残高: ¥[player['money']:,]"
        himo "...払えた"
    else:
        "残高不足で引き落とせなかった。"
        himo "...やばい"
        jump ending_bankruptcy_30days

    # 以下、既存のエンディング分岐判定
    python:
        is_honest = stats["lies_told"] <= 3
        is_dependent = misaki["dependence"] >= 65
        met_often = stats["times_met"] >= 10
        concern_shown = himo_aptitude["showed_concern"] >= 5
        all_misaki_events = (misaki_events["M02_done"] and misaki_events["M03_done"] and misaki_events["M05_done"])

    if is_honest and met_often and not is_dependent and concern_shown:
        jump ending_balance_30days
    elif is_dependent or not is_honest:
        jump ending_himou_30days
    else:
        jump ending_unstable_30days
```

### ファイル: `time_system.rpy`

`advance_day()` の月次請求処理は体験版では不要になるため、コメントアウトまたは製品版用に条件を変更。

```python
# 132-133行目を修正
# 体験版（30日制）ではエンディングで精算するため月次処理は不要
# 製品版（60日以上）では15日目・45日目等に中間請求を入れる
# if game_date["day"] > 1 and (game_date["day"] - 1) % 30 == 0:
#     _pending_events.append(("monthly_billing", None))
```

---

## 修正2: 約束管理システムの統合

### 問題の構造

約束管理が2系統ある:

**旧システム（56-62行目）**: `weekend_promised` + `met_misaki_this_weekend`
- 「今週末会えるよね？」等で `weekend_promised = True` がセットされる
- 日曜→月曜のタイミングで `met_misaki_this_weekend` をチェック
- 美咲の部屋訪問（`misaki_room_visit`）でこのフラグが立つか不明

**新システム（71-83行目）**: `appointments` + `misaki_appointment_kept`
- v1.3で追加。日付指定で約束を管理
- デート共通処理で `misaki_appointment_kept` を立てる想定
- 美咲の部屋訪問（`misaki_room_visit`）がこの処理を通らない

2つのシステムが連動していないため、片方で約束を入れてもう片方でチェックされると不履行扱いになる。

### 修正方針

旧システム（`weekend_promised`）を廃止し、`appointments` 系に一本化する。

### ファイル: `time_system.rpy`

```python
def advance_day():
    global game_date, misaki, flags, daily_flags
    global location_flags, misaki_events, misaki_streak
    global _game_over

    # v2.1: 日曜朝シーン処理
    if flags.get("misaki_sunday_morning", False):
        location_flags["staying_at_misaki"] = True
        flags["misaki_sunday_morning"] = False
        _pending_events.append(("misaki_sunday_morning_scene", None))

    # Phase 4 v1.1: 食事回数カウント
    if daily_flags.get("ate_today", False):
        stats["meals_eaten"] = stats.get("meals_eaten", 0) + 1

    # 食事ペナルティチェック
    if not daily_flags["ate_today"]:
        _pending_events.append(("hunger_penalty", None))

    # === v1.3.1修正: 旧weekend_promisedシステムを削除 ===
    # 以下のブロックを削除:
    # if game_date["weekday"] == 0:
    #     if weekend_promised:
    #         if not flags.get("met_misaki_this_weekend", False):
    #             _pending_events.append(("misaki_broken_promise", None))
    #         flags["met_misaki_this_weekend"] = False
    #         weekend_promised = False

    # === v1.3.1修正: misaki_tonight 不履行チェック（泊まり対応） ===
    if flags.get("misaki_tonight", False):
        if not misaki["met_today"] and not location_flags.get("staying_at_misaki", False):
            # 会ってもいないし泊まってもいない → 不履行
            flags["misaki_tonight_broken"] = True
        flags["misaki_tonight"] = False

    # === v1.3.1修正: 約束不履行チェック（appointments一本化） ===
    _misaki_appt = appointments.get("misaki", None)
    if _misaki_appt is not None and game_date["day"] >= _misaki_appt:
        # 約束の日を過ぎた（当日含む）
        # met_today または staying_at_misaki で履行判定
        if misaki["met_today"] or location_flags.get("staying_at_misaki", False):
            # 約束を果たした
            pass
        else:
            _pending_events.append(("misaki_appointment_broken", None))
        appointments["misaki"] = None

    _kana_appt = appointments.get("kana", None)
    if _kana_appt is not None and game_date["day"] >= _kana_appt:
        if kana["met_today"] or location_flags.get("staying_at_kana", False):
            pass
        else:
            _pending_events.append(("kana_appointment_broken", None))
        appointments["kana"] = None

    # （以降は既存処理: 日付進行、daily_flagsリセット等）
    # ...
```

### ファイル: 探り「今週末会えるよね？」の修正

`date_incidents.rpy` の `schedule` 探りを `appointments` 系に統一。

```python
elif probe_key == "schedule":
    menu:
        "空いてるよ":
            misaki_c "じゃあ約束ね！"
            # v1.3.1: appointments に統一（weekend_promised は使わない）
            python:
                current_day = game_date["day"]
                weekday_idx = game_date["weekday"]
                days_until_saturday = (6 - weekday_idx) % 7
                if days_until_saturday == 0:
                    days_until_saturday = 7
                appointments["misaki"] = current_day + days_until_saturday
            "（来週の土曜に約束した）"

        "まだ分からない":
            misaki_c "...そう"
            $ suspicion["misaki"] = min(suspicion["misaki"] + 1, SUSPICION_MAX)
```

### ファイル: 美咲の部屋訪問で約束履行扱いにする

`misaki_room_visit` ラベル内に `met_today` の設定があるか確認し、なければ追加。

```python
# misaki_room_visit の処理内（または呼び出し元）に追加
$ misaki["met_today"] = True
$ reset_contact()
```

これにより、`advance_day()` の約束チェックで `misaki["met_today"]` が `True` になり、部屋訪問＝約束履行として正しく判定される。

---

## 削除する変数

```python
# 以下は不要になるため削除（または未使用として放置）
# weekend_promised
# flags["met_misaki_this_weekend"]
# flags["misaki_appointment_kept"]
# flags["kana_appointment_kept"]
```

`misaki_appointment_kept` と `kana_appointment_kept` は不要になる。`advance_day()` 内で直接 `met_today` / `staying_at_*` を見て判定するため。

---

## テスト確認項目

### 家賃請求
- [ ] 30日目のエンディング突入時に家賃¥50,000＋通信費¥3,000が請求される
- [ ] 所持金が¥53,000未満の場合にBAD END（破産）になる
- [ ] 所持金が¥53,000以上の場合に差し引かれてからエンディング分岐に入る

### 約束管理
- [ ] 「今週末会えるよね？」で `appointments["misaki"]` に土曜の日付が入る
- [ ] 約束の日に美咲とデートすると不履行にならない
- [ ] 約束の日に美咲の部屋に泊まっても不履行にならない
- [ ] 約束の日に会わなかった場合のみ「昨日来なかったね」が発生する
- [ ] `weekend_promised` 関連のコードが動作していない（旧システム無効化確認）

---

*phase4_v1.3.1_critical_fixes.md - 2026年3月8日作成*
