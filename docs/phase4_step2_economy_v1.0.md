# ヒモ男シミュレーター Phase 4 ステップ2 実装指示書 v1.0

## 経済圏システム: 美咲の対面お金交渉＋カナの交換経済

**前提**: Phase 4 ステップ1 v1.6が実装・テスト完了済みであること  
**参照設計書**: `docs/character_economy_and_energy_design.md`  
最終更新日: 2026年3月15日

---

## 概要

このステップでは2つの経済システムを実装する。

1. **美咲の対面お金交渉ゲーム**: デート中に3段階の会話で中〜大額を引き出す
2. **カナの交換経済モデル**: 現物恩恵（食事・泊まり・魅力UP）と引き換えに時間・束縛・エナ期待を支払う

エナジーシステム本体はステップ3で実装するが、カナの泊まりイベントで「エナ期待の匂わせ」演出だけ先行して入れる。

---

## 変更対象ファイル一覧

| ファイル | 変更種別 | 内容 |
|---|---|---|
| `data/variables.rpy` | 追加 | 新規変数（週間要求カウント・カナ経済統計） |
| `data/constants.rpy` | 追加 | 交渉・交換経済の閾値定数 |
| `systems/parameter_system.rpy` | 追加 | 週間カウントリセット・搾取スコア計算 |
| `systems/time_system.rpy` | 修正 | advance_day()に週間リセット・搾取チェック追加 |
| `events/misaki_events.rpy` | 追加 | 対面交渉ラベル群 |
| `events/date_misaki_places.rpy` | 修正 | デート中に「お金の話を切り出す」メニュー追加 |
| `events/kana_events.rpy` | 追加 | 交換経済・ご機嫌取りQTE・疑念イベント |
| `events/date_kana_places.rpy` | 修正 | カナデート後の泊まり判定追加 |
| `events/midgame_events.rpy` | 追加 | カナ版疑念イベントの発動チェック |
| `systems/gokiragen_qte.rpy` | **新規** | ご機嫌取りQTEシステム |

---

## Part 1: 新規変数

### `data/variables.rpy` に追加

```python
# === 美咲の対面交渉 ===
default money_request_weekly = {
    "count": 0,              # 週間お金要求回数（LINE＋対面合算）
    "last_reset_day": 1      # 最後にリセットした日
}

# === カナの交換経済 ===
# stats 辞書に以下のキーを追加する
# ※ default stats の中に追記すること
#   "kana_benefits_received": 0,    # カナから恩恵を受けた回数
#   "kana_ena_given": 0,            # カナにエナを使った回数（ステップ3で使用。今は0固定）
#   "kana_gokiragen_success": 0,    # ご機嫌取り成功回数
#   "kana_gokiragen_failed": 0,     # ご機嫌取り失敗回数
#   "kana_stayed_over": 0,          # カナの部屋に泊まった回数

# === ご機嫌取りQTE用フラグ ===
# daily_flags に以下のキーを追加する（advance_day()でリセット対象に含める）
#   "kana_mood_resolved": False     # その日のご機嫌取りが済んだか
```

### `data/constants.rpy` に追加

```python
# === 美咲の対面交渉 ===
define NEGOTIATION_WEEKLY_LIMIT = 4          # 週4回以上で拒否率大幅UP
define NEGOTIATION_PENALTY_2ND = 10          # 2回目の成功率ペナルティ（%）
define NEGOTIATION_PENALTY_3RD = 25          # 3回目の成功率ペナルティ（%）

define NEGOTIATION_AMOUNT_LOW = (5000, 10000)
define NEGOTIATION_AMOUNT_MID = (10000, 15000)
define NEGOTIATION_AMOUNT_HIGH = (15000, 30000)

define NEGOTIATION_LOCATION_BONUS = {
    "famires": 0,      # ファミレス: 補正なし。大額選択不可
    "izakaya": 15,     # 居酒屋: +15%。翌日疑念+2リスク
    "room": 10,        # 美咲の部屋: +10%。依存度影響大
    "fancy": 20,       # いい店（自腹後）: +20%。信頼減少緩和
    "himo_room": 5     # ヒモ太郎の部屋: +5%
}

# === カナの交換経済 ===
define KANA_EXPLOITATION_THRESHOLD = 15      # 搾取スコアがこれ以上でカナ版疑念イベント
define KANA_GOKIRAGEN_TIME_LIMIT = 8.0       # ご機嫌取りQTEの制限時間（秒）

# === カナの泊まり恩恵 ===
define KANA_STAY_STAMINA = 40
define KANA_STAY_CLEANLINESS = 30
define KANA_STAY_DEPENDENCE = 8
define KANA_STAY_TRUST = 3
```

