# ---------------------------
# 메시지 생성
# ---------------------------
armory_list.sort(key=lambda x: x["level"], reverse=True)
msg = "```css\n"
for c in armory_list:
    msg += f"[{c['class']}] {c['name']} ({c['level']}, 전투력 {c['combat_power']})\n"
    if c["gems"]:
        gem_counter = Counter()
        # clean + bound info 처리
        for g in c["gems"]:
            clean_name, is_bound = clean_gem_name(g)
            gem_counter[(clean_name, is_bound)] += 1

        total_price = 0
        for (gem_name, is_bound), count in gem_counter.items():
            # 메시지에는 귀속 여부 표시
            display_name = f"{gem_name} (귀속)" if is_bound else gem_name
            msg += f"• {display_name} x{count}\n"

            # 가격 계산: 귀속이면 제외
            if not is_bound:
                price = 0
                if gem_name in gem_prices_local:
                    price = gem_prices_local[gem_name]
                elif "광휘" in gem_name:
                    # 거래 가능한 광휘는 겁화 가격으로
                    level = re.search(r"\d+레벨", gem_name).group()
                    price = gem_prices_local.get(f"{level} 겁화", 0)
                total_price += price * count

            print(
                f"DEBUG {gem_name}, bound: {is_bound} -> price considered: {0 if is_bound else price}, count: {count}")

        msg += f"💰 보석 총 가격: {total_price:,} 골드\n"
    else:
        msg += "• 보석 없음\n"
    msg += "\n"
msg += "```"

await message.channel.send(msg)
return True