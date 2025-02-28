from Helpers import load_sheet, group_by_date, create_correct_quantities_start

data = load_sheet("Test.xlsx")

grouped = list(group_by_date(data).items())

previous_day_date, previous_day_portfolio = grouped[0]
# print(previous_day)
correct_quantities= create_correct_quantities_start(previous_day_portfolio)
print(correct_quantities)


for date, portfolio in grouped[1:]:
    for ticker,position in portfolio.items():
        # check if yesterday's price is recorded accurately
        # if ticker in previous_day_portfolio and position.price_yesterday != previous_day_portfolio[ticker].price_close:
        #     print(f"{ticker} price mismatch")
        #     print(f"previous day {previous_day_date} price {previous_day_portfolio[ticker].price_close}")
        #     print(f"today {date} yesterday price {position.price_yesterday}")

        # if position.qty_close != position.qty_open + position.qty_traded_today:
        #     print(f"{date} {ticker} close qty != open qty + trade qty")

        if ticker in correct_quantities:
            #check if holding qty changed
            if position.qty_open != correct_quantities[ticker]:
                print(f"{date} {ticker} holding qty changed without trade "
                      f"open qty {position.qty_open} "
                      f"correct {correct_quantities[ticker]}")
            correct_quantities[ticker]=position.qty_close
        else:
            correct_quantities[ticker] = position.qty_close

        if position.qty_traded_today !=0:


        # calculated_price_change = round(position.price_yesterday * (1+position.stock_movement_pct),2)
        # if abs(calculated_price_change - position.price_close) > 0.011:
        #     print(f"{date} {ticker} incorrect price and/or %move calculated {calculated_price_change} actual {position.price_close}")

        # if close qty zero, set to 0, dont delete. then we'l be able to compare. and zero you dont have to handle keyerror

    previous_day = (date, portfolio)




