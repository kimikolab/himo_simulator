# debug_log.rpy
# テストプレイ用のログ出力システム
# DEBUG_MODE = True のときのみ機能する

init python:
    debug_log_entries = []
    _last_logged_day = None
    _last_logged_time = None
    _last_logged_bg = [None]  # mutable container for closure

    def _scene_change_logger():
        """インタラクション開始時に master レイヤーの bg/cg タグを監視し、
        変化したら SCENE ログを残す。"""
        if not DEBUG_MODE:
            return
        try:
            tags = renpy.get_showing_tags(layer="master")
        except Exception:
            return
        current_bg = None
        for tag in tags:
            if tag.startswith("bg_") or tag.startswith("cg_"):
                current_bg = tag
                break
        if current_bg != _last_logged_bg[0]:
            _last_logged_bg[0] = current_bg
            if current_bg:
                log_action("SCENE", current_bg)

    config.start_interact_callbacks.append(_scene_change_logger)

    _last_logged_sprites = [None, None]  # [misaki, kana]

    def _sprite_change_logger():
        """立ち絵の表示・切替・非表示を監視してログを残す"""
        if not DEBUG_MODE:
            return
        try:
            tags = renpy.get_showing_tags(layer="master")
        except Exception:
            return

        for i, chara in enumerate(["misaki", "kana"]):
            if chara in tags:
                attrs = renpy.get_attributes(chara)
                current = chara + " " + " ".join(attrs) if attrs else chara
            else:
                current = None

            if current != _last_logged_sprites[i]:
                if current is None:
                    log_action("SPRITE", chara + " hide")
                elif _last_logged_sprites[i] is None:
                    log_action("SPRITE", current + " (show)")
                else:
                    log_action("SPRITE", current)
                _last_logged_sprites[i] = current

    config.start_interact_callbacks.append(_sprite_change_logger)

    def get_turn_header():
        """現在のターンヘッダー文字列を返す"""
        return "========== [Day " + str(game_date["day"]) + " / " + game_date["time"] + "] =========="

    def log_action(action_name, notes=""):
        """行動ログを記録する"""
        global _last_logged_day, _last_logged_time

        if not DEBUG_MODE:
            return

        # ターンが変わったらヘッダーを挿入
        if game_date["day"] != _last_logged_day or game_date["time"] != _last_logged_time:
            _last_logged_day = game_date["day"]
            _last_logged_time = game_date["time"]
            header_entry = {
                "is_header": True,
                "text": get_turn_header(),
            }
            debug_log_entries.append(header_entry)

        entry = {
            "is_header":   False,
            "day":         game_date["day"],
            "time":        game_date["time"],
            "action":      action_name,
            "notes":       notes,
            "money":       player["money"],
            "stamina":     player["stamina"],
            "cleanliness": player["cleanliness"],
            "charm":       player["charm"],
            "m_trust":     misaki["trust"],
            "m_depend":    misaki["dependence"],
            "k_trust":     kana["trust"]    if kana_flags["met"] else "-",
            "k_depend":    kana["dependence"] if kana_flags["met"] else "-",
        }
        debug_log_entries.append(entry)

    def export_debug_log():
        """ログをファイルに書き出す"""
        if not DEBUG_MODE:
            return

        import datetime
        import os
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = "debug_log_{}.txt".format(timestamp)

        lines = []
        lines.append("=== ヒモ男シミュレーター デバッグログ ===")
        lines.append("出力日時: {}".format(timestamp))
        lines.append("")

        # ヘッダー
        lines.append("日  時        行動                所持金    体力 清潔 魅力 美信 美依 カ信 カ依 備考")
        lines.append("-" * 100)

        for e in debug_log_entries:
            if e.get("is_header", False):
                lines.append("")
                lines.append(e["text"])
                continue
            lines.append(
                "{:2}日 {:9} "
                "{:18} "
                "¥{:7,} "
                "{:3} "
                "{:3} "
                "{:3} "
                "{:3} "
                "{:3} "
                "{:>3} "
                "{:>3} "
                "{}".format(
                    e["day"], e["time"],
                    e["action"],
                    e["money"],
                    e["stamina"],
                    e["cleanliness"],
                    e["charm"],
                    e["m_trust"],
                    e["m_depend"],
                    str(e["k_trust"]),
                    str(e["k_depend"]),
                    e["notes"]
                )
            )

        lines.append("")
        lines.append("=== クリア時サマリー ===")
        lines.append("最終所持金:       ¥{:,}".format(player["money"]))
        lines.append("美咲 信頼/依存:   {}/{}".format(misaki["trust"], misaki["dependence"]))
        if kana_flags["met"]:
            lines.append("カナ 信頼/依存:   {}/{}".format(kana["trust"], kana["dependence"]))
        lines.append("総収入:           ¥{:,}".format(stats["total_earned"]))
        lines.append("美咲と会った回数: {}回".format(stats["times_met"]))
        lines.append("お金を要求:       {}回".format(stats["times_asked_money"]))
        lines.append("嘘をついた回数:   {}回".format(stats["lies_told"]))
        lines.append("パチンコ収支:     ¥{:,}".format(stats.get("pachinko_profit", 0)))
        lines.append("SNSリスク:        {}".format(kana_flags.get("sns_risk", 0)))

        # Phase 4 v1.1追加情報
        lines.append("")
        lines.append("=== Phase 4 追加情報 ===")
        lines.append("疑念度 美咲/カナ:  {}/{}".format(
            suspicion.get("misaki", 0), suspicion.get("kana", 0)))
        lines.append("嘘パズル: {}回挑戦 / {}回バレ".format(
            stats.get("lie_puzzles_faced", 0), stats.get("lie_puzzles_busted", 0)))
        lines.append("食事回数: {}/{}日".format(
            stats.get("meals_eaten", 0), game_date["day"] - 1))

        # v1.1: 経済圏統計
        lines.append("")
        lines.append("--- 経済圏統計 ---")
        lines.append("対面交渉: {}/{} (総収入 ¥{:,})".format(
            stats.get("negotiation_success", 0),
            stats.get("negotiation_attempts", 0),
            stats.get("negotiation_total_earned", 0)))
        lines.append("LINE要求: {}/{}".format(
            stats.get("line_request_success", 0),
            stats.get("line_request_attempts", 0)))
        if kana_flags["met"]:
            lines.append("カナ泊まり: {}回 (うちヒモ太郎の部屋: {}回)".format(
                stats.get("kana_stayed_over", 0),
                stats.get("kana_stayed_himo_room", 0)))
            lines.append("カナ恩恵受取: {}回".format(stats.get("kana_benefits_received", 0)))
            lines.append("ご機嫌取りQTE: 成功{} / 失敗{}".format(
                stats.get("kana_gokiragen_success", 0),
                stats.get("kana_gokiragen_failed", 0)))
            lines.append("カナ搾取スコア: {}".format(calculate_kana_exploitation()))

        lines.append("")
        lines.append("--- 中盤イベント発生状況 ---")
        midgame_flags = [
            ("美咲「最近忙しい？」", "midgame_busymisaki_done"),
            ("ダブルブッキング危機", "midgame_doublebooking_done"),
            ("目撃情報",             "midgame_sighting_done"),
            ("目撃→対面修羅場",     "midgame_sighting_confronted"),
            ("カナ突撃訪問",         "midgame_kana_raid_done"),
            ("美咲直球質問v2",       "midgame_misaki_direct_done"),
        ]
        for label, key in midgame_flags:
            status = "発生済" if flags.get(key, False) else "未発生"
            lines.append("{:20} {}".format(label, status))

        lines.append("")
        lines.append("--- デート場所統計 ---")
        dl = stats.get("date_locations", {})
        misaki_locs = "ファミレス{} / 居酒屋{} / 部屋{} / いい店{}".format(
            dl.get("famires", 0), dl.get("izakaya", 0),
            dl.get("misaki_room", 0), dl.get("fancy", 0))
        kana_locs = "カフェ{} / カラオケ{} / 大学{} / 部屋{}".format(
            dl.get("cafe", 0), dl.get("karaoke", 0),
            dl.get("campus", 0), dl.get("himo_room", 0))
        lines.append("美咲: {}".format(misaki_locs))
        lines.append("カナ: {}".format(kana_locs))

        content = "\n".join(lines)

        try:
            # Ren'Py の game/debug_log/ フォルダに書き出す
            log_dir = os.path.join(config.gamedir, "debug_log")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            filepath = os.path.join(log_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            renpy.notify("ログを出力しました: {}".format(filename))
        except Exception as ex:
            renpy.notify("ログ出力エラー: {}".format(ex))
