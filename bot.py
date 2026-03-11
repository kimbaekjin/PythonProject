import discord
from discord.ext import commands
import math

TOKEN = "MTQ4MDc5NjcwMjgzMDIzMTYxNQ.Gf4bFL.RDSEL4ze7nuAYPJmWZXOB70FmAa5a52UGP3x-w"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

count_4 = 0
count_last = 0

TARGET_4 = 4
TARGET_LAST = 4


@bot.event
async def on_ready():
    print("봇 로그인 완료")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content

    if await handle_auction(message, content):
        return

    if await handle_raid(message, content):
        return

    if await handle_status(message, content):
        return

    if await handle_reset(message, content):
        return

    if await handle_misc(message, content):
        return


# 경매 계산
async def handle_auction(message, content):
    if not content.startswith("/"):
        return False

    parts = content[1:].split()

    if len(parts) != 2:
        return False

    try:
        price = int(parts[0])
        party = int(parts[1])
    except:
        return False

    if party not in [4, 8]:
        return False

    bid = (price - 500) * (party - 1) / party / 1.025
    result = math.floor(bid)

    await message.channel.send(result)
    return True


# 레이드 기록
async def handle_raid(message, content):
    global count_4, count_last

    if not content.startswith("/"):
        return False

    parts = content.split()

    if len(parts) != 2:
        return False

    raid = parts[1]

    if raid not in ["4막", "종막"]:
        return False

    if raid == "4막":
        count_4 += 1
    elif raid == "종막":
        count_last += 1

    await message.channel.send(
        f"📊 진행 상황\n"
        f"4막 : {count_4}/{TARGET_4}\n"
        f"종막 : {count_last}/{TARGET_LAST}"
    )

    return True


# 현황 보기
async def handle_status(message, content):
    if content != "/현황":
        return False

    await message.channel.send(
        f"📊 현재 진행\n"
        f"4막 : {count_4}/{TARGET_4}\n"
        f"종막 : {count_last}/{TARGET_LAST}"
    )

    return True


# 초기화
async def handle_reset(message, content):
    global count_4, count_last

    if content != "/초기화":
        return False

    count_4 = 0
    count_last = 0

    await message.channel.send("초기화 진행중...")

    async for msg in message.channel.history(limit=100):
        await msg.delete()

    await message.channel.send("✅ 모든 기록 초기화 완료")

    return True


# 기타
async def handle_misc(message, content):
    if content == "/혜진":
        await message.channel.send("뱃살보송...")
        return True

    return False


bot.run(TOKEN)