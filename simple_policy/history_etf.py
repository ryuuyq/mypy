import akshare as ak
import datetime

class HistoryEtf(object):
    """
    场内ETF基金历史行情
    symbol查询地址：http://vip.stock.finance.sina.com.cn/fund_center/index.html#jjhqetf
    """
    def __init__(self, symbol : str):
        if symbol is None or symbol == "":
            raise TypeError("Expected symbol")
        self._symbol = symbol
        self._hist = ak.fund_etf_hist_sina(symbol=symbol)
    
    def get_symbol(self):
        return self._symbol
    
    def get_history(self):
        """
        全部的行情数据
        """
        return self._hist
    
    def get_first_data_by_year_month(self, year: int, month: int):
        """
        year年month月的第一个交易日的行情数据
        """
        # print("行情数据 start")
        # print(self._symbol)
        # print(self._hist)
        # print("行情数据 end")
        above_hist = self._hist[self._hist["date"] > datetime.date(year, month, 1)]
        row_data = above_hist.iloc[0]
        the_date = row_data['date']
        if the_date.year == year and the_date.month == month:
            return row_data
        else:
            return None
    
    def get_open_price_by_year_month(self, year: int, month: int):
        firt_data_year_month = self.get_first_data_by_year_month(year, month)
        if firt_data_year_month is None:
            return 0.0
        open_price = firt_data_year_month["open"]
        return open_price