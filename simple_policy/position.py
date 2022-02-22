import datetime
from simple_policy.history_abs import HistoryAbs

class Position(object):
    """
    资产的持仓 
    """
    def __init__(self, ins_history : HistoryAbs):
        if ins_history is None :
            raise TypeError("Expected ins_history")
        self._position_price = 0
        self._position_amount = 0
        self._ins_hist = ins_history
    
    
    def get_total_amount_by_year_month(self, year: int, month: int):
        """
        year年month月的第一个交易日的持仓总金额（按open价计算）
        """
        if self._position_price <= 0:
            return 0
        if self._position_amount <= 0:
            return 0
        
        # 获取涨跌幅（4位小数，ru: +0.1234.即 +12.34%）
        open_price = self._ins_hist.get_open_price_by_year_month(year, month)
        rate = (open_price - self._position_price)/self._position_price
        rate = round(rate, 4)
        
        # 最新持仓金额
        current_amount = self._position_amount * (1+rate)
        return round(current_amount, 2)
        
    
    def update_position_by_amount_year_month(self, total_amount: int, year: int, month: int):
        """
        更新当前的持仓和价格
        """
        open_price = self._ins_hist.get_open_price_by_year_month(year, month)
        self._position_price = open_price
        self._position_amount = total_amount
    
    def get_price_by_year_month(self, year: int, month: int):
        return self._ins_hist.get_open_price_by_year_month(year, month)
        
        