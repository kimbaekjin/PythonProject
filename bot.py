from discord.ext import commands
import aiohttp, math, discord, re
from urllib.parse import quote
from collections import Counter
import asyncio
import datetime, json, os
from zoneinfo import ZoneInfo
from critical import *

# =========================
# 환경변수
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")
LOSTARK_API_KEY = os.getenv("LOSTARK_API_KEY")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN 환경변수가 없습니다.")

if not LOSTARK_API_KEY:
    raise ValueError("LOSTARK_API_KEY 환경변수가 없습니다.")

# =========================
# 디스코드 봇 기본 설정
# =========================
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

TARGET_CHANNEL = 1481571646832775169
SCHEDULE_CHANNEL = 1491719061048922202
KST = ZoneInfo("Asia/Seoul")

# =========================
# 요일별 레이드 일정
# =========================
RAID_SCHEDULE = {
    "월요일": [],

    "화요일": [
        ["종노버스", "서머너", "나혜찌니"],
        ["종노버스", "스읔", "혜진이"],
    ],

    "수요일": [
        ["4막하드", "배쉬증함", "흐앙계란주께"],
        ["종노버스", "배쉬증함", "흐앙계란주께"],
        ["세르카하드", "리퍼님", "흐앙계란주께"],
        ["세르카하드", "바훈", "적묵법"],
        ["종노버스", "바훈", "이풀립"],
        ["종노버스", "리퍼님", "콩당콩설"],
    ],

    "목요일": [
        ["세르카노말", "이겸필", "도빵울", "암거나"],
        ["4막노말버스", "정겸필", "이풀립", "블레이드"],
        ["세르카 노말", "강겸필", "이콩덩", "암거나"],
        ["4막노말버스", "강겸필", "콩당콩설", "배마"],
        ["세르카노말", "리퍼길동이", "블레이드", "워로드"],
        ["4막하드", "바훈", "나혜찌니"],
        ["4막하드", "리퍼님", "적묵법"],
        ["4막하드", "김겸필", "또아가"],
    ],

    "금요일": [
        ["4노 본1부3 버스", "스윽(본)", "블레이드", "데헌", "도화가"],
        ["4노 본1부3 버스", "박겸필", "이콩덩", "디트", "창술(본)"],
        ["4노 본1부3 버스", "이겸필", "혜진이(본)", "호크", "워로드"],
        ["4노 본1부3 버스", "최겸필", "도빵울", "디트(본)", "브커"],
        ["종막 버스", "이겸필", "또아가", "호크", "워로드"],
        ["종막 버스", "김겸필", "블레이드", "인파", "도화가"],
        ["종막 버스", "강겸필", "이콩덩", "워로드", "블레이드"],
        ["종막 버스", "휴지", "적묵법", "데헌", "스커"],
    ],

    "토요일": [],

    "일요일": [
        ["종막노말", "리퍼길동이", "도빵울"],
        ["세르카하드", "암살자길동", "이풀립"],
        ["세르카하드", "저달호", "콩당콩설"],
        ["세르카 하드버스", "상소", "혜진이", "디트"],
        ["세르카 하드버스", "스윽", "나혜찌니", "워로드"],
        ["세르카 하드버스", "휴지", "또아가", "스커"],
    ],
}

# =========================
# 쌀먹/분배 데이터
# =========================
targets = {
    "본계": 36,
    "스카": 18,
    "도화가": 18,
    "리퍼": 30
}

progress = {
    "본계": 0,
    "스카": 0,
    "도화가": 0,
    "리퍼": 0
}

DATA_FILE = "account_data.json"
SCHEDULE_SENT_FILE = "schedule_sent.json"

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_data():
    if not os.path.exists(DATA_FILE):
        data = {
            "start_date": str(datetime.date.today()),
            "progress": {k: 0 for k in targets},
            "gold": {
                "my_gold": 0,
                "eight_gold": 0
            }
        }
        save_data(data)
        return data

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "gold" not in data:
        data["gold"] = {
            "my_gold": 0,
            "eight_gold": 0
        }

    if "progress" not in data:
        data["progress"] = {k: 0 for k in targets}

    if "start_date" not in data:
        data["start_date"] = str(datetime.date.today())

    return data

