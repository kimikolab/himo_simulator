# game/tests/smoke_test.rpy
# Layer 1: ゲームがクラッシュせずに完走することを確認するテスト


# === スモークテスト: ランダム選択で通し走行 ===
testcase smoke_random_playthrough:
    description "全体通し走行（seed=42）"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(42)
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30


# === スモークテスト: 別シードで2回目 ===
testcase smoke_random_playthrough_seed2:
    description "全体通し走行（seed=123）"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(123)
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30


# === スモークテスト: さらに別シード ===
testcase smoke_random_playthrough_seed3:
    description "全体通し走行（seed=999）"
    $ _test.timeout = 600
    click "スタート"
    $ test_fix_random_seed(999)
    click until eval (test_game_ended()) timeout 600
    click until eval (test_at_main_menu()) timeout 30
