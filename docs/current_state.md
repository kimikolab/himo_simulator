# ヒモ男シミュレーター コードベース状態スナップショット

**最終更新**: 2026-04-04（Phase 4 Step 2.5 v1.6 修正済み）
**ブランチ**: feature/Phase4

> Web Claude での修正指示書作成時に参照する。変数名・ラベル名・フラグキーはこの文書を正とする。

---

## 1. ファイル構成

```
game/
  script.rpy              # メインループ・行動選択メニュー
  screens.rpy             # UI スクリーン定義
  options.rpy             # ゲーム設定
  gui.rpy                 # UI スタイル
  test_helpers.rpy        # テスト用ヘルパー

  data/
    characters.rpy        # キャラクター定義
    constants.rpy         # 閾値・定数
    variables.rpy         # 全 default 宣言

  systems/
    time_system.rpy       # 日時進行・減衰・advance_day()・advance_time()
    parameter_system.rpy  # パラメータ更新・通知
    sns_system.rpy        # SNS/LINE
    dialogue_log.rpy      # セリフログ（config.all_character_callbacks方式）
    debug_log.rpy         # デバッグログ出力
    lie_puzzle.rpy        # 嘘パズル
    evidence_qte.rpy      # 証拠QTE
    gokiragen_qte.rpy     # ご機嫌取りQTE

  events/
    intro.rpy             # オープニング
    tutorial.rpy          # チュートリアル
    daily_events.rpy      # 日常イベント・強制朝イベント
    misaki_events.rpy     # 美咲イベント全般
    kana_events.rpy       # カナイベント全般
    midgame_events.rpy    # 中盤イベント（疑念・修羅場等）
    date_misaki_places.rpy # 美咲デート場所
    date_kana_places.rpy  # カナデート場所
    date_incidents.rpy    # デート中ハプニング
    endings.rpy           # 5種エンディング＋ヒモ適性診断

  tests/
    smoke_test.rpy
    system_test.rpy
```

---

## 2. 主要ラベル一覧

### script.rpy
- `start` — エントリーポイント
- `main_loop` — メインゲームループ
- `process_pending_events` — 遅延イベントキュー処理
- `morning_actions` / `afternoon_actions` / `night_actions` — 各ターン行動
- `double_booking_event` — ダブルブッキング処理

### misaki_events.rpy
- `contact_misaki` — 美咲にLINE送信
- `contact_misaki_menu` — LINE選択肢メニュー
- `misaki_chat` — 美咲との雑談
- `misaki_date_request` — 美咲をデートに誘う（当日）
- `misaki_meet_planned` — 約束済みのデート
- `misaki_date` — 美咲デート本体
- `misaki_money_request` — お金要求（LINE経由）
- `misaki_doubt_event` — 美咲の疑念イベント
- `misaki_check_in` — **美咲の自発的LINE**（旧名なし。指示書で「initiative_event」と呼ばれることがあるが正式名はこれ）
- `misaki_stress_call` — 美咲のストレス深夜電話
- `misaki_dependence_milestone(threshold)` — 依存度マイルストーン
- `misaki_room_visit` — 美咲の部屋訪問
- `misaki_sunday_morning_scene` — 日曜朝シーン（advance_day経由）
- `misaki_confession` — 告白イベント
- `misaki_daytime_date_request` — 美咲からの昼デート誘い
- `misaki_line_listen_work` — LINE: 仕事の愚痴聞く
- `misaki_line_offer_help` — LINE: 手伝い申し出
- `misaki_line_invite_home` — LINE: 家飲み誘い
- `misaki_line_miss_you` — LINE: 声聞きたい
- `misaki_line_amaeru` — LINE: 甘える
- `misaki_negotiation_start` — 対面交渉開始
- `misaki_negotiation_reaction` — 交渉リアクション
- `misaki_negotiation_refuse` — 交渉拒否時
- `misaki_negotiation_amount` — 交渉金額決定
- `misaki_negotiation_shuraba` — 修羅場
- `misaki_event_M02` / `misaki_event_M03` / `misaki_event_M05` — ストーリーイベント

### kana_events.rpy
- `kana_initiative_event` — カナの自発的LINE
- `k01_nanpa_success` — ナンパ成功
- `kana_visit` — カナ訪問
- `contact_kana` — カナに連絡
- `kana_date_request` — カナをデートに誘う
- `kana_date` — カナデート本体
- `kana_stay_offer` — 泊まり提案（夜デート後）
- `kana_stay_event` — カナの部屋に泊まる
- `kana_stay_decline` — 泊まり辞退
- `kana_stay_at_himo_room` — ヒモ太郎の部屋にカナが泊まる（分岐）
- `kana_stay_at_himo_room_event` — ヒモ太郎の部屋泊まり本体
- `kana_stay_at_himo_decline` — ヒモ太郎の部屋泊まり辞退
- `kana_doubt_event` — カナ版疑念イベント
- `demo_end_scene` — デモ版エンドシーン

