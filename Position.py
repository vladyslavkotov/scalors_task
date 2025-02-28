class Position:
    def __init__(self, row):
        self.ticker = row[1]
        self.qty_open = int(row[4])
        self.qty_close = int(row[5])
        self.price_close = round(row[8],2)
        self.price_yesterday = round(row[11],2)
        self.stock_movement_pct = float(row[12])
        self.value = float(row[10])

        self.qty_traded_today = 0 if row[14] == '' else int(row[14])
        self.price_traded_today = 0 if row[15] == '' else round(float(row[15]), 2)

    def __str__(self):
        return f"{self.ticker} " \
               f"OPEN QTY {self.qty_open} " \
               f"CLOSE QTY {self.qty_close} " \
               f"CLOSE PRICE {self.price_close} " \
               f"YEST PRICE {self.price_yesterday} " \
               f"QTY TODAY {self.qty_traded_today} " \
               f"PRICE TODAY {self.price_traded_today}" \
               f"MOVE % {self.stock_movement_pct}"

    def __repr__(self):
        return self.__str__()
