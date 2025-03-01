class PortfolioValidator:
    def __init__(self, portfolio_data):
        self.portfolio_data = portfolio_data
        self.grouped = self.group_by_date(portfolio_data)
        self.correct_quantities = {}
        self.previous_day_date = None
        self.previous_day_portfolio = None

    def is_performance_contribution_correct(self, position, date, ticker):
        # Check if Performance Contribution is correctly calculated
        if self.previous_day_portfolio and ticker in self.previous_day_portfolio:
            prev = self.previous_day_portfolio[ticker]
            prev_nav = prev['Calculated NAV']

            if prev_nav > 0 and 'Stock Movement' in position and position['Stock Movement'] != 0:
                # Calculate performance contribution based on position change
                expected_contribution = (position['Value in USD'] - prev['Value in USD']) / prev_nav * 100
                actual_contribution = position['Performance Contribution']

                if abs(expected_contribution - actual_contribution) > 0.02:  # Allow for some rounding
                    print(f"{date} {ticker} performance contribution error: "
                          f"reported {actual_contribution:.4f}% vs calculated {expected_contribution:.4f}%")


    def is_closing_weight_correct(self, position, date, ticker):
        # Check if Closing Weight is correctly calculated
        if 'Close Quantity' in position and position['Close Quantity'] != 0 and position['Calculated NAV'] != 0:
            expected_closing_weight = (position['Close Quantity'] * position['Price'] * position['Exchange Rate']) / position['Calculated NAV'] * 100
            actual_closing_weight = position['Closing Weights']

            if abs(expected_closing_weight - actual_closing_weight) > 0.01:
                print(f"{date} {ticker} closing weight error: "
                      f"reported {actual_closing_weight:.4f}% vs calculated {expected_c