import datetime
from simple_policy.history_abs import HistoryAbs
from simple_policy.position import Position

class SmallPolicy(object):
    """
    simple策略：起投一个金额start_amount，平均到几个资产里，然后每隔step_month个月做一次市值大平均，高于平均值的卖，低于平均值的买。
    ins_his_list类型 = list([(HistoryAbs, float)])
    """
    
    def __init__(self, ins_his_list: list([(HistoryAbs, float)])):
        self._amount_dict = {}
        self._position_dict = {}
        self._rate_dict = {}
        self._is_inited = False
        if len(ins_his_list) == 0:
            raise "SimplePolicy init param ins_his_list is empty"
        for (item_ins, item_rate) in ins_his_list:
            self._position_dict[item_ins.get_symbol()] = Position(item_ins)
            self._rate_dict[item_ins.get_symbol()] = item_rate
    
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
            _etf_list.append(tmp_key)
            # tmp_item = self._position_dict[tmp_key]
            # if tmp_item.get_price_by_year_month(year, month) > 0:
            #     _etf_list.append(tmp_key)
        
        if len(_etf_list) == 0:
            return
        
        # print("_adjust_position _etf_list = ", _etf_list)
        for tmp_key in _etf_list:
            tmp_rate = self._rate_dict[tmp_key]
            tmp_amount = total * tmp_rate
            tmp_item = self._position_dict[tmp_key]
            tmp_item.update_position_by_amount_year_month(tmp_amount, year, month)
        
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