import discord
from discord.ext import commands

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
    global count_4, count_last

    if message.author.bot:
        return

    content = message.content

    # 레이드 기록
    if content.startswith("/") and " " in content:
        parts = content.split()

        if len(parts) == 2:
            raid = parts[1]

            if raid == "4막":
                count_4 += 1

            elif raid == "종막":
                count_last += 1

            await message.channel.send(
                f"📊 진행 상황\n"
                f"4막 : {count_4}/{TARGET_4}\n"
                f"종막 : {count_last}/{TARGET_LAST}"
            )

    # 현황 보기
    if content == "/현황":
        await message.channel.send(
            f"📊 현재 진행\n"
            f"4막 : {count_4}/{TARGET_4}\n"
            f"종막 : {count_last}/{TARGET_LAST}"
        )

    # 초기화
    if content == "/초기화":
        count_4 = 0
        count_last = 0

        await message.channel.send("초기화 진행중...")

        async for msg in message.channel.history(limit=100):
            await msg.delete()

        await message.channel.send("✅ 모든 기록 초기화 완료")

bot.run(TOKEN)