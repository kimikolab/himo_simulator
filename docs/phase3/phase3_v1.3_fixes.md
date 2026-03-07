# ヒモ男シミュレーター Phase 3 修正指示書 v1.3

**前提**: Phase 3 v1.2が実装済みであること  
最終更新日: 2026年3月1日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | カナ出会いがログに未記録 | kana_events.rpy |
| 2 | バグ | 清潔感0でペナルティが発生しない | time_system.rpy |
| 3 | バランス | reset_contact()をデート時のみに限定 | misaki_events.rpy / kana_events.rpy |
| 4 | 設計 | カナ「推しの人」への複数ルート実装 | parameter_system.rpy / kana_events.rpy |

---

## 修正1: カナ出会いがログに未記録

**ファイル**: `events/kana_events.rpy`

`k01_nanpa_success` の先頭に追加。

```python
label k01_nanpa_success:
    $ log_action("カナ出会い K-01")   # 追加
    scene bg_placeholder
    # ...以降既存コード
```

---

## 修正2: 清潔感0でペナルティが発生しない

**ファイル**: `systems/time_system.rpy`

`advance_time()` 内のスタミナチェックと同様に、清潔感チェックを追加。

```python
def advance_time():
    # ...既存コード...

    player["stamina"]     = max(0, player["stamina"]     - STAMINA_DECAY_PER_TURN)
    player["cleanliness"] = max(0, player["cleanliness"] - CLEANLINESS_DECAY_PER_TURN)

    misaki["last_contact"] += 1
    if kana_flags["met"]:
        kana["last_contact"] += 1

    if player["stamina"] <= 15:
        renpy.call("event_low_stamina")

    # v1.3追加: 清潔感ペナルティ
    if player["cleanliness"] <= 0:
        renpy.call("event_low_cleanliness")
```

```python
label event_low_cleanliness:
    if flags.get("game_ended", False):
        return

    "（体が臭い気がする...）"
    "（さすがに不潔すぎる）"

    python:
        import random
        # 美咲・カナと会う予定がある日はペナルティ強化
        if flags.get("misaki_tonight") or flags.get("kana_tonight"):
            renpy.notify("美咲: 「...ちょっと、大丈夫？」")
            change_trust(-3)
        else:
            change_charm(-2)

    return
```

---

## 修正3: reset_contact()をデート時のみに限定

**コンセプト**:  
- `reset_contact()` → 実際に会った時のみ呼ぶ  
- LINEでの連絡・雑談では `last_contact` をリセットしない  
- これにより「会ってから2ターン以内しかお金を要求できない」制限が正しく機能する

### 確認・修正箇所

以下のラベルで `reset_contact()` が呼ばれているか確認し、**LINEのみのやり取りでは削除する**。

```python
# ✅ reset_contact() を呼ぶべき場所（実際に会った時）
label misaki_date:          # デート
label misaki_room_visit:    # 美咲宅訪問
label kana_date:            # カナとのデート
label kana_visit:           # カナ宅訪問

# ❌ reset_contact() を呼んではいけない場所（LINEのみ）
label contact_misaki:       # LINEで連絡するだけ → 削除
label contact_kana:         # LINEで連絡するだけ → 削除
label misaki_chat:          # LINEでの雑談 → 削除
label kana_initiative_event: # カナからのLINE → 削除
label morning_phone_misaki: # 電話のみ → 削除
label morning_phone_kana:   # 電話のみ → 削除
```

**美咲用の修正**

```python
label contact_misaki:
    # v1.3修正: LINEのみなのでreset_contactを呼ばない
    # $ reset_contact()  ← 削除

    "美咲にLINEを送った..."
    # ...以降既存コード
```

**カナ用の修正**

```python
label contact_kana:
    # v1.3修正: LINEのみなのでlast_contactをリセットしない
    # $ kana["last_contact"] = 0  ← 削除

    "カナにLINEを送った..."
    # ...以降既存コード
```

---

## 修正4: カナ「推しの人」への複数ルート実装

### ルート設計

```
ルートA（会った回数）: trust >= 70 and kana_dates_count >= 8
ルートB（SNS公開）:    trust >= 65 and sns_risk >= 15
                       ※到達時に美咲へのバレリスクも上昇
ルートC（信頼単独）:   trust >= 80
                       ※どのルートにも乗れない場合のフォールバック
```

### variables.rpy

```python
# statsまたはkana_flagsに追加
default kana_dates_count = 0   # カナとのデート回数（kana_dateとkana_visitを合算）
```

### kana_events.rpy

`kana_date` と `kana_visit` の末尾にカウントを追加。

```python
label kana_date:
    # ...既存コード...
    $ kana_dates_count += 1
    $ log_action("カナデート", f"累計{kana_dates_count}回")
    return

label kana_visit:
    # ...既存コード...
    $ kana_dates_count += 1
    return
```

### parameter_system.rpy

`update_kana_stage()` を複数ルート対応に書き換え。

