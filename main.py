import os
import random
import re
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# ==========================================
# 🛠️ 設定項目（ここを自由に変えられます）
# ==========================================
FREQUENCY = 10  # 発言頻度を10%（10回に1回）に固定

INITIAL_WORDS = ["なるほど", "たしかに", "おもしろい", "草", "おか", "天才", "りゅさん", "せん主", "まじで"]
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

# 文字の種類（漢字・ひらがな・カタカナ・英数字）の変わり目で単語を切り分ける関数
def split_by_script(text):
    pattern = re.compile(r'([\u4e00-\u9fff]+|[\u3040-\u309f]+|[\u30a0-\u30ff]+|[a-zA-Z0-9]+)')
    return [m.group(0) for m in pattern.finditer(text)]

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤖 にあの左脳ちゃんがVer8(5〜12個連結版)で起動しました: {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    
    content = message.content.strip()

    # --- 1. 文字種判別による超軽量・自動単語学習機能 ---
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

    # --- 2. 乱数による発言頻度の制御 (10%固定) ---
    if random.randint(1, FREQUENCY) == 1:
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
            # 【【最新】単語を5〜12個、確率に傾斜をつけて繋げるモード】
            if words:
                # ── 繋げる個数を確率で決定する（傾斜システム） ──
                dice = random.randint(1, 100)
                if dice <= 85:
                    # 85%の確率で 5〜9個
                    target_count = random.randint(5, 9)
                else:
                    # 15%の確率で 10〜12個（限界突破）
                    target_count = random.randint(10, 12)
                
                # 覚えている単語数が足りない場合は、今ある単語数を上限にする
                word_count = min(target_count, len(words))
                
                # 覚えた言葉の中から重複なしで指定個数選ぶ
                chosen_list = random.sample(words, word_count)
                
                # スペースなしで結合して送信
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
