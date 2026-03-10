import discord
from discord.ext import commands

TOKEN = "MTQ4MDc5NjcwMjgzMDIzMTYxNQ.Gf4bFL.RDSEL4ze7nuAYPJmWZXOB70FmAa5a52UGP3x-w"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

count_4 = 0
count_last = 0

TARGET_4 = 7
TARGET_LAST = 6

history = []

@bot.event
async def on_ready():
    print("봇 로그인 완료")

@bot.event
async def on_message(message):
    global count_4, count_last

    if message.author.bot:
        return

    content = message.content

    # 입력
    if content.startswith("/") and not content.startswith("/취소") and not content.startswith("/현재") and not content.startswith("/초기화"):

        parts = content.split()

        if len(parts) == 2:
            character = parts[0][1:]
            raid = parts[1]

            if raid == "4막":
                count_4 += 1
                history.append("4막")

            elif raid == "종막":
                count_last += 1
                history.append("종막")

            else:
                await message.channel.send("레이드는 4막 또는 종막만 입력해주세요.")
                return

            await message.channel.send(
                f"{character} → {raid} 완료\n"
                f"4막 : {count_4}/{TARGET_4}\n"
                f"종막 : {count_last}/{TARGET_LAST}"
            )

            if count_4 >= TARGET_4 and count_last >= TARGET_LAST:
                await message.channel.send("정산 완료 🎉")

    # 취소
    if content == "/취소":
        if history:
            last = history.pop()

            if last == "4막":
                count_4 -= 1
            elif last == "종막":
                count_last -= 1

            await message.channel.send(
                f"{last} 취소됨\n"
                f"4막 : {count_4}/{TARGET_4}\n"
                f"종막 : {count_last}/{TARGET_LAST}"
            )
        else:
            await message.channel.send("취소할 기록이 없습니다.")

    # 현재 상태
    if content == "/현재":
        await message.channel.send(
            f"현재 진행 상황\n"
            f"4막 : {count_4}/{TARGET_4}\n"
            f"종막 : {count_last}/{TARGET_LAST}"
        )

    # 초기화
    if content == "/초기화":
        count_4 = 0
        count_last = 0
        history.clear()
        await message.channel.send("주간 기록 초기화 완료")

bot.run(TOKEN)