def load_schedule_sent():
    if not os.path.exists(SCHEDULE_SENT_FILE):
        return {"last_sent_date": ""}
    with open(SCHEDULE_SENT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_schedule_sent(data):
    with open(SCHEDULE_SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

data = load_data()
schedule_sent_data = load_schedule_sent()

progress = data["progress"]
start_date = datetime.date.fromisoformat(data["start_date"])

my_gold = data["gold"]["my_gold"]
eight_gold = data["gold"]["eight_gold"]

count_4 = 0
count_last = 0

TARGET_4 = 4
TARGET_LAST = 4

# =========================
# 공통 헤더
# =========================
def get_auth_headers():
    return {
        "accept": "application/json",
        "authorization": f"bearer {LOSTARK_API_KEY}"
    }

def get_json_headers():
    return {
        "accept": "application/json",
        "authorization": f"bearer {LOSTARK_API_KEY}",
        "content-type": "application/json"
    }

# =========================
# 레이드 일정 메시지
# =========================
def get_korean_weekday_name(dt: datetime.datetime) -> str:
    weekday_map = {
        0: "월요일",
        1: "화요일",
        2: "수요일",
        3: "목요일",
        4: "금요일",
        5: "토요일",
        6: "일요일",
    }
    return weekday_map[dt.weekday()]

def build_schedule_message(day_name: str) -> str:
    rows = RAID_SCHEDULE.get(day_name, [])

    if not rows:
        return f"📅 오늘의 레이드 일정 ({day_name})\n\n오늘은 등록된 일정이 없습니다."

    msg = f"📅 오늘의 레이드 일정 ({day_name})\n\n"

    for idx, row in enumerate(rows, start=1):
        raid_name = row[0]
        members = [x for x in row[1:] if x and str(x).strip()]
        msg += f"**{idx}. {raid_name}**\n"
        msg += " / ".join(members) + "\n\n"

    return msg.strip()

# =========================
# 봇 이벤트
# =========================
@bot.event
async def on_ready():
    await bot.tree.sync()
    bot.loop.create_task(monthly_check_loop())
    bot.loop.create_task(raid_schedule_loop())
    print("봇 로그인 완료")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content = message.content
    print(f"DEBUG on_message called: {content} from {message.author}")

    if content == "/테스트레이드":
        msg = build_schedule_message("목요일")
        await message.channel.send(msg)
        return

    if content == "/오늘레이드":
        await handle_today_raid(message, content)
        return

    if content == "/남은시간":
        await handle_remaining_time(message, content)
        return

    if content.startswith("/치적 "):
        await handle_crit(message, content)
        return

    if content.startswith("/유각"):
        await handle_engraving(message, content)
        return

    if content == "/보석":
        await handle_gem(message, content)
        return

    if re.match(r"^/\d+ (3|4|8)$", content):
        await handle_auction(message, content)
        return

    if re.match(r"^/.+ (4막|종막)$", content):
        await handle_raid(message, content)
        return

    if content == "/현황":
        await handle_status(message, content)
        return

    if content == "/초기화":
        await handle_reset(message, content)
        return

    if content == "/혜진":
        await handle_misc(message, content)
        return

    if content == "/분배초기화":
        await handle_gold_status(message, content)
        return

    if content == "/내놔":
        await handle_split_reset(message, content)
        return

    if re.match(r"^/\d+$", content):
        await handle_split(message, content)
        return

    if re.match(r"^/(나|에잇) \d+$", content):
        await handle_spend(message, content)
        return

    if message.channel.id == TARGET_CHANNEL:
        if re.match(r"^/(본계|스카|도화가|리퍼) \d+$", content):
            await handle_account(message, content)
            return

        if content == "/쌀먹초기화":
            await handle_account_reset(message, content)
            return

        if content == "/쌀먹현황":
            await handle_account_status(message, content)
            return

    if content.startswith("/") and " " not in content:
        await handle_armory(message, content)
        return

    return True

# =========================
# 자동 루프
# =========================
async def raid_schedule_loop():
    await bot.wait_until_ready()

    while not bot.is_closed():
        try:
            now = datetime.datetime.now(KST)
            today_str = now.strftime("%Y-%m-%d")
            today_name = get_korean_weekday_name(now)
            channel = bot.get_channel(SCHEDULE_CHANNEL)

            already_sent = schedule_sent_data.get("last_sent_date") == today_str

            if now.hour == 19 and now.minute == 50 and not already_sent:
                if channel:
                    msg = build_schedule_message(today_name)
                    await channel.send(msg)
                    schedule_sent_data["last_sent_date"] = today_str
                    save_schedule_sent(schedule_sent_data)

            await asyncio.sleep(30)

        except Exception as e:
            print(f"[raid_schedule_loop ERROR] {e}")
            await asyncio.sleep(30)

async def monthly_check_loop():
    global start_date
    await bot.wait_until_ready()

    warned = False

    while not bot.is_closed():
        now = datetime.date.today()

        reset_date = start_date + datetime.timedelta(days=30)
        warn_date = reset_date - datetime.timedelta(days=7)

        channel = bot.get_channel(TARGET_CHANNEL)

        if now == warn_date and not warned:
            if channel:
                await channel.send("⚠️ 일주일 후 월간 정산이 초기화됩니다.")
            warned = True

        if now >= reset_date:
            for k in progress:
                progress[k] = 0

            start_date = now

            data["progress"] = progress
            data["start_date"] = str(start_date)
            save_data(data)

            warned = False

            if channel:
                await channel.send("🔄 월간 정산이 초기화되었습니다.")

        await asyncio.sleep(86400)

# =========================
# 명령 처리
# =========================
async def handle_today_raid(message, content):
    if content != "/오늘레이드":
        return False

    now = datetime.datetime.now(KST)
    today_name = get_korean_weekday_name(now)
    msg = build_schedule_message(today_name)
    await message.channel.send(msg)
    return True

async def handle_crit(message, content):
    parts = content.split()
    if len(parts) != 2:
        await message.channel.send("❌ 사용법: /치적 캐릭터이름")
        return False

    char_name = parts[1]

    try:
        char_class = get_character_class(char_name)
        crit_stat = get_crit_stat(char_name)
        stat_crit = crit_from_stat(crit_stat)
        engraving_crit = get_engraving_crit(char_name)
        ark_data = get_arkpassive_data(char_name)
        arkpassive_crit = get_arkpassive_crit(ark_data, char_class)
        accessory_crit, bracelet_crit = get_accessory_bracelet_crit(char_name)

        total = stat_crit + engraving_crit + arkpassive_crit + bracelet_crit + accessory_crit

        if char_class in ["건슬링어", "기상술사", "데빌헌터", "스트라이커", "배틀마스터", "아르카나"]:
            total += 10
            msg = (
                f"📊 {char_name} ({char_class}) 치명률\n"
                f"시너지: 10%\n"
                f"스탯 치적: {round(stat_crit, 2)}%\n"
                f"각인 치적: {engraving_crit}%\n"
                f"팔찌 치적: {bracelet_crit}%\n"
                f"악세 치적: {round(accessory_crit, 2)}%\n"
                f"아크패시브 치적: {arkpassive_crit}%\n"
                f"총 치적: {round(total, 2)}%"
            )
            await message.channel.send(msg)
            return True

        msg = (
            f"📊 {char_name} ({char_class}) 치명률\n"
            f"스탯 치적: {round(stat_crit, 1)}%\n"
            f"각인 치적: {engraving_crit}%\n"
            f"팔찌 치적: {bracelet_crit}%\n"
            f"악세 치적: {round(accessory_crit, 1)}%\n"
            f"아크패시브 치적: {arkpassive_crit}%\n"
            f"총 치적: {round(total, 1)}%"
        )

        await message.channel.send(msg)
        return True

    except Exception as e:
        await message.channel.send(f"❌ 치적 계산 중 오류 발생: {e}")
        return False

async def handle_account_reset(message, content):
    global start_date

    if content != "/쌀먹초기화":
        return False

    for k in progress:
        progress[k] = 0

    start_date = datetime.date.today()

    data["progress"] = progress
    data["start_date"] = str(start_date)
    save_data(data)

    await message.channel.send("🔄 쌀먹 현황이 초기화되었습니다.")
    return True

async def handle_account_status(message, content):
    if content != "/쌀먹현황":
        return False

    await send_status(message.channel)
    return True

async def handle_remaining_time(message, content):
    if content != "/남은시간":
        return False

    now = datetime.datetime.now()
    reset_datetime = datetime.datetime.combine(start_date + datetime.timedelta(days=30), datetime.time(0, 0))

    remaining = reset_datetime - now
    if remaining.total_seconds() < 0:
        remaining = datetime.timedelta(seconds=0)

    days = remaining.days
    hours, rem = divmod(remaining.seconds, 3600)
    minutes, seconds = divmod(rem, 60)

    await message.channel.send(
        f"⏳ 월간 정산까지 남은 시간: {days}일 {hours}시간 {minutes}분 {seconds}초"
    )

    return True

async def handle_armory(message, content):
    if not content.startswith("/"):
        return False

    char_name = content[1:].strip()
    if not char_name:
        return False

    headers = get_auth_headers()

    siblings_url = f"https://developer-lostark.game.onstove.com/characters/{char_name}/siblings"
    armory_list = []

    async with aiohttp.ClientSession() as session:
        async with session.get(siblings_url, headers=headers) as resp:
            if resp.status != 200:
                await message.channel.send("원정대 API 조회 실패")
                return True
            siblings_data = await resp.json()

        gem_prices_local = await get_gem_prices()

        for c in siblings_data:
            item_level = float(c["ItemAvgLevel"].replace(",", ""))
            if item_level < 1660:
                continue

            single_name = c["CharacterName"]
            encoded = aiohttp.helpers.quote(single_name)

            profile_url = f"https://developer-lostark.game.onstove.com/armories/characters/{encoded}/profiles"
            async with session.get(profile_url, headers=headers) as resp2:
                if resp2.status != 200:
                    continue
                profile_data = await resp2.json()
                char_class = profile_data.get("CharacterClassName", "Unknown")
                combat_power = profile_data.get("CombatPower", 0)

            gem_url = f"https://developer-lostark.game.onstove.com/armories/characters/{encoded}/gems"
            async with session.get(gem_url, headers=headers) as resp3:
                if resp3.status != 200:
                    gems = []
                else:
                    gem_data = await resp3.json()
                    gems_raw = gem_data.get("Gems")
                    if not isinstance(gems_raw, list):
                        gems_raw = []
                    gems = [
                        re.sub(r"<.*?>", "", g.get("Name", "")).strip().replace(" ", "")
                        for g in gems_raw if g.get("Name")
                    ]

            armory_list.append({
                "name": single_name,
                "class": char_class,
                "level": item_level,
                "combat_power": combat_power,
                "gems": gems
            })

    armory_list.sort(key=lambda x: x["level"], reverse=True)
    grand_total = 0
    msg = "```css\n"
    for c in armory_list:
        msg += f"[{c['class']}] {c['name']} ({c['level']}, 전투력 {c['combat_power']})\n"
        if c["gems"]:
            gem_counter = Counter()
            for g in c["gems"]:
                clean_name, is_bound = clean_gem_name(g)
                gem_counter[(clean_name, is_bound)] += 1

            total_price = 0
            for (gem_name, is_bound), count in gem_counter.items():
                display_name = f"{gem_name} (귀속)" if is_bound else gem_name
                msg += f"• {display_name} x{count}\n"

                if not is_bound:
                    price = 0
                    if gem_name in gem_prices_local:
                        price = gem_prices_local[gem_name]
                    elif "광휘" in gem_name:
                        level_match = re.search(r"\d+레벨", gem_name)
                        if level_match:
                            level = level_match.group()
                            price = gem_prices_local.get(f"{level} 겁화", 0)
                    total_price += price * count

                print(
                    f"DEBUG {gem_name}, bound: {is_bound} -> price considered: {0 if is_bound else price}, count: {count}"
                )

            msg += f"💰 보석 총 가격: {total_price:,} 골드\n"
            grand_total += total_price
        else:
            msg += "• 보석 없음\n"
        msg += "\n"
    msg += "\n====================\n"
    msg += f"🔥 원정대 총 보석 가격: {grand_total:,} 골드\n"
    msg += "```"

    await message.channel.send(msg)
    return True

def clean_gem_name(name: str):
    is_bound = "(귀속)" in name
    name_clean = name.replace("(귀속)", "").strip()
    match = re.search(r"(\d+레벨)\s*(겁화|작열|광휘)", name_clean)
    if match:
        return match.group(1) + " " + match.group(2), is_bound
    return name_clean, is_bound

async def get_gem_prices():
    url = "https://developer-lostark.game.onstove.com/auctions/items"
    headers = get_json_headers()

    gems = [
        "6레벨 겁화", "6레벨 작열",
        "7레벨 겁화", "7레벨 작열",
        "8레벨 겁화", "8레벨 작열",
        "9레벨 겁화", "9레벨 작열",
        "10레벨 겁화", "10레벨 작열"
    ]

    gem_prices_local = {}

    async with aiohttp.ClientSession() as session:
        for gem in gems:
            payload = {
                "ItemLevelMin": 0,
                "ItemLevelMax": 1800,
                "CategoryCode": 210000,
                "ItemTier": 4,
                "ItemName": gem,
                "PageNo": 1,
                "Sort": "BUY_PRICE",
                "SortCondition": "ASC"
            }

            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    gem_prices_local[gem] = 0
                    continue

                data = await resp.json()
                items = data.get("Items", [])
                cheapest_price = None

                for item in items:
                    price = item["AuctionInfo"]["BuyPrice"]
                    if price and (cheapest_price is None or price < cheapest_price):
                        cheapest_price = price

                gem_prices_local[gem] = cheapest_price or 0

    print(gem_prices_local)
    return gem_prices_local

async def handle_gem(message, content):
    if content != "/보석":
        return False

    url = "https://developer-lostark.game.onstove.com/auctions/items"
    headers = get_json_headers()

    gems = [
        "6레벨 겁화", "6레벨 작열",
        "7레벨 겁화", "7레벨 작열",
        "8레벨 겁화", "8레벨 작열",
        "9레벨 겁화", "9레벨 작열",
        "10레벨 겁화", "10레벨 작열"
    ]

    result_msg = "💎 보석 시세 (최저가)\n\n"

    async with aiohttp.ClientSession() as session:
        for gem in gems:
            payload = {
                "ItemLevelMin": 0,
                "ItemLevelMax": 1800,
                "CategoryCode": 210000,
                "ItemTier": 4,
                "ItemName": gem,
                "PageNo": 1,
                "Sort": "BUY_PRICE",
                "SortCondition": "ASC"
            }

            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    result_msg += f"{gem} : 조회 실패\n"
                    continue

                data = await resp.json()
                items = data.get("Items", [])

                cheapest_price = None

                for item in items:
                    price = item["AuctionInfo"]["BuyPrice"]
                    if price and (cheapest_price is None or price < cheapest_price):
                        cheapest_price = price

                if cheapest_price:
                    result_msg += f"{gem} : {cheapest_price:,} 골드\n"
                else:
                    result_msg += f"{gem} : 매물 없음\n"

    await message.channel.send(result_msg)
    return True

async def handle_gold_status(message, content):
    global my_gold, eight_gold

    if content != "/분배초기화":
        return False

    my_gold = 0
    eight_gold = 0

    data["gold"]["my_gold"] = my_gold
    data["gold"]["eight_gold"] = eight_gold
    save_data(data)

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

async def send_status(channel):
    msg = "📊 이번달 진행 상황\n\n"

    total_now = 0
    total_target = sum(targets.values())

    for acc in targets:
        current = progress[acc]
        target = targets[acc]
        remain = target - current
        total_now += current

        msg += f"{acc} : {current}/{target} (남음 {remain})\n"

    msg += f"\n💰 총합 : {total_now}/{total_target}"

    await channel.send(msg)

async def handle_engraving(message, content):
    if content != "/유각":
        return False

    url = "https://developer-lostark.game.onstove.com/markets/items"
    headers = get_json_headers()

    result_msg = "📜 유물 각인서 시세\n\n"

    async with aiohttp.ClientSession() as session:
        all_items = []

        for page in range(1, 3):
            payload = {
                "CategoryCode": 40000,
                "PageNo": page,
                "Sort": "CURRENT_MIN_PRICE",
                "SortCondition": "DESC"
            }

            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    await message.channel.send("API 조회 실패")
                    return True

                data = await resp.json()
                items = data.get("Items", [])
                all_items.extend(items)

        for item in all_items:
            name = item["Name"].replace("유물 ", "").replace(" 각인서", "")
            price = item["CurrentMinPrice"]
            result_msg += f"{name} : {price:,}g\n"

    await message.channel.send(result_msg)
    return True

async def handle_account(message, content):
    parts = content.split()
    if len(parts) != 2:
        return False

    name = parts[0][1:]
    amount = parts[1]

    if name not in targets:
        return False

    if not amount.isdigit():
        return False

    amount = int(amount)

    progress[name] += amount
    data["progress"] = progress
    save_data(data)

    await send_status(message.channel)
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

    data["gold"]["my_gold"] = my_gold
    data["gold"]["eight_gold"] = eight_gold
    save_data(data)

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
    if gold > 150000:
        split = int(gold * 0.95 / 4) - 2000
    elif gold > 100000:
        split = int(gold * 0.95 / 4) - 1500
    elif gold > 50000:
        split = int(gold * 0.95 / 4) - 1000
    elif gold > 20000:
        split = int(gold * 0.95 / 4) - 500
    else:
        split = int(gold * 0.95 / 4)

    my_gold += split
    eight_gold += split

    data["gold"]["my_gold"] = my_gold
    data["gold"]["eight_gold"] = eight_gold
    save_data(data)

    await message.channel.send(
        f"💰 분배 결과\n"
        f"나 : {my_gold}\n"
        f"에잇 : {eight_gold}"
    )

    return True

async def handle_auction(message, content):
    global my_gold, eight_gold

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

    if party not in [3, 4, 8]:
        return False

    if party == 3:
        split = int(price * 0.95 / 3)

        my_gold += split

        data["gold"]["my_gold"] = my_gold
        save_data(data)

        await message.channel.send(
            f"💰 3인 분배 결과\n"
            f"1인당 : {split:,} 골드\n\n"
            f"나 : {my_gold}\n"
        )
        return True

    if party == 4:
        direct_price = price * 0.75
    else:
        direct_price = price * 0.875

    direct_share = direct_price / (party - 1)

    break_even = price * 0.95 * (party - 1) / party
    break_even_share = break_even / (party - 1)
    break_even_profit = price * 0.95 - break_even

    bid = break_even / 1.1
    bid_share = bid / (party - 1)
    bid_profit = price * 0.95 - bid

    await message.channel.send(
        f"💰 {party}인 경매 계산\n\n"
        f"직접사용\n"
        f"입찰적정가 {int(direct_price):,}\n"
        f"분배금 {int(direct_share):,}\n\n"
        f"손익분기점\n"
        f"{int(break_even):,}\n"
        f"분배금 {int(break_even_share):,}\n"
        f"판매차익 {int(break_even_profit):,}\n\n"
        f"입찰적정가\n"
        f"{int(bid):,}\n"
        f"분배금 {int(bid_share):,}\n"
        f"판매차익 {int(bid_profit):,}"
    )

    return True

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

async def handle_status(message, content):
    if content != "/현황":
        return False

    def progress_bar(current, total):
        filled = "🟩" * current
        empty = "⬜" * (total - current)
        return f"{filled}{empty} {current}/{total}"

    embed = discord.Embed(
        title="🛡️ 이번달 레이드 진행 현황",
        color=0x00ff00
    )
    embed.add_field(name="4막", value=progress_bar(count_4, TARGET_4), inline=True)
    embed.add_field(name="종막", value=progress_bar(count_last, TARGET_LAST), inline=True)

    await message.channel.send(embed=embed)
    return True

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

async def handle_misc(message, content):
    if content == "/혜진":
        await message.channel.send("뱃살보송...")
        return True

    return False

# =========================
# 슬래시 명령어
# =========================
@bot.tree.command(name="도움", description="명령어 목록 보기")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(
        "📖 명령어 목록\n"
        "/오늘레이드\n"
        "/17000(혜진이한테 유각분배 대신 버스비로 받을 금액)\n"
        "/나 or 에잇 17000(혜진이한테 유각분배 대신 버스비로 받은 금액)\n"
        "/분배초기화(그냥 귀찮아서 만든거)\n"
        "/내놔(현재 유각분배 대신 버스비로 받아야 하는 남은 금액)\n"
        "/15000 4 or 8(/유각금액 인원수)\n"
        "/캐릭터이름 4막\n"
        "/캐릭터이름 종막\n"
        "/현황\n"
        "/초기화(현재 채널 메시지기록 초기화)"
    )

bot.run(TOKEN)