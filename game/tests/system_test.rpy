# game/tests/system_test.rpy
# Layer 2: パラメータ・フラグの整合性を検証するテスト


# === パラメータ境界値テスト（中盤） ===
testcase param_bounds_midgame:
    description "15日目パラメータ境界値チェック"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (game_date["day"] >= 15) timeout 600
    $ _bounds_error = test_assert_param_bounds()
    assert eval (_bounds_error == "") timeout 1.0
    # ゲーム終了→メインメニューまで走り切る
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30


# === パラメータ境界値テスト（終盤） ===
testcase param_bounds_endgame:
    description "25日目パラメータ境界値チェック"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (game_date["day"] >= 25) timeout 600
    $ _bounds_error = test_assert_param_bounds()
    assert eval (_bounds_error == "") timeout 1.0
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30


# === daily_flags リセットテスト ===
testcase daily_flags_reset:
    description "daily_flagsリセット確認"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (game_date["day"] >= 5 and game_date["time"] == "morning") timeout 600
    $ _reset_error = test_assert_daily_flags_reset()
    assert eval (_reset_error == "") timeout 1.0
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30


# === 約束管理整合性テスト（中盤） ===
testcase appointment_integrity_midgame:
    description "15日目約束管理整合性チェック"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (game_date["day"] >= 15) timeout 600
    $ _appt_error = test_assert_appointment_integrity()
    assert eval (_appt_error == "") timeout 1.0
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30


# === 約束管理整合性テスト（終盤） ===
testcase appointment_integrity_endgame:
    description "25日目約束管理整合性チェック"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (game_date["day"] >= 25) timeout 600
    $ _appt_error = test_assert_appointment_integrity()
    assert eval (_appt_error == "") timeout 1.0
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30


# === エンディング到達テスト ===
testcase ending_type_is_set:
    description "エンディング到達時に_ending_typeがセットされる"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (test_game_ended()) timeout 600
    assert eval (_ending_type != "") timeout 1.0
    assert eval (_ending_type in ["good", "gray", "normal", "bad_bankruptcy", "demo"]) timeout 1.0
    click until eval (test_at_main_menu()) timeout 30