### midgame_events.rpy
- `check_midgame_events()` — 中盤イベント発火判定（init python関数）
- `midgame_misaki_busy` — 美咲「最近忙しいの？」
- `midgame_kana_urgent` — カナからの急な呼び出し
- `midgame_double_booking` — ダブルブッキング危機
- `midgame_sighting_confrontation` — 目撃情報→修羅場
- `midgame_kana_raid` — カナの突撃訪問
- `midgame_misaki_direct` — 美咲の直球質問ver.2
- `evidence_trace_event` — 痕跡イベント（泊まり翌朝の証拠発見）
- `cold_war_contact(target)` — 冷戦中の連絡テキスト
- `apology_event(target)` — 謝罪イベント
- `apology_conversation(target)` — 謝罪会話
- `apology_honest` / `apology_gift` / `apology_dodge` — 謝罪方法別

### daily_events.rpy
- `check_forced_morning_event` — 強制朝イベント分岐（翌朝フラグ消費）
- `misaki_sunday_morning_icha` — 日曜朝イチャイチャ
- `misaki_morning_at_himo_room` — 美咲がヒモ太郎の部屋に泊まった翌朝
- `kana_morning_after_event` — カナ宅泊まり翌朝
- `kana_himo_room_morning_event` — カナがヒモ太郎の部屋に泊まった翌朝
- `morning_phone_misaki` / `morning_phone_kana` — 朝の電話
- `check_forced_afternoon_event` — 強制午後イベント
- `afternoon_street` — 街に出る
- `nanpa_event` / `shopping_event` / `pachinko_event` — 各種日常

### time_system.rpy（init python 内の関数）
- `advance_day()` — 日付進行。約束不履行チェック・フラグリセット含む
- `advance_time()` — 時間帯進行（朝→昼→夜）
- `queue_misaki_initiative()` — 美咲の自発連絡をキューに追加
- `check_misaki_event_unlock()` — イベント解放条件チェック

---

## 3. 変数・フラグ一覧

### flags（永続フラグ）

| キー | 型 | 説明 |
|------|------|------|
| `tutorial_done` | bool | チュートリアル完了 |
| `first_money` | bool | 初回お金要求済み |
| `first_date` | bool | 初回デート済み |
| `street_unlocked` | bool | 「街に出る」解放（4日目） |
| `nanpa_unlocked` | bool | ナンパ解放 |
| `had_doubt_moment` | bool | 疑念モーメント発生済み |
| `doubt_event_done` | bool | 美咲疑念イベント済み |
| `confession_done/pending/accepted/ambiguous/rejected` | bool | 告白関連 |
| `misaki_tonight` | bool | 今夜美咲と約束あり |
| `misaki_tonight_broken` | bool | 美咲との約束を破った |
| `misaki_visit_himo_room` | bool | 美咲がヒモ太郎の部屋に来る |
| `misaki_stayed_at_himo` | bool | 美咲がヒモ太郎の部屋に泊まった |
| `misaki_sunday_morning` | bool | 土曜泊まり→日曜朝シーン待ち |
| `misaki_good_mood_tonight` | bool | 美咲のテンションが高い |
| `kana_tonight` | bool | 今夜カナと約束あり |
| `kana_morning_after` | bool | カナ宅泊まり翌朝イベント待ち |
| `kana_himo_room_morning` | bool | カナがヒモ太郎の部屋に泊まった翌朝 |
| `kana_at_himo_room` | bool | カナがヒモ太郎の部屋に泊まり中 |
| `kana_doubt_event_done` | bool | カナ版疑念イベント済み |
| `kana_friend_info_obtained` | bool | カナの友人情報入手済み |
| `game_ended` | bool | ゲーム終了 |
| `morning_consumed` | bool | 朝ターン消費済み |
| `afternoon_consumed` | bool | 午後ターン消費済み |
| `k05_accepted/ambiguous` | bool | K-05回答 |
| `qte_failed_badly` | bool | QTE大失敗 |
| `izakaya_money_hangover` | bool | 居酒屋交渉の翌日疑念リスク |
| `midgame_*` | bool | 各中盤イベント済みフラグ（7種） |
| `last_sns_poster` | str | SNS重複防止 |
| `last_news_item` | str | ニュース重複防止 |
| `misaki_stayed_himo_this_week` | bool | 美咲が今週ヒモ太郎の部屋に泊まった（週間リセット） |
| `kana_stayed_himo_this_week` | bool | カナが今週ヒモ太郎の部屋に泊まった（週間リセット） |
| `evidence_trace_done_this_week` | bool | 今週痕跡イベント済み（週間リセット） |
| `evidence_trace_count` | int | 痕跡イベント発生回数（永続。2回目以降は専用テキスト＋即level=2冷戦） |
| `offered_help_this_week` | bool | 今週「手伝い」選択済み（週間リセット） |

