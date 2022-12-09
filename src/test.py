price = ""
price_raw = "100.000.000"
for i in range (0, len(price_raw)):
    if price_raw[i].isdigit() :
        print(price_raw[i])
        price += price_raw[i]

print(price)