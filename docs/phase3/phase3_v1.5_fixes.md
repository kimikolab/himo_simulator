# ヒモ男シミュレーター Phase 3 修正指示書 v1.5

**前提**: Phase 3 v1.4が実装済みであること  
最終更新日: 2026年3月2日

---

## 修正一覧

| # | 種別 | 内容 | ファイル |
|---|---|---|---|
| 1 | バグ | カナへの連絡「雑談する」で確定的に会える | kana_events.rpy |
| 2 | バグ | カナすっぽかし時のペナルティが発生しない | script.rpy |
| 3 | バグ | ナンパ失敗時にafternoon_consumedが立たない | daily_events.rpy |

---

## 修正1: カナへの連絡「雑談する」で確定的に会える

**原因**: `contact_kana` の「雑談する」選択肢内で `flags["kana_tonight"] = True` を直接セットしており、当日誘いの成功率チェックをスキップしている。

**ファイル**: `events/kana_events.rpy`

```python
label contact_kana:
    $ kana["last_contact"] = 0   # LINEした記録のみ（last_contactはリセットしない）
    # ※ v1.3修正: last_contactのリセットはデート時のみのはずなので
    #    この行自体も削除対象かもしれない。Claude Codeが判断すること。

    "カナにLINEを送った..."

    if kana["trust"] >= 40:
        "すぐに返信が来た。"
    elif kana["trust"] >= 20:
        "しばらくして返信が来た。"
    else:
        "既読スルーされた..."
        $ change_trust_kana(-1)
        $ daily_flags["ignored_kana_today"] = True
        return

    menu:
        kana_c "なに？"

        "雑談する":
            kana_c "暇〜。ヒモ太郎も暇？"
            himo "暇だよ"
            kana_c "じゃあ会おう"
            # ✅ 成功率チェックを通す（直接フラグを立てない）
            call kana_date_request

        "今日会いたいと言う":
            call kana_date_request

    return
```

---

## 修正2: カナすっぽかし時のペナルティが発生しない

**原因**: `night_actions` の冒頭で `misaki_tonight` を優先処理する際、`kana_tonight` も立っている場合に `double_booking_event` を経由せず `kana_tonight` をそのままFalseにしている。

**ファイル**: `script.rpy`

`night_actions` の冒頭を以下の順番で処理するよう修正。

```python
label night_actions:
    "――夜、21時――"

    # 1. ダブルブッキングチェックを最初に行う
    if flags.get("misaki_tonight") and flags.get("kana_tonight"):
        call double_booking_event
        # double_booking_event内でどちらかのフラグがFalseになる
        # その後は通常の夜メニューへ続く

    # 2. 美咲の約束のみある場合
    if flags.get("misaki_tonight") and not flags.get("kana_tonight"):
        "今夜は美咲と約束がある。"
        $ flags["misaki_tonight"] = False
        call misaki_date
        return

    # 3. カナの約束のみある場合
    if flags.get("kana_tonight") and not flags.get("misaki_tonight"):
        "今夜はカナと約束がある。"
        $ flags["kana_tonight"] = False
        call kana_date
        return

    # 4. 約束なし → 通常の夜メニュー
    if game_date["day"] <= 5:
        "夜9時。サラリーマンは終電心配してる時間。"
        himo "大変だなあ"

    menu:
        "【[game_date[day]]日目・夜】何をする？"
        # ...既存の選択肢...
```

**合わせて確認**: `double_booking_event` 内でどちらかを優先した後、残ったフラグ（`misaki_tonight` or `kana_tonight`）がTrueのまま残るようにすること。`double_booking_event` から `return` した後、上記の2番・3番の処理に自然に流れるようにする。

```python
label double_booking_event:
    "スマホを見ると、二つの約束が重なっていることに気づいた。"
    "美咲とカナ、両方と今夜の約束が入っている。"
    himo "...やばい"

    menu:
        "どちらを優先する？"

        "美咲を優先":
            "カナにLINEを送った。"
            himo "ごめん、今日急用が入って"
            kana_c "え〜、そうなんだ。まあいいけど"
            $ flags["kana_tonight"] = False     # カナをキャンセル
            # misaki_tonightはTrueのまま → 上記2番の処理へ
            $ change_trust_kana(-5)
            $ change_dependence_kana(3)

        "カナを優先":
            "美咲にLINEを送った。"
            himo "ごめん、今日急用が入って"
            misaki_c "...そうなんだ。分かった"
            $ flags["misaki_tonight"] = False   # 美咲をキャンセル
            # kana_tonightはTrueのまま → 上記3番の処理へ
            $ change_trust(-8)
            $ change_dependence(5)
            $ add_suspicion("contact_delay")

        "両方すっぽかす":
            himo "...両方に謝るか"
            "美咲とカナ、両方に言い訳のLINEを送った。"
            $ flags["misaki_tonight"] = False
            $ flags["kana_tonight"]   = False
            $ change_trust(-5)
            $ change_trust_kana(-5)
            $ himo_aptitude["lies"] += 1
            # 両方Falseなので4番の通常メニューへ

    return
```

---

## 修正3: ナンパ失敗時にafternoon_consumedが立たない

**原因**: `nanpa_event` のナンパ失敗時（成功率チェックで失敗）に `return` しており、`afternoon_consumed = True` を設定する前に抜けている。

**ファイル**: `events/daily_events.rpy`

```python
label nanpa_event:
    scene bg_placeholder

    "繁華街をぶらぶらしていた。"

    python:
        import random
        charm = player["charm"]
        if charm >= 70:
            success_rate = 0.60
        elif charm >= 50:
            success_rate = 0.40
        elif charm >= 35:
            success_rate = 0.25
        else:
            success_rate = 0.10

        nanpa_success = random.random() < success_rate

    if not nanpa_success:
        "声をかけてみたが、うまくいかなかった。"
        himo "...まあ、そんなもんか"
        $ change_stamina(-5)
        $ flags["afternoon_consumed"] = True   # ✅ 失敗時も追加
        return

    # 成功
    "前を歩く女の子に声をかけた。"
    himo "あの、ちょっといいですか"
    "振り返ったのは、明るそうな女の子だった。"

    $ flags["afternoon_consumed"] = True   # 成功時も念のため確認
    jump k01_nanpa_success
```

---

## テスト確認項目

- [ ] カナへの連絡「雑談する」の後に「今日会おう」となっても、当日誘いの成功率チェックが走る（断られることがある）
- [ ] 美咲とカナの両方に夜の約束がある場合、ダブルブッキングイベントが発生する
- [ ] ダブルブッキングでカナを優先した場合、美咲の信頼が下がる
- [ ] ダブルブッキングで美咲を優先した場合、カナの信頼が下がる
- [ ] ナンパ失敗後に再度ナンパできない（昼ターン消費）
- [ ] ナンパ成功→カナ出会い後に再度ナンパできない

---

*phase3_v1.5_fixes.md - 2026年3月2日作成*