---

## Part 2: 美咲の対面お金交渉ゲーム

### 概要

デート中のメニューに「お金の話を切り出す」を追加。3段階の会話ゲームで、嘘パズルと同様のscreen資産（タイマー表示）を流用する。

### LINE経由との棲み分け

既存の `misaki_money_request`（LINE経由）はそのまま残す。対面交渉はデート中のみ発生し、LINE経由より高額だがリスクも高い。両方の回数が `money_request_weekly["count"]` に合算される。

### 2-1. デートメニューへの統合

**ファイル**: `events/date_misaki_places.rpy`

各デート場所ラベル（`misaki_date_famires` / `misaki_date_izakaya` / `misaki_date_room` / `misaki_date_fancy`）の**末尾**（return直前）に、以下の共通メニューを挿入する。

```python
    # === 対面交渉の切り出しチャンス（各デート場所ラベルの return 直前に挿入）===
    # 条件: 信頼35以上、今週4回未満、今日まだ要求していない
    if misaki["trust"] >= 35 and money_request_weekly["count"] < NEGOTIATION_WEEKLY_LIMIT and not daily_flags.get("asked_money_today", False):
        menu:
            "会話が落ち着いてきた。"

            "お金の話を切り出す":
                call misaki_negotiation_start

            "このまま楽しむ":
                pass
```

**注意**: `misaki_date_famires` では大額選択肢を表示しない制御がある（後述の第3段階で対応）。

### 2-2. 交渉ラベル群

**ファイル**: `events/misaki_events.rpy` に追加

#### 第1段階: 切り出し方

```python
label misaki_negotiation_start:
    # 週間カウント加算
    $ money_request_weekly["count"] += 1
    $ daily_flags["asked_money_today"] = True
    $ himo_aptitude["money_requests"] += 1

    # 週間カウントに応じた美咲の反応分岐
    python:
        weekly_count = money_request_weekly["count"]

    if weekly_count >= 4:
        # 4回目以上: 高確率拒否
        call misaki_negotiation_refuse
        return

    # 切り出し方の選択
    menu:
        "どう切り出す？"

        "「なあ、ちょっとお金の話なんだけど...」":
            # 直球。成功率低め
            $ _nego_approach = "direct"
            $ _nego_base_rate = 40
            $ change_trust(-3)
            himo "なあ、ちょっとお金の話なんだけど..."

        "「最近ほんとにヤバくてさ...」":
            # 泣き落とし。依存度依存
            $ _nego_approach = "sob"
            $ _nego_base_rate = 30 + int(misaki["dependence"] * 0.4)
            himo "最近ほんとにヤバくてさ..."

        "「実はさ、今月の家賃がちょっと...」" if misaki["trust"] >= 50:
            # 具体的。成功率中
            $ _nego_approach = "specific"
            $ _nego_base_rate = 55
            himo "実はさ、今月の家賃がちょっと..."

        "「美咲に相談したいことがあるんだけど」" if misaki["trust"] >= 50:
            # 信頼してる感。成功率中〜高
            $ _nego_approach = "consult"
            $ _nego_base_rate = 65
            himo "美咲に相談したいことがあるんだけど"

        "「俺、ちゃんと就活も考えてて。でも今月だけ」" if misaki["trust"] >= 70:
            # 将来性アピール。成功率高
            $ _nego_approach = "future"
            $ _nego_base_rate = 75
            himo "俺、ちゃんと就活も考えてて。でも今月だけ..."

        "...（やっぱりやめる）":
            himo "（...やっぱり言えなかった）"
            # カウントを戻す
            $ money_request_weekly["count"] -= 1
            $ daily_flags["asked_money_today"] = False
            $ himo_aptitude["money_requests"] -= 1
            return

    # 第2段階へ
    call misaki_negotiation_reaction
    return
```

#### 第2段階: 反応を見て押すか引くか

