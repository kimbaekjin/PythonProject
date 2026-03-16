import requests,re,json

headers = {
    "content-type": "application/json",
    "accept": "application/json",
    "authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyIsImtpZCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyJ9.eyJpc3MiOiJodHRwczovL2x1ZHkuZ2FtZS5vbnN0b3ZlLmNvbSIsImF1ZCI6Imh0dHBzOi8vbHVkeS5nYW1lLm9uc3RvdmUuY29tL3Jlc291cmNlcyIsImNsaWVudF9pZCI6IjEwMDAwMDAwMDA1MDk4MDMifQ.Sju8nBJKOXK2WJhNeTczoV2srz14C688OGWIs5nh6qAiL1EBzkg_n6dJze5hK9WgxGd6munpmcfbFe1uOK8yLg5p5qCzOXXDzYYGjyX1gI-N9_D729ucIxCHa7VKS2VfVZoz1n3zyd83XHGkjZ5Ye2WIPgdYiuZWfjgxr7YfKZpVXM24A7bZMot-Do_3Or9EbZUn5llWoB2Q_bxbNtKWsevWAA-JIJzdiDS6S2rjKyQCRo5sJb6KhA3xauPz0uWKpmuTrD2AkTWObj9grGWDpbr1ROiMEYFUCUevz3J_jHIHKe6lOK9Hp6scKV8nfQQyyDDy_oCNlG-pb-rN6vlzxA"
}

def get_character_class(name):

    url = f"https://developer-lostark.game.onstove.com/armories/characters/{name}/profiles"

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return None

    data = res.json()

    return data.get("CharacterClassName")

def get_crit_stat(name):

    url = f"https://developer-lostark.game.onstove.com/armories/characters/{name}/profiles"

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("캐릭터 조회 실패")
        return 0

    data = res.json()

    for stat in data["Stats"]:
        if stat["Type"] == "치명":
            return int(stat["Value"])

    return 0

def crit_from_stat(crit_stat):

    return round(crit_stat / 27.943, 1)

def get_arkpassive_data(name):

    url = f"https://developer-lostark.game.onstove.com/armories/characters/{name}/arkpassive"

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {}

    return res.json()

def get_arkpassive_crit(ark_data, char_class):

    total_crit = 0

    effects = ark_data.get("Effects", [])

    for effect in effects:
        name = effect.get("Name","")
        desc = effect.get("Description", "")
        # 티어 확인
        tier_match = re.search(r'(\d)티어', desc)
        if not tier_match:
            continue

        tier = int(tier_match.group(1))

        # 1티어, 5티어 제외
        if tier in [1, 5]:
            continue

        # ⭐ 기상술사 깨달음 처리
        if  name == "깨달음" and "기민함" in desc:
            total_crit += 12
            continue

        # ⭐ 달인 처리
        if tier == 4 and "달인" in desc:
            total_crit += 7
            continue

        tooltip_raw = effect.get("ToolTip")

        if not tooltip_raw:
            continue

        try:
            tooltip = json.loads(tooltip_raw)
        except:
            continue

        for element in tooltip.values():

            if not isinstance(element, dict):
                continue

            text = element.get("value")

            if not isinstance(text, str):
                continue

            # 이동속도 기반 치적 제외
            if "기본 이동 속도 증가량" in text:
                continue

            if "치명타 적중률" in text:

                match = re.search(r'치명타 적중률.*?(\d+\.?\d*)%', text)

                if match:
                    crit_value = float(match.group(1))
                    total_crit += crit_value

    return total_crit

def find_crit_recursive(data):

    crit = 0

    if isinstance(data, dict):
        for v in data.values():
            crit += find_crit_recursive(v)

    elif isinstance(data, list):
        for v in data:
            crit += find_crit_recursive(v)

    elif isinstance(data, str):

        if "치명타 적중률" in data:

            match = re.search(r'치명타 적중률.*?(\d+\.?\d*)%', data)

            if match:
                value = float(match.group(1))
                crit += value

    return crit


def get_accessory_bracelet_crit(name):

    url = f"https://developer-lostark.game.onstove.com/armories/characters/{name}/equipment"

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        print("장비 조회 실패")
        return 0,0

    data = res.json()

    accessory_crit = 0
    bracelet_crit = 0

    for item in data:

        item_type = item.get("Type")

        tooltip_raw = item.get("Tooltip")

        if not tooltip_raw:
            continue

        try:
            tooltip = json.loads(tooltip_raw)
        except:
            continue

        crit = find_crit_recursive(tooltip)

        if item_type in ["목걸이", "귀걸이", "반지"]:
            accessory_crit += crit

        elif item_type == "팔찌":
            bracelet_crit += crit

    return accessory_crit, bracelet_crit

def get_engraving_crit(name):

    url = f"https://developer-lostark.game.onstove.com/armories/characters/{name}/engravings"

    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return 0

    data = res.json()

    engravings = data.get("ArkPassiveEffects")

    if engravings is None:
        return 0

    crit_bonus = 0

    for eng in engravings:
        eng_name = eng["Name"]
        if "아드레날린" in eng_name:
            if eng["Level"] == 0:
                crit_bonus += 14
            elif eng["Level"] == 1:
                crit_bonus += 15.5
            elif eng["Level"] == 2:
                crit_bonus += 17
            elif eng["Level"] == 3:
                crit_bonus += 18.5
            elif eng["Level"] == 4:
                crit_bonus += 20

    return crit_bonus

def calculate_crit_rate(name):
    char_class = get_character_class(name)

    crit_stat = get_crit_stat(name)
    stat_crit = crit_from_stat(crit_stat)

    engraving_crit = get_engraving_crit(name)

    ark_data = get_arkpassive_data(name)
    arkpassive_crit = get_arkpassive_crit(ark_data, char_class)

    accessory_crit, bracelet_crit = get_accessory_bracelet_crit(name)

    total = stat_crit + engraving_crit + arkpassive_crit + bracelet_crit + accessory_crit

    if char_class == "건슬링어" or char_class == "기상술사" or char_class == "데빌헌터" or char_class == "스트라이커" or char_class == "배틀마스터" or char_class == "아르카나":
        total += 10
        print("직업 치적:", 10)
        print("스탯 치적:", round(stat_crit, 1))
        print("각인 치적:", engraving_crit)
        print("팔찌 치적:", bracelet_crit)
        print("악세 치적:", round(accessory_crit,2))
        print("아크패시브 치적:", arkpassive_crit)

        print("총 치적:", round(total, 1), "%")
        return True

    print("스탯 치적:", round(stat_crit,1))
    print("각인 치적:", engraving_crit)
    print("팔찌 치적:", bracelet_crit)
    print("악세 치적:", round(accessory_crit,2))
    print("아크패시브 치적:", arkpassive_crit)

    print("총 치적:", round(total,1), "%")
    return None

if __name__ == "__main__":
    character_name = input("캐릭터 이름 입력: ")
    calculate_crit_rate(character_name)