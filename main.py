import os
import random
import re
import discord
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread

# ==========================================
# 🛠️ 設定項目（ここを自由に変えられます）
# ==========================================
# 【修正】乱数の上限を「8」にしました（1〜8の数字から「1」が出たら喋ります。確率約12.5%）
# これで「割とチャットに出てくるな」という存在感になります。
RANDOM_MAX = 8  

INITIAL_WORDS = ["なるほど", "たしかに", "おもしろい", "草", "すごい", "天才", "さすがに", "やばい", "まじで"]
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

# 指定された確率比率（、:35%, 。:25%, !:20%, ?:20%）で記号を1つ選ぶ関数
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
    print(f"🤖 にあの左脳ちゃんがVer12(1/8確率版)で起動しました: {client.user}")

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

    # --- 2. 乱数ガチャによる発言頻度の制御（1/8の確率に微調整） ---
    if random.randint(1, RANDOM_MAX) == 1:
        words = load_words()
        
        # 50%の確率で「絵文字だけ」、50%の確率で「ランダムな数の単語を密着させた文」にする
        if random.choice([True, False]):
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
                    target_count = random.randint(5, 7) # 95%の確率で 5〜7個
                else:
                    target_count = random.randint(8, 9) # 5%の確率で 8〜9個
                
                word_count = min(target_count, len(words))
                chosen_list = random.sample(words, word_count)
                
                # ── 30%の確率で単語の間に指定比率の記号を挟みながら結合する ──
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
    # Renderが指定するポート（10000番）で確実にWebサーバーを立ち上げます
    server = HTTPServer(('0.0.0.0', 10000), SimpleHTTPRequestHandler)
    server.serve_forever()

Thread(target=run_web, daemon=True).start()

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if token:
        client.run(token)