```python
label misaki_negotiation_reaction:
    # 成功率計算: ベース + 場所補正 - 週間ペナルティ - 疑念ペナルティ
    python:
        location = daily_flags.get("date_location", "famires")
        location_bonus = NEGOTIATION_LOCATION_BONUS.get(location, 0)

        weekly_count = money_request_weekly["count"]
        if weekly_count == 2:
            weekly_penalty = NEGOTIATION_PENALTY_2ND
        elif weekly_count >= 3:
            weekly_penalty = NEGOTIATION_PENALTY_3RD
        else:
            weekly_penalty = 0

        suspicion_penalty = suspicion.get("misaki", 0) * 3

        _nego_success_rate = _nego_base_rate + location_bonus - weekly_penalty - suspicion_penalty
        _nego_success_rate = max(5, min(95, _nego_success_rate))

    # 美咲の反応テキスト（信頼度・週間回数で変化）
    if misaki["trust"] >= 60 and weekly_count <= 1:
        # 好反応
        misaki_c "え、大丈夫？ いくら必要？"
        $ _nego_reaction = "positive"
    elif misaki["trust"] >= 40 or weekly_count <= 2:
        # 微妙な反応
        if weekly_count >= 2:
            misaki_c "また...？ ちゃんと仕事探してる？"
        else:
            misaki_c "...うん、どうしたの？"
        $ _nego_reaction = "neutral"
    else:
        # 拒否寄り反応
        misaki_c "...ねえ、私のこと何だと思ってる？"
        $ _nego_reaction = "negative"

    # 押す/引くの選択
    menu:
        "「...」":
            pass

        "押す（お金を頼む）" if _nego_reaction != "negative":
            call misaki_negotiation_amount
            return

        "控えめに頼む" if _nego_reaction == "positive":
            # 少額で確定成功
            python:
                amount = renpy.random.randint(3000, 5000)
            misaki_c "...はい、これ"
            "美咲から¥[amount:,]をもらった。"
            $ change_money(amount, "美咲（対面交渉・控えめ）")
            $ change_trust(-1)
            $ change_dependence(5)
            $ stats["total_earned"] += amount
            return

        "引く（話題を変える）":
            himo "いや、やっぱいい。気にしないで"
            if _nego_reaction == "negative":
                misaki_c "...そう"
                "気まずい空気が流れた。"
                $ add_suspicion("too_many_requests")
            else:
                misaki_c "...ほんとに？ 困ったら言ってね"
                $ change_trust(2)
            return

        "強引に頼む" if _nego_reaction == "negative":
            # 修羅場リスク
            himo "頼むって、マジで困ってんだよ"
            misaki_c "..."
            python:
                # 30%の確率で修羅場に発展
                if renpy.random.random() < 0.30:
                    renpy.call("misaki_negotiation_shuraba")
                else:
                    # 渋々了承
                    amount = renpy.random.randint(3000, 8000)
                    change_money(amount, "美咲（対面交渉・強引）")
                    change_trust(-8)
                    change_dependence(3)
                    add_suspicion("too_many_requests")
            if _nego_reaction == "negative":
                misaki_c "...分かった。でも、もうこれ最後にして"
                "美咲から¥[amount:,]をもらった。"
            return

    return


label misaki_negotiation_refuse:
    # 週4回以上の場合の拒否イベント
    misaki_c "...ヒモ太郎"
    misaki_c "最近、お金のことばっかりだよね"
    himo "..."
    misaki_c "私、ATMじゃないよ？"

    menu:
        "何と言う？"

        "謝る":
            himo "...ごめん。調子に乗りすぎた"
            misaki_c "...分かった。でも、ちょっと考えて"
            $ change_trust(-5)
            $ add_suspicion("too_many_requests")
            $ himo_aptitude["honest_moments"] += 1

        "誤魔化す":
            himo "そんなつもりじゃ..."
            misaki_c "...そうかな"
            "美咲の目が冷たい。"
            $ change_trust(-10)
            $ add_suspicion("too_many_requests")
            $ himo_aptitude["lies"] += 1
            $ stats["lies_told"] += 1

    return
```

#### 第3段階: 金額提示

