# endings.rpy
# エンディング（Phase 2: 30日版）

label day7_ending:
    # Phase 2ではこのラベルは使わない
    # main_loopの終了条件は GAME_DAYS = 30 に変更済み
    # ラベル名は互換性のため残しておく
    jump ending_30days

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


label ending_balance_30days:
    $ flags["game_ended"] = True
    $ _ending_type = "good"
    $ log_action("GOOD END")
    $ export_debug_log()
    $ export_dialogue_log()
    scene bg_placeholder with fade

    centered "{size=40}エンディング: 新しい関係{/size}"

    "30日目。"
    "気がついたら、ひと月が経っていた。"

    misaki_c "ヒモ太郎、最近ちょっと変わったよね"
    himo "え、そうか？"
    misaki_c "なんか...ちゃんと向き合ってくれる感じがして"
    himo "...そりゃまあ"

    "自分でもよくわからないけど、何かが変わった気がした。"
    "ヒモのままかもしれない。でも、美咲との関係は本物だと思う。"

    centered "{size=30}GOOD END{/size}"
    "「少し、前に進めた気がした」"

    call show_himo_aptitude_result

    return


label ending_himou_30days:
    $ flags["game_ended"] = True
    $ _ending_type = "gray"
    $ log_action("GRAY END")
    $ export_debug_log()
    $ export_dialogue_log()
    scene bg_placeholder with fade

    centered "{size=40}エンディング: ヒモへの道{/size}"

    "30日目。"
    "振り返ると、美咲に頼りっぱなしのひと月だった。"

    misaki_c "ねえ、ヒモ太郎って...私がいないとダメだよね？"
    himo "...そうかもな"
    misaki_c "...そっか"

    "美咲の顔には、愛情と、あと何か複雑な感情があった。"
    "この関係が、どこへ向かうのかわからない。"

    centered "{size=30}GRAY END{/size}"
    "「楽な道は、終わらない」"

    call show_himo_aptitude_result

    return


label ending_unstable_30days:
    $ flags["game_ended"] = True
    $ _ending_type = "normal"
    $ log_action("NORMAL END")
    $ export_debug_log()
    $ export_dialogue_log()
    scene bg_placeholder with fade

    centered "{size=40}エンディング: 不安定な日々{/size}"

    "30日目。"
    "なんとか生き延びた。"

    himo "まあ、何とかなったな"
    "でも、このままでいいのかという気持ちが消えない。"

    centered "{size=30}NORMAL END{/size}"
    "「不安定な自由が、まだ続く」"

    call show_himo_aptitude_result

    return


# === v1.5追加: 体験版END ===

label ending_demo:
    $ flags["game_ended"] = True
    $ _ending_type = "demo"
    $ log_action("demo END")
    $ export_debug_log()
    $ export_dialogue_log()
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


label ending_bankruptcy_30days:
    # === Phase 4 Step 2.5: 破滅END分岐 ===
    python:
        _misaki_rescue = (
            misaki["stage"] >= STAGE_DATING
            and misaki["trust"] > kana.get("trust", 0)
            and suspicion.get("misaki", 0) < 30
        )
        _kana_rescue = (
            kana_flags.get("met", False)
            and kana["stage"] >= STAGE_CLOSE
            and kana["trust"] > misaki["trust"]
            and suspicion.get("kana", 0) < 30
        )

    if _misaki_rescue:
        jump ending_bankruptcy_misaki_rescue
    elif _kana_rescue:
        jump ending_bankruptcy_kana_rescue
    else:
        jump ending_bankruptcy


# === 美咲居候END ===

label ending_bankruptcy_misaki_rescue:
    $ flags["game_ended"] = True
    $ _ending_type = "gray"
    $ log_action("BANKRUPTCY_MISAKI_RESCUE END")
    $ export_debug_log()
    $ export_dialogue_log()

    scene bg_placeholder with fade
    centered "{size=40}エンディング: 居候{/size}"

    "家賃が払えなかった。"
    "大家からの催促が来た。"
    himo "...やばい"

    "途方に暮れていると、美咲から連絡が来た。"

    misaki_c "ヒモ太郎、大丈夫？"
    himo "...実は、家賃が"
    misaki_c "..."
    misaki_c "...うち、来る？"
    himo "え"
    misaki_c "しょうがないな...って言ったら怒る？"

    "美咲の声には、どこか諦めたような響きがあった。"
    "でも、拒絶ではなかった。"
    himo "...ありがとう"

    "こうして、俺は美咲の部屋に転がり込んだ。"
    "..."
    "美咲は優しかった。"
    "でも、対等な関係はもう崩れていた。"

    misaki_c "ヒモ太郎は...このままでいいの？"
    himo "..."
    "答えられなかった。"

    centered "{size=30}GRAY END — 居候{/size}"
    centered "『助けてもらえた。でも、これは本当に救いなのか。』"

    call show_himo_aptitude_result
    return


