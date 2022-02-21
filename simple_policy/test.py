from history_abs import HistoryAbs
from history_etf import HistoryEtf
from history_bond import HistoryBond
from position import Position
from simple_policy import SimplePolicy


def test001():
    symbol="sh513030"
    etf_sh510050 = HistoryEtf(symbol)
    
    print("all history\n")
    print(etf_sh510050.get_history())
    
    print("year month history\n")
    first_data = etf_sh510050.get_first_data_by_year_month(2019, 1)
    print("type(first_data) = \n", type(first_data))
    print("first_data = \n", first_data)
    
    
    position_sh510050 = Position(etf_sh510050)
    position_sh510050.update_position_by_amount_year_month(1000000, 2022, 1)
    print("position_sh510050 持仓总金额=", position_sh510050.get_total_amount_by_year_month(2022, 1))


def test_2017_01():
    his_list = [
        HistoryEtf('sh513030'), 
        HistoryEtf('sh513520'), 
        HistoryEtf('sz159920'),
        HistoryEtf('sh510050'), 
        HistoryEtf('sh518880')
    ]
    # etf_list = ['sh518880']
    test_policy = SimplePolicy(his_list)
    test_policy.set_params(start_year=2017, start_month=1, start_amount=1000000, next_fixed_amount=0, step_month=12, fixed_times=100)
    test_policy.run_policy()
    tmp_result = test_policy.get_results()
    print(tmp_result)
    
def main():
    if __name__ != "__main__":
        return

    # test001()
    test_2017_01()
  
    

main()