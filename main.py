import os
import random
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from janome.tokenizer import Tokenizer

# ==========================================
# 🛠️ 初期設定（ここを自由に変えられます）
# ==========================================
INITIAL_WORDS = ["なるほど", "たしかに", "おもしろい", "草", "すごい"]
# ==========================================

DATA_FILE = "learned_words.txt"
tokenizer = Tokenizer()

# 起動時は必ず「観測モード（15回に1回）」からスタート
current_frequency = 15 

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
    print(f"🤖 にあの左脳ちゃんがVer6(スペースなし結合版)で起動しました: {client.user}")

@client.event
async def on_message(message):
    global current_frequency
    
    if message.author.bot:
        return
    
    content = message.content.strip()
    
    # --- 1. モード切り替えコマンドの処理 ---
    if content == "にあの左脳、会話モード":
        current_frequency = 4
        await message.channel.send("🧠 ──会話モードに切り替えました。")
        return
        
    if content == "にあの左脳、観測モード":
        current_frequency = 15
        await message.channel.send("👁️ ──観測モードに切り替えました。静かに見守ります。")
        return

    # --- 2. 文章を単語ごとに区切って学習する機能 ---
    if content and not content.startswith(("http", "<:")):
        current_words = load_words()
        try:
            tokens = tokenizer.tokenize(content)
            for token in tokens:
                word = token.surface.strip()
                pos = token.part_of_speech.split(',')
                if pos in ['名詞', '動詞', '形容詞', '副詞'] and 2 <= len(word) <= 10 and not word.startswith("<:"):
                    if word not in current_words:
                        save_word(word)
                        current_words.append(word)
        except Exception as e:
            print(f"学習エラー: {e}")

    # --- 3. 乱数による発言頻度の制御 ---
    if random.randint(1, current_frequency) == 1:
        words = load_words()
        
        # 50%の確率で「絵文字だけ」、50%の確率で「ランダムな数の単語を密着させた文」にする
        if random.choice([True, False]):
            # 【絵文字だけモード】
            custom_emojis = message.guild.emojis
            if custom_emojis:
                chosen_emoji = random.choice(custom_emojis)
                await message.channel.send(f"<:{chosen_emoji.name}:{chosen_emoji.id}>")
            else:
                await message.channel.send("✨")
        else:
            # 【【最新】単語をスペースなしでギュッと繋げて喋るモード】
            if words:
                max_count = min(4, len(words))
                word_count = random.randint(1, max_count)
                chosen_list = random.sample(words, word_count)
                
                # 【修正】スペースなし（""）で結合します
                reply_text = "".join(chosen_list)
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
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_web, daemon=True).start()

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        client.run(token)
