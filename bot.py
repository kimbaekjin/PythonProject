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

my_gold = 0
eight_gold = 0


@bot.event
async def on_ready():
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

    if await handle_commands(message, content):
        return

    if await handle_misc(message, content):
        return

async def handle_commands(message, content):

    if content != "/명령어":
        return False

    await message.channel.send(
        "📖 사용 가능한 명령어\n\n"
        "💰 버스 유각 분배(신뢰도 대용)\n"
        "/숫자\n"
        "예: /15000\n"
        "→ 골드를 95% 기준으로 나, 에잇에게 분배 후 누적\n\n"

        "💸 버스 유각 분배완료\n"
        "/나 숫자\n"
        "/에잇 숫자\n"
        "예: /나 17000\n"
        "→ 해당 금액 차감\n\n"

        "🔄 유각분배 초기화\n"
        "/분배초기화\n"
        "→ 분배된 골드 0으로 초기화\n\n"

        "🎯 경매 계산\n"
        "/아이템가격 파티인원\n"
        "예: /15000 8\n"
        "→ 로아 경매 입찰가 계산\n\n"

        "📈 현재 혜진이한테 줘야하는 골드현황\n"
        "/현황\n"
        "→ 현재 레이드 진행 상황 표시\n\n"

        "🧹 레이드 기록 초기화\n"
        "/초기화\n\n"

        "🐷 숨겨진 명령어\n"
        "/혜진"
    )

    return True

async def handle_split_reset(message, content):
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


bot.run(TOKEN)