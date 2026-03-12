import requests

url = "https://developer-lostark.game.onstove.com/markets/items"

headers = {
    "content-type": "application/json",
    "accept": "application/json",
    "authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyIsImtpZCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyJ9.eyJpc3MiOiJodHRwczovL2x1ZHkuZ2FtZS5vbnN0b3ZlLmNvbSIsImF1ZCI6Imh0dHBzOi8vbHVkeS5nYW1lLm9uc3RvdmUuY29tL3Jlc291cmNlcyIsImNsaWVudF9pZCI6IjEwMDAwMDAwMDA1MDk4MDMifQ.Sju8nBJKOXK2WJhNeTczoV2srz14C688OGWIs5nh6qAiL1EBzkg_n6dJze5hK9WgxGd6munpmcfbFe1uOK8yLg5p5qCzOXXDzYYGjyX1gI-N9_D729ucIxCHa7VKS2VfVZoz1n3zyd83XHGkjZ5Ye2WIPgdYiuZWfjgxr7YfKZpVXM24A7bZMot-Do_3Or9EbZUn5llWoB2Q_bxbNtKWsevWAA-JIJzdiDS6S2rjKyQCRo5sJb6KhA3xauPz0uWKpmuTrD2AkTWObj9grGWDpbr1ROiMEYFUCUevz3J_jHIHKe6lOK9Hp6scKV8nfQQyyDDy_oCNlG-pb-rN6vlzxA",
}

all_items = []

for page in range(1,3):

    payload = {
        "CategoryCode": 40000,
        "PageNo": page,
        "Sort": "CURRENT_MIN_PRICE",
        "SortCondition": "DESC"
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)

    if response.status_code != 200:
        print("Response:", response.text)
        continue

    data = response.json()

    items = data.get("Items", [])
    all_items.extend(items)

for item in all_items:

    name = item["Name"].replace("유물 ", "").replace(" 각인서", "")
    price = item.get("CurrentMinPrice")

    if price:
        print(f"{name} : {price:,}g")
    else:
        print(f"{name} : 매물 없음")