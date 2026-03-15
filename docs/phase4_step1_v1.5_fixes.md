# ヒモ男シミュレーター Phase 4 ステップ1 修正指示書 v1.5

**前提**: Phase 4 ステップ1 v1.4（session_report_20260315.md の追加修正含む）が実装済みであること  
最終更新日: 2026年3月15日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | 設計変更 | 体験版ENDを30日目の分岐に統合、K-05はフラグのみ | endings.rpy / script.rpy / kana_events.rpy |
| 2 | 機能追加 | 美咲への連絡に信頼度別の選択肢を追加 | misaki_events.rpy |

---

## 修正1: エンディング構造の再設計

### 現状の問題

K-05（カナ「俺のこと好き？」）の発生時にそのまま体験版ENDに流れるため、30日目のエンディング（GOOD/GRAY/NORMAL）に到達する前にゲームが終わる。家賃精算も行われず、体験版END以外のエンディングが見られない。

### 修正方針

K-05は**ストーリーイベント**として途中で発生するが、ゲームを終了させない。体験版ENDは30日目のエンディング分岐の一つとして統合する。

### エンディング判定フロー（修正後）

```
30日目夜 → ending_30days

  ① 家賃精算（¥53,000）
     → 払えない → BAD END（破滅）

  ② 払えた → 条件分岐（上から順に判定）

     → K-05完了（カナルート到達）
       → demo END（カナが麗子に言及＋製品版へ続く）

     → GOOD END条件（嘘3以下＋10回以上会った＋依存65未満＋気遣い5以上）
       → GOOD END（新しい関係）

     → GRAY END条件（依存65以上 or 嘘4以上）
       → GRAY END（ヒモへの道）

     → 上記いずれにも該当しない
       → NORMAL END（不安定な日々）
```

### ファイル: `events/kana_events.rpy`

K-05イベントのラベル末尾を修正。ゲーム終了処理を削除し、フラグのみ立てる。

```python
label k05_do_you_like_me:
    # （既存のK-05イベント内容はそのまま維持）
    # カナ「俺のこと好き？」の一連のシーン

    # ...（既存の会話・選択肢処理）...

    $ kana_flags["k05_done"] = True

    # v1.5修正: ゲーム終了処理を削除
    # 以下を削除:
    # call demo_ending
    # return（ゲーム終了）

    # 代わりに、K-05後の余韻テキストを追加
    "カナとの関係は、新しい段階に入った。"
    "でも、まだ月末まで日がある。"
    himo "（...どうなるんだろ、この先）"

    return
```

### ファイル: `script.rpy`

K-05トリガー箇所でゲーム終了処理を呼ばないようにする。

```python
# 既存のK-05トリガー（午後の行動内等）
# v1.5修正: K-05後に体験版ENDへのジャンプがあれば削除
# K-05はフラグを立てるだけで、ゲームは継続する

# 例: afternoon_actions 内のK-05トリガー
if ((kana["dependence"] >= 50 or kana_dates_count >= 12) and game_date["day"] >= 25 and not kana_flags["k05_done"]):
    call k05_do_you_like_me
    # v1.5修正: ここでreturnやjumpを入れない。通常フローに戻る
```

### ファイル: `events/endings.rpy`

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

    # === v1.5修正: エンディング分岐 ===
    python:
        is_honest = stats["lies_told"] <= 3
        is_dependent = misaki["dependence"] >= 65
        met_often = stats["times_met"] >= 10
        concern_shown = himo_aptitude["showed_concern"] >= 5
        kana_route_done = kana_flags.get("k05_done", False)

    # 優先順位1: カナルート到達 → demo END
    if kana_route_done:
        jump ending_demo

    # 優先順位2: GOOD END
    if is_honest and met_often and not is_dependent and concern_shown:
        jump ending_balance_30days

    # 優先順位3: GRAY END
    if is_dependent or not is_honest:
        jump ending_himou_30days

    # 優先順位4: NORMAL END
    jump ending_unstable_30days


# === v1.5追加: 体験版END ===

label ending_demo:
    $ flags["game_ended"] = True
    $ log_action("demo END")
    $ export_debug_log()
    scene bg_placeholder with fade

    centered "{size=40}エンディング: 始まりの予感{/size}"

    "30日が経った。"
    "家賃は何とか払えた。"
    "美咲との関係、カナとの関係。"
    "どちらも、どこへ向かうのか分からない。"

    "ある日、カナがふと言った。"

    kana_c "...ねえ、ほんとに私だけ？"
    himo "......"
    kana_c "まあいいけど。あ、そういえばさ"
    kana_c "麗子さんって人、ヒモ太郎のこと知ってるって言ってたよ？"
    himo "麗子？誰だそれ"
    kana_c "私も知らない。なんか大人っぽい感じの人"
    kana_c "ヒモ太郎のこと、『面白い』って言ってたって聞いたけど"

    "麗子――？"
    "心当たりはない。"
    "でも、なぜか気になった。"

    scene bg_placeholder with fade

    "俺のヒモ生活は、まだ始まったばかりだった――"

    centered "{size=30}体験版 END{/size}"
    centered "製品版へ続く"

    call show_himo_aptitude_result

    return
