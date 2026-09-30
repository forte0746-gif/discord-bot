import os
import random
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# ==========================================
# 🛠️ 設定項目（ここを自由に変えられます）
# ==========================================
FREQUENCY = 4
INITIAL_WORDS = ["なるほど", "たしかに", "おもしろい", "草", "すごい"]
MIN_LEN = 2   
MAX_LEN = 15  
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

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"🤖 BOTが正常に起動しました: {client.user}")

@client.event
async def on_message(message):
    if message.author.bot:
        return
    content = message.content.strip()
    if MIN_LEN <= len(content) <= MAX_LEN and not content.startswith(("http", "<:")):
        current_words = load_words()
        if content not in current_words:
            save_word(content)
    if random.randint(1, FREQUENCY) == 1:
        custom_emojis = message.guild.emojis
        if custom_emojis:
            chosen_emoji = random.choice(custom_emojis)
            emoji_str = f"<:{chosen_emoji.name}:{chosen_emoji.id}>"
        else:
            emoji_str = "✨"
        words = load_words()
        chosen_word = random.choice(words) if words else "..."
        await message.channel.send(f"{emoji_str} {chosen_word}")

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
        pass # ログ出力を抑止してさらに軽量化

def run_web():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_web, daemon=True).start()

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        client.run(token)
