from datetime import datetime, date
from Position import Position
from ReportCreator import ReportCreator
from ErrorType import ErrorType

class Validator:
    def __init__(self, grouped_positions:list[tuple[datetime, dict[str, Position]]]):
        self.previous_day_date, self.previous_day_portfolio = grouped_positions[0]
        self.correct_quantities = self.create_correct_quantities_start(self.previous_day_date, self.previous_day_portfolio)
        self.grouped = grouped_positions
        self.threshold = 5
        self.precision_error = 0.011
        self.base_currency = "USD"
        self.pnl_deviation = 1 #assuming at least 1 dollar commission
        self.report = ReportCreator()
        self.validate_against_previous_day()
        self.validate_per_position()
        self.report.save()

    def create_correct_quantities_start(self, date:date, data: dict[str, Position]) -> dict[str, int]:
        correct_quantities = {}
        for ticker, position in data.items():
            if position.qty_close != 0:
                correct_quantities[ticker] = position.qty_open + position.qty_traded_today
                if position.qty_close != position.qty_open + position.qty_traded_today:
                    self.report.write(date, 
                              ticker, 
                              ErrorType.QUANTITY, 
                              f"Inconsistent quantity {ticker} in day 1 when creating initial quantities")

        return correct_quantities

    def is_qty_incorrect(self, position: Position, date: str, ticker: str):
        if position.qty_close != position.qty_open + position.qty_traded_today:
            self.report.write(date, 
                              ticker, 
                              ErrorType.QUANTITY, 
                              f"Close qty: {position.qty_close:.2f} != open qty: {position.qty_open:.2f} + today traded qty: {position.qty_traded_today:.2f}")

    def is_holding_qty_changed(self, position: Position, date: str, ticker: str):
        if ticker in self.correct_quantities:
            self.is_qty_incorrect(position, date, ticker)
            if position.qty_open != self.correct_quantities[ticker]:
                self.report.write(date, 
                            ticker, 
                            ErrorType.HOLDING_QTY, 
                            f"Holding qty changed, no trade open. Recorded open qty: {position.qty_open:,.2f} Expected Qty: {self.correct_quantities[ticker]:,.2f}")
            self.correct_quantities[ticker] = position.qty_close
        else:
            self.correct_quantities[ticker] = position.qty_close

    def get_value_close(self, position:Position):
        return position.qty_close * position.price_close * position.exchange_rate
    
    def is_value_incorrect(self, position: Position, date: str, ticker: str):
        calculated_value = self.get_value_close(position)
        if (position.qty_close != 0 and
            abs(calculated_value - position.value) > self.precision_error):
            self.report.write(date, 
                              ticker, 
                              ErrorType.DOLLAR_VALUE, 
                              f"Incorrect $ value. Recorded: {position.value:,.2f} Expected: {calculated_value:,.2f}")

    def is_exchange_rate_or_currency_incorrect(self, position: Position, date: str, ticker: str):
        if position.currency == self.base_currency and position.exchange_rate != 1:
            self.report.write(date, 
                              ticker, 
                              ErrorType.EXCHANGE_RATE_OR_BASE_CURRENCY, 
                              f"Currency should be {self.base_currency} or incorrect Exchange Rate {position.exchange_rate:.2f}")

    def is_price_equal_to_stock_mvmt(self, position: Position, date: str, ticker: str):
        calculated_price_change = round(position.price_yesterday * (1 + position.stock_move_pct), 2)
        if abs(calculated_price_change - position.price_close) > self.precision_error:
            self.report.write(date, 
                              ticker, 
                              ErrorType.PRICE_OR_PCT_MOVE, 
                              f"Incorrect price and/or %move. Recorded price: {position.price_close:.2f} Expected: {calculated_price_change:.2f}")

    def is_trade_price_incorrect(self, position: Position, date: str, ticker: str):
        calculated_price_move = abs(position.price_close - position.price_traded_today) / position.price_close
        if (position.price_close != 0 and
            position.price_traded_today != 0 and
            calculated_price_move > abs(position.stock_move_pct) * self.threshold):
            self.report.write(date, 
                              ticker, 
                              ErrorType.TRADE_PRICE, 
                              f"Price move is more than {self.threshold} times of recorded daily % move. Recorded % move: {position.stock_move_pct:.5f} Expected: {calculated_price_move:.5f}")

    def is_yesterday_price_incorrect(self, position: Position, date: str, ticker: str):
        if (ticker in self.previous_day_portfolio and
            position.price_yesterday != self.previous_day_portfolio[ticker].price_close):
            self.report.write(date, 
                              ticker, 
                              ErrorType.YESTERDAY_PRICE, 
                              f"Mismatch between recorded yesterday price: {position.price_yesterday:.2f} and close price: {self.previous_day_portfolio[ticker].price_close:.2f} on {self.previous_day_date}")

    def is_existing_positions_missing(self, portfolio: dict[str, Position], date: str):
        for ticker, qty in self.correct_quantities.items():
            if qty !=0 and ticker not in portfolio:
                self.report.write(date, 
                              ticker, 
                              ErrorType.EXISTING_POSITION_MISSING, 
                              f"Missing position from date: {self.previous_day_date} Expected qty: {self.correct_quantities[ticker]:,.2f}")

    def is_pnl_incorrect(self, position: Position, date: str, ticker: str):
        if ticker in self.previous_day_portfolio:
            yesterday_calculated_pnl = self.get_value_close(self.previous_day_portfolio[ticker])
            sign = -1 if position.is_short else 1
            if position.qty_traded_today == 0 and position.price_traded_today == 0:
                today_calculated_pnl = self.get_value_close(position)
                
                dollar_change = round((today_calculated_pnl - yesterday_calculated_pnl)*sign,2)
                if abs(dollar_change - round(position.dollar_pnl,2)) > self.pnl_deviation:
                    self.report.write(date, 
                              ticker, 
                              ErrorType.PNL, 
                              f"Incorrect PnL. Recorded: {position.dollar_pnl:,.2f} Expected qty: {dollar_change:,.2f}")
            else:
                if position.qty_close !=0:
                    today_calculated_pnl = (position.qty_open * position.price_close * position.exchange_rate)+((position.price_close - position.price_traded_today) * position.qty_traded_today * position.exchange_rate)
                    dollar_change = round((today_calculated_pnl - yesterday_calculated_pnl)*sign,2)
                    if abs(dollar_change - round(position.dollar_pnl,2)) > self.pnl_deviation:
                        self.report.write(date, 
                              ticker, 
                              ErrorType.PNL, 
                              f"Incorrect PnL. Increased/decreased holding qty. Recorded: {position.dollar_pnl:,.2f} Expected qty: {dollar_change:,.2f}")
                else:
                    today_calculated_pnl = position.price_traded_today*position.qty_traded_today*-sign
                    dollar_change = round((today_calculated_pnl - yesterday_calculated_pnl)*sign,2)
                    if abs(dollar_change - round(position.dollar_pnl,2)) > self.pnl_deviation:
                        self.report.write(date, 
                              ticker, 
                              ErrorType.PNL, 
                              f"Incorrect PnL. Closed position. Recorded: {position.dollar_pnl:,.2f} Expected qty: {dollar_change:,.2f}")

    def is_close_weight_incorrect(self, position: Position, date: str, ticker: str):
        if position.weight_close != 0 and position.nav != 0 and position.price_traded_today == 0 and position.qty_traded_today == 0:
            expected_weight_close = (self.get_value_close(position))/position.nav
            if abs(expected_weight_close - position.weight_close) > self.precision_error:
                self.report.write(date, 
                              ticker, 
                              ErrorType.CLOSE_WEIGHT, 
                              f"Incorrect close weight. Recorded: {position.weight_close:.5f} Expected qty: {expected_weight_close:.5f}")

    def is_open_weight_incorrect(self, position: Position, date: str, ticker: str):
        if position.weight_open != 0 and position.nav_yesterday != 0 and position.price_traded_today == 0 and position.qty_traded_today == 0:
            expected_weight_open = (position.price_yesterday * position.qty_open * position.exchange_rate)/position.nav_yesterday
            if abs(expected_weight_open - position.weight_open) > self.precision_error:
                self.report.write(date, 
                              ticker, 
                              ErrorType.OPEN_WEIGHT, 
                              f"Incorrect open weight. Recorded: {position.weight_open:.5f} Expected qty: {expected_weight_open:.5f}")

    def validate_against_previous_day(self):
        for date, portfolio in self.grouped[1:]:
            self.is_existing_positions_missing(portfolio, date)
            for ticker, position in portfolio.items():
                self.is_holding_qty_changed(position, date, ticker)
                self.is_yesterday_price_incorrect(position, date, ticker)
                self.is_pnl_incorrect(position, date, ticker)

            self.previous_day_date = date
            self.previous_day_portfolio = portfolio

    def validate_per_position(self):
        for date, portfolio in self.grouped:
            for ticker, position in portfolio.items():
                self.is_close_weight_incorrect(position,date,ticker)
                self.is_trade_price_incorrect(position, date, ticker)
                self.is_price_equal_to_stock_mvmt(position, date, ticker)
                self.is_qty_incorrect(position, date, ticker)
                self.is_value_incorrect(position, date, ticker)
                self.is_exchange_rate_or_currency_incorrect(position, date, ticker)
                self.is_open_weight_incorrect(position,date,ticker)

