# 用数据测试一下简单策略

import akshare as ak
import datetime

class EtfHistory(object):
    """
    symbol查询地址：http://vip.stock.finance.sina.com.cn/fund_center/index.html#jjhqetf
    """
    def __init__(self, symbol : str):
        if symbol is None or symbol == "":
            raise TypeError("Expected symbol")
        self._symbol = symbol
        self._hist = ak.fund_etf_hist_sina(symbol=symbol)
    
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

class EtfPosition(object):
    """
    ETF的持仓 
    """
    def __init__(self, symbol : str):
        if symbol is None or symbol == "":
            raise TypeError("Expected symbol")
        self._position_price = 0
        self._position_amount = 0
        self._symbol = symbol
        self._etf_hist = EtfHistory(symbol)
    
    
    def get_total_amount_by_year_month(self, year: int, month: int):
        """
        year年month月的第一个交易日的持仓总金额（按open价计算）
        """
        if self._position_price <= 0:
            return 0
        if self._position_amount <= 0:
            return 0
        
        # 获取涨跌幅（4位小数，ru: +0.1234.即 +12.34%）
        open_price = self._etf_hist.get_open_price_by_year_month(year, month)
        rate = (open_price - self._position_price)/self._position_price
        rate = round(rate, 4)
        
        # 最新持仓金额
        current_amount = self._position_amount * (1+rate)
        return round(current_amount, 2)
        
    
    def update_position_by_amount_year_month(self, total_amount: int, year: int, month: int):
        """
        更新当前的持仓和价格
        """
        open_price = self._etf_hist.get_open_price_by_year_month(year, month)
        self._position_price = open_price
        self._position_amount = total_amount
    
    def get_price_by_year_month(self, year: int, month: int):
        return self._etf_hist.get_open_price_by_year_month(year, month)
        
        
class EtfPolicy(object):
    """
    ETF策略：起投一个金额start_amount，平均到几支基金里，然后每隔step_month个月做一次市值大平均，高于平均值的卖，低于平均值的买。
    """
    
    def __init__(self, symbols: list):
        self._amount_dict = {}
        self._position_dict = {}
        self._is_inited = False
        if len(symbols) == 0:
            raise "EtfPolicy init symbols is empty"
        for item in symbols:
            self._position_dict[item] = EtfPosition(item)
    
    def set_params(self, start_year: int, start_month: int, start_amount: int, next_fixed_amount: int, step_month: int, fixed_times: int):
        """
        start_year 启投的年
        start_month 启投的月
        start_amount 启投的金额
        next_fixed_amount 后面继续投的固定金额
        step_month 定投间隔的月数
        fixed_times 共投多少轮 
        """
        self._current_year = start_year
        self._current_month = start_month
        self._start_amount = start_amount
        self._next_fixed_amount = next_fixed_amount
        self._step_month = step_month
        self._fixed_times = fixed_times
        self._is_inited = True
    
    def _get_position_total_amount(self, year: int, month: int):
        _total_amount = 0.0
        for item in self._position_dict.values():
            _total_amount += item.get_total_amount_by_year_month(year, month)
        return _total_amount

    def _adjust_position(self, year: int, month: int, total: int):
        """
        重新设置每个基金的持仓金额
        """
        # print("_adjust_position = %04d-%02d" % (year, month))
        
        _etf_list = []
        for tmp_key in self._position_dict.keys():
            tmp_item = self._position_dict[tmp_key]
            if tmp_item.get_price_by_year_month(year, month) > 0:
                _etf_list.append(tmp_key)
        
        if len(_etf_list) == 0:
            return
        
        # print("_adjust_position _etf_list = ", _etf_list)
        
        _amount_to_divide = total / len(_etf_list)
        for tmp_key in _etf_list:
            tmp_item = self._position_dict[tmp_key]
            tmp_item.update_position_by_amount_year_month(_amount_to_divide, year, month)
        
        #保存当前持仓金额
        self._amount_dict["%04d-%02d" % (year, month)] = self._get_position_total_amount(year, month)
            
    def run_policy(self):
        if self._is_inited != True:
            raise "not inited"
        
        #启投
        self._adjust_position(self._current_year, self._current_month, self._start_amount)
        
        #后续的定投
        for i in range(self._fixed_times):
            #下一轮的年月
            next_year = self._current_year + int((self._current_month + self._step_month) / 13)
            next_month = (self._current_month + self._step_month) % 12
            if next_month == 0:
                next_month = 12
            
            if datetime.datetime.now().date() <= datetime.date(next_year, next_month, 1):
                break
            
            self._current_year = next_year
            self._current_month = next_month
            
            prev_total_amount = self._get_position_total_amount(self._current_year, self._current_month)
            next_total_amount = prev_total_amount + self._next_fixed_amount
            self._adjust_position(self._current_year, self._current_month, next_total_amount)
        
    
    def get_results(self):
        return self._amount_dict
    
    
    
def test001():
    symbol="sh513030"
    etf_sh510050 = EtfHistory(symbol)
    
    print("all history\n")
    print(etf_sh510050.get_history())
    
    print("year month history\n")
    first_data = etf_sh510050.get_first_data_by_year_month(2019, 1)
    print("type(first_data) = \n", type(first_data))
    print("first_data = \n", first_data)
    
    
    position_sh510050 = EtfPosition(symbol)
    position_sh510050.update_position_by_amount_year_month(1000000, 2022, 1)
    print("position_sh510050 持仓数量=", position_sh510050.get_position())
    print("position_sh510050 持仓总金额=", position_sh510050.get_total_amount_by_year_month(2022, 1))


def test_2017_01():
    etf_list = ['sh513030', 'sh513520', 'sz159920','sh510050', 'sh518880']
    # etf_list = ['sh518880']
    etf_policy = EtfPolicy(etf_list)
    etf_policy.set_params(start_year=2017, start_month=1, start_amount=1000000, next_fixed_amount=0, step_month=12, fixed_times=100)
    etf_policy.run_policy()
    etf_policy.get_results()
    
def main():
    if __name__ != "__main__":
        return

    # test001()
    test_2017_01()
  
    

main()
