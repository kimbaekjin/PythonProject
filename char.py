import requests
import urllib.parse
import re

API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyIsImtpZCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyJ9.eyJpc3MiOiJodHRwczovL2x1ZHkuZ2FtZS5vbnN0b3ZlLmNvbSIsImF1ZCI6Imh0dHBzOi8vbHVkeS5nYW1lLm9uc3RvdmUuY29tL3Jlc291cmNlcyIsImNsaWVudF9pZCI6IjEwMDAwMDAwMDA1MDk4MDMifQ.Sju8nBJKOXK2WJhNeTczoV2srz14C688OGWIs5nh6qAiL1EBzkg_n6dJze5hK9WgxGd6munpmcfbFe1uOK8yLg5p5qCzOXXDzYYGjyX1gI-N9_D729ucIxCHa7VKS2VfVZoz1n3zyd83XHGkjZ5Ye2WIPgdYiuZWfjgxr7YfKZpVXM24A7bZMot-Do_3Or9EbZUn5llWoB2Q_bxbNtKWsevWAA-JIJzdiDS6S2rjKyQCRo5sJb6KhA3xauPz0uWKpmuTrD2AkTWObj9grGWDpbr1ROiMEYFUCUevz3J_jHIHKe6lOK9Hp6scKV8nfQQyyDDy_oCNlG-pb-rN6vlzxA"

def clean_gem_name(html_name):
    # 모든 HTML 태그 제거
    return re.sub(r"<.*?>", "", html_name).strip()

def get_gem(char_name):
    """단일 캐릭터 장착 보석 조회"""
    import requests, urllib.parse

    encoded = urllib.parse.quote(char_name)
    url = f"https://developer-lostark.game.onstove.com/armories/characters/{encoded}/gems"
    headers = {
        "accept": "application/json",
        "authorization": f"bearer {API_KEY}"
    }
    res = requests.get(url, headers=headers)

    if res.status_code != 200:
        return {"gems": []}  # 실패 시 빈 리스트 반환

    data = res.json()
    gems = data.get("Gems")  # None 가능
    if not isinstance(gems, list):
        gems = []  # 항상 리스트로
    return {"gems": gems}

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
            char_name = c["CharacterName"]
            profile = get_armory_profile(char_name)

            # 장착 보석 가져오기
            gems_data = get_gem(char_name)
            profile["gems"] = [clean_gem_name(g.get("Name")) for g in gems_data["gems"] if g.get("Name")]

            armory_list.append(profile)

    # 아이템레벨 내림차순
    armory_list.sort(key=lambda x: x["level"], reverse=True)

    # 출력
    for c in armory_list:
        gem_str = ", ".join(c["gems"]) if c["gems"] else "보석 없음"
        print(f"[{c['class']}] {c['name']} ({c['level']}, 전투력 {c['combat_power']}), 보석 : {gem_str}")