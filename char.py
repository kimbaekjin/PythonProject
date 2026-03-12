import requests
import urllib.parse

API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyIsImtpZCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyJ9.eyJpc3MiOiJodHRwczovL2x1ZHkuZ2FtZS5vbnN0b3ZlLmNvbSIsImF1ZCI6Imh0dHBzOi8vbHVkeS5nYW1lLm9uc3RvdmUuY29tL3Jlc291cmNlcyIsImNsaWVudF9pZCI6IjEwMDAwMDAwMDA1MDk4MDMifQ.Sju8nBJKOXK2WJhNeTczoV2srz14C688OGWIs5nh6qAiL1EBzkg_n6dJze5hK9WgxGd6munpmcfbFe1uOK8yLg5p5qCzOXXDzYYGjyX1gI-N9_D729ucIxCHa7VKS2VfVZoz1n3zyd83XHGkjZ5Ye2WIPgdYiuZWfjgxr7YfKZpVXM24A7bZMot-Do_3Or9EbZUn5llWoB2Q_bxbNtKWsevWAA-JIJzdiDS6S2rjKyQCRo5sJb6KhA3xauPz0uWKpmuTrD2AkTWObj9grGWDpbr1ROiMEYFUCUevz3J_jHIHKe6lOK9Hp6scKV8nfQQyyDDy_oCNlG-pb-rN6vlzxA"

def get_armory_profile(char_name):
    """단일 캐릭터 profiles 조회"""
    encoded = urllib.parse.quote(char_name)
    url = f"https://developer-lostark.game.onstove.com/armories/characters/{encoded}/profiles"
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {API_KEY}"
    }
    res = requests.get(url, headers=headers)
    data = res.json()

    item_level_str = data.get("ItemAvgLevel", "0")
    item_level = float(item_level_str.replace(",", ""))
    combat_power = data.get("CombatPower", 0)
    char_class = data.get("CharacterClassName", "Unknown")
    return {
        "name": char_name,
        "class": char_class,
        "level": item_level,
        "combat_power": combat_power
    }


def get_siblings(char_name):
    """원정대 캐릭터 목록 조회"""
    encoded = urllib.parse.quote(char_name)
    url = f"https://developer-lostark.game.onstove.com/characters/{encoded}/siblings"
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {API_KEY}"
    }
    res = requests.get(url, headers=headers)
    return res.json()


if __name__ == "__main__":
    main_char = "스읔꺼내보니유산스읔"
    siblings_data = get_siblings(main_char)

    armory_list = []
    for c in siblings_data:
        level = float(c["ItemAvgLevel"].replace(",", ""))
        if level >= 1660:  # 1660 이상만
            profile = get_armory_profile(c["CharacterName"])
            armory_list.append(profile)

    # 아이템레벨 내림차순
    armory_list.sort(key=lambda x: x["level"], reverse=True)

    # 출력
    for c in armory_list:
        print(f"[{c['class']}] {c['name']} ({c['level']}, 전투력 {c['combat_power']})")