```python
label misaki_negotiation_amount:
    python:
        location = daily_flags.get("date_location", "famires")

    menu:
        "いくら頼む？"

        "控えめに（¥5,000〜10,000）":
            $ _nego_amount_type = "low"
            $ _nego_range = NEGOTIATION_AMOUNT_LOW

        "普通に（¥10,000〜15,000）" if location != "famires":
            # ファミレスでは中額以上は不自然
            $ _nego_amount_type = "mid"
            $ _nego_range = NEGOTIATION_AMOUNT_MID

        "思い切って（¥15,000〜30,000）" if location not in ["famires", "himo_room"]:
            # ファミレス・ヒモ太郎の部屋では大額不可
            $ _nego_amount_type = "high"
            $ _nego_range = NEGOTIATION_AMOUNT_HIGH

    # 成功判定
    python:
        # 金額タイプによる成功率補正
        amount_penalty = {"low": 0, "mid": -10, "high": -25}
        final_rate = _nego_success_rate + amount_penalty.get(_nego_amount_type, 0)
        final_rate = max(5, min(95, final_rate))

        success = renpy.random.random() * 100 < final_rate

    if success:
        python:
            amount = renpy.random.randint(_nego_range[0], _nego_range[1])
        misaki_c "...分かった。これ、使って"
        "美咲から¥[amount:,]をもらった。"

        $ change_money(amount, "美咲（対面交渉）")
        $ stats["total_earned"] += amount

        # パラメータ変動（金額タイプで変化）
        if _nego_amount_type == "low":
            $ change_trust(-2)
            $ change_dependence(5)
            $ suspicion["misaki"] = suspicion.get("misaki", 0) + 1
        elif _nego_amount_type == "mid":
            $ change_trust(-4)
            $ change_dependence(8)
            $ suspicion["misaki"] = suspicion.get("misaki", 0) + 2
        else:
            $ change_trust(-6)
            $ change_dependence(12)
            $ suspicion["misaki"] = suspicion.get("misaki", 0) + 3

        # 居酒屋ボーナス使用時の翌日リスク
        if location == "izakaya":
            $ flags["izakaya_money_hangover"] = True
            # ← advance_day()で翌日「酔ってる時に頼むのズルい」疑念+2を処理

    else:
        # 失敗
        misaki_c "...ごめん、今月厳しくて"
        himo "そっか..."
        $ change_trust(-3)
        $ add_suspicion("too_many_requests")

    return


label misaki_negotiation_shuraba:
    # 強引に頼んで修羅場に発展した場合
    misaki_c "...ヒモ太郎"
    misaki_c "私、ずっと我慢してたんだけど"
    misaki_c "お金のことばっかり言われると、利用されてるみたいで..."

    "美咲の目に涙が浮かんでいる。"

    # 嘘パズルに発展（高難度）
    call run_lie_puzzle("money_shuraba", "misaki")

    return
```

### 2-3. 週間カウントのリセット

**ファイル**: `systems/time_system.rpy`

`advance_day()` に以下を追加する。

```python
    # === 美咲の対面交渉: 週間カウントリセット ===
    if (game_date["day"] - money_request_weekly["last_reset_day"]) >= 7:
        money_request_weekly["count"] = 0
        money_request_weekly["last_reset_day"] = game_date["day"]

    # === 居酒屋ボーナスの翌日リスク ===
    if flags.get("izakaya_money_hangover", False):
        flags["izakaya_money_hangover"] = False
        suspicion["misaki"] = suspicion.get("misaki", 0) + 2
        # 翌日の美咲連絡時に「昨日酔ってたからって...」テキストを出す
        # ※ これは misaki_events.rpy の contact_misaki で izakaya_money_hangover 済みを判定
```

### 2-4. LINE経由のお金要求にも週間カウント連動

**ファイル**: `events/misaki_events.rpy`

既存の `misaki_money_request` ラベルの先頭付近で `money_request_weekly["count"]` を加算する。

```python
label misaki_money_request:
    # v1.6: 1日1回制限（既存）
    if daily_flags.get("asked_money_today", False):
        himo "...さっきもらったばかりだし、今日はやめとこう"
        return

    # ステップ2追加: 週間カウント加算
    $ money_request_weekly["count"] += 1

    # 週4回以上はLINEでも反応が変わる
    if money_request_weekly["count"] >= NEGOTIATION_WEEKLY_LIMIT:
        misaki_c "...最近、お金のことばっかりだね"
        himo "（ヤバい、頼みすぎた）"
        $ add_suspicion("too_many_requests")
        return

    # 以下、既存の処理を続行
    himo "実は...お金が厳しくて"
    # ...（既存コードそのまま）
```

---

## Part 3: カナの交換経済モデル

### 概要

カナは金をくれない。代わりに生活インフラ（食事・泊まり・シャワー・魅力UP）を提供する。対価は「時間」「束縛（依存度上昇）」「エナ期待（ステップ3で本格化）」。

### 3-1. カナの泊まりイベント

**ファイル**: `events/kana_events.rpy` に追加

カナデート後の夜に泊まり判定を挿入する。

