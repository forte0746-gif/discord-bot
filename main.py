import os
import random
import discord
from flask import Flask
from threading import Thread

# ==========================================
# 🛠️ 設定項目（ここを自由に変えられます）
# ==========================================
# 発言する確率を設定します（例: 4 なら「4回に1回の確率(25%)」で発言します）
# 「2」にすると50%、「10」にすると10%の確率になります。
FREQUENCY = 4

# BOTが最初に覚えている初期単語（学習が進むとここへ自動的に追加されていきます）
INITIAL_WORDS = ["なるほど", "たしかに", "おもしろい", "草", "すごい"]

# 学習する文字数の制限（短すぎる、または長すぎる文を学習しないようにします）
MIN_LEN = 2   # 最低2文字以上
MAX_LEN = 15  # 最高15文字まで
# ==========================================

# データの保存先ファイル
DATA_FILE = "learned_words.txt"

# 初期単語の読み込み・作成
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(INITIAL_WORDS))

def load_words():
    if not os.path.exists(DATA_FILE):
        return INITIAL_WORDS.copy()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def save_word(word):
    with open(DATA_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{word}")

# Discord BOTの起動準備
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤖 BOTが正常に起動しました: {client.user}")

@client.event
async def on_message(message):
    # BOT自身の発言、または他のBOTの発言には反応しない
    if message.author.bot:
        return

    content = message.content.strip()

    # --- 1. 単語の学習機能 ---
    # 条件（文字数制限、URLや絵文字単体ではない等）に合えば学習する
    if MIN_LEN <= len(content) <= MAX_LEN and not content.startswith(("http", "<:")):
        current_words = load_words()
        if content not in current_words:
            save_word(content)

    # --- 2. 乱数による発言頻度の制御 ---
    # 設定した確率（FREQUENCY）で1が当たったら発言する
    if random.randint(1, FREQUENCY) == 1:
        
        # --- 3. サーバー限定絵文字の取得 ---
        # メッセージが送られたサーバーの絵文字リストを取得
        custom_emojis = message.guild.emojis
        
        if custom_emojis:
            # サーバー限定絵文字がある場合、ランダムで1つ選ぶ
            chosen_emoji = random.choice(custom_emojis)
            emoji_str = f"<:{chosen_emoji.name}:{chosen_emoji.id}>"
        else:
            # 限定絵文字が1つもない場合の予備（通常の絵文字）
            emoji_str = "✨"

        # 最新の単語リストからランダムに1つ選ぶ
        words = load_words()
        chosen_word = random.choice(words) if words else "..."

        # メッセージを送信
        await message.channel.send(f"{emoji_str} {chosen_word}")

# ==========================================
# 💤 Renderで24時間無料起動させるためのWebサーバー
# ==========================================
app = Flask('')

@app.route('/')
def home():
    return "BOT is running!"

def run_web():
    # Renderが指定するポート番号を自動取得して起動します
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# バックグラウンドでWebサーバーを起動
Thread(target=run_web).start()

# Discord BOTの起動（Renderの環境変数からトークンを読み込みます）
if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        client.run(token)
    else:
        print("エラー: DISCORD_TOKEN が設定されていません。")
