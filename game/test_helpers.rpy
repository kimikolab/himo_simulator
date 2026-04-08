# test_helpers.rpy
# テスト実行時のみ使用されるヘルパー関数

init python:

    def test_fix_random_seed(seed=42):
        """テスト用にランダムシードを固定する。デバッグログもクリア"""
        renpy.random.seed(seed)
        global debug_log_entries
        debug_log_entries = []

    def test_game_ended():
        """flags["game_ended"] のラッパー（testcase構文から呼びやすくするため）"""
        return flags.get("game_ended", False)

    def test_assert_param_bounds():
        """全パラメータが0-100範囲内か確認。エラーがあれば文字列で返す"""
        errors = []
        if player["stamina"] < 0 or player["stamina"] > 100:
            errors.append("stamina: {}".format(player["stamina"]))
        if player["cleanliness"] < 0 or player["cleanliness"] > 100:
            errors.append("cleanliness: {}".format(player["cleanliness"]))
        if player["charm"] < 0 or player["charm"] > 100:
            errors.append("charm: {}".format(player["charm"]))
        if misaki["trust"] < 0 or misaki["trust"] > 100:
            errors.append("misaki trust: {}".format(misaki["trust"]))
        if misaki["dependence"] < 0 or misaki["dependence"] > 100:
            errors.append("misaki dependence: {}".format(misaki["dependence"]))
        if kana_flags.get("met", False):
            if kana["trust"] < 0 or kana["trust"] > 100:
                errors.append("kana trust: {}".format(kana["trust"]))
            if kana["dependence"] < 0 or kana["dependence"] > 100:
                errors.append("kana dependence: {}".format(kana["dependence"]))
        return ", ".join(errors)

    def test_assert_daily_flags_reset():
        """advance_day()後にdaily_flagsがリセットされているか確認"""
        errors = []
        # time_system.rpy のリセット対象と一致させる
        expected = {
            "asked_money_today": False,
            "ignored_today": False,
            "date_planned_tonight": False,
            "ate_today": False,
            "ignored_kana_today": False,
            "date_location": None,
            "date_with": None,
            "sns_shown_today": False,
            "double_booking_checked": False,
            "misaki_wants_tonight": False,
            "kana_wants_tonight": False,
            "money_refused_today": False,
            "kana_tonight_source": None,
            "misaki_lined_only": False,
        }
        for key, expected_val in expected.items():
            actual = daily_flags.get(key, "MISSING")
            if actual != expected_val:
                errors.append("{}: got {}".format(key, actual))
        return ", ".join(errors)

    def test_at_main_menu():
        """メインメニューに戻ったかどうか"""
        return renpy.get_screen("main_menu") is not None

    def test_assert_appointment_integrity():
        """約束管理の整合性チェック（過去の約束残存・同日重複）"""
        errors = []
        current_day = game_date["day"]
        active_days = {}
        for key in ("misaki", "kana"):
            appt_day = appointments.get(key, None)
            if appt_day is None:
                continue
            if appt_day < current_day:
                errors.append("stale: {} day {} (now {})".format(key, appt_day, current_day))
            if appt_day in active_days:
                errors.append("double booking day {}: {} vs {}".format(appt_day, active_days[appt_day], key))
            else:
                active_days[appt_day] = key
        return ", ".join(errors)


# ========================================
# デバッグ用: エナマッチ単体テスト
# Shift+O → jump debug_ena_test で起動
# ========================================

label debug_ena_test:
    # テスト用パラメータセット
    $ energy = 3
    $ energy_max = 3
    $ energy_full_days = 0
    $ energy_charm_bonus = 0

    $ misaki["trust"] = 80
    $ misaki["stage"] = STAGE_DATING
    $ misaki["dependence"] = 60

    $ kana["trust"] = 80
    $ kana["stage"] = STAGE_DATING
    $ kana["dependence"] = 60

    $ game_date["day"] = 15

    menu:
        "誰とテスト？"
        "美咲":
            call ena_battle("misaki")
        "カナ":
            call ena_battle("kana")
        "美咲（低信頼）":
            $ misaki["trust"] = 30
            $ misaki["stage"] = STAGE_FRIEND
            call ena_battle("misaki")
        "カナ（低信頼）":
            $ kana["trust"] = 30
            $ kana["stage"] = STAGE_FRIEND
            call ena_battle("kana")
        "カナ（エナ1・依存100）":
            $ energy = 1
            $ kana["dependence"] = 100
            call ena_battle("kana")

    "テスト終了"
    jump debug_ena_test
