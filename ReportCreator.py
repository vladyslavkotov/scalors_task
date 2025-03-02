from datetime import datetime
from openpyxl import Workbook


class ReportCreator:
    def __init__(self):
        today=datetime.today().strftime('%Y-%m-%d--%H-%M-%S-%f')
        self.name = f"Error Report {today}.xlsx"
        self.wb = Workbook()
        self.ws = self.wb.active
        self.ws.title = "Report"
        self.ws.append(["Date", "Ticker", "Error Type", "Error Message"])

    def write(self, date:str, ticker:str, error_type:str, error_message:str):
        self.ws.append([date, ticker, error_type, error_message])

    def save(self):
        self.wb.save(self.name)