# === カナ居候END ===

label ending_bankruptcy_kana_rescue:
    $ flags["game_ended"] = True
    $ _ending_type = "gray"
    $ log_action("BANKRUPTCY_KANA_RESCUE END")
    $ export_debug_log()
    $ export_dialogue_log()

    scene bg_placeholder with fade
    centered "{size=40}エンディング: ヒモの完成{/size}"

    "家賃が払えなかった。"
    "大家からの催促が来た。"
    himo "...マジでやばい"

    "カナに電話した。"

    kana_c "え、家賃？"
    kana_c "..."
    kana_c "じゃあ、うち来れば？"

    "カナはあっさり言った。"
    "21歳の大学生に養われる25歳。"

    himo "...いいの？"
    kana_c "いいよ。ヒモ太郎がいると楽しいし"

    "カナは嬉しそうだった。"
    "でも、カナの友達の目が痛い。"
    "狭いワンルームに二人。"
    "依存関係が、完全に逆転した。"

    kana_c "ヒモ太郎は私のものだからね"
    himo "..."
    "助かった。"
    "でも、自由は消えた。"

    centered "{size=30}GRAY END — ヒモの完成{/size}"
    centered "『カナに飼われている。それが、俺の選んだ道。』"

    call show_himo_aptitude_result
    return


# === 通常破滅END ===

label ending_bankruptcy:
    $ flags["game_ended"] = True
    $ _ending_type = "bad_bankruptcy"
    $ log_action("BAD END 破産")
    $ export_debug_log()
    $ export_dialogue_log()

    scene bg_placeholder with fade
    centered "{size=40}エンディング: 破滅{/size}"

    "家賃が払えなかった。"
    himo "...あれ、マジで？"
    "大家からの催促。"

    "美咲にも、カナにも、頼れなかった。"
    "いや、頼る資格がなかった。"

    himo "...どうすんだよ、これ"
    "荷物をまとめて、部屋を出た。"

    centered "{size=30}BAD END{/size}"
    centered "『楽観も、ほどほどに。』"

    call show_himo_aptitude_result
    return


# ========================================
# ヒモ適性診断結果表示
# ========================================

label show_himo_aptitude_result:
    scene bg_placeholder

    python:
        total_choices = (
            himo_aptitude["easy_choices"] +
            himo_aptitude["honest_moments"] +
            himo_aptitude["showed_concern"] +
            max(himo_aptitude["avoided_work"], 1)
        )

        easy_ratio = himo_aptitude["easy_choices"] / max(total_choices, 1)
        honest_ratio = himo_aptitude["honest_moments"] / max(total_choices, 1)

        if easy_ratio > 0.6 and himo_aptitude["avoided_work"] >= 3:
            aptitude_type = "筋金入りのヒモ"
            aptitude_desc = "楽な選択を優先し、働くことを避ける傾向が強い"
        elif honest_ratio > 0.4 and himo_aptitude["showed_concern"] >= 3:
            aptitude_type = "根は真面目"
            aptitude_desc = "楽な道があっても、踏みとどまることができる"
        elif himo_aptitude["lies"] >= 3:
            aptitude_type = "口先巧者"
            aptitude_desc = "嘘で誤魔化すことに慣れている"
        else:
            aptitude_type = "日和見主義者"
            aptitude_desc = "状況次第で態度を変える"

    "＝＝＝＝ あなたのヒモ適性診断 ＝＝＝＝"

    "タイプ: 「[aptitude_type]」"

    "[aptitude_desc]"

    "---- 行動統計 ----"
    "楽な選択: [himo_aptitude['easy_choices']]回"
    "お金の要求: [himo_aptitude['money_requests']]回"
    "嘘: [himo_aptitude['lies']]回"
    "正直な瞬間: [himo_aptitude['honest_moments']]回"
    "働くことを避けた: [himo_aptitude['avoided_work']]回"
    "美咲を気遣った: [himo_aptitude['showed_concern']]回"

    # v2.2: パチンコ結果表示
    python:
        _pachinko_total = stats["pachinko_wins"] + stats["pachinko_losses"]

    if _pachinko_total > 0:
        "---- パチンコ成績 ----"
        "勝率: [stats['pachinko_wins']]勝 [stats['pachinko_losses']]敗"
        python:
            _profit = stats["pachinko_profit"]
            if _profit >= 0:
                _profit_str = "+" + "{:,}".format(_profit)
            else:
                _profit_str = "{:,}".format(_profit)
        "収支: ¥[_profit_str]"

    "プレイありがとうございました"

    return
