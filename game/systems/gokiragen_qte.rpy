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
    # テスト実行時: QTEをスキップし、成功として処理
    if renpy.is_in_test():
        $ daily_flags["kana_mood_resolved"] = True
        $ stats["kana_gokiragen_success"] = stats.get("kana_gokiragen_success", 0) + 1
        return

    $ daily_flags["kana_mood_resolved"] = True
    $ _gokiragen_choices = []

    "カナの機嫌が悪い。"

    # === 第1段階 ===
    kana_c "私のこと好き？"

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


# ========================================
# 疑念イベント版ご機嫌取りQTE（高難度・3段階固定）
# ========================================

label gokiragen_qte_doubt:
    # テスト実行時: スキップして部分成功として処理
    if renpy.is_in_test():
        $ change_trust_kana(-8)
        $ suspicion["kana"] = max(0, suspicion.get("kana", 0) - 5)
        $ stats["kana_gokiragen_success"] = stats.get("kana_gokiragen_success", 0) + 1
        return

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