```python
label kana_stay_offer:
    # カナデート後に呼ばれる。条件: 夜のデート＋信頼30以上
    if game_date["time"] != "night" or kana["trust"] < 30:
        return

    # 依存度で誘い方が変わる
    if kana["dependence"] >= 50:
        kana_c "今日泊まってくよね？"
        # 依存高: 半強制的
    elif kana["dependence"] >= 30:
        kana_c "泊まってく？"
    else:
        kana_c "もし良かったら...泊まってく？"

    menu:
        "泊まる":
            call kana_stay_event
            return

        "帰る":
            call kana_stay_decline
            return


label kana_stay_event:
    "カナの部屋に泊まることにした。"

    $ stats["kana_stayed_over"] = stats.get("kana_stayed_over", 0) + 1
    $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1

    # 恩恵
    $ change_stamina(KANA_STAY_STAMINA)
    $ change_cleanliness(KANA_STAY_CLEANLINESS)
    $ change_trust_kana(KANA_STAY_TRUST)
    $ change_dependence_kana(KANA_STAY_DEPENDENCE)
    $ daily_flags["ate_today"] = True

    # 泊まりフラグ（翌朝消費用）
    $ flags["staying_at_kana"] = True

    # === エナ期待の匂わせ（ステップ3で本格化）===
    "..."
    "カナがくっついてきた。"

    # ステップ3ではここでエナマッチが発生する。
    # 今は暗転＋事後会話で処理。
    "一緒に過ごした。"

    kana_c "...えへへ"

    "カナが幸せそうに笑った。"

    # 翌朝の演出用フラグ
    $ flags["kana_morning_after"] = True

    return


label kana_stay_decline:
    # 帰る場合。依存度で反応が変わる
    if kana["dependence"] >= 60:
        kana_c "...なんで？"
        "カナの声が少し震えている。"
        $ change_trust_kana(-5)
        $ suspicion["kana"] = suspicion.get("kana", 0) + 2

        # ご機嫌取りQTE発動（依存60以上で断った場合）
        if not daily_flags.get("kana_mood_resolved", False):
            call gokiragen_qte_start
    elif kana["dependence"] >= 30:
        kana_c "え〜、帰るの？"
        $ change_trust_kana(-3)
    else:
        kana_c "そっか〜"
        $ change_trust_kana(-1)

    return
```

### 3-2. カナ泊まり翌朝イベント

**ファイル**: `events/daily_events.rpy`

`check_forced_morning_event` に追加する。

```python
    # イベント: カナ宅泊まり翌朝
    if flags.get("kana_morning_after", False):
        $ flags["kana_morning_after"] = False
        $ flags["staying_at_kana"] = False
        call kana_morning_after_event
        $ flags["morning_consumed"] = True
        return
```

```python
label kana_morning_after_event:
    scene bg_placeholder

    "カナの部屋で目が覚めた。"
    "隣でカナがまだ寝ている。"

    kana_c "...んん"
    kana_c "おはよ..."

    "カナが朝ごはんを作ってくれた。"

    $ daily_flags["ate_today"] = True
    $ change_stamina(15)   # 追加の朝食回復

    # 匂わせテキスト（ステップ3への伏線）
    kana_c "...昨日、ありがとう"
    kana_c "また泊まりに来てね"

    himo "（泊まるたびに"期待"されてる気がする...）"
    himo "（まあ、今はいっか）"

    "気づいたら昼になっていた。"
    "（朝の時間が消えた）"

    return
```

### 3-3. カナの恩恵追跡

既存の `kana_visit` ラベルで恩恵を受けた際にカウントする。

**ファイル**: `events/kana_events.rpy`

`kana_visit` 内の食事・シャワー等の処理に追加:

```python
    # 食事を受けた場合（既存のchange_stamina等の後に追加）
    $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1

    # シャワーを借りた場合（同様）
    $ stats["kana_benefits_received"] = stats.get("kana_benefits_received", 0) + 1
```

### 3-4. カナデート後の泊まり誘いの統合

**ファイル**: `events/date_kana_places.rpy`

`kana_date_with_location` の共通処理（デート場所選択後、`check_date_incidents` の前）に泊まり判定を挿入:

```python
    # デート後の共通処理（既存）
    $ kana["met_today"] = True
    $ kana["last_contact"] = 0
    $ daily_flags["date_with"] = "kana"
    $ daily_flags["ate_today"] = True

    # 探り・地雷・ハプニング（既存）
    call check_date_incidents("kana")

    # === ステップ2追加: 夜デートの場合、泊まり判定 ===
    if game_date["time"] == "night" and kana["trust"] >= 30:
        call kana_stay_offer

    return
```

---

## Part 4: ご機嫌取りQTEシステム

### 概要

嘘パズルの亜種。「嘘をつく」のではなく「カナの承認欲求を満たす」選択肢を制限時間内に選ぶ。2〜3段階の会話で構成。

### 新規ファイル: `systems/gokiragen_qte.rpy`

