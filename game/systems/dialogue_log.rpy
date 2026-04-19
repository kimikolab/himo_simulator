# dialogue_log.rpy
# テストプレイ用のセリフ・テキスト全文ログ
# DEBUG_MODE = True のときのみ機能する
#
# 採用アプローチ: C (config.history_callbacks)
# Ren'Py のセリフ履歴システムを利用し、HistoryEntry 追加時に
# who/what を取得してログに記録する。
# Character 定義の変更が不要で、全キャラ・ナレーションを自動捕捉できる。

init python:

    def log_dialogue(speaker, text):
        """セリフをログに記録する"""
        if not DEBUG_MODE:
            return

        # speaker が None の場合はナレーション
        if speaker is None or speaker == "":
            tag = "---"
        else:
            tag = speaker

        entry = {
            "day": game_date["day"],
            "time": game_date["time"],
            "tag": tag,
            "text": text,
        }
        dialogue_log_entries.append(entry)


    def log_choice(choice_text):
        """メニュー選択をログに記録する"""
        if not DEBUG_MODE:
            return

        entry = {
            "day": game_date["day"],
            "time": game_date["time"],
            "tag": ">>> CHOICE",
            "text": choice_text,
        }
        dialogue_log_entries.append(entry)


    def log_notify(text):
        """システム通知をログに記録する"""
        if not DEBUG_MODE:
            return

        entry = {
            "day": game_date["day"],
            "time": game_date["time"],
            "tag": "NOTIFY",
            "text": text,
        }
        dialogue_log_entries.append(entry)


    # --- 背景・立ち絵の変化をセリフログに挿入 ---

    _dlg_last_bg = [None]
    _dlg_last_sprites = [None, None]  # [misaki, kana]

    def _dialogue_scene_logger():
        """背景変化を dialogue_log_entries に挿入する"""
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
        if current_bg != _dlg_last_bg[0]:
            _dlg_last_bg[0] = current_bg
            if current_bg:
                dialogue_log_entries.append({
                    "day": game_date["day"],
                    "time": game_date["time"],
                    "tag": "SCENE",
                    "text": current_bg,
                })

    def _dialogue_sprite_logger():
        """立ち絵の変化を dialogue_log_entries に挿入する"""
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
            if current != _dlg_last_sprites[i]:
                if current is None:
                    text = chara + " hide"
                else:
                    text = current
                dialogue_log_entries.append({
                    "day": game_date["day"],
                    "time": game_date["time"],
                    "tag": "SPRITE",
                    "text": text,
                })
                _dlg_last_sprites[i] = current

    config.start_interact_callbacks.append(_dialogue_scene_logger)
    config.start_interact_callbacks.append(_dialogue_sprite_logger)

    # v1.4: 根本修正 — config.all_character_callbacks に移行
    # history_callbacks は Ren'Py 内部で複数回呼ばれるケースがあるため、
    # all_character_callbacks の begin イベントのみ捕捉する方式に変更。
    import time as _time_module

    def _dialogue_log_callback(event, interact=True, **kwargs):
        """全キャラクターの発話時に呼ばれるコールバック"""
        # ガード1: prediction時はスキップ
        if not interact:
            return
        # ガード2: beginイベントのみ記録
        if event != "begin":
            return
        # ガード3: 同一テキスト100ms以内の重複スキップ
        what = kwargs.get("what", "") or ""
        who = kwargs.get("name", "") or ""
        now = _time_module.time()
        if (what == _dialogue_log_callback._last_text
                and who == _dialogue_log_callback._last_who
                and (now - _dialogue_log_callback._last_time) < 0.1):
            return
        _dialogue_log_callback._last_text = what
        _dialogue_log_callback._last_who = who
        _dialogue_log_callback._last_time = now
        log_dialogue(who if who else None, what)

    _dialogue_log_callback._last_text = ""
    _dialogue_log_callback._last_who = ""
    _dialogue_log_callback._last_time = 0

    # 旧 history_callbacks を除去
    config.history_callbacks = [
        cb for cb in config.history_callbacks
        if getattr(cb, '__name__', '') != '_on_history_entry'
    ]

    # 既存の同名コールバックを除去してから追加（Shift+R リロード対策）
    config.all_character_callbacks = [
        cb for cb in config.all_character_callbacks
        if getattr(cb, '__name__', '') != '_dialogue_log_callback'
    ]
    config.all_character_callbacks.append(_dialogue_log_callback)


    def export_dialogue_log():
        """セリフログをファイルに書き出す"""
        if not DEBUG_MODE:
            return
        if not dialogue_log_entries:
            return

        import datetime
        import os
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "dialogue_log_" + timestamp + ".txt"

        lines = []
        lines.append("=== ヒモ男シミュレーター セリフログ ===")
        lines.append("出力日時: " + timestamp)
        lines.append("")

        current_day = None
        current_time = None

        for e in dialogue_log_entries:
            # ターンが変わったらヘッダーを挿入
            if e["day"] != current_day or e["time"] != current_time:
                current_day = e["day"]
                current_time = e["time"]
                lines.append("")
                lines.append("========== [Day " + str(current_day) + " / " + current_time + "] ==========")

            lines.append("[" + e["tag"] + "] " + e["text"])

        lines.append("")
        lines.append("=== ログ終了 ===")

        content = "\n".join(lines)

        try:
            log_dir = os.path.join(config.gamedir, "debug_log")
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            log_path = os.path.join(log_dir, filename)
            with open(log_path, "w", encoding="utf-8") as f:
                f.write(content)
            renpy.notify("セリフログを出力しました: " + filename)
        except Exception as ex:
            renpy.notify("セリフログ出力エラー: " + str(ex))
