# characters.rpy
# キャラクター定義

define himo = Character("ヒモ太郎", color="#ffffff")
define misaki_c = Character("美咲", color="#ffb7c5")

# Phase 3: カナ追加
define kana_c  = Character("カナ",   color="#ffe066")
# define reiko_c = Character("麗子",   color="#b7d7ff")
# define yui_c   = Character("ゆい",   color="#c8f7c5")
# define airi_c  = Character("あいり", color="#e8b7ff")
# define risa_c  = Character("理沙",   color="#ffd4b7")


# ========================================
# 立ち絵画像定義
# ========================================

# 共通Transform: 画面に収まるようスケーリング＋足元固定
transform sprite_base:
    zoom 0.7
    yalign 1.0

init python:
    def sprite(path):
        """立ち絵画像をTransform付きで返す"""
        return Transform(path, zoom=0.7, yalign=1.0, yoffset=110)

# --- 美咲 (OLスーツ) ---
image misaki angry = sprite("images/misaki/angry.png")
image misaki blush = sprite("images/misaki/blush.png")
image misaki cry = sprite("images/misaki/cry.png")
image misaki happy = sprite("images/misaki/happy.png")
image misaki laugh = sprite("images/misaki/laugh.png")
image misaki neutral = sprite("images/misaki/neutral.png")
image misaki normal = sprite("images/misaki/normal.png")
image misaki pleased = sprite("images/misaki/pleased.png")
image misaki sad = sprite("images/misaki/sad.png")
image misaki serious = sprite("images/misaki/serious.png")
image misaki shock = sprite("images/misaki/shock.png")
image misaki shy = sprite("images/misaki/shy.png")
image misaki sleepy = sprite("images/misaki/sleepy.png")
image misaki smile = sprite("images/misaki/smile.png")
image misaki surprised = sprite("images/misaki/surprised.png")
image misaki thinking = sprite("images/misaki/thinking.png")
image misaki wink = sprite("images/misaki/wink.png")
image misaki worried = sprite("images/misaki/worried.png")

# --- 美咲 (カジュアル) ---
image misaki casual angry = sprite("images/misaki casual/angry.png")
image misaki casual blush = sprite("images/misaki casual/blush.png")
image misaki casual cry = sprite("images/misaki casual/cry.png")
image misaki casual happy = sprite("images/misaki casual/happy.png")
image misaki casual laugh = sprite("images/misaki casual/laugh.png")
image misaki casual neutral = sprite("images/misaki casual/neutral.png")
image misaki casual normal = sprite("images/misaki casual/normal.png")
image misaki casual pleased = sprite("images/misaki casual/pleased.png")
image misaki casual sad = sprite("images/misaki casual/sad.png")
image misaki casual serious = sprite("images/misaki casual/serious.png")
image misaki casual shock = sprite("images/misaki casual/shock.png")
image misaki casual shy = sprite("images/misaki casual/shy.png")
image misaki casual sleepy = sprite("images/misaki casual/sleepy.png")
image misaki casual smile = sprite("images/misaki casual/smile.png")
image misaki casual surprised = sprite("images/misaki casual/surprised.png")
image misaki casual thinking = sprite("images/misaki casual/thinking.png")
image misaki casual wink = sprite("images/misaki casual/wink.png")
image misaki casual worried = sprite("images/misaki casual/worried.png")

# --- 美咲 (パジャマ) ---
image misaki pajama angry = sprite("images/misaki pajama/angry.png")
image misaki pajama blush = sprite("images/misaki pajama/blush.png")
image misaki pajama cry = sprite("images/misaki pajama/cry.png")
image misaki pajama happy = sprite("images/misaki pajama/happy.png")
image misaki pajama laugh = sprite("images/misaki pajama/laugh.png")
image misaki pajama neutral = sprite("images/misaki pajama/neutral.png")
image misaki pajama normal = sprite("images/misaki pajama/normal.png")
image misaki pajama pleased = sprite("images/misaki pajama/pleased.png")
image misaki pajama sad = sprite("images/misaki pajama/sad.png")
image misaki pajama serious = sprite("images/misaki pajama/serious.png")
image misaki pajama shock = sprite("images/misaki pajama/shock.png")
image misaki pajama shy = sprite("images/misaki pajama/shy.png")
image misaki pajama sleepy = sprite("images/misaki pajama/sleepy.png")
image misaki pajama smile = sprite("images/misaki pajama/smile.png")
image misaki pajama surprised = sprite("images/misaki pajama/surprised.png")
image misaki pajama thinking = sprite("images/misaki pajama/thinking.png")
image misaki pajama wink = sprite("images/misaki pajama/wink.png")
image misaki pajama worried = sprite("images/misaki pajama/worried.png")