```python
# gokiragen_qte.rpy
# カナのご機嫌取りQTE — 承認欲求を満たす会話ゲーム

init python:
    def calculate_gokiragen_result(choices):
        """ご機嫌取りの結果を計算する
        choices: list of ("good"/"ok"/"bad") — 各段階の選択結果
        """
        good_count = choices.count("good")
        bad_count = choices.count("bad")

        if bad_count >= 2:
            return "critical_fail"
        elif bad_count >= 1:
            return "fail"
        elif good_count >= 2:
            return "success"
        else:
            return "partial"


label gokiragen_qte_start:
    $ daily_flags["kana_mood_resolved"] = True
    $ _gokiragen_choices = []

    "カナの機嫌が悪い。"

    # === 第1段階 ===
    kana_c "私のこと好き？"

    # タイマー付き選択（KANA_GOKIRAGEN_TIME_LIMIT 秒）
    # ※ テスト時は renpy.is_in_test() でタイマーをスキップ
    $ _gokiragen_timer = KANA_GOKIRAGEN_TIME_LIMIT

    menu:
        "「好きだよ」":
            # 普通。次の段階へ
            kana_c "...ほんとに？"
            $ _gokiragen_choices.append("ok")

        "「一番好きだよ」":
            # 強い。成功寄り
            kana_c "...うれしい"
            $ _gokiragen_choices.append("good")

        "「まあまあ？」":
            # 地雷
            kana_c "は？"
            $ _gokiragen_choices.append("bad")

    # === 第2段階 ===
    kana_c "じゃあなんで帰るの？"

    menu:
        "「今日は本当に疲れてて」":
            # 体力が実際に低い場合は真実扱い
            if player["stamina"] < 30:
                kana_c "...そうなんだ。無理しないで"
                $ _gokiragen_choices.append("good")
            else:
                kana_c "...ほんとに？元気そうだけど"
                $ _gokiragen_choices.append("ok")

        "「お前のこと大事にしたいから」":
            # 上手い切り返し
            kana_c "..."
            kana_c "...なにそれ。ズルい"
            $ _gokiragen_choices.append("good")

        "「めんどくさい」":
            # 即死級地雷
            kana_c "..."
            "カナが黙った。"
            $ _gokiragen_choices.append("bad")

    # === 第3段階（第2段階でbadがあった場合のみ）===
    if "bad" in _gokiragen_choices:
        kana_c "...もういい"
        "カナが背を向けた。"

        menu:
            "追いかける":
                himo "待って、ごめん。本気じゃなかった"
                kana_c "...ほんとに？"
                $ _gokiragen_choices.append("ok")

            "放っておく":
                "カナはそのまま黙ってしまった。"
                $ _gokiragen_choices.append("bad")

    # === 結果判定 ===
    python:
        result = calculate_gokiragen_result(_gokiragen_choices)

    if result == "success":
        kana_c "...もう。ヒモ太郎のバカ"
        "カナが笑った。機嫌は直ったようだ。"
        $ change_trust_kana(2)
        $ stats["kana_gokiragen_success"] = stats.get("kana_gokiragen_success", 0) + 1

    elif result == "partial":
        kana_c "...まあいいけど"
        "完全には納得していないが、落ち着いたようだ。"
        $ change_trust_kana(-1)
        $ stats["kana_gokiragen_success"] = stats.get("kana_gokiragen_success", 0) + 1

    elif result == "fail":
        kana_c "...口だけじゃん"
        "カナの機嫌は直らなかった。"
        $ change_trust_kana(-5)
        $ change_dependence_kana(-3)
        $ stats["kana_gokiragen_failed"] = stats.get("kana_gokiragen_failed", 0) + 1

    else:  # critical_fail
        kana_c "もう帰って"
        "カナに追い出された。"
        $ change_trust_kana(-10)
        $ change_dependence_kana(-5)
        $ suspicion["kana"] = suspicion.get("kana", 0) + 3
        $ stats["kana_gokiragen_failed"] = stats.get("kana_gokiragen_failed", 0) + 1

    return
```

### テスト対応

`renpy.is_in_test()` チェックを追加して、自動テスト時はタイマーをスキップする。

```python
# gokiragen_qte.rpy のメニュー表示前に追加
if renpy.is_in_test():
    $ _gokiragen_timer = 9999  # テスト時はタイムアウトしない
```

---

## Part 5: カナ版疑念イベント「都合いい女だと思ってない？」

### 搾取スコアの計算

**ファイル**: `systems/parameter_system.rpy` に追加

```python
init python:
    def calculate_kana_exploitation():
        """カナの搾取スコアを計算する。閾値を超えたら疑念イベント発動"""
        score = 0
        score += stats.get("kana_benefits_received", 0) * 2
        score -= stats.get("kana_ena_given", 0) * 3          # ステップ3で値が入る
        score -= stats.get("kana_gokiragen_success", 0) * 2
        return score
```

### 発動チェック

**ファイル**: `events/midgame_events.rpy`

`check_midgame_events()` に追加する。

