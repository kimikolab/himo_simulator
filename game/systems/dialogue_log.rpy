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


    def _on_history_entry(h):
        """セリフ履歴にエントリが追加されたときに呼ばれる (config.history_callbacks)"""
        log_dialogue(h.who, h.what)

    config.history_callbacks.append(_on_history_entry)


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