### location_flags（場所関連・永続）

| キー | 型 | 説明 |
|------|------|------|
| `misaki_room_unlocked` | bool | 美咲の部屋解放済み |
| `staying_at_misaki` | bool | 美咲の部屋に泊まり中 |
| `staying_at_kana` | bool | カナの部屋に泊まり中 |

### daily_flags（1日ごとにリセット）

| キー | 型 | 説明 |
|------|------|------|
| `asked_money_today` | bool | 当日お金要求済み |
| `ignored_today` | bool | 当日美咲に無視された |
| `ignored_kana_today` | bool | 当日カナに無視された |
| `date_planned_tonight` | bool | 夜デート予定あり |
| `ate_today` | bool | 食事済み |
| `date_location` | str/None | 当日デート場所 |
| `date_with` | str/None | 当日デート相手 |
| `sns_shown_today` | bool | SNS通知表示済み |
| `double_booking_checked` | bool | ダブルブッキングチェック済み |
| `misaki_wants_tonight` | bool | 美咲が今夜会いたい |
| `kana_wants_tonight` | bool | カナが今夜会いたい |
| `money_refused_today` | bool | 金銭要求拒否された |
| `kana_tonight_source` | str/None | "player" or "kana" |
| `misaki_lined_only` | bool | LINEのみで対面なし |
| `misaki_line_last_shown` | list | LINE選択肢の前回表示分 |
| `kana_mood_resolved` | bool | ご機嫌取り済み |

### appointments（約束日管理）

| キー | 型 | 説明 |
|------|------|------|
| `misaki` | int/None | 美咲との約束がある日（日数） |
| `kana` | int/None | カナとの約束がある日（日数） |

### suspicion（疑念度）

| キー | 型 | 説明 |
|------|------|------|
| `misaki` | int | 美咲の疑念度（0〜100） |
| `kana` | int | カナの疑念度（0〜100） |

### cold_war（冷戦状態・Phase 4 Step 2.5追加）

| キー | 型 | 説明 |
|------|------|------|
| `misaki_active` | bool | 美咲と冷戦中 |
| `misaki_level` | int | 冷戦レベル（1=軽度、2=重度） |
| `misaki_days_left` | int | 冷戦残り日数 |
| `misaki_apology_available` | bool | 謝罪イベント解禁済み |
| `kana_active` | bool | カナと冷戦中 |
| `kana_level` | int | 冷戦レベル |
| `kana_days_left` | int | 冷戦残り日数 |
| `kana_apology_available` | bool | 謝罪イベント解禁済み |
| `recovery_misaki` | int | 美咲の回復度 |
| `recovery_kana` | int | カナの回復度 |

冷戦中は対象キャラの自発連絡（`check_kana_initiative`、`queue_misaki_initiative`）と中盤イベント（`check_midgame_events` 内の該当キャラ分岐）が発火しない。

---

## 4. 主要定数（constants.rpy）

| 定数 | 値 | 説明 |
|------|------|------|
| `GAME_DAYS` | 30 | ゲーム期間 |
| `MONTHLY_RENT` | 50000 | 月額家賃 |
| `STAGE_ACQUAINTANCE/FRIEND/CLOSE/DATING` | 1/2/3/4 | 関係ステージ |
| `SUSPICION_MAX` | 100 | 疑念度上限 |
| `NEGOTIATION_WEEKLY_LIMIT` | 4 | 週間交渉上限 |
| `SUSPICION_SHURABA_THRESHOLD` | 3 | 修羅場発生の疑念度閾値 |
| `KANA_EXPLOITATION_THRESHOLD` | 15 | カナ版疑念イベント発火の搾取スコア閾値 |
| `DEBUG_MODE` | True | デバッグモード |

---

## 5. 翌朝フラグの排他ルール（v1.4追加）

同一ターンで複数の泊まり翌朝フラグが立つことを防ぐ:

- **美咲に泊まる時** → カナ翌朝フラグ4種をクリア
  - `flags["kana_morning_after"]`, `flags["kana_himo_room_morning"]`
  - `location_flags["staying_at_kana"]`, `flags["kana_at_himo_room"]`