```python
    # === カナ版疑念イベント ===
    if (kana_flags.get("met", False)
        and not flags.get("kana_doubt_event_done", False)
        and game_date["day"] >= 15
        and calculate_kana_exploitation() >= KANA_EXPLOITATION_THRESHOLD):
        return ("kana_doubt_event", "turn_consuming")
```

### イベント本体

**ファイル**: `events/kana_events.rpy` に追加

```python
label kana_doubt_event:
    scene bg_placeholder

    "カナと過ごしている時、急にカナが黙り込んだ。"

    kana_c "...ねえ"
    himo "ん？"

    kana_c "私のこと、都合のいい女だと思ってない？"

    himo "え？"

    kana_c "ご飯も作ったし、泊めてあげたし"
    kana_c "でもヒモ太郎は...私のこと大事にしてくれてる？"

    "カナの目に涙が浮かんでいる。"

    kana_c "前の彼氏もそうだった"
    kana_c "優しいフリして、利用してただけ"

    kana_c "ヒモ太郎は...違うよね？"

    # ※ kana_friend_info_obtained フラグ（大学付近デートで入手した情報）を
    # 持っているプレイヤーは、カナの地雷（過去の浮気被害）を理解している。
    # 持っていない場合は地雷を踏みやすい。

    menu:
        "何と答える？"

        "正直に認める":
            himo "...正直に言うと、甘えすぎてた"
            kana_c "...最低"

            "カナが泣き出した。"

            himo "でも、お前のこと嫌いじゃない。それは本当"
            kana_c "...嘘"
            himo "嘘じゃない"

            "長い沈黙。"

            kana_c "...正直に言ってくれたから、許す"
            kana_c "でも次やったら、もう知らないから"

            $ change_trust_kana(-15)
            $ suspicion["kana"] = 0     # 疑念リセット
            $ himo_aptitude["honest_moments"] += 2
            $ flags["kana_doubt_event_done"] = True

        "ご機嫌取りQTE（3段階・高難度）":
            call gokiragen_qte_doubt
            $ flags["kana_doubt_event_done"] = True

        "逆ギレする":
            himo "はあ？ 俺が何したってんだよ"
            kana_c "..."

            "カナが黙った。目に涙が溜まっている。"

            kana_c "...最低"

            "カナがスマホを取り出した。"

            $ change_trust_kana(-25)
            $ kana_flags["sns_risk"] = kana_flags.get("sns_risk", 0) + 10
            $ flags["kana_doubt_event_done"] = True

            himo "（やばい、SNSに書かれるかも...）"

    return


label gokiragen_qte_doubt:
    # 疑念イベント版のご機嫌取りQTE（高難度・3段階固定）
    $ _gokiragen_choices = []

    # 第1段階
    kana_c "...本当に私のこと好き？"

    menu:
        "「好きだよ」":
            kana_c "...何回も聞いた。その言葉"
            $ _gokiragen_choices.append("ok")

        "「好きじゃなかったら、こうやって一緒にいない」":
            kana_c "..."
            "カナが少し考え込んだ。"
            $ _gokiragen_choices.append("good")

    # 第2段階
    kana_c "じゃあ、私がご飯作らなくても泊めなくても、会ってくれる？"

    menu:
        "「当たり前だろ」":
            if stats.get("kana_benefits_received", 0) > stats.get("kana_stayed_over", 0) * 3:
                # 恩恵を受けすぎている場合、説得力がない
                kana_c "...嘘。毎回ご飯食べに来てるじゃん"
                $ _gokiragen_choices.append("bad")
            else:
                kana_c "...ほんと？"
                $ _gokiragen_choices.append("good")

        "「...正直、助かってる。でもそれだけじゃない」":
            kana_c "..."
            $ _gokiragen_choices.append("good")

        "「それは...」":
            kana_c "...やっぱりそうなんだ"
            $ _gokiragen_choices.append("bad")

    # 第3段階
    kana_c "私、次に裏切られたら、もう立ち直れないと思う"

    menu:
        "「裏切らない」":
            $ _gokiragen_choices.append("ok")

        "「俺は前の彼氏とは違う」" if flags.get("kana_friend_info_obtained", False):
            # 大学付近デートで情報を得ていた場合のみ選択可能
            kana_c "...！"
            "カナが驚いた顔をした。"
            kana_c "...知ってたの"
            $ _gokiragen_choices.append("good")

        "「約束はできない」":
            kana_c "...そっか"
            $ _gokiragen_choices.append("bad")

    # 結果判定
    python:
        result = calculate_gokiragen_result(_gokiragen_choices)

    if result in ["success", "partial"]:
        kana_c "...信じるから"
        "カナが涙を拭いた。"
        if result == "success":
            $ change_trust_kana(-5)      # 正直ルートほどのダメージはない
        else:
            $ change_trust_kana(-8)
        $ suspicion["kana"] = max(0, suspicion.get("kana", 0) - 5)
        $ stats["kana_gokiragen_success"] = stats.get("kana_gokiragen_success", 0) + 1
    else:
        kana_c "...もういい"
        "カナが部屋に引っ込んだ。"
        $ change_trust_kana(-15)
        $ change_dependence_kana(-8)
        $ stats["kana_gokiragen_failed"] = stats.get("kana_gokiragen_failed", 0) + 1

    return
```

