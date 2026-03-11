import discord
from discord.ext import commands
from discord import app_commands
import math

TOKEN = "MTQ4MDc5NjcwMjgzMDIzMTYxNQ.Gf4bFL.RDSEL4ze7nuAYPJmWZXOB70FmAa5a52UGP3x-w"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

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


# 골드 분배
@bot.tree.command(name="분배", description="골드 분배 계산")
async def split(interaction: discord.Interaction, gold: int):
    global my_gold, eight_gold

    split = int(gold * 0.95 / 2)

    my_gold += split
    eight_gold += split

    await interaction.response.send_message(
        f"💰 분배 결과\n"
        f"나 : {my_gold}\n"
        f"에잇 : {eight_gold}"
    )


# 골드 사용
@bot.tree.command(name="사용", description="골드 사용 기록")
async def spend(interaction: discord.Interaction, 사람: str, 골드: int):
    global my_gold, eight_gold

    if 사람 == "나":
        my_gold -= 골드
    elif 사람 == "에잇":
        eight_gold -= 골드
    else:
        await interaction.response.send_message("사람은 나 / 에잇만 가능")
        return

    await interaction.response.send_message(
        f"💰 현재 골드\n"
        f"나 : {my_gold}\n"
        f"에잇 : {eight_gold}"
    )


# 분배 초기화
@bot.tree.command(name="분배초기화", description="골드 기록 초기화")
async def split_reset(interaction: discord.Interaction):
    global my_gold, eight_gold

    my_gold = 0
    eight_gold = 0

    await interaction.response.send_message(
        "💰 분배 데이터 초기화 완료\n"
        "나 : 0\n"
        "에잇 : 0"
    )


# 경매 계산
@bot.tree.command(name="경매", description="경매 입찰 계산")
async def auction(interaction: discord.Interaction, 가격: int, 인원: int):

    if 인원 not in [4, 8]:
        await interaction.response.send_message("인원은 4 또는 8만 가능")
        return

    bid = (가격 - 500) * (인원 - 1) / 인원 / 1.025
    result = math.floor(bid)

    await interaction.response.send_message(f"추천 입찰가 : {result}")


# 레이드 기록
@bot.tree.command(name="레이드", description="레이드 기록")
async def raid(interaction: discord.Interaction, 종류: str):
    global count_4, count_last

    if 종류 == "4막":
        count_4 += 1
    elif 종류 == "종막":
        count_last += 1
    else:
        await interaction.response.send_message("4막 또는 종막만 가능")
        return

    await interaction.response.send_message(
        f"📊 진행 상황\n"
        f"4막 : {count_4}/{TARGET_4}\n"
        f"종막 : {count_last}/{TARGET_LAST}"
    )


# 현황
@bot.tree.command(name="현황", description="레이드 진행 현황")
async def status(interaction: discord.Interaction):

    await interaction.response.send_message(
        f"📊 현재 진행\n"
        f"4막 : {count_4}/{TARGET_4}\n"
        f"종막 : {count_last}/{TARGET_LAST}"
    )


# 초기화
@bot.tree.command(name="초기화", description="레이드 기록 초기화")
async def reset(interaction: discord.Interaction):
    global count_4, count_last

    count_4 = 0
    count_last = 0

    await interaction.response.send_message("✅ 레이드 기록 초기화 완료")


# 도움
@bot.tree.command(name="도움", description="명령어 목록 보기")
async def help_cmd(interaction: discord.Interaction):

    await interaction.response.send_message(
        "📖 명령어 목록\n"
        "/분배 골드\n"
        "/사용 사람 골드\n"
        "/분배초기화\n"
        "/경매 가격 인원\n"
        "/레이드 4막\n"
        "/레이드 종막\n"
        "/현황\n"
        "/초기화"
    )


bot.run(TOKEN)