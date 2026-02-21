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

    python:
        can_pay = player["money"] >= 0
        is_honest = stats["lies_told"] <= 3
        is_dependent = misaki["dependence"] >= 65
        met_often = stats["times_met"] >= 10
        concern_shown = himo_aptitude["showed_concern"] >= 5
        all_misaki_events = (misaki_events["M02_done"] and misaki_events["M03_done"] and misaki_events["M05_done"])

    if not can_pay:
        jump ending_bankruptcy_30days

    if is_honest and met_often and not is_dependent and concern_shown:
        jump ending_balance_30days
    elif is_dependent or not is_honest:
        jump ending_himou_30days
    else:
        jump ending_unstable_30days


label ending_balance_30days:
    $ flags["game_ended"] = True
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


label ending_bankruptcy_30days:
    $ flags["game_ended"] = True
    scene bg_placeholder with fade

    centered "{size=40}エンディング: 破滅{/size}"

    "家賃が払えなかった。"
    himo "...終わった"
    "大家から退去通知が来た。"

    centered "{size=30}BAD END{/size}"
    "「楽観も、ほどほどに」"

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