```

### 体験版ENDの条件についての補足

K-05の発生条件（`dependence >= 50 or kana_dates_count >= 12` かつ `day >= 25`）がそのまま体験版ENDの前提条件になる。カナとあまり関わらなかったプレイヤーはK-05が発生せず、美咲側のGOOD/GRAY/NORMAL ENDに到達する。

これにより:
- カナを深く攻略 → 体験版END（麗子の伏線で製品版への引き）
- 美咲を大事にプレイ → GOOD END
- ヒモ生活を満喫 → GRAY END
- どっちつかず → NORMAL END
- 金が足りない → BAD END

5つのENDが全て30日目で判定される。

---

## 修正2: 美咲への連絡に信頼度別の選択肢を追加

### 概要

カナの「写真送って」「なんか食べたい」「甘える」と同様に、美咲への連絡にも信頼度に応じた選択肢を追加する。美咲の性格（真面目・世話焼き・でも寂しい）に合わせた内容。

### ファイル: `events/misaki_events.rpy`

`contact_misaki` のメニュー部分を拡張。

```python
label contact_misaki:
    $ misaki["last_contact"] = 0

    "美咲にLINEを送った..."

    if misaki["trust"] >= 60:
        "すぐに返信が来た。"
    elif misaki["trust"] >= 40:
        "しばらくして返信が来た。"
    else:
        "既読スルーされた..."
        $ change_trust(-2)
        $ daily_flags["ignored_today"] = True
        $ daily_flags["misaki_lined_only"] = True
        return

    $ daily_flags["misaki_lined_only"] = True

    menu:
        misaki_c "どうしたの？"

        "雑談する":
            call misaki_chat
            return

        "会いたいと言う":
            call misaki_date_request
            return

        "お金の相談をする" if misaki["trust"] >= 35 and not daily_flags.get("misaki_lined_only_strict", False):
            # v1.5注: LINE経由のお金要求。misaki_money_request 内のガードで
            # misaki_lined_only チェックが入るため、イベント①直後はブロックされる
            call misaki_money_request
            return

        # === v1.5追加: 信頼度別の選択肢 ===

        "仕事の愚痴聞くよ" if misaki["trust"] >= 40:
            call misaki_line_listen_work

        "何か手伝えることある？" if misaki["trust"] >= 50:
            call misaki_line_offer_help

        "今日の夜、うちで飲まない？" if misaki["trust"] >= 55 and misaki["stage"] >= STAGE_CLOSE:
            call misaki_line_invite_home

        "声聞きたくなった" if misaki["trust"] >= 65:
            call misaki_line_miss_you

        "甘えていい？" if misaki["trust"] >= 75 and misaki["stage"] >= STAGE_DATING:
            call misaki_line_amaeru

    return


# === v1.5追加: 美咲LINE選択肢の各ラベル ===

label misaki_line_listen_work:
    himo "仕事どう？大変？"
    misaki_c "...聞いてくれるの？"
    misaki_c "実は最近、上司がさ..."

    "美咲の仕事の愚痴を30分くらい聞いた。"

    misaki_c "ごめんね、愚痴ばっかり"
    himo "いいって。いつでも聞くよ"
    misaki_c "...ありがとう"

    $ change_trust(4)
    $ change_dependence(3)
    $ himo_aptitude["showed_concern"] += 1

    return


label misaki_line_offer_help:
    himo "なんか手伝えることある？"
    misaki_c "え、急にどうしたの"
    himo "いや、なんとなく"

    misaki_c "...じゃあ、週末の買い出し付き合ってくれる？"

    menu:
        "いいよ":
            misaki_c "ほんと！？ありがとう"
            # 次の週末に美咲と約束
            python:
                current_day = game_date["day"]
                weekday_idx = game_date["weekday"]
                days_until_saturday = (6 - weekday_idx) % 7
                if days_until_saturday == 0:
                    days_until_saturday = 7
                appointments["misaki"] = current_day + days_until_saturday
            $ change_trust(5)
            $ change_dependence(4)
            $ himo_aptitude["showed_concern"] += 1
            "（週末に約束した）"

        "ちょっと考えさせて":
            misaki_c "...うん、いいよ"
            $ change_trust(1)

    return


