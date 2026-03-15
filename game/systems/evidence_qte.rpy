# evidence_qte.rpy
# 証拠隠滅QTE — 制限時間内にアイテムを処理する

init python:
    def create_evidence_items(scenario="kana_raid"):
        """シナリオに応じた証拠アイテムリストを生成"""
        if scenario == "kana_raid":
            items = [
                {"id": "phone", "name": "スマホ（LINE画面）", "risk": 40, "cleared": False},
                {"id": "hairpin", "name": "美咲の髪留め", "risk": 30, "cleared": False},
                {"id": "receipt", "name": "レシート", "risk": 20, "cleared": False},
            ]
            # 依存度が高いと証拠が増える
            if misaki["dependence"] >= 50:
                items.append(
                    {"id": "clothes", "name": "女物の上着", "risk": 50, "cleared": False}
                )
            return items
        return []

    def calculate_qte_result(items):
        """未処理アイテムのリスク合算"""
        total_risk = 0
        for item in items:
            if not item["cleared"]:
                total_risk += item["risk"]
        return total_risk


screen evidence_qte_screen(items, time_limit):
    timer time_limit action Return("timeout")

    # タイマーバー
    frame:
        xalign 0.5
        yalign 0.05
        padding (15, 8)
        background "#00000088"

        vbox:
            spacing 5
            text "証拠を隠せ！" size 28 color "#ff4444" xalign 0.5
            bar:
                value AnimatedValue(0, time_limit, time_limit, 0)
                xsize 400
                ysize 10
                left_bar "#ff4444"
                right_bar "#333333"
                xalign 0.5

    # アイテムボタン（散らばって配置）
    python:
        positions = [
            (0.2, 0.3), (0.7, 0.35),
            (0.4, 0.55), (0.6, 0.7),
            (0.25, 0.7),
        ]

    for i, item in enumerate(items):
        if not item["cleared"]:
            $ pos = positions[i] if i < len(positions) else (0.5, 0.5)
            textbutton item["name"]:
                xalign pos[0]
                yalign pos[1]
                action [SetDict(item, "cleared", True)]
                text_size 24
                text_color "#ffffff"
                background "#cc000088"
                padding (20, 15)


label run_evidence_qte(scenario="kana_raid"):
    python:
        qte_items = create_evidence_items(scenario)
        qte_time = QTE_TIME_LIMIT

    "（やばい！急いで隠さないと！）"

    # テスト実行時: QTEをスキップし、成功として処理
    if renpy.is_in_test():
        $ flags["qte_failed_badly"] = False
        return

    call screen evidence_qte_screen(qte_items, qte_time)

    python:
        total_risk = calculate_qte_result(qte_items)
        cleared_count = sum(1 for item in qte_items if item["cleared"])
        total_count = len(qte_items)

    if cleared_count == total_count:
        "（全部隠した！セーフ！）"
        himo "ふう..."
    elif total_risk >= 50:
        "（隠しきれなかった...）"
        # 高リスク — 証拠発見、修羅場へ
        $ flags["qte_failed_badly"] = True
    else:
        "（大体隠せた...たぶん大丈夫）"
        $ suspicion["kana"] = min(suspicion["kana"] + 10, SUSPICION_MAX)

    return
