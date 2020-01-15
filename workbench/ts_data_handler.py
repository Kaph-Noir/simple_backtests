import pandas as pd
from workbench.const import CALENDAR, DEFAULT_SETTING
from workbench.utils import FileHandler, ToolBox


class TimeSeriesDataLoader(object):
    @staticmethod
    def split_ts_by(init_year, time_window, reference_date, sep='y'):
        """
        For time segmentation
        :param init_year: first year of backtest
        :param time_window: number of years of backtest
        :param reference_date: market opening date or portfolio enter year
        :param sep: y, q, m
        :return: the first and last date of each time segment
        """
        if sep == 'y':
            ts_heads = [reference_date[init_year + i] for i in range(time_window)]
            ts_tails = [reference_date[init_year + (i + 1)] for i in range(time_window)]
        # else:  # not yet
        #     pass
        return ts_heads, ts_tails

    def get_ts_data(self, data_type, first_year=DEFAULT_SETTING.ENTER_YEAR,
                    time_window=DEFAULT_SETTING.TIME_WINDOW,
                    reference_date=CALENDAR.ENTER_DATE):
        ts_heads, ts_tails = self.split_ts_by(first_year, time_window, reference_date)
        ts_file = FileHandler.get_data_file(data_type)
        for head, tail in zip(ts_heads, ts_tails):
            ts_data = ts_file.loc[head:tail][:-1]  # 마지막 하루 잘라내기
            ts_data = ToolBox.get_candidates(ts_data, head)
            # ts_data = ts_data.astype('int32')
            ts_data.index = pd.to_datetime(ts_data.index)
            yield ts_data

    @staticmethod
    def get_benchmark(ts_benchmark, ts_portf_val):
        enter_year = ToolBox.get_enter_year(ts_portf_val)
        for i, data in enumerate(ts_benchmark):
            year = enter_year + i
            unit_vol = pd.DataFrame({'price': data.loc[CALENDAR.ENTER_DATE[year]],
                                     'volume': [1]}, index=[data.columns[0]])
            yield year, unit_vol

    @staticmethod
    def get_ts_daily_risk_free_rate(ts_portf_val, data_type='risk_free_rate'):
        ts_risk_free_rate = FileHandler.get_data_file(data_type)['CD91']
        ts_risk_free_rate.index = pd.to_datetime(ts_risk_free_rate.index)
        ts_risk_free_rate = ts_risk_free_rate[ts_portf_val.index].T.squeeze()[:-1]  #
        return (1 + ts_risk_free_rate / 100) ** (1 / 365) - 1  # 연이율을 일일 수익률로

    def get_codes_whose_shares_increased(self, init_year=DEFAULT_SETTING.INIT_YEAR,
                                         time_window=DEFAULT_SETTING.TIME_WINDOW):  # 변수명 정리 요구
        """
        작년 주식을 신규 발행한 회사의 코드를 가져오는 함수
        :param init_year:
        :param time_window:
        :return:
        """
        ts_shares_years = list(self.get_ts_data('num_shares',
                                                first_year=init_year - 1, time_window=time_window + 1,
                                                reference_date=CALENDAR.OPENING_DATE))
        last_year_state, init_year_state = ts_shares_years[0].iloc[-1], ts_shares_years[1].iloc[0]
        for_comparing = pd.concat([last_year_state, init_year_state], axis=1, sort=True)
        is_increased_init = for_comparing.iloc[:, 0] < for_comparing.iloc[:, 1]
        increased_first_year = ts_shares_years[0].loc[:, is_increased_init].columns
        diffs = [annual_shares[annual_shares.diff() > 0] for annual_shares in ts_shares_years[1:]]
        is_increased = [diff.dropna(axis='columns', how='all').columns for diff in diffs]
        is_increased[0] = is_increased[0].append(increased_first_year)
        is_increased[0] = is_increased[0].drop_duplicates()
        years = ToolBox.get_entire_years(ts_shares_years)
        for year, is_increased_each_year in zip(years, is_increased):
            yield (year + 1), is_increased_each_year


if __name__ == "__main__":
    ts_data_loader = TimeSeriesDataLoader()
    ts_price = list(ts_data_loader.get_ts_data('price'))
    print(ts_price[0])