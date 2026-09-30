import os
import random
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from janome.tokenizer import Tokenizer

# ==========================================
# 🛠️ 設定項目（ここを自由に変えられます）
# ==========================================
FREQUENCY = 4  # 発言頻度（4回に1回）
INITIAL_WORDS = ["なるほど", "たしかに", "おもしろい", "草", "すごい"]
# ==========================================

DATA_FILE = "learned_words.txt"
tokenizer = Tokenizer()

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

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤖 にあの左脳ちゃんがVer2で起動しました: {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    content = message.content.strip()
    
    # --- 1. 文章を単語ごとに区切って学習する機能 ---
    if content and not content.startswith(("http", "<:")):
        current_words = load_words()
        try:
            # 文章をバラバラに分析
            tokens = tokenizer.tokenize(content)
            for token in tokens:
                word = token.surface.strip()
                # 名詞、動詞、形容詞、副詞、カスタム絵文字以外の2文字〜10文字の単語を学習
                pos = token.part_of_speech.split(',')[0]
                if pos in ['名詞', '動詞', '形容詞', '副詞'] and 2 <= len(word) <= 10 and not word.startswith("<:"):
                    if word not in current_words:
                        save_word(word)
                        current_words.append(word) # 重複保存防止
        except Exception as e:
            print(f"学習エラー: {e}")

    # --- 2. 乱数による発言頻度の制御 ---
    if random.randint(1, FREQUENCY) == 1:
        words = load_words()
        
        # 50%の確率で「絵文字だけ」、50%の確率で「単語だけ」にする
        if random.choice([True, False]):
            # 【絵文字だけモード】
            custom_emojis = message.guild.emojis
            if custom_emojis:
                chosen_emoji = random.choice(custom_emojis)
                await message.channel.send(f"<:{chosen_emoji.name}:{chosen_emoji.id}>")
            else:
                await message.channel.send("✨")
        else:
            # 【単語だけモード】
            chosen_word = random.choice(words) if words else "..."
            await message.channel.send(chosen_word)

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
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_web, daemon=True).start()

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        client.run(token)
