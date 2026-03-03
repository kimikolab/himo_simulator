Phase 3 修正指示書 v1.6
同じバグが3件再発しています。Claude Codeに以下を渡してください。

修正1: 街に出るで何も発生しない
shopping_eventラベルが未実装の可能性があります。以下をdaily_events.rpyに追加してください。
pythonlabel shopping_event:
    "ショッピングモールをぶらぶらした。"
    himo "特に買うものもないけど"
    menu:
        "ウィンドウショッピング":
            himo "まあ、金ないしな"
            $ change_stamina(-5)
        "服を見る" if can_afford(3000):
            $ change_money(-3000)
            $ change_charm(5)
            himo "おっ、いい感じ"
        "何も買わず帰る":
            pass
    return

修正2: 「じゃあ会おう」→断られる流れがおかしい
contact_kanaの「雑談する」でフラグを立てるだけにして、成功率チェックは夜に移動します。
kana_events.rpyの「雑談する」選択肢:
python"雑談する":
    kana_c "暇〜。ヒモ太郎も暇？"
    himo "暇だよ"
    kana_c "じゃあ会おう"
    $ flags["kana_tonight"] = True   # フラグだけ立てる
    $ change_trust_kana(2)
    # kana_date_requestは呼ばない
script.rpyのnight_actionsでカナ約束処理に成功率チェックを追加:
pythonif flags.get("kana_tonight") and not flags.get("misaki_tonight"):
    "今夜はカナと約束がある。"
    $ flags["kana_tonight"] = False
    python:
        import random
        trust = kana["trust"]
        if trust >= 50:   success_rate = 0.90
        elif trust >= 35: success_rate = 0.75
        elif trust >= 20: success_rate = 0.65
        else:             success_rate = 0.50
        kana_shows_up = random.random() < success_rate
    if kana_shows_up:
        call kana_date
    else:
        kana_c "ごめん、やっぱり今日バイト入っちゃって"
        himo "そっか、しゃーない"
        $ change_trust_kana(-2)
    return

修正3: END後にイニシアティブメッセージが来る（3回目）
根本原因を特定するため以下を順番に確認してください。

endings.rpyの全エンディングラベルがreturnで終わっていてmain_loopにjumpで戻っていないか
check_misaki_initiative()とcheck_kana_initiative()の先頭にif flags.get("game_ended", False): returnが両方存在するか
advance_day()内でinitiativeチェックを呼ぶ前にgame_endedガードがあるか

3回同じ修正を指示しているので、実装されているが動いていない場合はgame_endedフラグ自体が正しくTrueにセットされているかをデバッグ画面で確認してください。