- **カナに泊まる時** → 美咲翌朝フラグ2種をクリア
  - `flags["misaki_sunday_morning"]`, `location_flags["staying_at_misaki"]`

消費順序（`check_forced_morning_event`）:
1. `kana_himo_room_morning` → カナがヒモ太郎の部屋翌朝
2. `kana_morning_after` → カナ宅翌朝
3. `misaki_stayed_at_himo` → 美咲がヒモ太郎の部屋翌朝
4. `misaki_tonight_broken` → 約束破り
5. `misaki_sunday_morning` → 日曜朝

---

## 6. 冷戦システム（Phase 4 Step 2.5追加）

### 発火条件
- 痕跡イベント（`evidence_trace_event`）で嘘パズル失敗 or 「正直に認める」選択

### days_leftカウントダウン仕様（v1.5明記）
- `advance_day()` 内で毎日 `days_left -= 1` が実行される
- `days_left <= 0` で `end_cold_war()` → 自動解除
- 悪化時（`escalate_cold_war()`）: `days_left = max(current, 3) + 3` で再設定
- デバッグログ: `冷戦TICK [target] level=X days_left=Y→Z active=True`
- 解除ログ: `冷戦解除 [target] 自動期限切れ`

### 冷戦中の制限
- 対象キャラの自発連絡が停止（`check_kana_initiative` / `queue_misaki_initiative` にガードあり）
- 対象キャラの中盤イベントが停止（`check_midgame_events` 内の全該当イベントにガードあり — v1.5で①⑤⑥を追加修正）
- 対象キャラへのLINE連絡が専用テキストに切り替わる（`cold_war_contact`）
- 対象キャラの部屋訪問・デート誘い選択肢が非表示（v1.5追加: `script.rpy` の `night_actions` / `afternoon_actions`）
- `process_pending_events` でチェックイン消費時に冷戦再チェック（v1.5追加）
- SNSステータスが冷戦レベル別テキストに切り替わる（v1.5追加: `sns_show_misaki_mood`）

### 冷戦の解除
- `cold_war[target+"_days_left"]` が0になると自動解除
- 謝罪イベント（`apology_event`）で解除を早められる

### 痕跡イベント発火条件
- 週間フラグ: 美咲 or カナがヒモ太郎の部屋に泊まった週に、もう片方が訪問
- `evidence_trace_done_this_week` で週1回制限

### 週間リセット対象フラグ（`advance_day` 内、7日ごと）
- `money_request_weekly["count"]` — 週間お金要求回数
- `misaki_stayed_himo_this_week` / `kana_stayed_himo_this_week` — 泊まり痕跡
- `evidence_trace_done_this_week` — 痕跡イベント済み
- `offered_help_this_week` — 手伝い選択肢の週間制限

---

## 7. デートハプニングの場所制限（v1.5追加）

`date_happening` で自宅系の場所（`himo_room`, `room`, `misaki_room`）では外出系ハプニング（`acquaintance` = 同僚遭遇・友人目撃）が発火しない。LINE通知・インスタ撮影・レシート落とし等は場所に関係なく発火する。

---

## 8. 最近のコミット（直近10件）

```
（v1.5 + v1.6 fixes — コミット前）
66f7e7f Claude.md更新、current_state.md追加
d92caea Phase4 step2 v1.4 fixes
e7c89cf ignore: debug_logフォルダ以下を無視
3aeacd3 docs整理: 旧修正指示書・実装記録・旧版設計書を削除
be77c0c phase4_step2_v1.2_fixes
5dd1138 Phase4 step2 v1.1 fixes
3151fff 台詞ログ機能を実装
e48bde8 Phase4 step1 v1.6 fixes
793d4bd Phase4 v1.5 fixes
```

---

## 9. 修正指示書を書くときの注意

1. **ラベル名は必ずこの文書のセクション2を参照**する
   - 例: 美咲の自発LINE = `misaki_check_in`（`misaki_initiative_event` ではない）
2. **フラグ辞書の使い分け**に注意
   - `flags[]` = 永続フラグ
   - `location_flags[]` = 場所関連（`staying_at_*`, `misaki_room_unlocked`）
   - `daily_flags[]` = 1日リセット
   - `appointments[]` = 約束日（キーは `"misaki"` / `"kana"`、値は日数 int or None）
3. **コード例よりも方針を書く**方がズレにくい
   - 「この変数をFalseにする」ではなく「断られた時点で約束フラグを消す」
4. この文書は Claude Code が更新する。Web Claude 側では編集しない