label misaki_line_invite_home:
    himo "今日の夜さ、うちで飲まない？"

    python:
        import random
        # 信頼度と曜日で成功率変動
        base_rate = 0.50
        if misaki["trust"] >= 65:
            base_rate += 0.20
        if is_weekend():
            base_rate += 0.15
        invite_success = random.random() < base_rate

    if invite_success:
        misaki_c "え、いいの？...行く"
        $ flags["misaki_tonight"] = True
        $ daily_flags["kana_tonight_source"] = None  # 美咲の約束
        $ change_trust(3)
        $ change_dependence(5)
        "（今夜、美咲がうちに来ることになった）"
        "（...部屋片付けないと）"
        if player["cleanliness"] < 40:
            himo "（やばい、部屋汚い）"
    else:
        misaki_c "ごめん、今日はちょっと..."
        misaki_c "また今度ね"
        $ change_trust(1)  # 誘ったこと自体は好印象

    return


label misaki_line_miss_you:
    himo "なあ美咲"
    misaki_c "ん？"
    himo "声聞きたくなった"

    "少し間があった。"

    misaki_c "...もう、急にそういうこと言う"

    python:
        import random
        if misaki["dependence"] >= 50:
            # 依存度が高いと嬉しさが先に出る
            response = "happy"
        elif random.random() < 0.7:
            response = "happy"
        else:
            response = "shy"

    if response == "happy":
        misaki_c "...うれしい"
        misaki_c "私も、聞きたかった"
        $ change_trust(5)
        $ change_dependence(6)
    else:
        misaki_c "...恥ずかしいんだけど"
        $ change_trust(4)
        $ change_dependence(3)

    $ himo_aptitude["showed_concern"] += 1

    return


label misaki_line_amaeru:
    himo "美咲〜"
    misaki_c "なに？"
    himo "甘えていい？"

    misaki_c "...なにそれ"

    "でも、声は嬉しそうだった。"

    misaki_c "...しょうがないな"
    misaki_c "今夜、来る？"

    menu:
        "行く":
            $ flags["misaki_tonight"] = True
            misaki_c "...待ってる"
            $ change_trust(6)
            $ change_dependence(8)
            # 美咲のテンションが高い → デートの雰囲気が良くなる
            $ flags["misaki_good_mood_tonight"] = True

        "今日は無理、ごめん":
            misaki_c "...そっか"
            "甘えたのに行かない。ちょっと罪悪感。"
            $ change_trust(-2)
            $ change_dependence(3)

    return
```

### 選択肢の段階一覧

| 信頼度 | 選択肢 | 効果 | 追加条件 |
|---|---|---|---|
| 35以上 | お金の相談（既存） | お金を得る | LINE直後ブロック |
| 40以上 | 仕事の愚痴聞くよ | 信頼+4、依存+3、気遣い+1 | なし |
| 50以上 | 何か手伝えることある？ | 信頼+5、依存+4、週末約束 | なし |
| 55以上 | 今日の夜、うちで飲まない？ | 夜の約束（確率）、依存+5 | Stage CLOSE以上 |
| 65以上 | 声聞きたくなった | 信頼+5、依存+6、気遣い+1 | なし |
| 75以上 | 甘えていい？ | 夜の約束＋好ムード、依存+8 | Stage DATING |

### 設計意図

信頼度が上がるほど「甘え」系の選択肢が開放される。これがヒモの本質で、最初は「愚痴を聞く」という対等な関係から始まり、信頼が上がるにつれて「甘える」「声聞きたい」という搾取寄りの行動が可能になる。

ただしこれらは全て依存度も上がる。特に「甘えていい？」は依存+8で、GOOD END条件の「依存65未満」を脅かす。甘えすぎるとGRAY ENDに流れる構造。

プレイヤーは「信頼を上げたい（お金をもらうため）けど依存は上げたくない（GOOD ENDのため）」というジレンマを抱える。これが経済圏設計の対面交渉ゲームとも繋がる。

---

## テスト確認項目

### エンディング構造
- [ ] K-05発生後もゲームが継続する（30日目まで遊べる）
- [ ] K-05完了＋家賃払える → 体験版END（麗子の伏線テキスト）
- [ ] K-05未完了＋GOOD条件 → GOOD END
- [ ] K-05未完了＋GRAY条件 → GRAY END
- [ ] 家賃払えない → BAD END（K-05の状態に関わらず）
- [ ] 全ENDで家賃精算が行われる
- [ ] 全ENDでヒモ適性診断が表示される

### 美咲の選択肢
- [ ] 信頼40未満では新規選択肢が表示されない
- [ ] 信頼40以上で「仕事の愚痴聞くよ」が出る
- [ ] 信頼55以上＋Stage CLOSE以上で「うちで飲まない？」が出る
- [ ] 「うちで飲まない？」成功時に `misaki_tonight` が立つ
- [ ] 信頼75以上＋Stage DATING で「甘えていい？」が出る
- [ ] 「甘えていい？」→「行く」で夜の約束＋好ムードフラグが立つ
- [ ] 各選択肢の信頼・依存の上昇量が正しい

---

*phase4_step1_v1.5_fixes.md - 2026年3月15日作成*
