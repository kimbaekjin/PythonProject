import requests

url = "https://developer-lostark.game.onstove.com/auctions/items"

headers = {
    "accept": "application/json",
    "authorization": "bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyIsImtpZCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyJ9.eyJpc3MiOiJodHRwczovL2x1ZHkuZ2FtZS5vbnN0b3ZlLmNvbSIsImF1ZCI6Imh0dHBzOi8vbHVkeS5nYW1lLm9uc3RvdmUuY29tL3Jlc291cmNlcyIsImNsaWVudF9pZCI6IjEwMDAwMDAwMDA1MDk4MDMifQ.Sju8nBJKOXK2WJhNeTczoV2srz14C688OGWIs5nh6qAiL1EBzkg_n6dJze5hK9WgxGd6munpmcfbFe1uOK8yLg5p5qCzOXXDzYYGjyX1gI-N9_D729ucIxCHa7VKS2VfVZoz1n3zyd83XHGkjZ5Ye2WIPgdYiuZWfjgxr7YfKZpVXM24A7bZMot-Do_3Or9EbZUn5llWoB2Q_bxbNtKWsevWAA-JIJzdiDS6S2rjKyQCRo5sJb6KhA3xauPz0uWKpmuTrD2AkTWObj9grGWDpbr1ROiMEYFUCUevz3J_jHIHKe6lOK9Hp6scKV8nfQQyyDDy_oCNlG-pb-rN6vlzxA",
    "content-type": "application/json"
}

payload = {
    "ItemLevelMin": 0,
    "ItemLevelMax": 1800,
    "CategoryCode": 210000,
    "ItemTier": 4,
    "ItemName": "10레벨 겁화",
    "PageNo": 1,
    "Sort": "BUY_PRICE",
    "SortCondition": "ASC"
}

response = requests.post(url, headers=headers, json=payload)
data = response.json()

items = data["Items"]

cheapest_item = None
cheapest_price = float("inf")

for item in items:
    price = item["AuctionInfo"]["BuyPrice"]

    if price and price < cheapest_price:
        cheapest_price = price
        cheapest_item = item

if cheapest_item:
    print("아이템:", cheapest_item["Name"])
    print("최저가:", cheapest_price)
else:
    print("즉구가 있는 아이템 없음")