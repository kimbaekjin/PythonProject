import discord
from discord.ext import commands
from discord import app_commands
import math

TOKEN = "MTQ4MDc5NjcwMjgzMDIzMTYxNQ.Gf4bFL.RDSEL4ze7nuAYPJmWZXOB70FmAa5a52UGP3x-w"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

count_4 = 0
count_last = 0

TARGET_4 = 4
TARGET_LAST = 4

my_gold = 0
eight_gold = 0


@bot.event
async def on_ready():
    await bot.tree.sync()
    print("봇 로그인 완료")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content

    if await handle_split(message, content):
        return

    if await handle_spend(message, content):
        return

    if await handle_gold_status(message, content):
        return

    if await handle_split_reset(message, content):
        return

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

    return True

async def handle_gold_status(message, content):
    global my_gold, eight_gold

    if content != "/분배초기화":
        return False

    my_gold = 0
    eight_gold = 0

    await message.channel.send(
        "💰 분배 데이터 초기화 완료\n"
        "나 : 0\n"
        "에잇 : 0"
    )

    return True

async def handle_split_reset(message, content):
    if content != "/내놔":
        return False

    await message.channel.send(
        f"💰 받아야하는 골드\n"
        f"나 : {my_gold}\n"
        f"에잇 : {eight_gold}"
    )

    return True

async def handle_spend(message, content):
    global my_gold, eight_gold

    if not content.startswith("/"):
        return False

    parts = content.split()

    if len(parts) != 2:
        return False

    name = parts[0][1:]
    amount = parts[1]

    if not amount.isdigit():
        return False

    amount = int(amount)

    if name == "나":
        my_gold -= amount

    elif name == "에잇":
        eight_gold -= amount

    else:
        return False

    await message.channel.send(
        f"💰 현재 골드\n"
        f"나 : {my_gold}\n"
        f"에잇 : {eight_gold}"
    )

    return True

async def handle_split(message, content):
    global my_gold, eight_gold

    if not content.startswith("/"):
        return False

    cmd = content[1:]

    if " " in cmd:
        return False

    if not cmd.isdigit():
        return False

    gold = int(cmd)

    split = int(gold * 0.95 / 2)

    my_gold += split
    eight_gold += split

    await message.channel.send(
        f"💰 분배 결과\n"
        f"나 : {my_gold}\n"
        f"에잇 : {eight_gold}"
    )

    return True

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

@bot.tree.command(name="도움", description="명령어 목록 보기")
async def help_cmd(interaction: discord.Interaction):

    await interaction.response.send_message(
        "📖 명령어 목록\n"
        "/17000(혜진이한테 유각분배 대신 버스비로 받을 금액)\n"
        "/나 or 에잇 17000(혜진이한테 유각분배 대신 버스비로 받은 금액)\n"
        "/분배초기화(그냥 귀찮아서 만든거)\n"
        "/내놔(현재 유각분배 대신 버스비로 받아야 하는 남은 금액)\n"
        "/15000 4 or 8(/유각금액 인원수\n"
        "/캐릭터이름 4막\n"
        "/캐릭터이름 종막\n"
        "/현황\n"
        "/초기화(현재 채널 메시지기록 초기화)"
    )

bot.run(TOKEN)