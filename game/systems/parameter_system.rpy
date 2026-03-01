# parameter_system.rpy
# パラメータ管理システム

init python:
    def clamp(value, min_val, max_val):
        return max(min_val, min(max_val, value))

    # v2.6追加: 支出可能かチェック
    def can_afford(amount):
        return player["money"] >= amount

    def change_money(amount, source=""):
        global player, stats
        player["money"] += amount
        if amount > 0:
            stats["total_earned"] += amount

    def change_stamina(amount):
        global player
        player["stamina"] = clamp(player["stamina"] + amount, 0, player["max_stamina"])

    def change_charm(amount):
        global player
        player["charm"] = clamp(player["charm"] + amount, 0, 100)

    def change_cleanliness(amount):
        global player
        player["cleanliness"] = clamp(player["cleanliness"] + amount, 0, 100)

    def change_trust(amount):
        global misaki
        trust = misaki["trust"]

        # 収穫逓減（v2.0追加）
        if trust >= 70:
            amount = int(amount * 0.3)
        elif trust >= 50:
            amount = int(amount * 0.6)

        old_stage = misaki["stage"]
        misaki["trust"] = clamp(misaki["trust"] + amount, 0, 100)
        update_misaki_stage()

    def change_dependence(amount):
        global misaki

        # v2.2: 逓減は増加時のみ適用
        if amount > 0:
            depend = misaki["dependence"]
            # 逓減処理（v2.2強化版）
            if depend >= 60:
                amount = int(amount * 0.3)
            elif depend >= 40:
                amount = int(amount * 0.5)

        old = misaki["dependence"]
        misaki["dependence"] = clamp(misaki["dependence"] + amount, 0, 100)
        update_misaki_stage()

        if old < 100 <= misaki["dependence"]:
            renpy.notify("美咲: 「ずっと一緒にいたい」")

        # マイルストーンを超えたらキューに追加（v2.2: 重複防止フラグ追加）
        for threshold in [DEPEND_MILD, DEPEND_MEDIUM, DEPEND_HEAVY]:
            if old < threshold <= misaki["dependence"]:
                flag_key = "depend_milestone_" + str(threshold)
                if not flags.get(flag_key, False):
                    flags[flag_key] = True
                    _pending_events.append(("misaki_dependence_milestone", threshold))

    def reset_contact():
        global misaki
        misaki["last_contact"] = 0

    def update_misaki_stage():
        global misaki
        old_stage = misaki["stage"]

        trust  = misaki["trust"]
        depend = misaki["dependence"]

        if trust >= 70 and depend >= 50:
            misaki["stage"] = STAGE_DATING
        elif trust >= 50:
            misaki["stage"] = STAGE_CLOSE
        elif trust >= 35:
            misaki["stage"] = STAGE_FRIEND
        else:
            misaki["stage"] = STAGE_ACQUAINTANCE

        # STAGE_DATING移行処理（v2.1修正: 再表示防止 / v1.2修正: 夜以外は持ち越し）
        if old_stage < STAGE_DATING and misaki["stage"] == STAGE_DATING:
            if not flags.get("confession_done", False):
                if game_date["time"] == "night":
                    _pending_events.append(("misaki_confession", None))
                else:
                    flags["confession_pending"] = True
            elif flags.get("confession_accepted", False):
                # 告白を受け入れていた場合のみテロップ表示
                renpy.notify("美咲との関係: 恋人")
            # confession_done済みで受け入れていない場合はテロップなし

        # それ以外のステージ上昇通知
        elif misaki["stage"] > old_stage:
            stage_names = {2: "友達", 3: "いい雰囲気"}
            if misaki["stage"] in stage_names:
                renpy.notify("美咲との関係が「" + stage_names[misaki["stage"]] + "」になった")

    def request_money_from_misaki(amount_type="small"):
        global stats, suspicion_count, himo_aptitude, money_refused_streak

        # v1.2追加: 最近会っていないとお金を要求しにくい
        if misaki["last_contact"] > 1:
            return False, 0, "最近会っていない"

        stats["times_asked_money"] += 1
        himo_aptitude["money_requests"] += 1

        required = {"small": 35, "medium": 55, "large": 75}
        if misaki["trust"] < required[amount_type]:
            return False, 0, "信頼度が足りない"

        import random

        # ムード補正（v2.1再調整）
        mood_modifier = {
            "good":     1.2,
            "normal":   1.0,
            "tired":    0.75,
            "stressed": 0.4,
        }
        modifier = mood_modifier.get(misaki_mood["today_mood"], 1.0)

        # v2.1: 3回連続拒否されたら強制成功（救済措置）
        force_success = money_refused_streak >= 3

        if not force_success and random.random() > modifier:
            mood_response = {
                "tired":    "ごめん、今日ちょっと余裕なくて",
                "stressed": "...今それどころじゃないんだけど",
            }
            msg = mood_response.get(misaki_mood["today_mood"], "今日は難しいかな")
            money_refused_streak += 1
            return False, 0, msg

        # 成功時はストリークリセット
        money_refused_streak = 0

        # 金額（v2.4上方修正）
        amounts = {
            "small": (3000, 6000),
            "medium": (6000, 10000),
            "large": (9000, 15000)
        }
        min_amt, max_amt = amounts[amount_type]
        amount = random.randint(min_amt, max_amt)

        change_trust(-3)
        change_dependence(2)
        change_money(amount, "美咲")

        if stats["times_asked_money"] >= 3:
            suspicion_count += 1
            if suspicion_count == 2:
                renpy.notify("美咲: 「...お金、大丈夫？」")

        return True, amount, "成功"

    # ========================================
    # Phase 3: カナ用パラメータ関数
    # ========================================

    def change_trust_kana(amount):
        global kana
        old_stage = kana["stage"]
        kana["trust"] = clamp(kana["trust"] + amount, 0, 100)
        update_kana_stage()

        if kana["stage"] > old_stage:
            stage_names_kana = {2: "友達", 3: "いい感じ", 4: "推しの人"}
            if kana["stage"] in stage_names_kana:
                renpy.notify("カナとの関係が「" + stage_names_kana[kana["stage"]] + "」になった")

    def change_dependence_kana(amount):
        global kana
        if amount > 0:
            depend = kana["dependence"]
            if depend >= 60:
                amount = int(amount * 0.3)
            elif depend >= 40:
                amount = int(amount * 0.5)

        old = kana["dependence"]
        kana["dependence"] = clamp(kana["dependence"] + amount, 0, 100)

        if old < 100 <= kana["dependence"]:
            renpy.notify("カナ: 「ヒモ太郎のことしか考えられない」")

    def update_kana_stage():
        global kana
        trust  = kana["trust"]
        depend = kana["dependence"]

        if trust >= 70 and depend >= 30:
            kana["stage"] = STAGE_OSHI
        elif trust >= 50:
            kana["stage"] = STAGE_CLOSE
        elif trust >= 35:
            kana["stage"] = STAGE_FRIEND
        elif trust > 0:
            kana["stage"] = STAGE_ACQUAINTANCE
        else:
            kana["stage"] = 0

    def add_suspicion(reason):
        global suspicion_count
        suspicion_count += 1

        messages = {
            "contact_delay": "美咲: 「最近忙しそうだね」",
            "vague_answer": "美咲: 「...そうなんだ」",
            "too_many_requests": "美咲: 「また？」",
            "avoided_question": "美咲: 「...」",
            "deflected": ""
        }
        if reason in messages and messages[reason]:
            renpy.notify(messages[reason])