# --- カナ (デフォルト) ---
image kana angry = sprite("images/kana/angry.png")
image kana blush = sprite("images/kana/blush.png")
image kana cry = sprite("images/kana/cry.png")
image kana excited = sprite("images/kana/excited.png")
image kana happy = sprite("images/kana/happy.png")
image kana laugh = sprite("images/kana/laugh.png")
image kana neutral = sprite("images/kana/neutral.png")
image kana normal = sprite("images/kana/normal.png")
image kana pleased = sprite("images/kana/pleased.png")
image kana pouty = sprite("images/kana/pouty.png")
image kana sad = sprite("images/kana/sad.png")
image kana serious = sprite("images/kana/serious.png")
image kana shock = sprite("images/kana/shock.png")
image kana sleepy = sprite("images/kana/sleepy.png")
image kana smile = sprite("images/kana/smile.png")
image kana surprised = sprite("images/kana/surprised.png")
image kana wink = sprite("images/kana/wink.png")
image kana yandere = sprite("images/kana/yandere.png")

# --- カナ (パジャマ) ---
image kana pajama angry = sprite("images/kana pajama/angry.png")
image kana pajama blush = sprite("images/kana pajama/blush.png")
image kana pajama cry = sprite("images/kana pajama/cry.png")
image kana pajama excited = sprite("images/kana pajama/excited.png")
image kana pajama happy = sprite("images/kana pajama/happy.png")
image kana pajama laugh = sprite("images/kana pajama/laugh.png")
image kana pajama neutral = sprite("images/kana pajama/neutral.png")
image kana pajama normal = sprite("images/kana pajama/normal.png")
image kana pajama pleased = sprite("images/kana pajama/pleased.png")
image kana pajama pouty = sprite("images/kana pajama/pouty.png")
image kana pajama sad = sprite("images/kana pajama/sad.png")
image kana pajama serious = sprite("images/kana pajama/serious.png")
image kana pajama shock = sprite("images/kana pajama/shock.png")
image kana pajama sleepy = sprite("images/kana pajama/sleepy.png")
image kana pajama smile = sprite("images/kana pajama/smile.png")
image kana pajama surprised = sprite("images/kana pajama/surprised.png")
image kana pajama wink = sprite("images/kana pajama/wink.png")
image kana pajama yandere = sprite("images/kana pajama/yandere.png")

# --- カナ (大学) ---
image kana university angry = sprite("images/kana university/angry.png")
image kana university blush = sprite("images/kana university/blush.png")
image kana university cry = sprite("images/kana university/cry.png")
image kana university excited = sprite("images/kana university/excited.png")
image kana university happy = sprite("images/kana university/happy.png")
image kana university laugh = sprite("images/kana university/laugh.png")
image kana university neutral = sprite("images/kana university/neutral.png")
image kana university normal = sprite("images/kana university/normal.png")
image kana university pleased = sprite("images/kana university/pleased.png")
image kana university pouty = sprite("images/kana university/pouty.png")
image kana university sad = sprite("images/kana university/sad.png")
image kana university serious = sprite("images/kana university/serious.png")
image kana university shock = sprite("images/kana university/shock.png")
image kana university sleepy = sprite("images/kana university/sleepy.png")
image kana university smile = sprite("images/kana university/smile.png")
image kana university surprised = sprite("images/kana university/surprised.png")
image kana university wink = sprite("images/kana university/wink.png")
image kana university yandere = sprite("images/kana university/yandere.png")
