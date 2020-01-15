from workbench.const import CALENDAR
from pandas import DataFrame
from collections import OrderedDict, defaultdict
from workbench.utils import ToolBox


class Filter(object):
    pass


class CapSizeFilter(object):
    @staticmethod
    def get_annual_capsize_mean(ts_capsize):
        return [data.mean() for _, data in enumerate(ts_capsize)]

    @staticmethod
    def get_small_capsize(ts_capsize, ascending=True, percentile=0.2):
        """
        For getting small capsize companies data
        :param ts_capsize:
        :param ascending:
        :param percentile:
        :return:
        """
        for annual_data in ts_capsize:
            annual_data = annual_data.dropna()
            # 매년 시가총액 평균, 오름차순 정렬
            capsize_mean = annual_data.mean().sort_values(ascending=ascending)
            # 시가총액 하위 percentile
            target_range = round(len(capsize_mean) * percentile)  # pd.cut()
            yield annual_data.loc[:, capsize_mean.iloc[:target_range].index]

    @staticmethod
    def get_small_cap_price(ts_price_years, ts_data):
        """
        시가총액 하위 X % 기업의 가격 데이터를 얻기 위해
        :param ts_price:
        :param ts_data: ts_capsize_years
        :return: 시가총액 하위 X % 기업의 가격 데이터
        """
        enter_year = ToolBox.get_enter_year(ts_price_years)
        for i, annual_data in enumerate(ts_price_years):
            begin, end = CALENDAR.ENTER_DATE[enter_year + i], \
                         CALENDAR.ENTER_DATE[enter_year + (i + 1)]
            annual_data = annual_data.loc[begin:end]
            candidates = ToolBox.get_candidates(annual_data, begin)
            yield candidates.loc[:, candidates.columns.intersection(ts_data[i].columns)]


class RatioFilter(object):
    @staticmethod
    def get_filtered_ratio(fn_data_years, threshold, and_over=True):
        """
        To compare with factor value and threshold.
        :param fn_data_years:
        :param threshold:
        :param and_over: True (default): >=, False: <=
        :return:
        """
        for year, annual_data in fn_data_years.items():
            if and_over:
                annual_data = annual_data.loc[annual_data >= threshold]
            else:
                annual_data = annual_data.loc[annual_data <= threshold]
            yield year, annual_data

    @staticmethod  # 아무 조건 없이도 주문 가능한가?
    def get_candidate_by_pct_rank(fn_data_years: OrderedDict, ascending=True, cut_off=-1):
        """
        To extract top rank tickers by factor value
        :param fn_data_years:
        :param ascending:
        :param cut_off: default: -1
        :return:
        """
        def get_pct_rank_from_ratio(data, ascending):
            """

            :param data:
            :param ascending:
            :return: sort-guaranteed ?
            """
            pct_ranks = data.rank(ascending=ascending, pct=True).sort_values()
            pct_ranks.name = 'rank'
            return pct_ranks
        for year, annual_data in fn_data_years.items():
            annual_data.name = 'ratio'
            pct_ranks = get_pct_rank_from_ratio(annual_data, ascending)
            if cut_off == -1:  # -1 means all
                yield year, pct_ranks  # 참고한 재무 데이터가 발생한 해
            else:
                yield year, pct_ranks.head(cut_off)  # 참고한 재무 데이터가 발생한 해

    @staticmethod
    def integrate_score(*ratios):
        """

        :param ratios:
        :return: score_board
        """
        for year in ratios[0].keys():
            score_sum = defaultdict(int)
            for ratio in ratios:
                max_score = ratio[year].max()
                for ticker, pct_rank in ratio[year].items():
                    score_sum[ticker] += max_score - pct_rank
            yield year, sorted(score_sum.items(), key=lambda x: x[1], reverse=True)

    @staticmethod
    def get_candidate_by_score(fn_data_years, cut_off=-1):
        """

        :param fn_data_years: score_board
        :param cut_off:
        :return: candidates
        """
        for year, annual_data in fn_data_years.items():
            if cut_off == -1:  # -1 means all
                candidates = DataFrame(annual_data, columns=['ticker', 'score'])
            else:
                candidates = DataFrame(annual_data[:cut_off], columns=['ticker', 'score'])
            yield year, candidates.set_index(['ticker'])

    @staticmethod
    def get_ratio_filtered_ts_price(ts_price_years, fn_data_years):
        enter_year = ToolBox.get_enter_year(ts_price_years)  # 참고한 재무 데이터가 발생한 해 + 1 (실제 진입하는 해)
        for i, annual_data in enumerate(ts_price_years):
            begin, end = CALENDAR.ENTER_DATE[enter_year + i], \
                         CALENDAR.ENTER_DATE[enter_year + (i + 1)]
            annual_data = annual_data.loc[begin:end]
            candidates = ToolBox.get_candidates(annual_data, begin)
            targets = fn_data_years[enter_year - 1 + i].index
            yield candidates.loc[:, candidates.columns.intersection(targets)]