```python
def update_kana_stage():
    global kana

    trust  = kana["trust"]
    depend = kana["dependence"]

    # Stage 4「推しの人」への到達判定（複数ルート）
    reached_oshi = False
    oshi_route   = None

    # ルートA: 会った回数
    if trust >= 70 and kana_dates_count >= 8:
        reached_oshi = True
        oshi_route   = "A"

    # ルートB: SNS公開（カナが積極的に露出）
    if trust >= 65 and kana_flags.get("sns_risk", 0) >= 15:
        reached_oshi = True
        oshi_route   = "B"

    # ルートC: 信頼単独フォールバック
    if trust >= 80:
        reached_oshi = True
        oshi_route   = "C"

    old_stage = kana["stage"]

    if reached_oshi:
        kana["stage"] = STAGE_OSHI
    elif trust >= 50:
        kana["stage"] = STAGE_CLOSE
    elif trust >= 35:
        kana["stage"] = STAGE_FRIEND
    elif trust > 0:
        kana["stage"] = STAGE_ACQUAINTANCE
    else:
        kana["stage"] = 0

    # Stage 4到達時の通知・演出
    if old_stage < STAGE_OSHI and kana["stage"] == STAGE_OSHI:
        renpy.call("kana_oshi_event", oshi_route)
```

### kana_events.rpy（ルート別演出）

```python
label kana_oshi_event(route):
    scene bg_placeholder

    if route == "A":
        "何度も会ううちに、カナとの時間が当たり前になってきた。"
        kana_c "ヒモ太郎って、なんか特別だよね"
        himo "そうか？"
        kana_c "うん。推しって感じ"
        himo "推し..."
        "なんか変な感じだけど、悪くない。"

    elif route == "B":
        "カナのインスタのストーリーに、俺の後ろ姿が映っていた。"
        "'今日も会ってる人'"
        "コメントが100件以上ついていた。"
        kana_c "フォロワーに紹介しちゃった。ヒモ太郎のこと、推しって言っといたから"
        himo "え"
        kana_c "ダメだった？"
        himo "...まあ、いいけど"

        # ルートB: 美咲へのバレリスクが上昇
        $ kana_flags["sns_risk"] += 10
        $ add_suspicion("sns_exposure")
        renpy.notify("SNSでの露出が増えた。美咲にバレるリスクが高まっている。")

    elif route == "C":
        "気づけば、カナのことをよく考えるようになっていた。"
        kana_c "なんか、最近ヒモ太郎のこと推しって思ってる"
        himo "は？"
        kana_c "褒めてるんだけど"
        himo "...そうか"

    return
```

### ルートBのSNSバレ連動

`add_suspicion()` に `sns_exposure` ケースを追加。

```python
# parameter_system.rpy の add_suspicion() 内

messages = {
    "contact_delay":  "美咲: 「最近忙しそうだね」",
    "vague_answer":   "美咲: 「...そうなんだ」",
    "too_many_requests": "美咲: 「また？」",
    "avoided_question":  "美咲: 「...」",
    "deflected":      "",
    "sns_exposure":   "美咲: 「...ねえ、これって知り合い？」",  # 追加
}
```

---

## バランス期待値（修正後の想定）

### お金要求の制限強化後

```
last_contact > 1 でブロック（デートしないとリセットされない）
→ デートした翌日・翌々日のみ要求可能

前回ログの問題箇所:
  24・26・28・29・30日朝の連続要求
  → デートなしでも要求できていた（LINEでリセットされていた）
  → 修正後はデートが必須になるため収入ペースが適正化される
```

### カナ「推しの人」の到達難易度

```
ルートA: 会った回数8回 + 信頼70
  → 週2〜3回ペースで会えば20日前後で到達可能
  → 前回ログ（4回・信頼57）では到達不可 → 適切な難易度

ルートB: SNSリスク15 + 信頼65
  → K-02で「気にしない」を選び続けると蓄積（1回+5）
  → 3回選択で15到達、信頼65は10日前後で可能
  → 美咲バレリスクとのトレードオフが機能する

ルートC: 信頼80
  → 最も時間がかかるフォールバック
  → 前回ログのペース（30日で57）では到達困難 → 難しすぎる可能性あり
     調整案: 信頼75に下げることも検討
```

---

## テスト確認項目

### バグ修正
- [ ] カナ出会いイベントがデバッグログに記録される
- [ ] 清潔感0が数ターン続くと美咲・カナの信頼が下がる

### reset_contact限定
- [ ] LINEのみの連絡後にお金を要求しようとするとブロックされる
- [ ] デートした翌日・翌々日はお金を要求できる
- [ ] デートから3ターン以上経過するとブロックされる

### カナ推しの人ルート
- [ ] ルートA: 信頼70以上・デート8回以上で「推しの人」になる
- [ ] ルートB: 信頼65以上・SNSリスク15以上で「推しの人」になる（美咲バレリスク上昇）
- [ ] ルートC: 信頼80以上で「推しの人」になる
- [ ] ルートによって演出が変わる
- [ ] ルートBでは美咲への疑念が蓄積される

---

*phase3_v1.3_fixes.md - 2026年3月1日作成*