---

## Part 6: advance_day() への統合

**ファイル**: `systems/time_system.rpy`

`advance_day()` に以下を追加する（既存処理の後に追記）。

```python
    # === ステップ2追加: daily_flags リセット対象 ===
    daily_flags["kana_mood_resolved"] = False

    # === ステップ2追加: 週間お金要求カウントのリセット ===
    if (game_date["day"] - money_request_weekly["last_reset_day"]) >= 7:
        money_request_weekly["count"] = 0
        money_request_weekly["last_reset_day"] = game_date["day"]

    # === ステップ2追加: 居酒屋ボーナスの翌日リスク ===
    if flags.get("izakaya_money_hangover", False):
        flags["izakaya_money_hangover"] = False
        suspicion["misaki"] = suspicion.get("misaki", 0) + 2
```

---

## Part 7: flags への追加

**ファイル**: `data/variables.rpy`

`flags` 辞書に以下を追加:

```python
    "izakaya_money_hangover": False,
    "staying_at_kana": False,
    "kana_morning_after": False,
    "kana_doubt_event_done": False,
```

---

## テスト確認項目

### 美咲の対面交渉
- [ ] デート中のメニューに「お金の話を切り出す」が表示される（信頼35以上）
- [ ] ファミレスでは「思い切って」（大額）が選べない
- [ ] 居酒屋で成功した翌日に疑念+2が発生する
- [ ] 週2回目の要求で「また？」と言われる
- [ ] 週3回目の要求で成功率が大幅に下がる
- [ ] 週4回以上で「ATMじゃない」拒否イベントが発生する
- [ ] LINE経由のお金要求も週間カウントに含まれる
- [ ] 「やっぱりやめる」でカウントが戻る
- [ ] 強引に頼む→修羅場→嘘パズルの連鎖が動作する

### カナの交換経済
- [ ] 夜デート後に泊まり誘いが発生する（信頼30以上）
- [ ] 泊まると翌朝が消費される（朝の時間が消える）
- [ ] 泊まり翌朝に食事・体力回復が入る
- [ ] 泊まりを断ると依存度に応じた反応が変わる
- [ ] 依存60以上で断るとご機嫌取りQTEが発動する
- [ ] 食事・シャワー利用時にbenefits_receivedがカウントされる

### ご機嫌取りQTE
- [ ] 2〜3段階の選択肢が順番に表示される
- [ ] 「めんどくさい」等の地雷選択で結果が悪化する
- [ ] success/partial/fail/critical_failの4段階で結果が変わる
- [ ] critical_failでカナに追い出される

### カナ版疑念イベント
- [ ] 搾取スコアが閾値（15）を超えると発動する
- [ ] 15日目以降にのみ発動する
- [ ] 正直に認める→信頼DOWN大きいが疑念リセット
- [ ] ご機嫌取りQTE（高難度版）が動作する
- [ ] kana_friend_info_obtainedフラグで追加選択肢が出る
- [ ] 逆ギレ→SNSリスク+10が正しく反映される
- [ ] 1回のみ発動し、再発動しない

### デバッグログ
- [ ] クリア時サマリーにカナ経済統計（benefits_received, stayed_over等）が出力される
- [ ] 週間お金要求カウントがログに記録される

---

## 今後のステップ3（エナジーシステム）への接続点

このステップで以下の「フック」を設置済み:

| フック | 場所 | ステップ3での役割 |
|---|---|---|
| `kana_stay_event` の暗転部分 | kana_events.rpy | エナマッチ（リズムゲーム）に差し替え |
| `stats["kana_ena_given"]` | variables.rpy | エナ使用回数のカウント→搾取スコア計算に使用 |
| `kana_stay_decline` のQTE発動 | kana_events.rpy | エナ不足時の分岐として本格化 |
| 匂わせテキスト | kana_morning_after_event | 「期待」がエナマッチとして具現化する伏線 |
| `flags["izakaya_money_hangover"]` | flags | 美咲のエナリンク効果（お金交渉成功率UP）に連動 |

---

*phase4_step2_economy_v1.0.md - 2026年3月15日作成*
