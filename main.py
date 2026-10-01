import os
import random
import re
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# ==========================================
# 🛠️ 設定項目（ここを自由に変えられます）
# ==========================================
RANDOM_MAX = 5  # 通常チャットでの発言頻度（1/5の確率）

# 【新機能】メンションされた時に送る、あらかじめ設定された固定文章リスト
PRESET_RESPONSES = [
    "🧠 起きてます、起きてますよ。、たぶん。",
    "マスター、サーヴァント遣いが荒いんじゃないのか？",
    "ねてない！",
    "( ˘ω˘)ｽﾔｧ",
    "うるさあああああああああああああああああああああああああああああああああああい",
    "は？"
]

INITIAL_WORDS = ["ねみい", "あほ", "おもしろい", "草", "天才", "さすがに", "やばい"]
# ==========================================

DATA_FILE = "learned_words.txt"

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

# 文字種別で単語を切り分ける関数
def split_by_script(text):
    pattern = re.compile(r'([\u4e00-\u9fff]+|[\u3040-\u309f]+|[\u30a0-\u30ff]+|[a-zA-Z0-9]+)')
    return [m.group(0) for m in pattern.finditer(text)]

# 記号を選ぶ関数
def choose_punctuation():
    dice = random.randint(1, 100)
    if dice <= 35:
        return "、"        
    elif dice <= 60:
        return "。"        
    elif dice <= 80:
        return "！"        
    else:
        return "？"        

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤖 にあの左脳ちゃんがVer14(メンション強制アクティブ版)で起動しました: {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    # --- 1. 【新機能】メンション（@にあの左脳）された場合の強制アクティブ処理 ---
    if client.user in message.mentions:
        # あらかじめ設定された文章からランダムに送信（確率は100%）
        chosen_preset = random.choice(PRESET_RESPONSES)
        await message.channel.send(chosen_preset)
        return  # メンションの時はここで処理を終了して通常発言はスキップする

    content = message.content.strip()

    # --- 2. 通常の自動単語学習機能 ---
    if content and not content.startswith(("http", "<:")):
        current_words = load_words()
        try:
            words_extracted = split_by_script(content)
            for word in words_extracted:
                word = word.strip()
                if 2 <= len(word) <= 10:
                    if word not in current_words:
                        save_word(word)
                        current_words.append(word)
        except Exception as e:
            print(f"学習エラー: {e}")

    # --- 3. 乱数ガチャによる通常発言頻度の制御（1/5） ---
    if random.randint(1, RANDOM_MAX) == 1:
        words = load_words()
        
        if random.choice([True, False]):
            # 【絵文字だけモード】
            custom_emojis = message.guild.emojis
            if custom_emojis:
                chosen_emoji = random.choice(custom_emojis)
                await message.channel.send(f"<:{chosen_emoji.name}:{chosen_emoji.id}>")
            else:
                await message.channel.send("✨")
        else:
            # 【単語を繋げるモード】
            if words:
                dice = random.randint(1, 100)
                if dice <= 95:
                    target_count = random.randint(5, 7)
                else:
                    target_count = random.randint(8, 9)
                
                word_count = min(target_count, len(words))
                chosen_list = random.sample(words, word_count)
                
                reply_text = ""
                for i, word in enumerate(chosen_list):
                    reply_text += word
                    if i < len(chosen_list) - 1:
                        if random.randint(1, 10) <= 3:
                            reply_text += choose_punctuation()
                
                await message.channel.send(reply_text)
            else:
                await message.channel.send("...")

# ==========================================
# 💤 超軽量（省メモリ）Webサーバーの仕組み
# ==========================================
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"BOT is running!")
    def log_message(self, format, *args):
        pass

def run_web():
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_web, daemon=True).start()

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        client.run(token)
